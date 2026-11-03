import logging
import pandas as pd

logger = logging.getLogger(__name__)


def remove_duplicates(df):
    """Remove duplicate rows."""
    rows_before = len(df)
    df = df.drop_duplicates()
    logger.debug("remove_duplicates: {} -> {} rows".format(rows_before, len(df)))
    return df


def handle_missing(df, axis="rows"):
    """Drop rows or columns containing missing values."""
    if axis == "rows":
        rows_before = len(df)
        df = df.dropna(axis=0)
        logger.debug("handle_missing: {} -> {} rows".format(rows_before, len(df)))
    elif axis == "columns":
        columns_before = len(df.columns)
        df = df.dropna(axis=1)
        logger.debug("handle_missing: {} -> {} columns".format(columns_before, len(df.columns)))
    else:
        logger.error("Unsupported axis for missing values: {}".format(axis))
        raise ValueError("Unsupported axis for missing values: {}".format(axis))
    return df


def remove_outliers(df, columns, method, threshold):
    """Remove outliers from the specified numeric columns."""
    if method not in ["iqr", "zscore"]:
        logger.error("Unsupported outlier method: {}".format(method))
        raise ValueError("Unsupported outlier method: {}".format(method))

    for col in columns:
        if col not in df.columns:
            logger.warning("Column not found: {}".format(col))
            continue

        if not pd.api.types.is_numeric_dtype(df[col]):
            logger.warning("Column is not numeric: {}".format(col))
            continue

        rows_before = len(df)

        if method == "iqr":
            q1 = df[col].quantile(0.25)
            q3 = df[col].quantile(0.75)
            iqr = q3 - q1
            lower = q1 - threshold * iqr
            upper = q3 + threshold * iqr
            keep = (df[col] >= lower) & (df[col] <= upper)
        else:
            mean = df[col].mean()
            std = df[col].std()
            z_scores = (df[col] - mean) / std
            keep = z_scores.abs() <= threshold

        df = df[keep]
        removed = rows_before - len(df)
        logger.debug("{}: method={}, threshold={}, removed={}".format(col, method, threshold, removed))

    return df


def process_data(df, config):
    """Apply the processing steps enabled in the configuration."""
    settings = config["processing"]

    if settings["remove_duplicates"]:
        df = remove_duplicates(df)

    missing = settings["missing"]
    if missing["enabled"]:
        df = handle_missing(df, missing["axis"])

    outliers = settings["outliers"]
    if outliers["enabled"]:
        df = remove_outliers(df, outliers["columns"], outliers["method"], outliers["threshold"])

    return df


def create_cleaning_report(df_before, df_after):
    """Return a dictionary summarizing the cleaning results."""
    rows_before = len(df_before)
    rows_after = len(df_after)
    columns_before = len(df_before.columns)
    columns_after = len(df_after.columns)

    report = {
        "rows_before": rows_before,
        "rows_after": rows_after,
        "rows_removed": rows_before - rows_after,
        "columns_before": columns_before,
        "columns_after": columns_after,
        "columns_removed": columns_before - columns_after,
    }
    return report
