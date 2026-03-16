# EDA Studio 📊

A web-based Exploratory Data Analysis tool built with Flask. Upload a CSV, explore your data, handle missing values, and generate charts — all from the browser.

🔗 **Live Demo:** [https://web-production-41996.up.railway.app](https://web-production-41996.up.railway.app)

---

## Features

- Upload any CSV file
- Dataset preview and column profile (type, missing count, unique, mean, min, max)
- Handle missing values with multiple methods (mean, median, mode, fill, drop)
- Generate 7 chart types: Histogram, Scatter, Box Plot, Bar, Line, Pie, Heatmap
- Download cleaned dataset as CSV
- Download generated charts as PNG

---

## Project Structure

```
eda-web-app/
├── app.py                  # Flask routes and request handling
├── Procfile                # Gunicorn start command for deployment
├── requirements.txt        # Python dependencies
├── .gitignore
├── README.md
├── utils/
│   ├── __init__.py
│   ├── data_cleaning.py    # CSV loading, cleaning, profiling logic
│   └── visualization.py    # Chart generation logic
├── static/
│   ├── style.css
│   └── plots/
│       └── .gitkeep
└── templates/
    └── index.html
```

---

## Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/yourusername/eda-web-app.git
cd eda-web-app
```

### 2. Create a virtual environment

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Mac/Linux
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the app

```bash
python app.py
```

Visit `http://127.0.0.1:5000` in your browser.

---

## Dependencies

- [Flask](https://flask.palletsprojects.com/)
- [Pandas](https://pandas.pydata.org/)
- [Matplotlib](https://matplotlib.org/)
- [Seaborn](https://seaborn.pydata.org/)
- [Gunicorn](https://gunicorn.org/)

---

## Deployment

This project is deployed on [Railway](https://railway.app). Any push to the `main` branch on GitHub will trigger an automatic redeploy.

```bash
git add .
git commit -m "your changes"
git push
```

---

## Notes

- Generated plots are saved to `static/plots/` and are ephemeral on Railway (cleared on redeploy)
- Uploaded CSVs are held in memory during the session and are not persisted to disk
