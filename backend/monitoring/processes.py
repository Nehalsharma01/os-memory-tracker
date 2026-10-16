
from datetime import datetime, timezone
import os


def read_process(pid, proc_path="/proc"):
    """Read memory and page-fault statistics for one process."""

    if pid <= 0:
        return None

    process_dir = os.path.join(proc_path, str(pid))
    status_path = os.path.join(process_dir, "status")
    stat_path = os.path.join(process_dir, "stat")

    try:
        details = {}

        with open(status_path, "r", encoding="utf-8") as file:
            for line in file:
                parts = line.split(":", 1)

                if len(parts) != 2:
                    continue

                key = parts[0].strip()
                value = parts[1].strip()

                if key in ("Name", "VmRSS", "VmSize"):
                    details[key] = value

        with open(stat_path, "r", encoding="utf-8") as file:
            stat_line = file.read().strip()

        # The process name inside parentheses can contain spaces.
        # Fields after the closing parenthesis begin with field 3.
        closing_paren = stat_line.rfind(")")
        if closing_paren == -1:
            return None

        stat_fields = stat_line[closing_paren + 2:].split()

        # Original /proc/[pid]/stat fields:
        # 10 = minflt, 12 = majflt (1-based field numbers).
        minor_faults = int(stat_fields[7])
        major_faults = int(stat_fields[9])

        return {
            "pid": pid,
            "name": details.get("Name", "unknown"),
            "memory_rss_kb": int(
                details.get("VmRSS", "0 kB").split()[0]
            ),
            "memory_virtual_kb": int(
                details.get("VmSize", "0 kB").split()[0]
            ),
            "minor_faults_total": minor_faults,
            "major_faults_total": major_faults,
        }

    except (OSError, ValueError, IndexError):
        # A process can exit or become inaccessible during a read.
        return None


def get_processes(proc_path="/proc"):
    """Return accessible Linux processes, sorted by resident memory."""

    processes = []

    for entry in os.listdir(proc_path):
        if not entry.isdigit():
            continue

        process = read_process(int(entry), proc_path)

        if process is not None:
            processes.append(process)

    processes.sort(
        key=lambda process: process["memory_rss_kb"],
        reverse=True,
    )

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": "linux-proc",
        "count": len(processes),
        "processes": processes,
    }


def get_process_by_pid(pid, proc_path="/proc"):
    """Return one process's statistics, or None if unavailable."""

    return read_process(pid, proc_path)

