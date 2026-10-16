from datetime import datetime, timezone
import time


class PageFaultMonitor:
    def __init__(self, vmstat_path="/proc/vmstat", clock=time.monotonic):
        self.vmstat_path = vmstat_path
        self.clock = clock
        self.previous = None

    def read_counters(self):
        counters = {}

        with open(self.vmstat_path, "r", encoding="utf-8") as file:
            for line in file:
                parts = line.split()

                if len(parts) == 2 and parts[0] in (
                    "pgfault",
                    "pgmajfault",
                ):
                    counters[parts[0]] = int(parts[1])

        if "pgfault" not in counters or "pgmajfault" not in counters:
            raise ValueError("Required page-fault counters are missing")

        return counters

    def sample(self):
        counters = self.read_counters()
        now = self.clock()

        minor_total = counters["pgfault"]
        major_total = counters["pgmajfault"]

        minor_rate = None
        major_rate = None

        if self.previous is not None:
            old_time, old_minor, old_major = self.previous
            elapsed = now - old_time

            if (
                elapsed > 0
                and minor_total >= old_minor
                and major_total >= old_major
            ):
                minor_rate = (minor_total - old_minor) / elapsed
                major_rate = (major_total - old_major) / elapsed

        self.previous = (now, minor_total, major_total)

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "linux-proc",
            "minor_faults_total": minor_total,
            "major_faults_total": major_total,
            "minor_faults_per_second": minor_rate,
            "major_faults_per_second": major_rate,
        }
