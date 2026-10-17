import pytest

from simulator.allocator import MemoryAllocator


def test_first_fit_allocation():
    allocator = MemoryAllocator(1000)

    assert allocator.allocate(1, 200, "first_fit") is True
    assert allocator.blocks[0]["pid"] == 1
    assert allocator.blocks[0]["size"] == 200


def test_best_fit_selects_smallest_suitable_block():
    allocator = MemoryAllocator(1000)

    allocator.allocate(1, 200)
    allocator.allocate(2, 300)
    allocator.allocate(3, 100)

    allocator.deallocate(1)
    allocator.deallocate(3)

    assert allocator.allocate(4, 80, "best_fit") is True

    allocated = next(
        block for block in allocator.blocks
        if block["pid"] == 4
    )

    assert allocated["start"] == 0


def test_worst_fit_selects_largest_suitable_block():
    allocator = MemoryAllocator(1000)

    allocator.allocate(1, 200)
    allocator.allocate(2, 300)
    allocator.allocate(3, 100)

    allocator.deallocate(1)
    allocator.deallocate(3)

    assert allocator.allocate(4, 80, "worst_fit") is True

    allocated = next(
        block for block in allocator.blocks
        if block["pid"] == 4
    )

    assert allocated["start"] == 500


def test_deallocation_merges_adjacent_free_blocks():
    allocator = MemoryAllocator(1000)

    allocator.allocate(1, 200)
    allocator.allocate(2, 300)

    assert allocator.deallocate(1) is True
    assert allocator.deallocate(2) is True

    assert len(allocator.blocks) == 1
    assert allocator.blocks[0]["size"] == 1000
    assert allocator.blocks[0]["pid"] is None


def test_external_fragmentation_calculation():
    allocator = MemoryAllocator(1000)

    allocator.allocate(1, 200)
    allocator.allocate(2, 300)
    allocator.allocate(3, 100)

    allocator.deallocate(1)
    allocator.deallocate(3)

    metrics = allocator.get_metrics()

    assert metrics["total_free_memory"] == 700
    assert metrics["largest_free_block"] == 500
    assert metrics["external_fragmentation_percent"] == 28.57

def test_allocation_fails_when_no_block_is_large_enough():
    allocator = MemoryAllocator(100)

    assert allocator.allocate(1, 80) is True
    assert allocator.allocate(2, 30) is False


def test_invalid_allocation_size():
    allocator = MemoryAllocator(100)

    with pytest.raises(ValueError):
        allocator.allocate(1, 0)


def test_unknown_algorithm():
    allocator = MemoryAllocator(100)

    with pytest.raises(ValueError):
        allocator.allocate(1, 10, "random_fit")
