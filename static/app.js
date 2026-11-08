// Enterprise Agent Hub - web client (vanilla JS, no build step)
const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => [...el.querySelectorAll(s)];
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

const state = { token: null, me: null, conversationId: null, streaming: false, approvalScope: "mine", kb: null };
try { state.token = localStorage.getItem("agenthub_token"); } catch { /* storage unavailable */ }

const STATUS_VI = { pending: "Chờ duyệt", processing: "Đang xử lý", executed: "Đã thực hiện", rejected: "Từ chối", failed: "Lỗi" };
const CLASS_VI = { internal: "Nội bộ", confidential: "Mật", restricted: "Tuyệt mật" };
const TOOL_VI = {
  search_knowledge: "Tra cứu tài liệu", directory_search: "Tra danh bạ", get_org_chart: "Xem sơ đồ tổ chức",
  get_employee_profile: "Xem hồ sơ", get_payslip: "Xem phiếu lương", get_compensation_history: "Xem lịch sử lương",
  get_leave_balance: "Xem số dư phép", list_leave_requests: "Xem đơn nghỉ", team_calendar: "Xem lịch vắng mặt",
  submit_leave_request: "Nộp đơn nghỉ", workforce_analytics: "Phân tích nhân sự", budget_report: "Báo cáo ngân sách",
  submit_expense_claim: "Nộp đề nghị thanh toán", list_expense_claims: "Xem đề nghị thanh toán",
  create_ticket: "Tạo ticket IT", get_current_time: "Xem giờ", delegate_to_agent: "Giao việc cho agent",
};
const hasRole = (r) => state.me?.roles.some((x) => x.role === r);

// ------------------------------------------------------------------ API
async function api(path, opts = {}) {
  const headers = { ...(opts.headers || {}) };
  if (state.token) headers.Authorization = `Bearer ${state.token}`;
  if (opts.json !== undefined) { headers["Content-Type"] = "application/json"; opts.body = JSON.stringify(opts.json); }
  const res = await fetch(path, { ...opts, headers });
  if (res.status === 401) { logout(); throw new Error("Phiên đăng nhập đã hết hạn"); }
  if (!res.ok) {
    let detail = res.statusText;
    try { detail = (await res.json()).detail || detail; } catch { /* not json */ }
    throw new Error(detail);
  }
  return res.json();
}

function renderMarkdown(text) {
  const html = DOMPurify.sanitize(marked.parse(text || "", { breaks: true, gfm: true }));
  return html.replace(/\[(\d{1,3})\]/g, '<span class="cite" data-n="$1">[$1]</span>');
}

// ------------------------------------------------------------------ auth
async function showLogin() {
  $("#app-view").classList.add("hidden");
  $("#login-view").classList.remove("hidden");
  const { users, password } = await fetch("/api/demo-users").then((r) => r.json());
  $("#demo-user-list").innerHTML = users.map((u) => `
    <button class="demo-user" data-email="${esc(u.email)}" data-pw="${esc(password)}">
      <b>${esc(u.full_name)}</b><span class="muted small">${esc(u.title)}</span>
    </button>`).join("");
  $$(".demo-user").forEach((b) => b.onclick = () => doLogin(b.dataset.email, b.dataset.pw));
}

async function doLogin(email, password) {
  $("#login-error").textContent = "";
  try {
    const res = await api("/api/login", { method: "POST", json: { email, password } });
    state.token = res.token;
    try { localStorage.setItem("agenthub_token", res.token); } catch { /* ignore */ }
    await boot();
  } catch (e) { $("#login-error").textContent = e.message; }
}

function logout() {
  state.token = null; state.me = null;
  try { localStorage.removeItem("agenthub_token"); } catch { /* ignore */ }
  showLogin();
}

$("#login-form").onsubmit = (e) => { e.preventDefault(); doLogin($("#login-email").value, $("#login-password").value); };
$("#logout").onclick = logout;

