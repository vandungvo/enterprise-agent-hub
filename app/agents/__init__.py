"""Agents: registry (platform.yaml), multi-agent runtime and the conversation service.

Intentionally imports nothing: tools depend on agents.registry while agents.runtime depends on tools,
so import submodules explicitly (app.agents.registry / .runtime / .conversation).
"""
