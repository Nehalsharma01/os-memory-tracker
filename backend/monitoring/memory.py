from datetime import datetime, timezone


def get_memory_stats(meminfo_path="/proc/meminfo"):
    """Read system memory and swap statistics from Linux."""

    memory = {}

    with open(meminfo_path, "r", encoding="utf-8") as file:
        for line in file:
            parts = line.split()

            if len(parts) >= 2:
                key = parts[0].rstrip(":")
                memory[key] = int(parts[1])

    total = memory["MemTotal"]
    available = memory.get("MemAvailable", memory.get("MemFree", 0))

    swap_total = memory.get("SwapTotal", 0)
    swap_free = memory.get("SwapFree", 0)

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": "linux-proc",
        "memory": {
            "total_kb": total,
            "available_kb": available,
            "used_kb": total - available,
        },
        "swap": {
            "total_kb": swap_total,
            "free_kb": swap_free,
            "used_kb": swap_total - swap_free,
        },
    }
