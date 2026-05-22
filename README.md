# COVID-19 Data Exploration — SQL Portfolio Project

A complete, end-to-end data analysis project using real-world COVID-19 data.
Covers SQL fundamentals through advanced techniques: joins, window functions, CTEs, temp tables, and views — all inside a local SQLite database driven by Python.

---

## Tools & Technologies

| Tool | Purpose |
|------|---------|
| Python 3 | Data download, conversion, and query runner |
| SQLite | Local relational database |
| pandas | Excel → CSV conversion and bulk loading |
| openpyxl | Excel file reading |
| requests | Downloading raw data from GitHub |
| tabulate | Clean terminal output formatting |

---

## Project Structure

```
new project/
├── data/
│   ├── CovidDeaths.xlsx          # Raw download
│   ├── CovidDeaths.csv           # Converted CSV
│   ├── CovidVaccinations.xlsx    # Raw download
│   └── CovidVaccinations.csv     # Converted CSV
├── covid_project.db              # SQLite database
├── setup.py                      # Download + convert + load DB
├── covid_exploration.sql         # 10-section SQL analysis file
├── run_queries.py                # Python runner — prints all results
└── README.md
```

---

## How to Run

### 1. Install dependencies
```bash
pip3 install pandas openpyxl requests tabulate
```

### 2. Run setup (download data, build database)
```bash
python3 setup.py
```
This will:
- Download `CovidDeaths.xlsx` and `CovidVaccinations.xlsx` from GitHub
- Convert both to `.csv`
- Load them into `covid_project.db` as SQL tables
- Create the `PercentPopulationVaccinated` view

### 3. Run the query explorer
```bash
python3 run_queries.py
```
Prints all 10 analysis sections to the terminal with formatted tables.

### 4. (Optional) Open the SQL file directly
Use any SQLite client (DB Browser for SQLite, DBeaver, VSCode SQLite extension) to open `covid_project.db` and run `covid_exploration.sql` interactively.

---

## SQL Analysis Sections

| # | Section | Description |
|---|---------|-------------|
| 1 | Basic Exploration | Preview raw rows, inspect column structure with `PRAGMA table_info` |
| 2 | Death Percentage | `total_deaths / total_cases * 100` — likelihood of dying if infected, per country and date |
| 3 | Infection Rate | `total_cases / population * 100` — what % of each country's population has been infected |
| 4 | Highest Infection Rate | Countries ranked by peak infection rate relative to population |
| 5 | Highest Death Count | Top countries and continents by total COVID deaths |
| 6 | Global Numbers | Worldwide daily and all-time totals: cases, deaths, death percentage |
| 7 | Vaccination Progress | JOIN deaths + vaccinations tables; rolling cumulative vaccinations using `SUM() OVER (PARTITION BY location ORDER BY date)` |
| 8 | CTE | Common Table Expression wrapping the vaccination join; outer query adds `% population vaccinated` |
| 9 | Temp Table | Same calculation as Section 8 using `CREATE TEMP TABLE AS SELECT ...` |
| 10 | View | `CREATE VIEW PercentPopulationVaccinated` — reusable query for dashboards and visualization tools |

---

## Key Insights

- **Death rate** peaked early in the pandemic (2020) before vaccines reduced mortality.
- **Infection rate** varies dramatically by country — small nations with high testing rates show the highest % infected.
- **Vaccination rollout** was highly uneven; high-income countries reached >60% vaccination months ahead of lower-income ones.
- **Global death percentage** (deaths/cases) trended downward over 2021–2022 as vaccines and treatment improved.

---

## Data Source

- **Dataset**: [Our World in Data — COVID-19](https://ourworldindata.org/covid-deaths)
- **Hosted by**: [Alex The Analyst — PortfolioProjects](https://github.com/AlexTheAnalyst/PortfolioProjects)
- Data covers COVID-19 cases, deaths, and vaccination records from early 2020 onward.
