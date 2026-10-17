from backend.monitoring.advisor import MemoryPressureAdvisor


class FakeFaultMonitor:
    def __init__(self, major_rate=None):
        self.major_rate = major_rate

    def sample(self):
        return {
            "timestamp": "test-time",
            "source": "linux-proc",
            "minor_faults_total": 100,
            "major_faults_total": 10,
            "minor_faults_per_second": 0.0,
            "major_faults_per_second": self.major_rate,
        }


def fake_memory(available_percent, swap_percent):
    total_kb = 1000
    swap_total_kb = 1000

    return {
        "timestamp": "test-time",
        "source": "linux-proc",
        "memory": {
            "total_kb": total_kb,
            "available_kb": total_kb * available_percent / 100,
            "used_kb": total_kb * (100 - available_percent) / 100,
        },
        "swap": {
            "total_kb": swap_total_kb,
            "free_kb": swap_total_kb * (100 - swap_percent) / 100,
            "used_kb": swap_total_kb * swap_percent / 100,
        },
    }


def test_normal_memory_status():
    advisor = MemoryPressureAdvisor(
        memory_reader=lambda: fake_memory(70, 10),
        fault_monitor=FakeFaultMonitor(0),
    )

    result = advisor.evaluate()

    assert result["status"] == "normal"
    assert result["reasons"] == []


def test_low_memory_causes_warning():
    advisor = MemoryPressureAdvisor(
        memory_reader=lambda: fake_memory(10, 10),
        fault_monitor=FakeFaultMonitor(0),
    )

    result = advisor.evaluate()

    assert result["status"] == "warning"
    assert any("Available memory" in reason for reason in result["reasons"])


def test_low_memory_and_high_swap_cause_high_status():
    advisor = MemoryPressureAdvisor(
        memory_reader=lambda: fake_memory(10, 90),
        fault_monitor=FakeFaultMonitor(0),
    )

    result = advisor.evaluate()

    assert result["status"] == "high"
    assert len(result["reasons"]) == 2


def test_high_major_fault_rate_causes_warning():
    advisor = MemoryPressureAdvisor(
        memory_reader=lambda: fake_memory(70, 10),
        fault_monitor=FakeFaultMonitor(8),
    )

    result = advisor.evaluate()

    assert result["status"] == "warning"
    assert any("Major page faults" in reason for reason in result["reasons"])
