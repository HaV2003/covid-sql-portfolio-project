"""
COVID-19 Portfolio Project — Query Runner
Connects to covid_project.db and prints results for all 10 SQL sections.
"""

import os
import sqlite3
from tabulate import tabulate

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "covid_project.db")

PREVIEW_ROWS = 10


def run_query(conn, title, sql, limit=PREVIEW_ROWS):
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")
    try:
        cursor = conn.execute(sql)
        cols = [d[0] for d in cursor.description]
        rows = cursor.fetchmany(limit)
        if rows:
            print(tabulate(rows, headers=cols, tablefmt="rounded_outline", floatfmt=".4f"))
            print(f"  (showing up to {limit} rows)")
        else:
            print("  No results returned.")
    except Exception as e:
        print(f"  ERROR: {e}")


def main():
    if not os.path.exists(DB_PATH):
        print("Database not found. Run 'python3 setup.py' first.")
        return

    conn = sqlite3.connect(DB_PATH)

    # Table counts
    print("\n" + "=" * 60)
    print("  COVID-19 Data Exploration — Query Runner")
    print("=" * 60)
    for table in ("CovidDeaths", "CovidVaccinations"):
        count = conn.execute(f"SELECT COUNT(*) FROM [{table}]").fetchone()[0]
        print(f"  {table}: {count:,} rows")

    # ----------------------------------------------------------
    # Section 1: Basic Exploration
    # ----------------------------------------------------------
    run_query(conn, "SECTION 1 — Basic Exploration (CovidDeaths)", """
        SELECT iso_code, continent, location, date, population,
               total_cases, new_cases, total_deaths, new_deaths
        FROM CovidDeaths
        LIMIT 10
    """)

    run_query(conn, "SECTION 1 — Basic Exploration (CovidVaccinations)", """
        SELECT iso_code, continent, location, date,
               new_vaccinations, total_vaccinations, people_vaccinated
        FROM CovidVaccinations
        LIMIT 10
    """)

    # ----------------------------------------------------------
    # Section 2: Death Percentage
    # ----------------------------------------------------------
    run_query(conn, "SECTION 2 — Death Percentage (Top 10 by death %)", """
        SELECT location, date, total_cases, total_deaths,
               ROUND(
                   CAST(NULLIF(total_deaths,'') AS REAL)
                   / NULLIF(CAST(NULLIF(total_cases,'') AS REAL), 0)
                   * 100, 4
               ) AS DeathPercentage
        FROM CovidDeaths
        WHERE continent IS NOT NULL AND continent != ''
          AND CAST(NULLIF(total_cases,'') AS REAL) > 0
        ORDER BY DeathPercentage DESC
        LIMIT 10
    """)

    # ----------------------------------------------------------
    # Section 3: Infection Rate
    # ----------------------------------------------------------
    run_query(conn, "SECTION 3 — Infection Rate (top 10 by % infected)", """
        SELECT location, date, population, total_cases,
               ROUND(
                   CAST(NULLIF(total_cases,'') AS REAL)
                   / NULLIF(CAST(NULLIF(population,'') AS REAL), 0)
                   * 100, 4
               ) AS PercentPopulationInfected
        FROM CovidDeaths
        WHERE continent IS NOT NULL AND continent != ''
        ORDER BY PercentPopulationInfected DESC
        LIMIT 10
    """)

    # ----------------------------------------------------------
    # Section 4: Highest Infection Rate by Country
    # ----------------------------------------------------------
    run_query(conn, "SECTION 4 — Highest Infection Rate by Country", """
        SELECT location, population,
               MAX(CAST(NULLIF(total_cases,'') AS REAL)) AS HighestInfectionCount,
               ROUND(
                   MAX(CAST(NULLIF(total_cases,'') AS REAL))
                   / NULLIF(CAST(NULLIF(population,'') AS REAL), 0)
                   * 100, 4
               ) AS PercentPopulationInfected
        FROM CovidDeaths
        WHERE continent IS NOT NULL AND continent != ''
        GROUP BY location, population
        ORDER BY PercentPopulationInfected DESC
        LIMIT 10
    """)

    # ----------------------------------------------------------
    # Section 5: Highest Death Count by Country
    # ----------------------------------------------------------
    run_query(conn, "SECTION 5a — Highest Death Count by Country", """
        SELECT location,
               MAX(CAST(NULLIF(total_deaths,'') AS INTEGER)) AS TotalDeathCount
        FROM CovidDeaths
        WHERE continent IS NOT NULL AND continent != ''
        GROUP BY location
        ORDER BY TotalDeathCount DESC
        LIMIT 10
    """)

    run_query(conn, "SECTION 5b — Highest Death Count by Continent", """
        SELECT location AS continent,
               MAX(CAST(NULLIF(total_deaths,'') AS INTEGER)) AS TotalDeathCount
        FROM CovidDeaths
        WHERE (continent IS NULL OR continent = '')
          AND location NOT IN ('World', 'International', 'High income', 'Upper middle income', 'Lower middle income', 'Low income')
        GROUP BY location
        ORDER BY TotalDeathCount DESC
    """)

    # ----------------------------------------------------------
    # Section 6: Global Numbers
    # ----------------------------------------------------------
    run_query(conn, "SECTION 6 — Global Numbers by Date (sample)", """
        SELECT date,
               SUM(CAST(NULLIF(new_cases,'') AS REAL))  AS total_new_cases,
               SUM(CAST(NULLIF(new_deaths,'') AS REAL)) AS total_new_deaths,
               ROUND(
                   SUM(CAST(NULLIF(new_deaths,'') AS REAL))
                   / NULLIF(SUM(CAST(NULLIF(new_cases,'') AS REAL)), 0)
                   * 100, 4
               ) AS DeathPercentage
        FROM CovidDeaths
        WHERE continent IS NOT NULL AND continent != ''
        GROUP BY date
        ORDER BY total_new_cases DESC
        LIMIT 10
    """)

    run_query(conn, "SECTION 6 — Global Totals (all time)", """
        SELECT
            SUM(CAST(NULLIF(new_cases,'') AS REAL))  AS total_cases,
            SUM(CAST(NULLIF(new_deaths,'') AS REAL)) AS total_deaths,
            ROUND(
                SUM(CAST(NULLIF(new_deaths,'') AS REAL))
                / NULLIF(SUM(CAST(NULLIF(new_cases,'') AS REAL)), 0)
                * 100, 4
            ) AS DeathPercentage
        FROM CovidDeaths
        WHERE continent IS NOT NULL AND continent != ''
    """)

    # ----------------------------------------------------------
    # Section 7: Vaccination Progress with Window Function
    # ----------------------------------------------------------
    run_query(conn, "SECTION 7 — Rolling Vaccination Count (JOIN + OVER)", """
        SELECT dea.continent, dea.location, dea.date, dea.population,
               vac.new_vaccinations,
               SUM(CAST(NULLIF(vac.new_vaccinations,'') AS REAL))
                   OVER (PARTITION BY dea.location ORDER BY dea.date)
                   AS RollingPeopleVaccinated
        FROM CovidDeaths dea
        JOIN CovidVaccinations vac
            ON dea.location = vac.location AND dea.date = vac.date
        WHERE dea.continent IS NOT NULL AND dea.continent != ''
          AND vac.new_vaccinations IS NOT NULL AND vac.new_vaccinations != ''
        ORDER BY dea.location, dea.date
        LIMIT 10
    """)

    # ----------------------------------------------------------
    # Section 8: CTE — % Population Vaccinated
    # ----------------------------------------------------------
    run_query(conn, "SECTION 8 — CTE: % Population Vaccinated", """
        WITH PopvsVac AS (
            SELECT dea.continent, dea.location, dea.date, dea.population,
                   vac.new_vaccinations,
                   SUM(CAST(NULLIF(vac.new_vaccinations,'') AS REAL))
                       OVER (PARTITION BY dea.location ORDER BY dea.date)
                       AS RollingPeopleVaccinated
            FROM CovidDeaths dea
            JOIN CovidVaccinations vac
                ON dea.location = vac.location AND dea.date = vac.date
            WHERE dea.continent IS NOT NULL AND dea.continent != ''
        )
        SELECT *,
               ROUND(
                   RollingPeopleVaccinated
                   / NULLIF(CAST(NULLIF(Population,'') AS REAL), 0)
                   * 100, 4
               ) AS PercentVaccinated
        FROM PopvsVac
        WHERE RollingPeopleVaccinated IS NOT NULL
        ORDER BY PercentVaccinated DESC
        LIMIT 10
    """)

    # ----------------------------------------------------------
    # Section 9: Temp Table — % Population Vaccinated
    # ----------------------------------------------------------
    try:
        conn.execute("DROP TABLE IF EXISTS PercentPopulationVaccinated_Temp")
        conn.execute("""
            CREATE TEMP TABLE PercentPopulationVaccinated_Temp AS
            SELECT dea.continent, dea.location, dea.date, dea.population,
                   vac.new_vaccinations,
                   SUM(CAST(NULLIF(vac.new_vaccinations,'') AS REAL))
                       OVER (PARTITION BY dea.location ORDER BY dea.date)
                       AS RollingPeopleVaccinated
            FROM CovidDeaths dea
            JOIN CovidVaccinations vac
                ON dea.location = vac.location AND dea.date = vac.date
            WHERE dea.continent IS NOT NULL AND dea.continent != ''
        """)
    except Exception as e:
        print(f"\n  Temp table creation error: {e}")

    run_query(conn, "SECTION 9 — Temp Table: % Population Vaccinated", """
        SELECT *,
               ROUND(
                   RollingPeopleVaccinated
                   / NULLIF(CAST(NULLIF(Population,'') AS REAL), 0)
                   * 100, 4
               ) AS PercentVaccinated
        FROM PercentPopulationVaccinated_Temp
        WHERE RollingPeopleVaccinated IS NOT NULL
        ORDER BY PercentVaccinated DESC
        LIMIT 10
    """)

    # ----------------------------------------------------------
    # Section 10: View — PercentPopulationVaccinated
    # ----------------------------------------------------------
    run_query(conn, "SECTION 10 — View: PercentPopulationVaccinated", """
        SELECT *
        FROM PercentPopulationVaccinated
        WHERE RollingPeopleVaccinated IS NOT NULL
        ORDER BY location, date
        LIMIT 10
    """)

    conn.close()
    print("\n" + "=" * 60)
    print("  All queries complete.")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
