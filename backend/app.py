from datetime import datetime, timezone

from flask import Flask, jsonify, request
from simulator.allocator import MemoryAllocator

from backend.monitoring.memory import get_memory_stats
from backend.monitoring.page_faults import PageFaultMonitor
from backend.monitoring.processes import get_processes, get_process_by_pid
from backend.monitoring.process_fault_rates import ProcessFaultRateMonitor
from backend.monitoring.advisor import MemoryPressureAdvisor

app = Flask(__name__)

page_fault_monitor = PageFaultMonitor()
process_fault_monitor = ProcessFaultRateMonitor()
memory_advisor = MemoryPressureAdvisor()
simulator = MemoryAllocator(1000)
@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })


@app.route("/api/system/memory", methods=["GET"])
def system_memory():
    stats = get_memory_stats()

    return jsonify({
        "timestamp": stats["timestamp"],
        "source": stats["source"],
        "total_kb": stats["memory"]["total_kb"],
        "available_kb": stats["memory"]["available_kb"],
        "used_kb": stats["memory"]["used_kb"],
        "swap_total_kb": stats["swap"]["total_kb"],
        "swap_free_kb": stats["swap"]["free_kb"],
        "swap_used_kb": stats["swap"]["used_kb"],
    })


@app.route("/api/system/page-faults", methods=["GET"])
def system_page_faults():
    return jsonify(page_fault_monitor.sample())


@app.route("/api/processes", methods=["GET"])
def list_processes():
    data = get_processes()
    data["processes"] = process_fault_monitor.sample(data["processes"])
    return jsonify(data)


@app.route("/api/processes/<int:pid>", methods=["GET"])
def process_details(pid):
    process = get_process_by_pid(pid)

    if process is None:
        return jsonify({"error": "Process not found"}), 404

    return jsonify(process)
@app.route("/api/system/memory-advisor", methods=["GET"])
def memory_advisor_status():
    return jsonify(memory_advisor.evaluate())

@app.route("/api/simulator/status", methods=["GET"])
def simulator_status():
    return jsonify(simulator.get_metrics())


@app.route("/api/simulator/allocate", methods=["POST"])
def simulator_allocate():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "JSON object required"}), 400

    pid = data.get("pid")
    size = data.get("size")
    algorithm = data.get("algorithm", "first_fit")

    if (
        not isinstance(pid, int)
        or isinstance(pid, bool)
        or pid <= 0
    ):
        return jsonify({"error": "pid must be a positive integer"}), 400

    if (
        not isinstance(size, int)
        or isinstance(size, bool)
        or size <= 0
    ):
        return jsonify({"error": "size must be a positive integer"}), 400

    if not isinstance(algorithm, str) or algorithm not in (
        "first_fit",
        "best_fit",
        "worst_fit",
    ):
        return jsonify({"error": "Invalid allocation algorithm"}), 400

    try:
        allocated = simulator.allocate(pid, size, algorithm)
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    if not allocated:
        return jsonify({
            "allocated": False,
            "message": "No suitable free block available",
            "metrics": simulator.get_metrics(),
        }), 409

    return jsonify({
        "allocated": True,
        "pid": pid,
        "size": size,
        "algorithm": algorithm,
        "metrics": simulator.get_metrics(),
    }), 200


@app.route("/api/simulator/deallocate", methods=["POST"])
def simulator_deallocate():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "JSON object required"}), 400

    pid = data.get("pid")

    if (
        not isinstance(pid, int)
        or isinstance(pid, bool)
        or pid <= 0
    ):
        return jsonify({"error": "pid must be a positive integer"}), 400

    if not simulator.deallocate(pid):
        return jsonify({"error": "Process not found in simulator"}), 404

    return jsonify({
        "deallocated": True,
        "pid": pid,
        "metrics": simulator.get_metrics(),
    })


@app.route("/api/simulator/reset", methods=["POST"])
def simulator_reset():
    global simulator
    simulator = MemoryAllocator(1000)

    return jsonify({
        "message": "Simulator reset successfully",
        "metrics": simulator.get_metrics(),
    })

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
