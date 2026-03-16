import pandas as pd


def load_csv(file) -> pd.DataFrame:
    return pd.read_csv(file)


def clean_column(df: pd.DataFrame, column: str, method: str) -> pd.DataFrame:

    df = df.copy()  # avoid mutating the original

    if method == "unknown":
        df[column] = df[column].fillna("Unknown")

    elif method == "zero":
        df[column] = df[column].fillna(0)

    elif method == "mean" and pd.api.types.is_numeric_dtype(df[column]):
        val = df[column].mean()
        df[column] = df[column].fillna(round(val) if column.lower() == "age" else val)

    elif method == "median" and pd.api.types.is_numeric_dtype(df[column]):
        val = df[column].median()
        df[column] = df[column].fillna(round(val) if column.lower() == "age" else val)

    elif method == "mode":
        df[column] = df[column].fillna(df[column].mode()[0])

    elif method == "drop":
        df = df.dropna(subset=[column])

    return df


def generate_profile(df: pd.DataFrame) -> list:

    profile = []

    for col in df.columns:

        col_type   = str(df[col].dtype)
        missing    = df[col].isnull().sum()
        unique     = df[col].nunique()
        mean       = None
        min_val    = None
        max_val    = None

        if pd.api.types.is_numeric_dtype(df[col]):
            mean    = round(df[col].mean(), 3)
            min_val = df[col].min()
            max_val = df[col].max()

        profile.append({
            "column":  col,
            "type":    col_type,
            "missing": missing,
            "unique":  unique,
            "mean":    mean,
            "min":     min_val,
            "max":     max_val,
        })

    return profile


def get_summary(df: pd.DataFrame) -> dict:
    missing      = df.isnull().sum().to_dict()
    missing_cols = [col for col, val in missing.items() if val > 0]
    numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns.tolist()
    cat_cols     = df.select_dtypes(include=["object"]).columns.tolist()

    return {
        "preview":      df.head().to_html(),
        "rows":         df.shape[0],
        "cols":         df.shape[1],
        "missing":      missing,
        "missing_cols": missing_cols,
        "numeric_cols": numeric_cols,
        "cat_cols":     cat_cols,
        "columns":      df.columns.tolist(),
        "profile":      generate_profile(df),
    }