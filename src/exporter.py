from urllib.parse import quote_plus
from sqlalchemy import create_engine, text


# --------------------------------------------------
# Export to MySQL
# --------------------------------------------------
def export_to_mysql(df, host, user, password, database, table_name):
    """
    Exports a cleaned DataFrame to a MySQL table.

    BUG FIX: Column name sanitization now happens BEFORE to_sql(),
    so the database receives properly-named columns.
    The old code sanitized columns AFTER writing, which had no effect.
    """
    # --- Step 1: Sanitize column names BEFORE writing ---
    df = df.copy()

    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(r'\s+', '_', regex=True)
        .str.replace(r'[^a-z0-9_]', '', regex=True)
        .str.replace(r'_+', '_', regex=True)
        .str.strip('_')
    )

    # --- Step 2: Connect and verify ---
    encoded_password = quote_plus(password)
    connection_string = (
        f"mysql+pymysql://{user}:{encoded_password}@{host}:3306/{database}"
    )

    engine = create_engine(connection_string)

    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))

    # --- Step 3: Write to MySQL ---
    df.to_sql(
        table_name,
        engine,
        if_exists="replace",
        index=False
    )

    return len(df)