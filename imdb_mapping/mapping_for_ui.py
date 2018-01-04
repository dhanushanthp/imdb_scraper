import pandas as pd

from sqlalchemy import create_engine

engine = create_engine('')


def get_missing_mapping():
    hooq_data = pd.read_sql_query("""""",  engine)

    return hooq_data.to_json(orient='records', force_ascii=False)