import os
import mysql.connector
from typing import Tuple


def maak_verbinding_met_database() -> mysql.connector.connection.MySQLConnection:
    """Maak verbinding met de lokale database."""
    verbinding = mysql.connector.connect(
        host="localhost",
        user="posta",
        password=os.environ.get("paswoord_db"),
        database="dbposta")
    return verbinding


def haal_laatste_id_op() -> int:
    """Haal het laatste ID op uit de photos tabel."""
    verbinding = maak_verbinding_met_database()
    cursor = verbinding.cursor()
    cursor.execute("SELECT MAX(id) FROM info;")
    resultaat = cursor.fetchone()[0] or 0
    cursor.close()
    verbinding.close()
    return resultaat


def sla_afbeelding_op(foto_locatie: str, id: int) -> None:
    """Sla de locatie van de afbeelding op in de database met behulp van het ID."""
    verbinding = maak_verbinding_met_database()
    cursor = verbinding.cursor()
    sql_command = f"""
        UPDATE info
        SET picture = %s
        WHERE id = %s;
    """
    cursor.execute(sql_command, (foto_locatie, id))
    verbinding.commit()
    cursor.close()
    verbinding.close()


def sla_beschrijving_op(beschrijving: str, id: int) -> None:
    """Sla de beschrijving op in de database met behulp van het ID."""
    verbinding = maak_verbinding_met_database()
    cursor = verbinding.cursor()
    sql_command = f"""
        UPDATE info
        SET description = %s
        WHERE id = %s;
    """
    cursor.execute(sql_command, (beschrijving, id))
    verbinding.commit()
    cursor.close()
    verbinding.close()


def afbeelding_met_beschrijving_uploaden(foto_locatie: str, beschrijving: str) -> Tuple[str, int]:
    """Upload een afbeelding samen met de beschrijving."""
    id = haal_laatste_id_op() + 1
    verbinding = maak_verbinding_met_database()
    cursor = verbinding.cursor()
    sql_command = f"""
        INSERT INTO info (id, picture, description)
        VALUES (%s, %s, %s);
    """
    cursor.execute(sql_command, (id, foto_locatie, beschrijving))
    verbinding.commit()
    cursor.close()
    verbinding.close()
    return beschrijving, id


def afbeelding_beschrijving_wijzigen(id: int, foto_locatie: str = None, beschrijving: str = None) -> None:
    """Wijzig de afbeelding, de beschrijving of beide."""
    if foto_locatie:
        sla_afbeelding_op(foto_locatie, id)
    if beschrijving:
        sla_beschrijving_op(beschrijving, id)

def haal_data_op() -> Tuple[str, int]:
    """Haal de foto en beschrijving op uit de photos tabel."""
    verbinding = maak_verbinding_met_database()
    cursor = verbinding.cursor()
    cursor.execute("SELECT id, picture, description FROM info;")
    resultaat = cursor.fetchall()
    cursor.close()
    verbinding.close()
    return resultaat