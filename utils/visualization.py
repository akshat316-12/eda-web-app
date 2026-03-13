import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

PLOT_PATH = "static/plots/manual_plot.png"


def generate_plot(df: pd.DataFrame, form: dict, plot_path: str = PLOT_PATH) -> tuple[str | None, str | None]:
    """
    Builds and saves a plot based on form inputs.
    Returns (plot_path, group_preview_html).
    """
    graph_type = form.get("graph_type")
    column     = form.get("column")
    column2    = form.get("column2")
    group_col  = form.get("group_col")
    value_col  = form.get("value_col")
    agg_method = form.get("agg_method")

    group_preview = None

    plt.figure(figsize=(10, 5))

    if graph_type == "hist":
        _plot_histogram(df, column)

    elif graph_type == "scatter":
        _plot_scatter(df, column, column2)

    elif graph_type == "box":
        _plot_box(df, column)

    elif graph_type == "pie":
        _plot_pie(df, column)

    elif graph_type == "heatmap":
        _plot_heatmap(df)

    elif graph_type in ["bar", "line"]:
        group_preview = _plot_grouped(df, graph_type, group_col, value_col, agg_method)

    plt.tight_layout()
    plt.savefig(plot_path)
    plt.close()

    return plot_path, group_preview


# ── private helpers ────────────────────────────────────────────────────────────

def _plot_histogram(df: pd.DataFrame, column: str):
    df[column].dropna().hist()
    plt.title(f"Distribution of {column}")
    plt.xlabel(column)
    plt.ylabel("Frequency")


def _plot_scatter(df: pd.DataFrame, column: str, column2: str):
    if not column or not column2:
        return
    plt.scatter(df[column], df[column2])
    plt.title(f"{column} vs {column2}")
    plt.xlabel(column)
    plt.ylabel(column2)


def _plot_box(df: pd.DataFrame, column: str):
    df.boxplot(column=column)
    plt.title(f"Box Plot of {column}")
    plt.ylabel(column)


def _plot_pie(df: pd.DataFrame, column: str):
    df[column].value_counts().head(5).plot(kind="pie", autopct="%1.1f%%")
    plt.title(f"Distribution of {column}")
    plt.ylabel("")


def _plot_heatmap(df: pd.DataFrame):
    numeric_df = df.select_dtypes(include=["int64", "float64"])
    if numeric_df.shape[1] > 1:
        sns.heatmap(numeric_df.corr(), annot=True)
        plt.title("Correlation Heatmap")


def _plot_grouped(df: pd.DataFrame, graph_type: str, group_col: str,
                  value_col: str, agg_method: str) -> str | None:

    if not (group_col and value_col and agg_method):
        return None

    grouped     = df.groupby(group_col)[value_col].agg(agg_method)
    grouped     = grouped.sort_values(ascending=False)
    preview_df  = grouped.reset_index().head(20)
    preview_df.columns = [group_col, f"{agg_method.capitalize()} of {value_col}"]

    grouped.plot(kind=graph_type)

    plt.title(f"{agg_method.capitalize()} of {value_col} by {group_col}")
    plt.xlabel(group_col)
    plt.ylabel(f"{agg_method.capitalize()} of {value_col}")
    plt.xticks(rotation=45, ha="right")

    return preview_df.to_html(index=False)