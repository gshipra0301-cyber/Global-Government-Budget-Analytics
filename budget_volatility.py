import os
import urllib.parse
from sqlalchemy import create_engine
import pandas as pd
def analyze_budget_volatility(country_name):
    password_quoted = urllib.parse.quote_plus(os.getenv("DB_PASSWORD"))
    engine = create_engine(
        f"mysql+pymysql://root:{password_quoted}@localhost/global_budget_db"
    )
    # Extract historical spending sequence
    query = """
        SELECT b.year, b.total_budget_billions_usd
        FROM budgets b
        JOIN countries c ON b.country_id = c.country_id
        WHERE c.country_name = %s ORDER BY b.year ASC;
    """ 
    df = pd.read_sql(query, engine, params=(country_name,))

    if df.empty:
        return

    #Calculate a 10-year rolling Mean and Standard Deviation using Pandas
    df['rolling_mean'] = df['total_budget_billions_usd'].rolling(windows=10).mean()
    df['rolling_std']  = df['total_budget_billions_usd'].rolling(windows=10).std()

    #Calculate volatility Index(Coefficient of variation)
    df['volatility_index'] = (df['rolling_std'] / df['rolling_mean']) * 100

    print(f"\n--- Era Volatility Index for {country_name} (sample) ---")
    print(df.dropna().head(10))
    return df
if __name__ == "__main__":
    analyze_budget_volatility("United States") # or your country name