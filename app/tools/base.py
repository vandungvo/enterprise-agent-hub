"""Tool framework: typed inputs (pydantic), per-agent descriptions, approval gating."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, ConfigDict

from app.agents.registry import AgentSpec, Platform

if TYPE_CHECKING:
    from app.access import Principal


class ToolInput(BaseModel):
    model_config = ConfigDict(extra="forbid")


@dataclass
class ToolContext:
    user: Principal
    platform: Platform
    agent: AgentSpec
    conversation_id: int | None
    # Shared across the whole run (router + delegated specialists).
    sources: list[dict] = field(default_factory=list)
    approvals: list[dict] = field(default_factory=list)
    sensitive: list[str] = field(default_factory=list)  # restricted resources touched in this run

    def allowed_kbs(self) -> list[str]:
        user_kbs = {k.id for k in self.platform.kbs_for(self.user)}
        return [k for k in self.agent.knowledge_bases if k in user_kbs]


@dataclass
class ToolDef:
    name: str
    input_model: type[ToolInput]
    describe: Callable[[ToolContext], str]
    # Read tools implement `run`. Side-effecting tools implement `execute` (+ `summarize`,
    # `approvers`) and go through the approval queue when gated.
    run: Callable[[ToolContext, Any], str] | None = None
    execute: Callable[[dict, Principal], str] | None = None
    summarize: Callable[[dict, Principal], str] | None = None
    approvers: Callable[[dict, Principal], list[int]] | None = None  # employee ids who may approve
    requires_approval: bool = False
    validate: Callable[[ToolContext, Any], None] | None = None  # raise ValueError to reject early

    def needs_approval(self, agent: AgentSpec) -> bool:
        return agent.approval_override.get(self.name, self.requires_approval)

    def api_schema(self, ctx: ToolContext) -> dict:
        schema = _strip_titles(self.input_model.model_json_schema())
        schema.setdefault("properties", {})
        return {"name": self.name, "description": self.describe(ctx), "input_schema": schema,
                "eager_input_streaming": True}


def _strip_titles(node, in_properties: bool = False):
    """Drops pydantic's `title` annotations, but keeps a *property* that happens to be named `title`."""
    if isinstance(node, dict):
        return {k: _strip_titles(v, in_properties=(k == "properties" and not in_properties))
                for k, v in node.items() if in_properties or k != "title"}
    if isinstance(node, list):
        return [_strip_titles(v) for v in node]
    return node


REGISTRY: dict[str, ToolDef] = {}


def register(tool: ToolDef) -> ToolDef:
    REGISTRY[tool.name] = tool
    return tool
