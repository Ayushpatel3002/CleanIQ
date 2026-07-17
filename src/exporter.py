from urllib.parse import quote_plus
from sqlalchemy import create_engine
from sqlalchemy import text
from urllib.parse import quote_plus


def export_to_mysql(
    df,
    host,
    user,
    password,
    database,
    table_name
):

    password = quote_plus(password)

    connection_string = (
        f"mysql+pymysql://{user}:{password}@{host}:3306/{database}"
    )

    engine = create_engine(connection_string)

    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))

    df.to_sql(
        table_name,
        engine,
        if_exists="replace",
        index=False
    )
    # Clean column names for MySQL
    df = df.copy()

    df.columns = (
    df.columns
      .str.strip()           # remove leading/trailing spaces
      .str.replace(" ", "_") # replace spaces with _
      .str.replace("-", "_")
      .str.replace("/", "_")
      .str.replace(r"[^A-Za-z0-9_]", "", regex=True)
    )

    return len(df)