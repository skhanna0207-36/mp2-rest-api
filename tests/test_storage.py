import pandas as pd

from src.storage import DatasetStorage


def test_storage_isolates_saved_retrieved_and_updated_frames():
    storage = DatasetStorage()
    original = pd.DataFrame({"score": [80, 90]})
    dataset_id = storage.save(original, "scores.csv")
    original.loc[0, "score"] = -1
    retrieved = storage.get(dataset_id)
    assert retrieved["score"].tolist() == [80, 90]
    retrieved.loc[0, "score"] = -2
    assert storage.get(dataset_id)["score"].tolist() == [80, 90]

    replacement = pd.DataFrame({"grade": [100]})
    assert storage.update(dataset_id, replacement) is True
    replacement.loc[0, "grade"] = -3
    assert storage.get(dataset_id)["grade"].tolist() == [100]
    assert storage.get_metadata(dataset_id) == {
        "id": dataset_id, "filename": "scores.csv", "rows": 1,
        "columns": 1, "column_names": ["grade"],
    }


def test_storage_unknown_ids_and_clear():
    storage = DatasetStorage()
    assert storage.get(999) is None
    assert storage.get_metadata(999) is None
    assert storage.update(999, pd.DataFrame()) is False
    first_id = storage.save(pd.DataFrame({"x": [1]}), "one.csv")
    second_id = storage.save(pd.DataFrame({"x": [2]}), "two.csv")
    assert second_id > first_id
    storage.clear()
    assert storage.get(first_id) is None
    assert storage.get(second_id) is None
    assert storage.save(pd.DataFrame(), "empty.csv") == 1
