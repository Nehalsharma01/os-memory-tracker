from backend.monitoring.processes import read_process
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
        assert process["minor_faults_total"] >= 0
        assert process["major_faults_total"] >= 0

def test_get_current_process():
    result = get_process_by_pid(1)

    # PID 1 may not be accessible in every environment.
    if result is not None:
        assert result["pid"] == 1
        assert result["memory_rss_kb"] >= 0


def test_invalid_pid_returns_none():
    assert get_process_by_pid(-1) is None
    assert get_process_by_pid(0) is None
def test_process_page_fault_counters(tmp_path):
    process_dir = tmp_path / "123"
    process_dir.mkdir()

    (process_dir / "status").write_text(
        "Name:\ttestprocess\n"
        "VmRSS:\t100 kB\n"
        "VmSize:\t200 kB\n"
    )

    # Fields after the closing parenthesis begin with field 3.
    # minflt is field 10; majflt is field 12.
    stat_fields = [
        "S", "0", "0", "0", "0", "0", "0",
        "15", "0", "4", "0", "2",
    ]
    (process_dir / "stat").write_text(
        "123 (testprocess) " + " ".join(stat_fields)
    )

    result = read_process(123, str(tmp_path))

    assert result is not None
    assert result["minor_faults_total"] == 15
    assert result["major_faults_total"] == 4


def test_process_missing_stat_returns_none(tmp_path):
    process_dir = tmp_path / "123"
    process_dir.mkdir()

    (process_dir / "status").write_text(
        "Name:\ttestprocess\nVmRSS:\t100 kB\n"
    )

    assert read_process(123, str(tmp_path)) is None
