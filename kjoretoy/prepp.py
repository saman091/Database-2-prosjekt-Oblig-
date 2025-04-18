from typing import Union

import polars as pl
import pathlib
import logging

THIS_FOLDER = pathlib.Path(__file__).parent
STATIC_DATA = THIS_FOLDER / "statiske_data"


def prepp_kjoretoy(inn_fil: Union[str, pathlib.Path]) -> pl.DataFrame:
    logging.info(f"Start prepping data in file {inn_fil}")
    lf = pl.scan_parquet(inn_fil)

    # Casting av dato-kolonner.
    # !!!! ERSTATT MED DIN KODE:
    lf = lf.with_columns([
        pl.col("tekn_reg_f_g_n").cast(str).str.strptime(pl.Date, "%Y%m%d"),
        pl.col("tekn_reg_f_g").cast(str).str.strptime(pl.Date, "%Y%m%d"),
        pl.col("tekn_reg_eier_dato").cast(str).str.strptime(pl.Date, "%Y%m%d"),
        pl.col("tekn_siste_pkk").str.strptime(pl.Date, "%Y%m%d", strict=False),
        pl.col("tekn_neste_pkk").str.strptime(pl.Date, "%Y%m%d", strict=False)
    ])

    # Denne er viktig fordi data er ikke unikt identifisert av kolonnene våre
    # Vi får trøbbel når vi skal gjøre group by senere - noen (forskjellige) biler har identiske data.
    lf = lf.with_row_index("id")

    # Vi leser inn fargekodene
    fargekode = pl.scan_csv(STATIC_DATA / "fargekode.csv", separator=";", dtypes={"kode": str})

    # Legg merke til at tekn_farge i lf har 0 først.
    # Dette må vi fikse også i fargekode for å kunne joine.
    # Vi vil også bytte navn på "beskrivelse"-kolonna til noe mer fornuftig.
    fargekode = fargekode.with_columns(
        pl.col("kode").str.pad_start(2, "0")
    ).rename(
        {"beskrivelse": "farge_navn"}
    )

    # Vi må gjøre en liten jobb for å kunne joine hver fargekode med fargen sin.
    # Først så lager vi en nøstet liste inne i hver kolonne ved å splitte på.
    lf = lf.with_columns(pl.col("tekn_farge").str.split(","))

    # Nå "sprenger" vi denne liste-kolonnen, og lager i stedet for en ny rad pr. listeelement i tekn_farge hvor de andre radene er identiske.
    lf = lf.explode("tekn_farge")

    # Med left join så mister vi ingen biler vi ikke vet fargen på.
    lf = lf.join(fargekode, left_on="tekn_farge", right_on="kode", how="left")

    # Vi grupperer på alle kolonner som ikke er tekn farge og farge navn.
    # Se https://docs.pola.rs/user-guide/expressions/column-selections/
    # Vi aggregerer farge_navn og tekn_farge - dette samler bare opp kolonnene som nøstede kolonner (liste-kolonner).
    # Fra liste-kolonnene kan vi joine elementene inne i listene til strenger.
    lf = lf.group_by(pl.col("*").exclude("tekn_farge", "farge_navn")).agg(
        pl.col("farge_navn"),
        pl.col("tekn_farge"),
    ).with_columns(
        pl.col("farge_navn").list.join(","),
        pl.col("tekn_farge").list.join(",")
    )

    # Vi lager en egen elbil-kolonne
    # !!!! ERSTATT MED DIN KODE:
    lf = lf.with_columns(
        (pl.col("tekn_drivstoff") == "Elektrisk").alias("elbil")
    )

    # Vi vil også ha inn skriftlig beskrivelse av bilmerket
    merkekode = pl.scan_csv(STATIC_DATA / "merkekode.csv", separator=";").rename(
        {"navn": "merke_navn"}
    )
    lf = lf.join(merkekode, left_on="tekn_merke", right_on="kode", how="left")

    # Vi henter ut kolonnene vi trenger
    lf = lf.select(
        "id",
        "tekn_reg_f_g_n",
        "tekn_reg_eier_dato",
        "tekn_aksler_drift",
        "merke_navn",
        "tekn_modell",
        "tekn_drivstoff",
        "tekn_neste_pkk",
        "farge_navn",
        "elbil")
    logging.info(f"Finished prepping {inn_fil}")
    return lf.collect()
