from convert.registry import registry, register
from convert.models import ConversionRequest

def test_registry_registers():
    @register("md", "docx")
    def fake(req): return req
    assert ("md", "docx") in registry.list_pairs()

def test_registry_get():
    @register("txt", "md")
    def fake2(req): return req
    fn = registry.get("txt", "md")
    assert fn is not None
    assert fn is fake2

def test_registry_missing():
    fn = registry.get("unknown", "fmt")
    assert fn is None

def test_registry_list_pairs():
    pairs = registry.list_pairs()
    assert isinstance(pairs, list)
    assert ("md", "docx") in pairs
    assert ("txt", "md") in pairs