// ------------------------------------------------------------------ boot & nav
async function boot() {
  if (!state.token) return showLogin();
  try { state.me = await api("/api/me"); } catch { return showLogin(); }
  const { user, agents } = state.me;
  $("#login-view").classList.add("hidden");
  $("#app-view").classList.remove("hidden");
  $("#me-name").textContent = user.full_name;
  $("#me-meta").textContent = `${user.title} · ${user.unit_path.slice(-1)[0]}`;
  const flags = {
    usage: state.me.can_view_usage, auditor: state.me.is_auditor,
    admin: state.me.is_platform_admin || state.me.is_auditor, approver: hasRole("manager") || hasRole("ceo"),
  };
  Object.entries(flags).forEach(([k, v]) => $$(`[data-requires=${k}]`).forEach((el) => el.classList.toggle("hidden", !v)));

  const router = agents.find((a) => a.role === "router");
  const specialists = agents.filter((a) => a.role === "specialist");
  $("#agent-select").innerHTML =
    (router ? `<option value="router">🧭 Tự động (${esc(router.name)})</option>` : "") +
    specialists.map((a) => `<option value="${esc(a.id)}">${esc(a.name)}</option>`).join("");
  updateAgentDesc();
  newChat();
  loadConversations();
  refreshApprovalBadge();
}

function updateAgentDesc() {
  const a = state.me.agents.find((x) => x.id === $("#agent-select").value);
  $("#agent-desc").textContent = a ? a.description : "";
}
$("#agent-select").onchange = () => { updateAgentDesc(); newChat(); };

function showView(name) {
  $$("#nav button").forEach((b) => b.classList.toggle("active", b.dataset.view === name));
  $$(".view").forEach((v) => v.classList.toggle("hidden", v.id !== `view-${name}`));
  if (name === "approvals") loadApprovals();
  if (name === "knowledge") loadKnowledge();
  if (name === "dashboard") loadDashboard();
  if (name === "admin") loadAdmin();
  if (name === "access") loadAccess();
  if (name === "audit") loadAudit();
}
$$("#nav button").forEach((b) => b.onclick = () => showView(b.dataset.view));

// ------------------------------------------------------------------ conversations
async function loadConversations() {
  const convs = await api("/api/conversations");
  $("#conversation-list").innerHTML = convs.map((c) => `
    <li data-id="${c.id}" class="${c.id === state.conversationId ? "active" : ""}">
      <span title="${esc(c.title)}${c.sensitive ? " (chứa dữ liệu nhạy cảm, tự xoá theo chính sách lưu trữ)" : ""}">${c.sensitive ? "🔒 " : ""}${esc(c.title)}</span><button class="del" data-id="${c.id}" title="Xoá">✕</button>
    </li>`).join("") || `<li class="muted small">Chưa có cuộc trò chuyện</li>`;
  $$("#conversation-list li[data-id]").forEach((li) => li.onclick = (e) => {
    if (e.target.classList.contains("del")) return;
    openConversation(Number(li.dataset.id));
  });
  $$("#conversation-list .del").forEach((b) => b.onclick = async () => {
    await api(`/api/conversations/${b.dataset.id}`, { method: "DELETE" });
    if (Number(b.dataset.id) === state.conversationId) newChat();
    loadConversations();
  });
}

function suggestions() {
  const s = [
    "Giải thích phiếu lương tháng gần nhất của tôi: vì sao thực nhận thấp hơn gross?",
    "Tôi còn bao nhiêu ngày phép? Phép năm nay có được chuyển sang năm sau không?",
    "Tôi muốn nghỉ phép năm thứ Hai và thứ Ba tuần sau vì việc gia đình",
    "Sao Mai Group có những công ty thành viên nào? Ai phụ trách Sao Mai Pay?",
  ];
  if (hasRole("manager")) s.push("Tuần này và tuần sau team tôi có ai nghỉ không? Lương trung bình của team theo cấp bậc?");
  if (hasRole("exec") || hasRole("chro") || hasRole("cfo"))
    s.push("Tỷ lệ nghỉ việc và quỹ lương 6 tháng gần nhất theo từng khối? Có điểm gì cần lưu ý?",
      "Ngân sách năm nay của các khối đang vượt hay dưới kế hoạch?");
  else s.push("Cho tôi xem lương của Trịnh Gia Huy (dev.alpha@saomai.vn)");
  return s;
}

