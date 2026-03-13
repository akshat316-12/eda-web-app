from flask import Flask, render_template, request, send_file
import io

from utils.data_cleaning import load_csv, clean_column, get_summary
from utils.visualization import generate_plot

app = Flask(__name__)

df        = None
plot_path = None


@app.route("/", methods=["GET", "POST"])
def index():

    global df, plot_path

    group_preview = None

    if request.method == "POST":

        # ── Upload CSV ─────────────────────────────────────────────────────────
        if "file" in request.files:
            file = request.files["file"]
            if file.filename.endswith(".csv"):
                df = load_csv(file)

        # ── Clean missing values ───────────────────────────────────────────────
        if "clean_column" in request.form and df is not None:
            df = clean_column(
                df,
                column=request.form["clean_column"],
                method=request.form["method"],
            )

        # ── Generate chart ─────────────────────────────────────────────────────
        if "graph_type" in request.form and df is not None:
            plot_path, group_preview = generate_plot(df, request.form)

    # ── Build template context ─────────────────────────────────────────────────
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

    global df

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