from typing import Union

from sqlalchemy import create_engine
import polars as pl
from .tabell import kjoretoy_tabell
import logging
from pathlib import Path

def last_opp_kjoretoy(connstr: str, df:pl.DataFrame):
    logging.info(f"Starting database upload")
    # Vi lager engine for å koble til databasen med connstr
    engine = create_engine(connstr)

    kjoretoy = kjoretoy_tabell()
    # Vi dropper tabellen og lager den på nytt.
    kjoretoy.drop(engine, checkfirst=True)
    kjoretoy.create(engine, checkfirst=False)
    n_rows = df.write_database("kjoretoy", connection=connstr, if_table_exists="append")
    logging.info(f"Finished writing {n_rows} to the database")
