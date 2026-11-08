"""Loads config/platform.yaml: agents, knowledge bases and who may use them."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

import yaml

from app.core.settings import settings

if TYPE_CHECKING:
    from app.access import Principal


@dataclass
class Access:
    """Allowed if the principal has ANY of `roles` (and level >= min_level)."""

    roles: list[str] = field(default_factory=lambda: ["employee"])
    min_level: int = 0

    def allows(self, p: Principal) -> bool:
        return bool(set(self.roles) & p.roles) and p.level >= self.min_level

    @classmethod
    def parse(cls, raw: dict | None) -> Access:
        raw = raw or {}
        return cls(roles=raw.get("roles", ["employee"]), min_level=raw.get("min_level", 0))


@dataclass
class KnowledgeBase:
    id: str
    name: str
    description: str
    access: Access
    managed_by: list[str]


@dataclass
class AgentSpec:
    id: str
    name: str
    role: str  # router | specialist
    model: str
    effort: str
    description: str
    system_prompt: str
    access: Access
    tools: list[str] = field(default_factory=list)
    knowledge_bases: list[str] = field(default_factory=list)
    approval_override: dict[str, bool] = field(default_factory=dict)


@dataclass
class Platform:
    company: dict[str, Any]
    knowledge_bases: dict[str, KnowledgeBase]
    agents: dict[str, AgentSpec]

    def agents_for(self, p: Principal) -> list[AgentSpec]:
        return [a for a in self.agents.values() if a.access.allows(p)]

    def specialists_for(self, p: Principal) -> list[AgentSpec]:
        return [a for a in self.agents_for(p) if a.role == "specialist"]

    def kbs_for(self, p: Principal) -> list[KnowledgeBase]:
        return [k for k in self.knowledge_bases.values() if k.access.allows(p)]

    def can_manage_kb(self, kb_id: str, p: Principal) -> bool:
        kb = self.knowledge_bases.get(kb_id)
        return kb is not None and bool(set(kb.managed_by) & p.roles)


def load_platform(path=None) -> Platform:
    with open(path or settings.config_path, encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    company = raw.get("company", {})
    kbs = {k["id"]: KnowledgeBase(k["id"], k["name"], k.get("description", ""), Access.parse(k.get("access")),
                                  k.get("managed_by", ["platform_admin"]))
           for k in raw.get("knowledge_bases", [])}
    agents: dict[str, AgentSpec] = {}
    for a in raw.get("agents", []):
        unknown = set(a.get("knowledge_bases", [])) - set(kbs)
        if unknown:
            raise ValueError(f"Agent {a['id']}: unknown knowledge bases {unknown}")
        agents[a["id"]] = AgentSpec(
            id=a["id"], name=a["name"], role=a.get("role", "specialist"), model=a.get("model", "claude-opus-5-5"),
            effort=a.get("effort", "medium"), description=a.get("description", ""),
            system_prompt=a["system_prompt"].replace("{company}", company.get("name", "công ty")),
            access=Access.parse(a.get("access")), tools=a.get("tools", []),
            knowledge_bases=a.get("knowledge_bases", []), approval_override=a.get("approval_override", {}))
    if sum(a.role == "router" for a in agents.values()) != 1:
        raise ValueError("Exactly one router agent is required")
    return Platform(company, kbs, agents)


_platform: Platform | None = None


def get_platform() -> Platform:
    global _platform
    if _platform is None:
        _platform = load_platform()
    return _platform


def reload_platform() -> Platform:
    global _platform
    _platform = load_platform()
    return _platform
