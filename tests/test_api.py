# required tests

def test_upload_csv(client, sample_csv_bytes):
    response = client.post(
        "/upload",
        files={"file": ("sample_data.csv", sample_csv_bytes, "text/csv")}
    )
    assert response.status_code == 200

    body = response.json()
    assert body["rows"] == 6
    assert body["columns"] == 2
    assert isinstance(body["id"], int)
    assert body["id"] > 0


def test_process_and_retrieve(client, uploaded_dataset_id, processing_body):
    process_url = "/datasets/{}/process".format(uploaded_dataset_id)
    response = client.post(process_url, json=processing_body)
    assert response.status_code == 200

    body = response.json()
    report = body["cleaning_report"]
    assert body["validation_rows_removed"] == 1
    assert report["rows_before"] == 5
    assert report["rows_after"] == 3

    response = client.get("/datasets/{}".format(uploaded_dataset_id))
    assert response.status_code == 200

    body = response.json()
    assert body["total_rows"] == 3

    student_ids = []
    scores = []
    for record in body["data"]:
        student_ids.append(record["student_id"])
        scores.append(record["score"])

    assert student_ids == [1, 2, 5]
    assert scores == [80, 90, 85]


def test_retrieve_missing_dataset(client):
    response = client.get("/datasets/999")
    assert response.status_code == 404


# optional tests (not graded)

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_unsupported_extension(client):
    response = client.post(
        "/upload",
        files={"file": ("notes.txt", b"hello", "text/plain")}
    )
    assert response.status_code == 400


def test_empty_csv(client):
    response = client.post(
        "/upload",
        files={"file": ("empty.csv", b"", "text/csv")}
    )
    assert response.status_code == 400


def test_retrieve_with_limit(client, uploaded_dataset_id):
    response = client.get("/datasets/{}?limit=2".format(uploaded_dataset_id))
    assert response.status_code == 200

    body = response.json()
    assert len(body["data"]) == 2
    assert body["total_rows"] == 6


def test_invalid_limit(client, uploaded_dataset_id):
    response = client.get("/datasets/{}?limit=0".format(uploaded_dataset_id))
    assert response.status_code == 422


def test_process_missing_dataset(client, processing_body):
    response = client.post("/datasets/999/process", json=processing_body)
    assert response.status_code == 404


def test_missing_required_column(client, uploaded_dataset_id, processing_body):
    processing_body["validation"]["required_columns"] = ["student_id", "grade"]
    response = client.post("/datasets/{}/process".format(uploaded_dataset_id), json=processing_body)
    assert response.status_code == 400

    # the stored data should not change
    response = client.get("/datasets/{}".format(uploaded_dataset_id))
    assert response.json()["total_rows"] == 6


def test_unsupported_outlier_method(client, uploaded_dataset_id, processing_body):
    processing_body["processing"]["outliers"]["enabled"] = True
    processing_body["processing"]["outliers"]["columns"] = ["score"]
    processing_body["processing"]["outliers"]["method"] = "percentile"
    response = client.post("/datasets/{}/process".format(uploaded_dataset_id), json=processing_body)
    assert response.status_code == 400

    response = client.get("/datasets/{}".format(uploaded_dataset_id))
    assert response.json()["total_rows"] == 6


def test_malformed_body(client, uploaded_dataset_id):
    bad_body = {"processing": {"remove_duplicates": "not a boolean"}}
    response = client.post("/datasets/{}/process".format(uploaded_dataset_id), json=bad_body)
    assert response.status_code == 422


def test_request_ids(client, uploaded_dataset_id):
    responses = [
        client.get("/health"),
        client.post("/upload", files={"file": ("notes.txt", b"hello", "text/plain")}),
        client.get("/datasets/999"),
        client.get("/datasets/{}?limit=0".format(uploaded_dataset_id)),
    ]
    expected_codes = [200, 400, 404, 422]

    request_ids = []
    for response, code in zip(responses, expected_codes):
        assert response.status_code == code
        request_id = response.headers["X-Request-ID"]
        assert len(request_id) == 8
        request_ids.append(request_id)

    # every request should get a different ID
    assert len(set(request_ids)) == len(request_ids)