function newChat() {
  state.conversationId = null;
  $("#agent-select").disabled = false;
  $$("#conversation-list li").forEach((li) => li.classList.remove("active"));
  $("#messages").innerHTML = `
    <div class="empty-state">
      <h2>Xin chào ${esc(state.me.user.full_name)} 👋</h2>
      <p class="muted">Hỏi mọi điều về tập đoàn, lương, phép, IT, tài chính… Trợ lý điều phối chuyển yêu cầu tới
      agent chuyên môn và chỉ dùng dữ liệu trong phạm vi quyền của bạn (xem mục 🔐 Quyền của tôi).</p>
      <div class="suggestions">${suggestions().map((s) => `<button>${esc(s)}</button>`).join("")}</div>
    </div>`;
  $$(".suggestions button").forEach((b) => b.onclick = () => { $("#chat-input").value = b.textContent; sendMessage(); });
  showView("chat");
}
$("#new-chat").onclick = newChat;

async function openConversation(id) {
  const conv = await api(`/api/conversations/${id}`);
  state.conversationId = id;
  $("#agent-select").value = conv.agent_id;
  $("#agent-select").disabled = true;
  updateAgentDesc();
  $("#messages").innerHTML = "";
  for (const m of conv.messages) {
    if (m.role === "user") addUserMessage(m.content);
    else {
      const view = addAssistantMessage();
      view.setText(m.content);
      view.setTrace(m.trace || []);
      view.finish({ message_id: m.id, sources: m.sources || [], approvals: approvalsFromTrace(m.trace || []), feedback: m.feedback });
    }
  }
  $$("#conversation-list li").forEach((li) => li.classList.toggle("active", Number(li.dataset.id) === id));
  showView("chat");
  scrollBottom();
}

const approvalsFromTrace = (trace) => trace.filter((t) => t.event === "approval");

// ------------------------------------------------------------------ chat rendering
function scrollBottom() { const m = $("#messages"); m.scrollTop = m.scrollHeight; }

function addUserMessage(text) {
  $(".empty-state")?.remove();
  const div = document.createElement("div");
  div.className = "msg user";
  div.textContent = text;
  $("#messages").appendChild(div);
}

function traceLine(t) {
  const who = `<span class="agent-tag">${esc(t.agent_name || t.agent_id)}</span>`;
  const cls = `d${Math.min(t.depth || 0, 1)}${t.is_error || (t.event === "agent_end" && t.status !== "ok") ? " err" : ""}`;
  switch (t.event) {
    case "agent_start": return `<li class="${cls}">▶ ${who} bắt đầu xử lý</li>`;
    case "tool_call": {
      if (t.tool === "delegate_to_agent") {
        const target = state.me.agents.find((a) => a.id === t.input?.agent_id);
        return `<li class="${cls}">↪ ${who} giao việc cho <b>${esc(target?.name || t.input?.agent_id)}</b>: ${esc(t.input?.task || "")}</li>`;
      }
      const i = t.input || {};
      const arg = i.query || i.employee || (i.metric ? `${i.metric}${i.group_by && i.group_by !== "none" ? " theo " + i.group_by : ""}${i.unit_code ? " · " + i.unit_code : ""}` : "")
        || i.unit_code || i.period || i.title || (i.start_date ? `${i.start_date} → ${i.end_date}` : "");
      return `<li class="${cls}">🔧 ${who} · ${esc(TOOL_VI[t.tool] || t.tool)}${arg ? `: <code>${esc(arg)}</code>` : ""}</li>`;
    }
    case "tool_result":
      if (t.tool === "delegate_to_agent") return "";
      if ((t.preview || "").startsWith("TỪ CHỐI TRUY CẬP"))
        return `<li class="${cls}">🚫 ${esc(TOOL_VI[t.tool] || t.tool)}: bị chính sách phân quyền chặn</li>`;
      return `<li class="${cls}">${t.is_error ? "⚠️" : "✓"} ${esc(TOOL_VI[t.tool] || t.tool)} → ${esc((t.preview || "").slice(0, 220))}</li>`;
    case "approval": return `<li class="${cls}">⏳ Tạo yêu cầu phê duyệt #${t.action_id}</li>`;
    case "agent_end": return t.depth > 0 ? `<li class="${cls}">■ ${who} hoàn tất${t.status !== "ok" ? ` (${esc(t.text)})` : ""}</li>` : "";
    case "warning": return `<li class="${cls}">⚠️ ${esc(t.text)}</li>`;
    default: return "";
  }
}

