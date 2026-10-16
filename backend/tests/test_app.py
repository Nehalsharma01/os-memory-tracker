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
