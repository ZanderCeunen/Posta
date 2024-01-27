import os
import getpass

def bericht(melding):
    """Print message."""
    print(f'\033[1;32m{melding}\033[0m')

def voer_commando_uit(commando, foutmelding):
    """Voer een commando uit en geef een foutmelding als het mislukt."""
    if os.system(commando) != 0:
        bericht(foutmelding, ValueError)

def installeer_mysql():
    """Installeer MySQL-server als deze nog niet is geïnstalleerd."""
    if 'mysql-server' not in (i.strip() for i in os.popen('dpkg --list').read().splitlines()):
        voer_commando_uit('sudo apt-get update', "Fout tijdens het bijwerken van de pakketlijst.")
        voer_commando_uit('sudo apt-get install mysql-server', "Fout tijdens het installeren van MySQL-server.")

def maak_gebruiker(gebruiker_db, wachtwoord_db):
    """Maak een nieuwe gebruiker aan en verleen rechten."""
    voer_commando_uit(f'mysql -u root -p -e "CREATE USER \'{gebruiker_db}\'@\'localhost\' IDENTIFIED BY \'{wachtwoord_db}\';"', "Fout tijdens het aanmaken van de gebruiker.")
    voer_commando_uit(f'mysql -u root -p -e "GRANT ALL PRIVILEGES ON dbdata.* TO \'{gebruiker_db}\'@\'localhost\';"', "Fout tijdens het verlenen van rechten aan de gebruiker.")

def maak_database_en_tabellen():
    """Maak een nieuwe database en tabellen aan."""
    voer_commando_uit('mysql -u root -p -e "CREATE DATABASE dbdata;"', "Fout tijdens het aanmaken van de databases.")
    voer_commando_uit('mysql -u root -p -e "USE dbdata; CREATE TABLE Omschrijving (id INT AUTO_INCREMENT PRIMARY KEY, beschrijving TEXT); CREATE TABLE Foto (id INT AUTO_INCREMENT PRIMARY KEY, foto BLOB);"', "Fout tijdens het aanmaken van de tabellen.")

def main():
    """Hoofdfunctie."""
    try:
        installeer_mysql()
        gebruiker_db = "python_applicatie"
        wachtwoord_db = getpass.getpass("Voer het wachtwoord voor de database in: ")
        maak_gebruiker(gebruiker_db, wachtwoord_db)
        maak_database_en_tabellen()
    except Exception as excepp:
        bericht(f"\nEr is een fout opgetreden tijdens uitvoering:\n{excepp}")
        input("\nDruk Enter om af te sluiten...")

    # Testcode om te controleren of alles goed gegaan is
    if os.path.exists('/etc/mysql/mysql.conf.d/mysqld.cnf'):
        bericht('\nTest succesvol!\n')
    else:
        bericht('\nTest mislukt!\n', ValueError)

if __name__ == "__main__":
    main()