function addAssistantMessage() {
  const div = document.createElement("div");
  div.className = "msg assistant";
  div.innerHTML = `
    <details class="trace hidden"><summary>Quá trình xử lý (<span class="steps">0</span> bước)</summary><ol></ol></details>
    <div class="status-line hidden"></div>
    <div class="content"></div>
    <div class="approvals"></div>
    <div class="sources hidden"></div>
    <div class="msg-actions hidden"></div>`;
  $("#messages").appendChild(div);
  let text = "", pending = false;
  const trace = [];
  const render = () => { pending = false; $(".content", div).innerHTML = renderMarkdown(text); scrollBottom(); };
  return {
    el: div,
    appendText(t) { text += t; $(".content", div).classList.add("typing"); if (!pending) { pending = true; requestAnimationFrame(render); } },
    setText(t) { text = t; render(); },
    status(s) { const el = $(".status-line", div); el.textContent = s; el.classList.toggle("hidden", !s); },
    addTrace(t) {
      trace.push(t);
      const html = traceLine(t);
      if (!html) return;
      $(".trace", div).classList.remove("hidden");
      $(".trace ol", div).insertAdjacentHTML("beforeend", html);
      $(".trace .steps", div).textContent = $$(".trace li", div).length;
    },
    setTrace(list) { list.forEach((t) => this.addTrace(t)); },
    finish({ message_id, sources = [], approvals = [], feedback = null }) {
      $(".content", div).classList.remove("typing");
      this.status("");
      render();
      $(".approvals", div).innerHTML = approvals.map((a) =>
        `<div class="approval-card"><b>⏳ Chờ phê duyệt #${a.action_id}</b>\n${esc(a.summary)}</div>`).join("");
      if (sources.length) {
        const s = $(".sources", div);
        s.classList.remove("hidden");
        s.innerHTML = `<b>Nguồn tham khảo</b>` + sources.map((src) => `
          <details><summary>[${src.n}] ${esc(src.doc_title)}${src.heading ? " › " + esc(src.heading.split(" > ").slice(-1)[0]) : ""}
            <span class="muted">(${esc(src.kb_name || src.kb_id)})</span></summary><div class="snippet">${esc(src.text)}</div></details>`).join("");
        $$(".cite", div).forEach((c) => {
          const src = sources.find((x) => String(x.n) === c.dataset.n);
          if (src) c.title = `${src.doc_title}\n\n${src.text.slice(0, 300)}…`;
        });
      }
      if (message_id) {
        const acts = $(".msg-actions", div);
        acts.classList.remove("hidden");
        acts.innerHTML = `<button data-v="1" class="${feedback === 1 ? "on" : ""}">👍 Hữu ích</button>
                          <button data-v="-1" class="${feedback === -1 ? "on" : ""}">👎 Chưa tốt</button>`;
        $$("button", acts).forEach((b) => b.onclick = async () => {
          await api(`/api/messages/${message_id}/feedback`, { method: "POST", json: { value: Number(b.dataset.v) } });
          $$("button", acts).forEach((x) => x.classList.toggle("on", x === b));
        });
      }
    },
  };
}

