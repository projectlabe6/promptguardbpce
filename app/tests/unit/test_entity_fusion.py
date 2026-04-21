from app.pipeline.entity_fusion import fuse_entities
from app.schemas.entity import Entity


def _make(type: str, start: int, end: int) -> Entity:
    return Entity(
        type=type, value="x", start=start, end=end, confidence=0.99, source="rules"
    )


def test_fuse_single_list():
    entities = [_make("EMAIL", 0, 5), _make("PHONE", 10, 20)]
    result = fuse_entities(entities)
    assert len(result) == 2


def test_fuse_multiple_lists():
    a = [_make("EMAIL", 0, 5)]
    b = [_make("PHONE", 10, 20)]
    result = fuse_entities(a, b)
    assert len(result) == 2


def test_removes_exact_duplicates():
    a = [_make("EMAIL", 0, 5)]
    b = [_make("EMAIL", 0, 5)]
    result = fuse_entities(a, b)
    assert len(result) == 1


def test_sorted_by_position():
    a = [_make("EMAIL", 10, 20)]
    b = [_make("PHONE", 0, 5)]
    result = fuse_entities(a, b)
    assert result[0].start == 0
    assert result[1].start == 10


def test_empty_lists():
    assert fuse_entities([], []) == []
