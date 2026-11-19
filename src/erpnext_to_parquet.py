from ast import List
import os
import json
import logging
from dotenv import load_dotenv
import pyarrow.parquet as pq
import pyarrow as pa
from datetime import datetime
from sqlalchemy import create_engine, exists, text
from sqlalchemy.pool import QueuePool
from config import TABLE_LIST
import pandas as pd
from pathlib import Path
import sqlalchemy.engine as Engine



logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def get_connection_details():
    load_dotenv(".env")
    host = os.getenv("HOST")
    port = os.getenv("PORT")
    user = os.getenv("DB_USER")
    db = os.getenv("DB_NAME")
    password = os.getenv("PASSWORD")

    return {"host":host,
            "port":port, 
            "user":user, 
            "db_name": db, 
            "password": password}

def get_engine():
    connection_details = get_connection_details()
    host = connection_details["host"]
    user  = connection_details["user"]
    password = connection_details["password"]
    db_name = connection_details["db_name"]

    sql_alchemy_URL = f"mysql+pymysql://{user}:{password}@{host}/{db_name}"

    mysql_engine = create_engine(sql_alchemy_URL,
                                poolclass=QueuePool,
                                pool_size=10,
                                pool_pre_ping=True, echo=False)

    return mysql_engine




def extract_from_erp(engine: Engine, table_list: List):
    table_names = table_list
    assert len(table_names) > 0
    engine = get_engine()
    for table in table_names:
        select_query = text(f""" SELECT * FROM `tab{table}`""")
        clean_table_name = table.replace(" ","")
        table_folder = f"data/{clean_table_name}"

        ## We need to have a sub-directory for every table
        os.makedirs(table_folder, exist_ok=True)






def test_extract_query(outpath, compression="snappy"):
    mysql_engine = get_engine()
    print(mysql_engine)
    query = text("""SELECT 
                    name, 
                    supplier, 
                    supplier_name, 
                    posting_date, 
                    due_date, 
                    base_grand_total FROM `tabPurchase Invoice` WHERE docstatus = 1 
                    AND YEAR(posting_date) = 2026 """)

    with mysql_engine.connect() as connection:
        logging.info("Extracting data from purchase invoices ...")
        df_test = pd.read_sql(query, connection)
        extraction_date = datetime.strftime(datetime.now(), "%Y_%m_%d_%H_%M_%S")
        logging.info("Finshed extracting data, saving data to file ....")
        
        df_test.to_parquet(outpath / f"purchase_invoices_{extraction_date}.parquet", compression=compression)


if __name__ == "__main__":
    get_engine()

