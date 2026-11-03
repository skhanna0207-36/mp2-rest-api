import logging
import pandas as pd


logger = logging.getLogger(__name__)


def validate_dataframe(df, required_columns, numeric_columns):
    """Validate the DataFrame and return valid data.

    required_columns: a list of column names that must exist.
    numeric_columns: a list of column names whose values should be numeric.
    """
    # work on a copy so the original DataFrame is not changed
    df = df.copy()
    rows_before = len(df)

    for col in required_columns:
        if col not in df.columns:
            logger.error("Missing required column: {}".format(col))
            raise ValueError("Missing required column: {}".format(col))

    for col in numeric_columns:
        invalid_rows = []
        for i, value in df[col].items():
            if pd.notna(value):
                try:
                    float(value)
                except ValueError:
                    logger.warning("Invalid value in {}: {}".format(col, value))
                    invalid_rows.append(i)

        # remove the invalid rows
        df = df.drop(index=invalid_rows)

        # convert to a numeric data type
        df[col] = pd.to_numeric(df[col])

    rows_after = len(df)
    removed = rows_before - rows_after
    logger.debug("Validation: {} -> {} rows (removed {})".format(rows_before, rows_after, removed))

    return df
