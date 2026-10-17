from backend.monitoring.memory import get_memory_stats
from backend.monitoring.page_faults import PageFaultMonitor


class MemoryPressureAdvisor:
    def __init__(
        self,
        memory_reader=get_memory_stats,
        fault_monitor=None,
        low_available_percent=15,
        high_swap_percent=80,
        high_major_faults_per_second=5,
    ):
        self.memory_reader = memory_reader
        self.fault_monitor = fault_monitor or PageFaultMonitor()

        self.low_available_percent = low_available_percent
        self.high_swap_percent = high_swap_percent
        self.high_major_faults_per_second = (
            high_major_faults_per_second
        )

    def evaluate(self):
        stats = self.memory_reader()
        faults = self.fault_monitor.sample()

        memory = stats["memory"]
        swap = stats["swap"]

        total_kb = memory["total_kb"]
        available_kb = memory["available_kb"]

        available_percent = (
            available_kb / total_kb * 100
            if total_kb > 0
            else None
        )

        swap_total_kb = swap["total_kb"]
        swap_used_kb = swap["used_kb"]

        swap_used_percent = (
            swap_used_kb / swap_total_kb * 100
            if swap_total_kb > 0
            else None
        )

        reasons = []

        if (
            available_percent is not None
            and available_percent < self.low_available_percent
        ):
            reasons.append(
                "Available memory is below the configured threshold."
            )

        if (
            swap_used_percent is not None
            and swap_used_percent > self.high_swap_percent
        ):
            reasons.append(
                "Swap usage is above the configured threshold."
            )

        major_rate = faults["major_faults_per_second"]

        if (
            major_rate is not None
            and major_rate > self.high_major_faults_per_second
        ):
            reasons.append(
                "Major page faults are occurring at a high rate."
            )

        low_memory = (
            available_percent is not None
            and available_percent < self.low_available_percent
        )

        high_swap = (
            swap_used_percent is not None
            and swap_used_percent > self.high_swap_percent
        )

        high_major_faults = (
            major_rate is not None
            and major_rate > self.high_major_faults_per_second
        )

        if low_memory and (high_swap or high_major_faults):
            status = "high"
        elif low_memory or high_swap or high_major_faults:
            status = "warning"
        else:
            status = "normal"

        return {
            "timestamp": stats["timestamp"],
            "source": stats["source"],
            "status": status,
            "reasons": reasons,
            "memory": {
                "available_kb": available_kb,
                "total_kb": total_kb,
                "available_percent": available_percent,
            },
            "swap": {
                "used_kb": swap_used_kb,
                "total_kb": swap_total_kb,
                "used_percent": swap_used_percent,
            },
            "page_faults": faults,
            "thresholds": {
                "low_available_percent": (
                    self.low_available_percent
                ),
                "high_swap_percent": self.high_swap_percent,
                "high_major_faults_per_second": (
                    self.high_major_faults_per_second
                ),
            },
        }
