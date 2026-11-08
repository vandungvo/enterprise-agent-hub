from app.policy import AccessDenied, principal_for
from app.registry import get_platform
from app.tools import REGISTRY, ToolContext


def P(key: str):
    """Principal for a demo persona, e.g. P('dev.alpha')."""
    p = principal_for(f"{key}@saomai.vn", 0)
    assert p is not None, key
    return p


def ctx_for(key: str, agent: str = "people") -> ToolContext:
    pl = get_platform()
    return ToolContext(user=P(key), platform=pl, agent=pl.agents[agent], conversation_id=None)


def run_tool(key: str, tool: str, agent: str = "people", **inp) -> str:
    ctx = ctx_for(key, agent)
    t = REGISTRY[tool]
    return t.run(ctx, t.input_model.model_validate(inp))


def denied(key: str, tool: str, agent: str = "people", **inp) -> bool:
    try:
        run_tool(key, tool, agent, **inp)
    except AccessDenied:
        return True
    return False