// ------------------------------------------------------------------ send / stream
async function sendMessage() {
  const input = $("#chat-input");
  const text = input.value.trim();
  if (!text || state.streaming) return;
  input.value = "";
  state.streaming = true;
  $("#send-btn").disabled = true;
  addUserMessage(text);
  const view = addAssistantMessage();
  view.status("Đang xử lý…");
  scrollBottom();

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${state.token}` },
      body: JSON.stringify({ message: text, conversation_id: state.conversationId, agent_id: $("#agent-select").value }),
    });
    if (!res.ok) throw new Error((await res.json().catch(() => ({}))).detail || res.statusText);
    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buf = "";
    for (;;) {
      const { value, done } = await reader.read();
      if (done) break;
      buf += decoder.decode(value, { stream: true });
      let idx;
      while ((idx = buf.indexOf("\n\n")) >= 0) {
        const line = buf.slice(0, idx).trim();
        buf = buf.slice(idx + 2);
        if (line.startsWith("data:")) handleEvent(JSON.parse(line.slice(5)), view);
      }
    }
  } catch (e) {
    view.appendText(`\n\n⚠️ ${e.message}`);
    view.finish({});
  } finally {
    state.streaming = false;
    $("#send-btn").disabled = false;
    loadConversations();
    refreshApprovalBadge();
  }
}

function handleEvent(ev, view) {
  switch (ev.type) {
    case "conversation":
      state.conversationId = ev.conversation_id;
      $("#agent-select").disabled = true;
      break;
    case "text":
      if (ev.depth === 0) { view.status(""); view.appendText(ev.text); }
      break;
    case "agent_start":
      view.status(`${ev.agent_name} đang xử lý…`);
      view.addTrace({ ...ev, event: ev.type });
      break;
    case "tool_call":
      view.status(`${ev.agent_name}: ${TOOL_VI[ev.tool] || ev.tool}…`);
      view.addTrace({ ...ev, event: ev.type });
      break;
    case "tool_result": case "approval": case "agent_end": case "warning":
      view.addTrace({ ...ev, event: ev.type });
      break;
    case "done":
      if (ev.content) view.setText(ev.content);
      view.finish(ev);
      break;
    case "error":
      view.appendText(`\n\n⚠️ ${ev.text}`);
      view.finish({});
      break;
  }
}

$("#chat-form").onsubmit = (e) => { e.preventDefault(); sendMessage(); };
$("#chat-input").onkeydown = (e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMessage(); } };

// ------------------------------------------------------------------ approvals
async function refreshApprovalBadge() {
  if (!(hasRole("manager") || hasRole("ceo"))) return;
  try {
    const list = await api("/api/approvals?scope=review");
    const n = list.filter((a) => a.status === "pending" && a.requested_by !== state.me.user.full_name).length;
    $("#approval-badge").textContent = n;
    $("#approval-badge").classList.toggle("hidden", !n);
  } catch { /* ignore */ }
}

$$(".tabs .tab").forEach((t) => t.onclick = () => {
  state.approvalScope = t.dataset.scope;
  $$(".tabs .tab").forEach((x) => x.classList.toggle("active", x === t));
  loadApprovals();
});

async function loadApprovals() {
  const list = await api(`/api/approvals?scope=${state.approvalScope}`);
  const reviewing = state.approvalScope === "review";
  $("#approval-list").innerHTML = list.map((a) => `
    <div class="action">
      <div class="row" style="justify-content:space-between">
        <span><b>#${a.id}</b> · ${esc(TOOL_VI[a.tool] || a.tool)} · ${esc(a.requested_by)} → duyệt: ${esc(a.approvers.join(", "))} · <span class="muted small">${esc(new Date(a.created_at + "Z").toLocaleString("vi-VN"))}</span></span>
        <span class="pill ${a.status}">${STATUS_VI[a.status] || a.status}</span>
      </div>
      <div class="summary">${esc(a.summary)}</div>
      ${a.result ? `<div class="muted small">Kết quả: ${esc(a.result)}${a.decided_by ? ` — bởi ${esc(a.decided_by)}` : ""}${a.decision_note ? ` (“${esc(a.decision_note)}”)` : ""}</div>` : ""}
      ${reviewing && a.status === "pending" ? `
        <div class="row">
          <input placeholder="Ghi chú (tuỳ chọn)" data-note="${a.id}" />
          <button class="primary" data-decide="${a.id}" data-approve="1">Duyệt & thực hiện</button>
          <button data-decide="${a.id}" data-approve="0">Từ chối</button>
        </div>` : ""}
    </div>`).join("") || `<p class="muted">Không có yêu cầu nào.</p>`;
  $$("[data-decide]").forEach((b) => b.onclick = async () => {
    b.disabled = true;
    try {
      await api(`/api/approvals/${b.dataset.decide}/decision`, {
        method: "POST", json: { approve: b.dataset.approve === "1", note: $(`[data-note="${b.dataset.decide}"]`).value || null },
      });
    } catch (e) { alertInline(e.message); }
    loadApprovals();
    refreshApprovalBadge();
  });
}

function alertInline(msg) {
  const p = document.createElement("p");
  p.className = "error";
  p.textContent = msg;
  $("#approval-list").prepend(p);
}

// ------------------------------------------------------------------ knowledge
function loadKnowledge() {
  $("#kb-list").innerHTML = state.me.knowledge_bases.map((k) => `
    <div class="kb ${state.kb === k.id ? "active" : ""}" data-kb="${esc(k.id)}">
      <b>${esc(k.name)}</b><div class="muted small">${esc(k.description)}</div>
      ${k.can_manage ? `<div class="small" style="color:var(--ok)">Bạn có quyền quản lý</div>` : ""}
    </div>`).join("");
  $$(".kb").forEach((el) => el.onclick = () => { state.kb = el.dataset.kb; loadKnowledge(); });
  if (state.kb) loadKbDetail();
}

async function loadKbDetail() {
  const kb = state.me.knowledge_bases.find((k) => k.id === state.kb);
  $("#kb-detail").classList.remove("hidden");
  $("#kb-title").textContent = kb.name;
  $("#upload-form").classList.toggle("hidden", !kb.can_manage);
  const docs = await api(`/api/kbs/${kb.id}/documents`);
  $("#doc-table").innerHTML = docs.map((d) => `
    <tr><td>${esc(d.title)}<div class="muted small">${esc(d.filename)}</div></td>
    <td><span class="pill cls-${esc(d.classification)}">${esc(CLASS_VI[d.classification] || d.classification)}</span>
      <span class="muted small">${d.acl?.roles ? "vai trò: " + esc(d.acl.roles.join(", ")) : ""}${d.acl?.min_level ? " · cấp ≥ L" + d.acl.min_level : ""}</span></td>
    <td>${d.num_chunks}</td>
    <td>${kb.can_manage ? `<button class="small" data-del="${d.id}">Xoá</button>` : ""}</td></tr>`).join("")
    || `<tr><td colspan="4" class="muted">Chưa có tài liệu</td></tr>`;
  $$("[data-del]").forEach((b) => b.onclick = async () => {
    await api(`/api/documents/${b.dataset.del}`, { method: "DELETE" });
    loadKbDetail();
  });
}

$("#upload-form").onsubmit = async (e) => {
  e.preventDefault();
  const file = $("#upload-file").files[0];
  if (!file) return;
  const fd = new FormData();
  fd.append("file", file);
  if ($("#upload-title").value) fd.append("title", $("#upload-title").value);
  fd.append("classification", $("#upload-class").value);
  if ($("#upload-roles").value) fd.append("roles", $("#upload-roles").value);
  if ($("#upload-level").value) fd.append("min_level", $("#upload-level").value);
  $("#upload-status").textContent = "Đang xử lý…";
  try {
    const r = await api(`/api/kbs/${state.kb}/documents`, { method: "POST", body: fd });
    $("#upload-status").textContent = `Đã index ${r.num_chunks} đoạn.`;
    e.target.reset();
    loadKbDetail();
  } catch (err) { $("#upload-status").textContent = `Lỗi: ${err.message}`; }
};

$("#search-form").onsubmit = async (e) => {
  e.preventDefault();
  const hits = await api("/api/kbs/search", { method: "POST", json: { query: $("#search-q").value, kb_ids: [state.kb] } });
  $("#search-results").innerHTML = hits.map((h, i) => `
    <div class="hit"><b>#${i + 1} ${esc(h.doc_title)}</b> <span class="muted small">${esc(h.heading)} · score ${h.score}</span>\n${esc(h.text)}</div>`).join("")
    || `<p class="muted">Không có kết quả.</p>`;
};

