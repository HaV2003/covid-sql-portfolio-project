"""
COVID-19 Portfolio Project — Setup Script
Downloads data, converts to CSV, and loads into SQLite database.
"""

import os
import sqlite3
import requests
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(BASE_DIR, "covid_project.db")

FILES = {
    "CovidDeaths": "https://raw.githubusercontent.com/AlexTheAnalyst/PortfolioProjects/main/CovidDeaths.xlsx",
    "CovidVaccinations": "https://raw.githubusercontent.com/AlexTheAnalyst/PortfolioProjects/main/CovidVaccinations.xlsx",
}


def download_file(name, url):
    xlsx_path = os.path.join(DATA_DIR, f"{name}.xlsx")
    print(f"  Downloading {name}.xlsx ...")
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    with open(xlsx_path, "wb") as f:
        f.write(response.content)
    print(f"  Saved to {xlsx_path}")
    return xlsx_path


def convert_to_csv(name, xlsx_path):
    csv_path = os.path.join(DATA_DIR, f"{name}.csv")
    print(f"  Converting {name}.xlsx → {name}.csv ...")
    df = pd.read_excel(xlsx_path, engine="openpyxl")
    df.to_csv(csv_path, index=False)
    print(f"  Rows: {len(df):,}  |  Columns: {len(df.columns)}")
    return csv_path, df


def load_to_sqlite(conn, name, df):
    print(f"  Loading {name} into SQLite ...")
    df.to_sql(name, conn, if_exists="replace", index=False)
    count = conn.execute(f"SELECT COUNT(*) FROM [{name}]").fetchone()[0]
    print(f"  Table '{name}': {count:,} rows loaded")


def main():
    print("=" * 55)
    print("  COVID-19 Portfolio Project — Database Setup")
    print("=" * 55)

    os.makedirs(DATA_DIR, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    print(f"\nDatabase: {DB_PATH}\n")

    for name, url in FILES.items():
        print(f"[{name}]")
        xlsx_path = download_file(name, url)
        csv_path, df = convert_to_csv(name, xlsx_path)
        load_to_sqlite(conn, name, df)
        print()

    print("Creating view PercentPopulationVaccinated ...")
    conn.execute("DROP VIEW IF EXISTS PercentPopulationVaccinated")
    conn.execute("""
        CREATE VIEW PercentPopulationVaccinated AS
        SELECT
            dea.continent,
            dea.location,
            dea.date,
            dea.population,
            vac.new_vaccinations,
            SUM(CAST(NULLIF(vac.new_vaccinations, '') AS REAL))
                OVER (PARTITION BY dea.location ORDER BY dea.date) AS RollingPeopleVaccinated
        FROM CovidDeaths dea
        JOIN CovidVaccinations vac
            ON dea.location = vac.location
            AND dea.date = vac.date
        WHERE dea.continent IS NOT NULL
          AND dea.continent != ''
    """)
    conn.commit()
    conn.close()

    print("\nSetup complete!")
    print(f"  Data files : {DATA_DIR}/")
    print(f"  Database   : {DB_PATH}")
    print("\nNext step: python3 run_queries.py")


if __name__ == "__main__":
    main()
