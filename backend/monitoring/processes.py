from datetime import datetime, timezone
import os


def get_processes(proc_path="/proc"):
    """Return memory information for accessible Linux processes."""

    processes = []

    for entry in os.listdir(proc_path):
        if not entry.isdigit():
            continue

        pid = int(entry)
        status_path = os.path.join(proc_path, entry, "status")

        try:
            with open(status_path, "r", encoding="utf-8") as file:
                details = {}

                for line in file:
                    parts = line.split(":", 1)

                    if len(parts) != 2:
                        continue

                    key = parts[0].strip()
                    value = parts[1].strip()

                    if key in ("Name", "VmRSS", "VmSize"):
                        details[key] = value

            processes.append({
                "pid": pid,
                "name": details.get("Name", "unknown"),
                "memory_rss_kb": int(details.get("VmRSS", "0 kB").split()[0]),
                "memory_virtual_kb": int(details.get("VmSize", "0 kB").split()[0]),
            })

        except (OSError, ValueError, IndexError):
            # Processes can exit or become inaccessible while being read.
            continue

    processes.sort(key=lambda process: process["memory_rss_kb"], reverse=True)

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": "linux-proc",
        "count": len(processes),
        "processes": processes,
    }


def get_process_by_pid(pid, proc_path="/proc"):
    """Return memory information for one process, or None if unavailable."""

    if pid <= 0:
        return None

    result = get_processes(proc_path)

    for process in result["processes"]:
        if process["pid"] == pid:
            return process

    return None

