import sqlite3
from pathlib import Path

import pandas as pd

from hadoop.company_counts import run_hadoop_company_counts


PROJECT_DIR = Path(__file__).resolve().parent.parent
DATABASE = PROJECT_DIR / "data" / "jobmarket.db"
SCENARIOS = {
    "all": ("", ""),
    "engineer": ("engineer", ""),
    "engineer_mumbai": ("engineer", "mumbai"),
    "analyst": ("analyst", ""),
    "analyst_mumbai": ("analyst", "mumbai"),
}


def main():
    with sqlite3.connect(DATABASE) as connection:
        jobs = pd.read_sql_query(
            "SELECT title, company, location, remote, posted FROM jobs",
            connection
        )

    for column in ["title", "company", "location", "remote"]:
        jobs[column] = jobs[column].fillna("").astype(str)
    jobs["posted"] = pd.to_datetime(jobs["posted"], errors="coerce")

    valid_dates = jobs["posted"].dropna()
    if valid_dates.empty:
        raise ValueError("Cannot precompute demo counts: no valid posted dates.")

    default_start = valid_dates.min().date()
    default_end = valid_dates.max().date()
    filtered_jobs = jobs[
        (jobs["posted"] >= pd.Timestamp(default_start))
        & (jobs["posted"] < pd.Timestamp(default_end) + pd.Timedelta(days=1))
    ]

    results = {}
    for scenario, (role_filter, location_filter) in SCENARIOS.items():
        scenario_jobs = filtered_jobs[
            filtered_jobs["title"].str.contains(
                role_filter, case=False, na=False
            )
        ]
        if location_filter:
            scenario_jobs = scenario_jobs[
                scenario_jobs["location"].str.contains(
                    location_filter, case=False, na=False
                )
            ]

        counts = run_hadoop_company_counts(scenario_jobs["company"])
        results[scenario] = counts
        print(
            f"{scenario}: {len(scenario_jobs):,} matching rows, "
            f"{int(counts['Jobs'].sum()):,} counted by Hadoop"
        )

    with sqlite3.connect(DATABASE) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS demo_company_counts (
                scenario TEXT NOT NULL,
                company TEXT,
                jobs INTEGER,
                PRIMARY KEY (scenario, company)
            )
            """
        )
        connection.execute("DELETE FROM demo_company_counts")
        for scenario, counts in results.items():
            if counts.empty:
                connection.execute(
                    """
                    INSERT INTO demo_company_counts (scenario, company, jobs)
                    VALUES (?, NULL, NULL)
                    """,
                    (scenario,)
                )
                continue

            connection.executemany(
                """
                INSERT INTO demo_company_counts (scenario, company, jobs)
                VALUES (?, ?, ?)
                """,
                [
                    (scenario, row.Company, int(row.Jobs))
                    for row in counts.itertuples(index=False)
                ]
            )

    print(f"Saved Hadoop MapReduce demo counts to {DATABASE}")


if __name__ == "__main__":
    main()
