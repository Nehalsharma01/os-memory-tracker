from backend.app import app


def test_health_endpoint():
    client = app.test_client()

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json["status"] == "healthy"


def test_memory_endpoint():
    client = app.test_client()

    response = client.get("/api/system/memory")

    assert response.status_code == 200
    data = response.json

    assert data["source"] == "linux-proc"
    assert data["total_kb"] > 0
    assert data["available_kb"] >= 0
    assert data["used_kb"] == data["total_kb"] - data["available_kb"]
    assert data["swap_used_kb"] == (
        data["swap_total_kb"] - data["swap_free_kb"]
    )


def test_page_fault_endpoint():
    client = app.test_client()

    response = client.get("/api/system/page-faults")

    assert response.status_code == 200
    data = response.json

    assert data["source"] == "linux-proc"
    assert data["minor_faults_total"] >= 0
    assert data["major_faults_total"] >= 0
def test_processes_endpoint():
    client = app.test_client()

    response = client.get("/api/processes")

    assert response.status_code == 200
    data = response.json

    assert data["source"] == "linux-proc"
    assert data["count"] == len(data["processes"])

    for process in data["processes"]:
        assert process["pid"] > 0
        assert process["memory_rss_kb"] >= 0


def test_process_details_endpoint():
    client = app.test_client()

    response = client.get("/api/processes/1")

    # PID 1 should normally exist in this Linux environment.
    assert response.status_code == 200
    assert response.json["pid"] == 1


def test_nonexistent_process_returns_404():
    client = app.test_client()

    response = client.get("/api/processes/99999999")

    assert response.status_code == 404
    assert response.json["error"] == "Process not found"
