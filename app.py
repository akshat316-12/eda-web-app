from flask import Flask, render_template, request, send_file
import io
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

app = Flask(__name__)

df = None
plot_path = None


def generate_profile(dataframe):

    profile = []

    for col in dataframe.columns:

        col_type = str(dataframe[col].dtype)
        missing_count = dataframe[col].isnull().sum()
        unique_count = dataframe[col].nunique()

        mean = None
        min_val = None
        max_val = None

        if pd.api.types.is_numeric_dtype(dataframe[col]):
            mean = round(dataframe[col].mean(), 3)
            min_val = dataframe[col].min()
            max_val = dataframe[col].max()

        profile.append({
            "column": col,
            "type": col_type,
            "missing": missing_count,
            "unique": unique_count,
            "mean": mean,
            "min": min_val,
            "max": max_val
        })

    return profile


@app.route("/", methods=["GET","POST"])
def index():

    global df, plot_path

    preview = None
    rows = None
    cols = None
    missing = None
    profile = []
    numeric_cols = []
    cat_cols = []
    missing_cols = []
    group_preview = None

    if request.method == "POST":

        # Upload CSV
        if "file" in request.files:

            file = request.files["file"]

            if file.filename.endswith(".csv"):
                df = pd.read_csv(file)

        # Missing value cleaning
        if "clean_column" in request.form and df is not None:

            column = request.form["clean_column"]
            method = request.form["method"]

            if method == "unknown":
                df[column].fillna("Unknown", inplace=True)

            elif method == "zero":
                df[column].fillna(0, inplace=True)

            elif method == "mean" and pd.api.types.is_numeric_dtype(df[column]):
                df[column].fillna(df[column].mean(), inplace=True)

            elif method == "median" and pd.api.types.is_numeric_dtype(df[column]):
                df[column].fillna(df[column].median(), inplace=True)

            elif method == "mode":
                df[column].fillna(df[column].mode()[0], inplace=True)

            elif method == "drop":
                df.dropna(subset=[column], inplace=True)

        # Graph generator
        if "graph_type" in request.form and df is not None:

            graph_type = request.form["graph_type"]

            column = request.form.get("column")
            column2 = request.form.get("column2")

            group_col = request.form.get("group_col")
            value_col = request.form.get("value_col")
            agg_method = request.form.get("agg_method")

            plt.figure(figsize=(10,5))

            if graph_type == "hist":

                df[column].dropna().hist()

                plt.title(f"Distribution of {column}")
                plt.xlabel(column)
                plt.ylabel("Frequency")

            elif graph_type == "scatter" and column and column2:

                plt.scatter(df[column], df[column2])

                plt.title(f"{column} vs {column2}")
                plt.xlabel(column)
                plt.ylabel(column2)

            elif graph_type == "box":

                df.boxplot(column=column)

                plt.title(f"Box Plot of {column}")
                plt.ylabel(column)

            elif graph_type == "pie":

                df[column].value_counts().head(5).plot(kind="pie", autopct="%1.1f%%")

                plt.title(f"Distribution of {column}")
                plt.ylabel("")

            elif graph_type == "heatmap":

                numeric_df = df.select_dtypes(include=['int64','float64'])

                if numeric_df.shape[1] > 1:

                    sns.heatmap(numeric_df.corr(), annot=True)

                    plt.title("Correlation Heatmap")

            elif graph_type in ["bar","line"]:

                if group_col and value_col and agg_method:

                    grouped = df.groupby(group_col)[value_col].agg(agg_method)

                    grouped = grouped.sort_values(ascending=False)

                    preview_df = grouped.reset_index().head(20)

                    preview_df.columns = [group_col, f"{agg_method.capitalize()} of {value_col}"]

                    group_preview = preview_df.to_html(index=False)

                    if graph_type == "bar":
                        grouped.plot(kind="bar")

                    elif graph_type == "line":
                        grouped.plot(kind="line")

                    plt.title(f"{agg_method.capitalize()} of {value_col} by {group_col}")
                    plt.xlabel(group_col)
                    plt.ylabel(f"{agg_method.capitalize()} of {value_col}")

                    plt.xticks(rotation=45, ha="right")

            plot_path = "static/plots/manual_plot.png"

            plt.tight_layout()
            plt.savefig(plot_path)
            plt.close()

    if df is not None:

        preview = df.head().to_html()

        rows, cols = df.shape

        missing = df.isnull().sum().to_dict()

        missing_cols = [col for col,val in missing.items() if val > 0]

        numeric_cols = df.select_dtypes(include=['int64','float64']).columns.tolist()

        cat_cols = df.select_dtypes(include=['object']).columns.tolist()

        profile = generate_profile(df)

    return render_template(
        "index.html",
        preview=preview,
        rows=rows,
        cols=cols,
        missing=missing,
        columns=df.columns.tolist() if df is not None else [],
        missing_cols=missing_cols,
        numeric_cols=numeric_cols,
        cat_cols=cat_cols,
        profile=profile,
        plot_path=plot_path,
        group_preview=group_preview
    )


@app.route("/download_csv")
def download_csv():

    global df

    if df is None:
        return "No dataset loaded"

    buffer = io.StringIO()
    df.to_csv(buffer, index=False)

    buffer.seek(0)

    return send_file(
        io.BytesIO(buffer.getvalue().encode()),
        mimetype="text/csv",
        as_attachment=True,
        download_name="cleaned_dataset.csv"
    )


if __name__ == "__main__":
    app.run(debug=True)