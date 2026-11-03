import os
import json
import logging
from dotenv import load_dotenv
import pyarrow.parquet as pq
import pyarrow as pa
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.pool import QueuePool
from config import TABLE_LIST
import pandas as pd
from pathlib import Path



logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
test_data_folder = "../data/"
test_path = Path(test_data_folder)

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


def test_extract_query(outpath, compression="snappy"):
    mysql_engine = get_engine()

    query = text("""SELECT 
                    name, 
                    supplier, 
                    supplier_name, 
                    posting_date, 
                    due_date, 
                    base_grand_total FROM `tabPurchase Invoice` WHERE docstatus = 1 
                    AND YEAR(posting_date) = 2026 """)

    with mysql_engine.connect() as connection:
        df_test = pd.read_sql(query, connection)
        extraction_date = datetime.strftime(datetime.now(), "%Y-%m-%d %HH:%MM:%SS")
        
        df_test.to_parquet(outpath/"purchase_invoices_"{extraction_date}, compression=compression)
