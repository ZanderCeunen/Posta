"""Dit script is een verzameling van functies die zijn ontworpen om te werken met een MySQL-database genaamd photodb. Hier is een gedetailleerde beschrijving van elke functie:

maak_verbinding_met_database() -> mysql.connector.connection.MySQLConnection: Deze functie maakt verbinding met de lokale MySQL-database met behulp van de gegeven gebruikersnaam, wachtwoord, host en databasenaam. Het retourneert een MySQLConnection object dat kan worden gebruikt om interactie te hebben met de database.
haal_laatste_id_op() -> int: Deze functie haalt het hoogste ID op uit de photos tabel in de database. Het retourneert dit ID als een integer.
foto_naar_base64_encoderen(foto: bytes) -> str: Deze functie neemt een binaire afbeelding als invoer en retourneert een Base64-gecodeerde string van die afbeelding.
base64_naar_foto_decoderen(afbeelding_gecodeerd: str) -> bytes: Deze functie decodeert een Base64-gecodeerde string terug naar een binaire afbeelding.
sla_afbeelding_op(foto: bytes, id: int) -> None: Deze functie slaat een binaire afbeelding op in de photos tabel van de database onder het gegeven ID.
sla_beschrijving_op(beschrijving: str, id: int) -> None: Deze functie slaat een beschrijving op in de photos tabel van de database onder het gegeven ID.
afbeelding_met_beschrijving_uploaden(foto: bytes, beschrijving: str) -> Tuple[str, int]: Deze functie uploadt een binaire afbeelding en een beschrijving naar de photos tabel van de database. Het retourneert een tuple met de beschrijving en het ID van de nieuwe rij.
afbeelding_beschrijving_wijzigen(id: int, foto: bytes = None, beschrijving: str = None) -> None: Deze functie wijzigt de afbeelding, de beschrijving of beide in de photos tabel van de database onder het gegeven ID. Als foto of beschrijving None is, wordt dat veld niet gewijzigd."""

import os
import mysql.connector
import base64
from typing import Tuple


def maak_verbinding_met_database() -> mysql.connector.connection.MySQLConnection:
    """Maak verbinding met de lokale database."""
    verbinding = mysql.connector.connect(
        host="localHost",
        gebruiker="python_applicatie",
        wachtwoord=os.environ.get("paswoord_db"),
        database="dbposta")
    return verbinding


def haal_laatste_id_op() -> int:
    """Haal het laatste ID op uit de photos tabel."""
    verbinding = maak_verbinding_met_database()
    cursor = verbinding.cursor()
    cursor.execute("SELECT MAX(id) FROM photos;")
    resultaat = cursor.fetchone()[0] or 0
    cursor.close()
    verbinding.close()
    return resultaat


def foto_naar_base64_encoderen(foto: bytes) -> str:
    """Encodeer een binaire afbeelding naar een Base64-string."""
    afbeelding_gecodeerd = base64.b64encode(foto).decode("ascii")
    return afbeelding_gecodeerd


def base64_naar_foto_decoderen(afbeelding_gecodeerd: str) -> bytes:
    """Decodeer een Base64-string terug naar een binaire afbeelding."""
    afbeelding_gedecodeerd = base64.b64decode(afbeelding_gecodeerd.encode("ascii"))
    return afbeelding_gedecodeerd


def sla_afbeelding_op(foto: bytes, id: int) -> None:
    """Sla de afbeelding op in de database met behulp van het ID."""
    verbinding = maak_verbinding_met_database()
    cursor = verbinding.cursor()
    sql_command = f"""
        UPDATE photos
        SET picture = %s
        WHERE id = %s;
    """
    cursor.execute(sql_command, (foto, id))
    verbinding.commit()
    cursor.close()
    verbinding.close()


def sla_beschrijving_op(beschrijving: str, id: int) -> None:
    """Sla de beschrijving op in de database met behulp van het ID."""
    verbinding = maak_verbinding_met_database()
    cursor = verbinding.cursor()
    sql_command = f"""
        UPDATE photos
        SET description = %s
        WHERE id = %s;
    """
    cursor.execute(sql_command, (beschrijving, id))
    verbinding.commit()
    cursor.close()
    verbinding.close()


def afbeelding_met_beschrijving_uploaden(foto: bytes, beschrijving: str) -> Tuple[str, int]:
    """Upload een afbeelding samen met de beschrijving."""
    id = haal_laatste_id_op() + 1
    gecodeerde_afbeelding = foto_naar_base64_encoderen(foto)
    verbinding = maak_verbinding_met_database()
    cursor = verbinding.cursor()
    sql_command = f"""
        INSERT INTO photos (id, picture, description)
        VALUES (%s, %s, %s);
    """
    cursor.execute(sql_command, (id, gecodeerde_afbeelding, beschrijving))
    verbinding.commit()
    cursor.close()
    verbinding.close()
    return (beschrijving, id)


def afbeelding_beschrijving_wijzigen(id: int, foto: bytes = None, beschrijving: str = None) -> None:
    """Wijzig de afbeelding, de beschrijving of beide."""
    if foto:
        sla_afbeelding_op(foto, id)
    if beschrijving:
        sla_beschrijving_op(beschrijving, id)
