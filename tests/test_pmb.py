def test_register_success(client, registration):
    response = client.post("/api/pmb/register", json=registration)
    assert response.status_code == 201
    assert response.json()["status"] == "pending"
    assert response.json()["nim"] is None


def test_duplicate_email_is_conflict(client, registration):
    assert client.post("/api/pmb/register", json=registration).status_code == 201
    duplicate = {**registration, "phone": "081298765432"}
    response = client.post("/api/pmb/register", json=duplicate)
    assert response.status_code == 409


def test_invalid_phone_is_bad_request(client, registration):
    response = client.post("/api/pmb/register", json={**registration, "phone": "12345"})
    assert response.status_code == 400


def test_invalid_email_is_bad_request(client, registration):
    response = client.post("/api/pmb/register", json={**registration, "email": "bukan-email"})
    assert response.status_code == 400


def test_missing_program_is_bad_request(client, registration):
    response = client.post("/api/pmb/register", json={**registration, "program_studi_id": 999})
    assert response.status_code == 400


def test_approve_generates_sequential_nim_and_is_idempotent(client, registration):
    first_id = client.post("/api/pmb/register", json=registration).json()["id"]
    second = {**registration, "email": "budi@example.com", "phone": "081211112222"}
    second_id = client.post("/api/pmb/register", json=second).json()["id"]
    first_approval = client.put(f"/api/pmb/approve/{first_id}")
    second_approval = client.put(f"/api/pmb/approve/{second_id}")
    assert first_approval.status_code == second_approval.status_code == 200
    assert first_approval.json()["nim"] == "20260010001"
    assert second_approval.json()["nim"] == "20260010002"
    assert client.put(f"/api/pmb/approve/{first_id}").json()["nim"] == "20260010001"


def test_status_not_found(client):
    assert client.get("/api/pmb/status/999").status_code == 404


def test_approve_not_found(client):
    assert client.put("/api/pmb/approve/999").status_code == 404


def test_stats(client, registration):
    client.post("/api/pmb/register", json=registration)
    response = client.get("/api/pmb/stats")
    assert response.status_code == 200
    assert response.json() == {"total": 1, "pending": 1, "approved": 0, "rejected": 0}
