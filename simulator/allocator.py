class MemoryAllocator:
    def __init__(self, total_memory):
        if total_memory <= 0:
            raise ValueError("Total memory must be positive")

        self.total_memory = total_memory
        self.blocks = [
            {
                "start": 0,
                "size": total_memory,
                "pid": None,
            }
        ]

    def allocate(self, pid, size, algorithm="first_fit"):
        if size <= 0:
            raise ValueError("Allocation size must be positive")

        if any(block["pid"] == pid for block in self.blocks):
            raise ValueError("PID is already allocated")

        candidates = []

        for index, block in enumerate(self.blocks):
            if block["pid"] is None and block["size"] >= size:
                candidates.append(index)

        if not candidates:
            return False

        if algorithm == "first_fit":
            chosen = candidates[0]
        elif algorithm == "best_fit":
            chosen = min(
                candidates,
                key=lambda i: self.blocks[i]["size"],
            )
        elif algorithm == "worst_fit":
            chosen = max(
                candidates,
                key=lambda i: self.blocks[i]["size"],
            )
        else:
            raise ValueError("Unknown allocation algorithm")

        block = self.blocks[chosen]

        allocated_block = {
            "start": block["start"],
            "size": size,
            "pid": pid,
        }

        remaining_size = block["size"] - size
        replacement = [allocated_block]

        if remaining_size > 0:
            replacement.append({
                "start": block["start"] + size,
                "size": remaining_size,
                "pid": None,
            })

        self.blocks[chosen:chosen + 1] = replacement
        return True

    def deallocate(self, pid):
        found = False

        for block in self.blocks:
            if block["pid"] == pid:
                block["pid"] = None
                found = True
                break

        if not found:
            return False

        self._merge_free_blocks()
        return True

    def _merge_free_blocks(self):
        merged = []

        for block in self.blocks:
            if (
                merged
                and merged[-1]["pid"] is None
                and block["pid"] is None
            ):
                merged[-1]["size"] += block["size"]
            else:
                merged.append(block.copy())

        self.blocks = merged

    def get_metrics(self):
        free_blocks = [
            block["size"]
            for block in self.blocks
            if block["pid"] is None
        ]

        total_free = sum(free_blocks)
        largest_free = max(free_blocks, default=0)

        if total_free == 0:
            fragmentation_percent = 0.0
        else:
            fragmentation_percent = (
                1 - largest_free / total_free
            ) * 100

        return {
            "total_memory": self.total_memory,
            "total_free_memory": total_free,
            "largest_free_block": largest_free,
            "free_block_count": len(free_blocks),
            "external_fragmentation_percent": round(
                fragmentation_percent, 2
            ),
            "blocks": [block.copy() for block in self.blocks],
        }
