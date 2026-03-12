from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():

    preview = None
    rows = None
    cols = None
    missing = None

    if request.method == "POST":

        file = request.files["file"]

        if file:
            df = pd.read_csv(file)

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