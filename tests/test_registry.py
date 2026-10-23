from convert.registry import register, registry


def test_registry_registers():
    @register("test_src", "test_dst")
    def fake(req):
        return req

    assert ("test_src", "test_dst") in registry.list_pairs()


def test_registry_get():
    @register("test_src2", "test_dst2")
    def fake2(req):
        return req

    fn = registry.get("test_src2", "test_dst2")
    assert fn is not None
    assert fn is fake2


def test_registry_missing():
    fn = registry.get("unknown", "fmt")
    assert fn is None


def test_registry_list_pairs():
    pairs = registry.list_pairs()
    assert isinstance(pairs, list)
    # Real converters should be registered
    assert ("md", "docx") in pairs
    assert ("txt", "md") in pairs
