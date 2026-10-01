import os
import pandas as pd
import mysql.connector
from mysql.connector import Error


def run_robust_etl(csv_path):
    """
    Reads budget data from CSV and loads it into MySQL.000000000
    """
    
    # -----------------------------
    # Read CSV
    # -----------------------------
    df = pd.read_csv(csv_path)
    
    # Remove extra spaces from column names
    df.columns = df.columns.str.strip()
    
    # Replace missing values with 0
    df.fillna(0, inplace=True)
    
    print("\n========== CSV Columns ==========")
    for col in df.columns:
        print(col)
    print("=================================\n")

    sector_specs = [
        ("Defence", ["Defence", "Defense"]),
        ("Education", ["Education"]),
        ("Health", ["Health"]),
        ("Interest_Payments", ["Interest_Payments"]),
        ("Infrastructure", ["Infrastructure"]),
        ("Agriculture", ["Agriculture"]),
        ("State_Transfers", ["State_Transfers"]),
        ("Social_Welfare", ["Social_Welfare"])
    ]

    # -----------------------------
    # Check required columns
    # -----------------------------
    required_columns = [
        "Country",
        "Year",
        "Total_Budget_Billions_USD"
    ]

    missing = []

    for sector_name, aliases in sector_specs:
        percent_column = next(
            (
                f"{alias}_Percentage"
                for alias in aliases
                if f"{alias}_Percentage" in df.columns
            ),
            None
        )
        amount_column = next(
            (
                f"{alias}_Amount_Billions_USD"
                for alias in aliases
                if f"{alias}_Amount_Billions_USD" in df.columns
            ),
            None
        )

        if percent_column is None:
            missing.append(f"{sector_name}_Percentage")

        if amount_column is None:
            missing.append(f"{sector_name}_Amount_Billions_USD")

    if missing:
        print("\nERROR: These columns are missing from the CSV:\n")
        for m in missing:
            print(" -", m)

        print("\nPlease compare these with the printed CSV column names above.")
        return

    conn = None
    cursor = None

    try:

        # -----------------------------
        # Connect MySQL
        # -----------------------------
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password=os.getenv("DB_PASSWORD"),
            database="global_budget_db"
        )

        cursor = conn.cursor()

        print("Connected to MySQL.\n")

        # -----------------------------
        # Insert countries
        # -----------------------------
        print("Step 1 : Loading Countries")

        for country in df["Country"].unique():

            cursor.execute(
                """
                INSERT IGNORE INTO countries(country_name)
                VALUES(%s)
                """,
                (country.strip(),)
            )

        conn.commit()

        # -----------------------------
        # Create lookup dictionary
        # -----------------------------
        cursor.execute(
            "SELECT country_name, country_id FROM countries"
        )

        country_lookup = dict(cursor.fetchall())

        print("Step 2 : Loading Budgets")

        success = 0

        for index, row in df.iterrows():

            try:

                country = row["Country"].strip()

                country_id = country_lookup[country]

                year = int(row["Year"])

                total_budget = float(
                    row["Total_Budget_Billions_USD"]
                )

                cursor.execute(
                    "SELECT budget_id FROM budgets WHERE country_id = %s AND year = %s",
                    (country_id, year)
                )
                existing_budget = cursor.fetchone()

                if existing_budget is not None:
                    print(f"Row {index} skipped : budget already exists for {country} {year}")
                    continue

                cursor.execute(
                    """
                    INSERT INTO budgets
                    (
                        country_id,
                        year,
                        total_budget_billions_usd
                    )
                    VALUES
                    (
                        %s,
                        %s,
                        %s
                    )
                    """,
                    (
                        country_id,
                        year,
                        total_budget
                    )
                )

                budget_id = cursor.lastrowid

                for sector_name, aliases in sector_specs:

                    percent_column = next(
                        (
                            f"{alias}_Percentage"
                            for alias in aliases
                            if f"{alias}_Percentage" in df.columns
                        ),
                        None
                    )
                    amount_column = next(
                        (
                            f"{alias}_Amount_Billions_USD"
                            for alias in aliases
                            if f"{alias}_Amount_Billions_USD" in df.columns
                        ),
                        None
                    )

                    if percent_column is None or amount_column is None:
                        continue

                    pct = float(row[percent_column])

                    amt = float(row[amount_column])

                    cursor.execute(
                        """
                        INSERT INTO sector_allocations
                        (
                            budget_id,
                            sector_name,
                            allocated_percentage,
                            allocated_amount_billions_usd
                        )
                        VALUES
                        (
                            %s,
                            %s,
                            %s,
                            %s
                        )
                        """,
                        (
                            budget_id,
                            sector_name,
                            pct,
                            amt
                        )
                    )

                success += 1

            except Error as e:

                print(f"Row {index} failed : {e}")

        conn.commit()

        print("\n===================================")
        print(f"Inserted {success} budget records.")
        print("ETL Completed Successfully.")
        print("===================================")

    except Error as e:

        print("\nDatabase Error")
        print(e)

    finally:

        if cursor is not None:
            cursor.close()

        if conn is not None and conn.is_connected():
            conn.close()

        print("\nMySQL Connection Closed.")


if __name__ == "__main__":
    run_robust_etl("Master_Global_Budgets_Historical.csv")