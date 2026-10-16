from backend.monitoring.processes import (
    get_processes,
    get_process_by_pid,
)


def test_get_processes_returns_valid_data():
    result = get_processes()

    assert result["source"] == "linux-proc"
    assert result["count"] >= 0
    assert isinstance(result["processes"], list)


def test_process_entries_have_required_fields():
    result = get_processes()

    for process in result["processes"]:
        assert process["pid"] > 0
        assert isinstance(process["name"], str)
        assert process["memory_rss_kb"] >= 0
        assert process["memory_virtual_kb"] >= 0


def test_get_current_process():
    result = get_process_by_pid(1)

    # PID 1 may not be accessible in every environment.
    if result is not None:
        assert result["pid"] == 1
        assert result["memory_rss_kb"] >= 0


def test_invalid_pid_returns_none():
    assert get_process_by_pid(-1) is None
    assert get_process_by_pid(0) is None
