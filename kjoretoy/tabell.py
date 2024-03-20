from sqlalchemy import Table, Column, Integer, String, MetaData, Date, Boolean, text, literal


def kjoretoy_tabell() -> Table:
    metadata_obj = MetaData()
    kjoretoy = Table(
        "kjoretoy",
        metadata_obj,
        Column("id", Integer),
        Column("tekn_reg_f_g_n", Date, index=True),
        Column("tekn_reg_eier_dato", Date),
        Column("tekn_aksler_drift", Integer),
        Column("merke_navn", String(255)),
        Column("tekn_modell", String(255)),
        Column("tekn_drivstoff", String(255)),
        Column("tekn_neste_pkk", Date),
        Column("farge_navn", String(255)),
        Column("elbil", Boolean)
    )
    return kjoretoy
