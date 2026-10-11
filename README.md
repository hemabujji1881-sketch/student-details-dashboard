# Student Performance Dashboard

An interactive student data visualization project built with **Python, Streamlit, Pandas, and Plotly**.

## Features

- Sidebar filters for gender, race/ethnicity, parent education, lunch type, test preparation, average-score band, and score range.
- Every filter updates **all KPI cards, charts, and the student table** because they all use one shared filtered DataFrame.
- KPI cards: number of students in view, average score, highest-scoring subject, and percentage with average score of at least 40.
- Charts: subject averages, average score by gender, score distribution, test preparation comparison, math-vs-reading scatter plot, and subject correlation heatmap.
- Filtered records table and CSV download.

## Dataset

This project uses `data/StudentsPerformance.csv` (Students Performance in Exams). The original columns include gender, race/ethnicity, parental education, lunch, test preparation, and math/reading/writing scores. Check the original Kaggle dataset page for its current license and attribution requirements before redistributing the data.

## Run locally

1. Install Python 3.10 or newer.
2. Download or clone this repository.
3. Open a terminal in the project folder.
4. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

5. Start Streamlit:

   ```bash
   streamlit run app.py
   ```

6. Streamlit will print a local URL (usually `http://localhost:8501`). Open it in your browser.

## Upload to GitHub

Create a new empty repository on GitHub, then run these commands in the project folder:

```bash
git init
git add .
git commit -m "Add student performance dashboard"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/student-analytics-dashboard.git
git push -u origin main
```

Replace `YOUR-USERNAME` with your GitHub username and use the URL of your repository.

## Deploy with Streamlit Community Cloud

1. Push this project to GitHub.
2. Sign in to Streamlit Community Cloud with GitHub.
3. Choose **Create app** and select your repository, branch (`main`), and main file path (`app.py`).
4. Deploy. Streamlit installs packages from `requirements.txt`.
5. Add the deployed app URL to this README after deployment.

## Project structure

```text
student-analytics-dashboard/
├── app.py
├── requirements.txt
├── README.md
├── data/
│   └── StudentsPerformance.csv
└── screenshots/
```
