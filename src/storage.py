import logging

logger = logging.getLogger(__name__)


class DatasetStorage:
    def __init__(self):
        self._store = {}
        self._counter = 0

    def save(self, df, filename):
        """Store a copy of the data and return a new integer ID."""
        self._counter += 1
        dataset_id = self._counter

        self._store[dataset_id] = {
            "filename": filename,
            "data": df.copy(),
        }
        logger.debug("Stored dataset: id={}, rows={}".format(dataset_id, len(df)))
        return dataset_id

    def get(self, dataset_id):
        """Return a copy of the stored DataFrame, or None."""
        if dataset_id not in self._store:
            logger.debug("Dataset not in storage: id={}".format(dataset_id))
            return None

        df = self._store[dataset_id]["data"].copy()
        logger.debug("Retrieved dataset copy: id={}, rows={}".format(dataset_id, len(df)))
        return df

    def get_metadata(self, dataset_id):
        """Return the dataset metadata, or None."""
        if dataset_id not in self._store:
            return None

        entry = self._store[dataset_id]
        df = entry["data"]

        # calculated from the current data so it is still right after processing
        metadata = {
            "id": dataset_id,
            "filename": entry["filename"],
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": list(df.columns),
        }
        return metadata

    def update(self, dataset_id, df):
        """Replace an existing dataset; return True, or False if missing."""
        if dataset_id not in self._store:
            logger.debug("Cannot update, dataset not in storage: id={}".format(dataset_id))
            return False

        self._store[dataset_id]["data"] = df.copy()
        logger.debug("Updated dataset: id={}, rows={}".format(dataset_id, len(df)))
        return True

    def clear(self):
        """Clear all data and reset the ID counter."""
        self._store.clear()
        self._counter = 0
