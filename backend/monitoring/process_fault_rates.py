import time


class ProcessFaultRateMonitor:
    def __init__(self, clock=time.monotonic):
        self.clock = clock
        self.previous = {}

    def sample(self, processes):
        now = self.clock()
        results = []

        for process in processes:
            pid = process["pid"]
            minor = process["minor_faults_total"]
            major = process["major_faults_total"]

            minor_rate = None
            major_rate = None

            if pid in self.previous:
                old_time, old_minor, old_major = self.previous[pid]
                elapsed = now - old_time

                if (
                    elapsed > 0
                    and minor >= old_minor
                    and major >= old_major
                ):
                    minor_rate = (minor - old_minor) / elapsed
                    major_rate = (major - old_major) / elapsed

            self.previous[pid] = (now, minor, major)

            results.append({
                **process,
                "minor_faults_per_second": minor_rate,
                "major_faults_per_second": major_rate,
            })

        active_pids = {process["pid"] for process in processes}
        self.previous = {
            pid: values
            for pid, values in self.previous.items()
            if pid in active_pids
        }

        return results
