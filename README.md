# MP2: Data Processing REST API

This project is a FastAPI application that lets a client upload a CSV dataset, store it in memory, validate and clean it, and get the processed data back as JSON. `GET /health` returns the app status and version, `POST /upload` accepts a CSV file and returns its ID, row count and columns, and `GET /datasets/{dataset_id}` returns up to `limit` rows along with the total number of rows. `POST /datasets/{dataset_id}/process` takes a JSON config (required columns, numeric columns, duplicate removal, missing value handling and outlier settings), runs the validation and cleaning functions from my MP1 pipeline (copied into `data_pipeline/`), saves the cleaned data and returns a cleaning report. The `src/` package has the request and response models, the in-memory storage class, logging setup and a middleware that gives every request an 8 character ID (returned in the `X-Request-ID` header) and logs its method, path, status code and duration. Errors return the right status codes (400 for bad files or settings, 404 for unknown dataset IDs and 422 for invalid input), and the API is tested with pytest in `tests/`.

## How to run

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
python -m pip install -r requirements.txt

python -m uvicorn main:app --reload
```

Then open http://127.0.0.1:8000/docs, upload `fixtures/sample_data.csv` and process it with the returned ID.

## Run the tests

```bash
python -m pytest tests -v
```


## API example

With the server running, execute these commands from the project root. Replace
`1` with the `id` returned by the upload if another dataset has already been saved.

```bash
curl http://127.0.0.1:8000/health
curl -F 'file=@fixtures/sample_data.csv' http://127.0.0.1:8000/upload
curl -X POST http://127.0.0.1:8000/datasets/1/process \
  -H 'Content-Type: application/json' \
  -d '{"validation":{"required_columns":["student_id","score"],"numeric_columns":["score"]},"processing":{"remove_duplicates":true,"missing":{"enabled":true,"axis":"rows"},"outliers":{"enabled":false}}}'
curl 'http://127.0.0.1:8000/datasets/1?limit=10'
```

For the sample fixture, processing removes one invalid numeric row, then removes
the duplicate and missing-score rows. The remaining student IDs are `1`, `2`, and
`5`, with scores `80`, `90`, and `85`.
