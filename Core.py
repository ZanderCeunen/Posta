import mysql.connector
import getpass

def verbinding_met_databasesamestellen():
    """Maak verbinding met de database."""
    connectie = mysql.connector.connect(
        host="localHost",
        gebruiker="python_applicatie",
        wachtwoord=getpass.getpass("Voer het wachtwoord voor de database in: "),
        database="dbdata"
    )
    return connectie

def nieuw_record_in_omschrijving_toevoegen(beschrijving):
    """Voeg een record toe aan de tabel Omschrijving."""
    connectie = verbinding_met_databasesamestellen()
    cursor = connectie.cursor()
    query = "INSERT INTO Omschrijving (beschrijving) VALUES (%s)"
    cursor.execute(query, (beschrijving,))
    connectie.commit()
    cursor.sluiten()
    connectie.sluiten()

def nieuw_record_in_foto_toevoegen(foto):
    """Voeg een record toe aan de tabel Foto."""
    connectie = verbinding_met_databasesamestellen()
    cursor = connectie.cursor()
    query = "INSERT INTO Foto (foto) VALUES (%s)"
    cursor.execute(query, (foto,))
    connectie.commit()
    cursor.sluiten()
    connectie.sluiten()

def velddescription_in_omschrijving_wijzigen(nieuwe_beschrijving, id):
    """Wijzig het veld 'beschrijving' in de tabel 'Omschrijving'."""
    connectie = verbinding_met_databasesamestellen()
    cursor = connectie.cursor()
    query = "UPDATE Omschrijving SET beschrijving=%s WHERE id=%s"
    cursor.execute(query, (nieuwe_beschrijving, id))
    connectie.commit()
    cursor.sluiten()
    connectie.sluiten()

# Voorbeelden van hoe je de functies kunt aanroepen
#nieuw_record_in_omschrijving_toevoegen("Dit is een omschrijving")
#nieuw_record_in_foto_toevoegen(open("/pad/naar/afbeelding.jpg", "rb").lees())
#velddescription_in_omschrijving_wijzigen("Nieuwe omschrijving", 1)