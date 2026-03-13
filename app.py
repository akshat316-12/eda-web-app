import io
import os
import uuid

import pandas as pd
from flask import Flask, render_template, request, send_file, session

from utils.data_cleaning import load_csv, clean_column, get_summary
from utils.visualization import generate_plot

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-in-production")

# In-memory store: { session_id: dataframe }
USER_DATA: dict[str, pd.DataFrame] = {}


def get_df() -> pd.DataFrame | None:
    return USER_DATA.get(session.get("uid"))


def set_df(df: pd.DataFrame):
    if "uid" not in session:
        session["uid"] = str(uuid.uuid4())
    USER_DATA[session["uid"]] = df


def get_plot_path() -> str:
    """Each user gets their own plot file so charts don't overwrite each other."""
    if "uid" not in session:
        session["uid"] = str(uuid.uuid4())
    return f"static/plots/plot_{session['uid']}.png"


@app.route("/", methods=["GET", "POST"])
def index():

    group_preview = None
    plot_path     = None
    df            = get_df()

    if request.method == "POST":

        # ── Upload CSV ─────────────────────────────────────────────────────────
        if "file" in request.files:
            file = request.files["file"]
            if file.filename.endswith(".csv"):
                df = load_csv(file)
                set_df(df)

        # ── Clean missing values ───────────────────────────────────────────────
        if "clean_column" in request.form and df is not None:
            df = clean_column(
                df,
                column=request.form["clean_column"],
                method=request.form["method"],
            )
            set_df(df)

        # ── Generate chart ─────────────────────────────────────────────────────
        if "graph_type" in request.form and df is not None:
            plot_path, group_preview = generate_plot(df, request.form, get_plot_path())

    # ── Build template context ─────────────────────────────────────────────────
    df      = get_df()
    summary = get_summary(df) if df is not None else {}

    return render_template(
        "index.html",
        preview=      summary.get("preview"),
        rows=         summary.get("rows"),
        cols=         summary.get("cols"),
        missing=      summary.get("missing"),
        columns=      summary.get("columns", []),
        missing_cols= summary.get("missing_cols", []),
        numeric_cols= summary.get("numeric_cols", []),
        cat_cols=     summary.get("cat_cols", []),
        profile=      summary.get("profile", []),
        plot_path=    plot_path,
        group_preview=group_preview,
    )


@app.route("/download_csv")
def download_csv():

    df = get_df()

    if df is None:
        return "No dataset loaded", 400

    buffer = io.StringIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)

    return send_file(
        io.BytesIO(buffer.getvalue().encode()),
        mimetype="text/csv",
        as_attachment=True,
        download_name="cleaned_dataset.csv",
    )


if __name__ == "__main__":
    app.run(debug=True)