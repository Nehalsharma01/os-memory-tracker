from backend.monitoring.memory import get_memory_stats


def test_memory_and_swap_calculations(tmp_path):
    meminfo = tmp_path / "meminfo"
    meminfo.write_text(
        "MemTotal:       1000 kB\n"
        "MemAvailable:    400 kB\n"
        "MemFree:         300 kB\n"
        "SwapTotal:       500 kB\n"
        "SwapFree:        200 kB\n",
        encoding="utf-8",
    )

    stats = get_memory_stats(str(meminfo))

    assert stats["source"] == "linux-proc"
    assert stats["memory"]["total_kb"] == 1000
    assert stats["memory"]["available_kb"] == 400
    assert stats["memory"]["used_kb"] == 600
    assert stats["swap"]["total_kb"] == 500
    assert stats["swap"]["free_kb"] == 200
    assert stats["swap"]["used_kb"] == 300


def test_memory_without_swap(tmp_path):
    meminfo = tmp_path / "meminfo"
    meminfo.write_text(
        "MemTotal:       1000 kB\n"
        "MemAvailable:    700 kB\n",
        encoding="utf-8",
    )

    stats = get_memory_stats(str(meminfo))

    assert stats["memory"]["used_kb"] == 300
    assert stats["swap"]["total_kb"] == 0
    assert stats["swap"]["used_kb"] == 0