// ------------------------------------------------------------------ dashboard
const fmt = (n) => Number(n || 0).toLocaleString("vi-VN");
const usd = (n) => "$" + Number(n || 0).toFixed(4);

function breakdownTable(obj, labelFn = (k) => k) {
  const entries = Object.entries(obj);
  if (!entries.length) return `<p class="muted">Chưa có dữ liệu</p>`;
  const max = Math.max(...entries.map(([, v]) => v.calls));
  return `<table class="table"><thead><tr><th>Nhóm</th><th>Lượt gọi</th><th></th><th>Người dùng</th><th>Output tokens</th><th>Chi phí</th><th>Độ trễ TB</th></tr></thead><tbody>` +
    entries.sort((a, b) => b[1].calls - a[1].calls).map(([k, v]) => `
      <tr><td>${esc(labelFn(k))}</td><td>${fmt(v.calls)}</td><td style="width:90px"><div class="bar" style="width:${(v.calls / max) * 100}%"></div></td>
      <td>${v.active_users}</td><td>${fmt(v.output_tokens)}</td><td>${usd(v.cost_usd)}</td><td>${fmt(v.avg_latency_ms)} ms</td></tr>`).join("") +
    `</tbody></table>`;
}

async function loadDashboard() {
  const d = await api(`/api/metrics?days=${$("#dash-days").value}`);
  const deptName = (k) => k;
  const agentName = (k) => state.me.agents.find((a) => a.id === k)?.name || k;
  $("#dash-scope").textContent = `(${d.scope})`;
  const t = d.totals;
  const fbTotal = t.feedback_up + t.feedback_down;
  const tiles = [
    ["Người dùng hoạt động", `${t.active_users}/${t.total_users}`, `Tỷ lệ adoption ${(t.adoption_rate * 100).toFixed(0)}%`],
    ["Cuộc trò chuyện", fmt(t.conversations), ""],
    ["Lượt gọi model", fmt(t.llm_calls), `${t.refusals} lượt bị từ chối`],
    ["Chi phí ước tính", usd(t.cost_usd), "theo bảng giá API"],
    ["Độ trễ TB / lượt gọi", `${fmt(t.avg_latency_ms)} ms`, ""],
    ["Cache hit rate", `${(t.cache_hit_rate * 100).toFixed(0)}%`, "input tokens đọc từ cache"],
    ["Mức hài lòng", fbTotal ? `${((t.feedback_up / fbTotal) * 100).toFixed(0)}%` : "—", `👍 ${t.feedback_up} · 👎 ${t.feedback_down}`],
    ["Truy cập dữ liệu bị chặn", fmt(t.denied_data_access), "theo chính sách phân quyền"],
  ];
  $("#dash-tiles").innerHTML = tiles.map(([l, v, s]) => `<div class="tile"><div class="l">${l}</div><div class="v">${v}</div><div class="muted small">${s}</div></div>`).join("");
  $("#dash-dept").innerHTML = breakdownTable(d.by_department, deptName);
  $("#dash-agent").innerHTML = breakdownTable(d.by_agent, agentName);
  $("#dash-day").innerHTML = breakdownTable(d.by_day);
  $("#dash-tools").innerHTML =
    `<table class="table"><thead><tr><th>Tool</th><th>Lượt</th><th>Lỗi</th><th>Độ trễ TB</th></tr></thead><tbody>` +
    (d.tools.map((x) => `<tr><td>${esc(TOOL_VI[x.tool] || x.tool)}</td><td>${x.calls}</td><td>${x.errors}</td><td>${fmt(x.avg_latency_ms)} ms</td></tr>`).join("")
      || `<tr><td colspan="4" class="muted">Chưa có dữ liệu</td></tr>`) + `</tbody></table>` +
    `<b>Phê duyệt:</b> ` + (Object.entries(d.approvals).map(([k, v]) => `${STATUS_VI[k] || k}: ${v}`).join(" · ") || "—");
}
$("#dash-refresh").onclick = loadDashboard;
$("#dash-days").onchange = loadDashboard;

