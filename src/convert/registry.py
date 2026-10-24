"""Converter registry mapping (src, dst) -> converter function."""

from collections.abc import Callable
from types import SimpleNamespace

_REGISTRY: dict[tuple[str, str], Callable] = {}


def register(src: str, dst: str):
    """Decorator factory registering *fn* for the (src, dst) pair."""

    def deco(fn: Callable):
        _REGISTRY[(src, dst)] = fn
        return fn

    return deco


def list_pairs():
    return list(_REGISTRY.keys())


def get(src, dst):
    return _REGISTRY.get((src, dst))


# Backward-compatible namespace (cli and tests use registry.register/get/list_pairs/_d).
registry = SimpleNamespace(
    register=register,
    list_pairs=list_pairs,
    get=get,
    _d=_REGISTRY,
)
