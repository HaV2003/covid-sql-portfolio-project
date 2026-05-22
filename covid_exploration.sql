-- ============================================================
-- COVID-19 Data Exploration
-- Database : covid_project.db (SQLite)
-- Source   : Our World in Data via Alex The Analyst
-- ============================================================


-- ------------------------------------------------------------
-- SECTION 1: Basic Exploration
-- Preview the raw data and understand column structure.
-- ------------------------------------------------------------

-- First 10 rows of deaths table
SELECT *
FROM CovidDeaths
LIMIT 10;

-- First 10 rows of vaccinations table
SELECT *
FROM CovidVaccinations
LIMIT 10;

-- Column names and types for CovidDeaths
PRAGMA table_info(CovidDeaths);

-- Column names and types for CovidVaccinations
PRAGMA table_info(CovidVaccinations);

-- Count of records in each table
SELECT 'CovidDeaths' AS table_name, COUNT(*) AS row_count FROM CovidDeaths
UNION ALL
SELECT 'CovidVaccinations', COUNT(*) FROM CovidVaccinations;


-- ------------------------------------------------------------
-- SECTION 2: Death Percentage
-- Total Cases vs Total Deaths — likelihood of dying if infected,
-- filtered to country-level rows (continent is not null/empty).
-- ------------------------------------------------------------

SELECT
    location,
    date,
    total_cases,
    total_deaths,
    ROUND(
        CAST(NULLIF(total_deaths, '') AS REAL)
        / NULLIF(CAST(NULLIF(total_cases, '') AS REAL), 0)
        * 100, 4
    ) AS DeathPercentage
FROM CovidDeaths
WHERE continent IS NOT NULL
  AND continent != ''
ORDER BY location, date;


-- ------------------------------------------------------------
-- SECTION 3: Infection Rate
-- Total Cases vs Population — what % of each country's
-- population has been infected over time.
-- ------------------------------------------------------------

SELECT
    location,
    date,
    population,
    total_cases,
    ROUND(
        CAST(NULLIF(total_cases, '') AS REAL)
        / NULLIF(CAST(NULLIF(population, '') AS REAL), 0)
        * 100, 4
    ) AS PercentPopulationInfected
FROM CovidDeaths
WHERE continent IS NOT NULL
  AND continent != ''
ORDER BY location, date;


-- ------------------------------------------------------------
-- SECTION 4: Highest Infection Rate by Country
-- Countries ranked by the highest % of population ever infected.
-- ------------------------------------------------------------

SELECT
    location,
    population,
    MAX(CAST(NULLIF(total_cases, '') AS REAL)) AS HighestInfectionCount,
    ROUND(
        MAX(CAST(NULLIF(total_cases, '') AS REAL))
        / NULLIF(CAST(NULLIF(population, '') AS REAL), 0)
        * 100, 4
    ) AS PercentPopulationInfected
FROM CovidDeaths
WHERE continent IS NOT NULL
  AND continent != ''
GROUP BY location, population
ORDER BY PercentPopulationInfected DESC;


-- ------------------------------------------------------------
-- SECTION 5: Highest Death Count — by Country and Continent
-- Countries and continents with the most total COVID deaths.
-- ------------------------------------------------------------

-- By country (highest death count)
SELECT
    location,
    MAX(CAST(NULLIF(total_deaths, '') AS INTEGER)) AS TotalDeathCount
FROM CovidDeaths
WHERE continent IS NOT NULL
  AND continent != ''
GROUP BY location
ORDER BY TotalDeathCount DESC;

-- By continent (aggregate death totals)
SELECT
    continent,
    MAX(CAST(NULLIF(total_deaths, '') AS INTEGER)) AS TotalDeathCount
FROM CovidDeaths
WHERE continent IS NOT NULL
  AND continent != ''
GROUP BY continent
ORDER BY TotalDeathCount DESC;


-- ------------------------------------------------------------
-- SECTION 6: Global Numbers
-- Worldwide totals of new cases, new deaths, and death %
-- aggregated by date across all countries.
-- ------------------------------------------------------------

SELECT
    date,
    SUM(CAST(NULLIF(new_cases, '') AS REAL))  AS total_new_cases,
    SUM(CAST(NULLIF(new_deaths, '') AS REAL)) AS total_new_deaths,
    ROUND(
        SUM(CAST(NULLIF(new_deaths, '') AS REAL))
        / NULLIF(SUM(CAST(NULLIF(new_cases, '') AS REAL)), 0)
        * 100, 4
    ) AS DeathPercentage
FROM CovidDeaths
WHERE continent IS NOT NULL
  AND continent != ''
GROUP BY date
ORDER BY date;