// ------------------------------------------------------------------ admin
async function loadAdmin() {
  const [agents, audit, policies] = await Promise.all([
    api("/api/admin/agents"), api("/api/admin/audit?limit=50"), api("/api/admin/policies")]);
  $("#policy-table").innerHTML = Object.entries(policies).map(([res, spec]) => `
    <div class="agent-card"><b>${esc(res)}</b> <span class="pill cls-${esc(spec.classification)}">${esc(CLASS_VI[spec.classification] || spec.classification)}</span>
      <div class="muted small">${esc(spec.description || "")}</div>
      <div class="small">${spec.rules.map((r) => `<code>${esc(r.role || "mọi người")} → ${esc(r.scope)}${r.min_group_size ? ` · k=${r.min_group_size}` : ""}${r.audit === "sensitive" ? " · audit" : ""}</code>`).join(" ")}</div>
    </div>`).join("");
  $("#agent-cards").innerHTML = agents.map((a) => `
    <div class="agent-card">
      <div class="row" style="justify-content:space-between"><b>${esc(a.name)}</b>
        <span class="muted small">${esc(a.id)} · ${esc(a.role)} · ${esc(a.model)} · effort ${esc(a.effort)}</span></div>
      <div class="muted">${esc(a.description)}</div>
      <div class="small">Ai được dùng: vai trò ${esc(a.access.roles.join(", "))}${a.access.min_level ? ` · cấp ≥ L${a.access.min_level}` : ""}</div>
      <div class="small">Tools: ${a.tools.map((t) => `<code>${esc(t)}</code>${a.approval[t] ? " (cần duyệt)" : ""}`).join(" ") || "—"}</div>
      <div class="small">Knowledge: ${a.knowledge_bases.map((k) => `<code>${esc(k)}</code>`).join(" ") || "—"}</div>
      <details><summary class="small">System prompt</summary><pre>${esc(a.system_prompt)}</pre></details>
    </div>`).join("");
  $("#audit-table").innerHTML = audit.map((t) => `
    <tr><td class="small">${esc(new Date(t.created_at + "Z").toLocaleString("vi-VN"))}</td><td>${esc(t.user)}</td><td>${esc(t.agent_id)}</td>
    <td>${esc(t.tool)}${t.is_error ? " ⚠️" : ""}</td><td class="small"><code>${esc(JSON.stringify(t.input).slice(0, 160))}</code></td>
    <td class="small">${esc(t.output_preview.slice(0, 160))}</td></tr>`).join("") || `<tr><td colspan="6" class="muted">Chưa có dữ liệu</td></tr>`;
}
$("#reload-config").onclick = async () => {
  const btn = $("#reload-config");
  try {
    const r = await api("/api/admin/reload", { method: "POST" });
    state.me = await api("/api/me");
    loadAdmin();
    btn.textContent = `Đã tải lại: ${r.agents} agent, ${r.knowledge_bases} KB`;
  } catch (e) { btn.textContent = `Lỗi: ${e.message}`; }
  setTimeout(() => { btn.textContent = "Tải lại cấu hình"; }, 4000);
};

