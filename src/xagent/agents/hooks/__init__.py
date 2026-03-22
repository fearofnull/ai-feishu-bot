# -*- coding: utf-8 -*-
"""Agent hooks package.

This package provides hook implementations for CoPawAgent that follow
AgentScope's hook interface (any Callable).

Available Hooks:
    - MemoryCompactionHook: Automatic context window management

Example:
    >>> from copaw.agents.hooks import MemoryCompactionHook
    >>>
    >>> # Create hook (it's a callable following AgentScope's interface)
    >>> memory_compact = MemoryCompactionHook(
    ...     memory_manager=mm,
    ...     memory_compact_threshold=100000,
    ... )
    >>>
    >>> # Register with agent using AgentScope's register_instance_hook
    >>> agent.register_instance_hook(
    ...     "pre_reasoning", "compact", memory_compact
    ... )
"""

from .memory_compaction import MemoryCompactionHook

__all__ = [
    "MemoryCompactionHook",
]