-- Single global aggregate (all time)
SELECT
    SUM(CAST(NULLIF(new_cases, '') AS REAL))  AS total_cases,
    SUM(CAST(NULLIF(new_deaths, '') AS REAL)) AS total_deaths,
    ROUND(
        SUM(CAST(NULLIF(new_deaths, '') AS REAL))
        / NULLIF(SUM(CAST(NULLIF(new_cases, '') AS REAL)), 0)
        * 100, 4
    ) AS DeathPercentage
FROM CovidDeaths
WHERE continent IS NOT NULL
  AND continent != '';


-- ------------------------------------------------------------
-- SECTION 7: Vaccination Progress (JOIN + Window Function)
-- Join deaths and vaccinations tables.  Use a rolling SUM window
-- function (OVER / PARTITION BY) to show cumulative vaccinations
-- per country over time.
-- ------------------------------------------------------------

SELECT
    dea.continent,
    dea.location,
    dea.date,
    dea.population,
    vac.new_vaccinations,
    SUM(CAST(NULLIF(vac.new_vaccinations, '') AS REAL))
        OVER (
            PARTITION BY dea.location
            ORDER BY dea.date
        ) AS RollingPeopleVaccinated
FROM CovidDeaths dea
JOIN CovidVaccinations vac
    ON dea.location = vac.location
    AND dea.date    = vac.date
WHERE dea.continent IS NOT NULL
  AND dea.continent != ''
ORDER BY dea.location, dea.date;


-- ------------------------------------------------------------
-- SECTION 8: CTE — % Population Vaccinated
-- Wrap the vaccination join in a CTE so we can calculate
-- rolling vaccinated % of population in the outer SELECT.
-- ------------------------------------------------------------

WITH PopvsVac AS (
    SELECT
        dea.continent,
        dea.location,
        dea.date,
        dea.population,
        vac.new_vaccinations,
        SUM(CAST(NULLIF(vac.new_vaccinations, '') AS REAL))
            OVER (
                PARTITION BY dea.location
                ORDER BY dea.date
            ) AS RollingPeopleVaccinated
    FROM CovidDeaths dea
    JOIN CovidVaccinations vac
        ON dea.location = vac.location
        AND dea.date    = vac.date
    WHERE dea.continent IS NOT NULL
      AND dea.continent != ''
)
SELECT
    *,
    ROUND(
        RollingPeopleVaccinated
        / NULLIF(CAST(NULLIF(Population, '') AS REAL), 0)
        * 100, 4
    ) AS PercentVaccinated
FROM PopvsVac
ORDER BY location, date;


-- ------------------------------------------------------------
-- SECTION 9: Temp Table — % Population Vaccinated
-- Same calculation as Section 8, but using a temporary table
-- instead of a CTE.  Temp tables persist for the session.
-- ------------------------------------------------------------

DROP TABLE IF EXISTS PercentPopulationVaccinated_Temp;

CREATE TEMP TABLE PercentPopulationVaccinated_Temp AS
SELECT
    dea.continent,
    dea.location,
    dea.date,
    dea.population,
    vac.new_vaccinations,
    SUM(CAST(NULLIF(vac.new_vaccinations, '') AS REAL))
        OVER (
            PARTITION BY dea.location
            ORDER BY dea.date
        ) AS RollingPeopleVaccinated
FROM CovidDeaths dea
JOIN CovidVaccinations vac
    ON dea.location = vac.location
    AND dea.date    = vac.date
WHERE dea.continent IS NOT NULL
  AND dea.continent != '';

SELECT
    *,
    ROUND(
        RollingPeopleVaccinated
        / NULLIF(CAST(NULLIF(Population, '') AS REAL), 0)
        * 100, 4
    ) AS PercentVaccinated
FROM PercentPopulationVaccinated_Temp
ORDER BY location, date;


-- ------------------------------------------------------------
-- SECTION 10: View — PercentPopulationVaccinated
-- Create a reusable view for use in dashboards / visualizations.
-- The view stores the rolling vaccination join query so it can
-- be queried like a table at any time.
-- ------------------------------------------------------------

DROP VIEW IF EXISTS PercentPopulationVaccinated;

CREATE VIEW PercentPopulationVaccinated AS
SELECT
    dea.continent,
    dea.location,
    dea.date,
    dea.population,
    vac.new_vaccinations,
    SUM(CAST(NULLIF(vac.new_vaccinations, '') AS REAL))
        OVER (
            PARTITION BY dea.location
            ORDER BY dea.date
        ) AS RollingPeopleVaccinated
FROM CovidDeaths dea
JOIN CovidVaccinations vac
    ON dea.location = vac.location
    AND dea.date    = vac.date
WHERE dea.continent IS NOT NULL
  AND dea.continent != '';

-- Query the view
SELECT *
FROM PercentPopulationVaccinated
LIMIT 20;
