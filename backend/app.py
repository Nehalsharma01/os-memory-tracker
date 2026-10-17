from datetime import datetime, timezone

from flask import Flask, jsonify

from backend.monitoring.memory import get_memory_stats
from backend.monitoring.page_faults import PageFaultMonitor
from backend.monitoring.processes import get_processes, get_process_by_pid
from backend.monitoring.process_fault_rates import ProcessFaultRateMonitor
from backend.monitoring.advisor import MemoryPressureAdvisor

app = Flask(__name__)

page_fault_monitor = PageFaultMonitor()
process_fault_monitor = ProcessFaultRateMonitor()
memory_advisor = MemoryPressureAdvisor()

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

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
