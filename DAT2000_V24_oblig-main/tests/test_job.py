import logging
import pathlib
import pytest
import requests
from kjoretoy import last_opp_kjoretoy, prepp_kjoretoy
from dotenv import load_dotenv
import os
logging.basicConfig(level=logging.DEBUG)

THIS_FOLDER = pathlib.Path(__file__).parent

load_dotenv(dotenv_path=THIS_FOLDER / "test.env")
connstr = os.environ.get("CONN")
TESTDATA = THIS_FOLDER / "testdata"

URL = "http://127.0.0.1:8000"


@pytest.fixture(scope="session")
def db():
    df = prepp_kjoretoy(TESTDATA / "kjoretoyinfo_2022_jan.parquet")
    last_opp_kjoretoy(
        connstr,
        df
    )


def test_kjoretoy_regdato(db):
    kjoretoy_endpoint = URL + "/regdato"
    resp = requests.get(kjoretoy_endpoint)
    svar = resp.json()

    forventet = [
        {'farge': 'Svart (også blåsvart, grafitt mørk, gråsort, koksgrå mørk, koksgrå mørk metallic)',
         'modell': '2008'},
        {'farge': 'Rød (også burgunder)',
         'modell': 'ADVENTURE STD 600ACE'}]

    # Vi skal sortere lister bestående av dict, og da må vi angi manuelt hvordan disse skal sorteres med en funksjon.
    sorterer = lambda x:x["farge"] + x["modell"]

    # Vi sorterer de to listene
    forventet.sort(key=sorterer)
    svar.sort(key=sorterer)

    assert svar == forventet
