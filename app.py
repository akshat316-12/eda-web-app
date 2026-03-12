from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

df = None

@app.route("/", methods=["GET","POST"])
def index():

    global df

    preview = None
    rows = None
    cols = None
    missing = None

    if request.method == "POST":

        # CSV upload
        if "file" in request.files:

            file = request.files["file"]

            if file.filename != "":
                df = pd.read_csv(file)

        # Missing value cleaning
        if "column" in request.form and df is not None:

            column = request.form["column"]
            method = request.form["method"]

            if method == "unknown":
                df[column] = df[column].fillna("Unknown")

            elif method == "mean":
                df[column] = df[column].fillna(df[column].mean())

            elif method == "median":
                df[column] = df[column].fillna(df[column].median())

            elif method == "drop":
                df.dropna(subset=[column], inplace=True)

    if df is not None:

        preview = df.head().to_html()

        rows, cols = df.shape

        missing = df.isnull().sum().to_dict()

    return render_template(
        "index.html",
        preview=preview,
        rows=rows,
        cols=cols,
        missing=missing
    )


if __name__ == "__main__":
    app.run(debug=True)