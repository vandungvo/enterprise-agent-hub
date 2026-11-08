import asyncio

from sqlalchemy import select

from app.db import PendingAction, SessionLocal, ToolCall
from app.orchestrator import AgentRuntime
from app.registry import get_platform
from app.settings import settings
from app.tools import ToolContext
from tests.fake_claude import FakeClaude, text, tool
from tests.helpers import P


async def _collect(runtime, agent, messages, ctx):
    return [ev async for ev in runtime.run(agent, messages, ctx)]


def _ctx(key, agent):
    pl = get_platform()
    return ToolContext(user=P(key), platform=pl, agent=pl.agents[agent], conversation_id=None)


def test_router_delegates_and_leave_goes_to_direct_manager():
    pl = get_platform()
    fake = FakeClaude([
        [tool("delegate_to_agent", agent_id="people", task="Nộp đơn nghỉ phép năm 2 ngày cho Huy")],
        [tool("search_knowledge", query="thủ tục nghỉ phép")],
        [tool("submit_leave_request", start_date="2030-01-07", end_date="2030-01-08", leave_type="annual",
              reason="Việc gia đình")],
        [text("Đã gửi đơn, chờ quản lý duyệt [1].")],
        [text("Đơn nghỉ đã gửi tới quản lý trực tiếp [1].")],
    ])
    ctx = _ctx("dev.alpha", "router")
    messages = [{"role": "user", "content": "Cho tôi nghỉ 7-8/1/2030"}]
    events = asyncio.run(_collect(AgentRuntime(client=fake), pl.agents["router"], messages, ctx))

    assert [e for e in events if e["type"] == "agent_end" and e["depth"] == 0][0]["status"] == "ok"
    enum = next(t for t in fake.calls[0]["tools"] if t["name"] == "delegate_to_agent")["input_schema"]["properties"]["agent_id"]["enum"]
    assert "people" in enum and "insights" not in enum  # staff cannot reach the leadership analyst
    assert [m["role"] for m in messages] == ["user", "assistant", "user", "assistant"]
    # identity block tells the model who is authenticated
    assert "dev.alpha@saomai.vn" in fake.calls[0]["system"][1]["text"]

    with SessionLocal() as db:
        action = db.scalars(select(PendingAction).order_by(PendingAction.id.desc())).first()
    assert action.tool == "submit_leave_request" and action.status == "pending"
    assert action.approver_ids == [P("manager.alpha").employee_id]


def test_denied_tool_call_is_reported_and_output_redacted_in_ops_log():
    fake = FakeClaude([
        [tool("get_payslip", employee="manager.alpha@saomai.vn")],
        [tool("get_payslip")],
        [text("Bạn không có quyền xem lương người khác. Đây là phiếu lương của bạn.")],
    ])
    ctx = _ctx("dev.alpha", "people")
    events = asyncio.run(_collect(AgentRuntime(client=fake), ctx.agent, [{"role": "user", "content": "x"}], ctx))
    results = [e for e in events if e["type"] == "tool_result"]
    assert results[0]["is_error"] and results[0]["preview"].startswith("TỪ CHỐI TRUY CẬP")
    assert not results[1]["is_error"]
    assert "compensation.individual" in ctx.sensitive  # conversation gets flagged sensitive
    with SessionLocal() as db:
        last = db.scalars(select(ToolCall).where(ToolCall.tool == "get_payslip").order_by(ToolCall.id.desc())).first()
    assert "net" not in last.output_preview and "ẩn" in last.output_preview  # platform admins can't read salaries in logs


def test_invalid_tool_input_returns_error_result():
    fake = FakeClaude([[tool("create_ticket", title="VPN lỗi")], [text("Cần thêm thông tin.")]])
    ctx = _ctx("newbie", "it_helpdesk")
    messages = [{"role": "user", "content": "Tạo ticket"}]
    events = asyncio.run(_collect(AgentRuntime(client=fake), ctx.agent, messages, ctx))
    assert next(e for e in events if e["type"] == "tool_result")["is_error"]
    assert messages[2]["content"][0]["is_error"] is True


def test_agent_cannot_use_tools_outside_config():
    fake = FakeClaude([[tool("get_payslip")], [text("Không thể.")]])
    ctx = _ctx("newbie", "it_helpdesk")
    events = asyncio.run(_collect(AgentRuntime(client=fake), ctx.agent, [{"role": "user", "content": "x"}], ctx))
    res = next(e for e in events if e["type"] == "tool_result")
    assert res["is_error"] and "không khả dụng" in res["preview"]


def test_last_round_disables_tools():
    n = settings.max_agent_iterations
    fake = FakeClaude([[tool("get_current_time")] for _ in range(n - 1)] + [[text("Xong.")]])
    ctx = _ctx("newbie", "company_info")
    events = asyncio.run(_collect(AgentRuntime(client=fake), ctx.agent, [{"role": "user", "content": "x"}], ctx))
    assert fake.calls[-1]["tool_choice"] == {"type": "none"} and events[-1]["status"] == "ok"