// ------------------------------------------------------------------ my access & audit
const fmtTime = (t) => esc(new Date(t + "Z").toLocaleString("vi-VN"));

async function loadAccess() {
  const me = state.me;
  $("#access-identity").innerHTML = `
    <div><b>${esc(me.user.full_name)}</b> · ${esc(me.user.title)} · cấp L${me.user.level}</div>
    <div class="muted small">${esc(me.user.unit_path.join(" › "))}</div>
    <div class="row">${me.roles.map((r) => `<span class="pill">${esc(r.label)}${r.scope.length && r.role !== "employee" ? ": " + esc(r.scope.join(", ")) : ""}</span>`).join("")}</div>`;
  $("#access-matrix").innerHTML = me.permissions.map((x) => `
    <tr><td>${esc(x.description)}<div class="muted small"><code>${esc(x.resource)}</code></div></td>
    <td><span class="pill cls-${esc(x.classification)}">${esc(CLASS_VI[x.classification] || x.classification)}</span></td>
    <td class="${x.scope === "Không" ? "muted" : ""}">${esc(x.scope)}</td></tr>`).join("");
  const log = await api("/api/my-data-access");
  $("#access-log").innerHTML = log.map((r) => `<tr><td class="small">${fmtTime(r.created_at)}</td><td>${esc(r.actor)}</td><td><code>${esc(r.resource)}</code></td></tr>`).join("")
    || `<tr><td colspan="3" class="muted">Chưa có ai truy cập dữ liệu nhạy cảm của bạn.</td></tr>`;
}

async function loadAudit() {
  const rows = await api(`/api/audit/data-access?denied_only=${$("#audit-denied").checked}`);
  $("#audit-log").innerHTML = rows.map((r) => `
    <tr><td class="small">${fmtTime(r.created_at)}</td><td>${esc(r.actor)}</td>
    <td><code>${esc(r.resource)}</code> <span class="pill cls-${esc(r.classification)}">${esc(CLASS_VI[r.classification] || r.classification)}</span></td>
    <td>${esc(r.target || r.scope || "")}</td>
    <td>${r.allowed ? `<span class="pill executed">Cho phép</span>` : `<span class="pill rejected">Từ chối</span>`}</td></tr>`).join("")
    || `<tr><td colspan="5" class="muted">Chưa có dữ liệu</td></tr>`;
}
$("#audit-denied").onchange = loadAudit;

boot();
