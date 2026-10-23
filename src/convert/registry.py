from typing import Callable

class _Registry:
    def __init__(self):
        self._d = {}

    def register(self, src: str, dst: str):
        def deco(fn: Callable):
            self._d[(src, dst)] = fn
            return fn
        return deco

    def list_pairs(self):
        return list(self._d.keys())

    def get(self, src, dst):
        return self._d.get((src, dst))

registry = _Registry()
def register(src, dst): return registry.register(src, dst)