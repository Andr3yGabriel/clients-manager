import sqlite3
from pathlib import Path

ROOT_DIR = Path(__file__).parent

connection = sqlite3.connect(ROOT_DIR / "clients.sqlite")
cursor = connection.cursor()
cursor.row_factory = sqlite3.Row


def create_table(connection, cursor):
    """
    Create a table in the database if it doesn't exist.
    """
    try:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS clients_pf (
                document VARCHAR(11) PRIMARY KEY UNIQUE,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(150) NOT NULL
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS clients_pj (
                document VARCHAR(14) PRIMARY KEY UNIQUE,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(150) NOT NULL
            )
            """
        )
        connection.commit()
    except Exception as e:
        print(f"Error creating tables: {e}")
        connection.rollback()


def register_client(connection, cursor, document, name, email):
    """
    Register a new client in the database.
    """
    # Validate the document length
    if len(document) not in [11, 14]:
        print("Document must be 11 characters for PF or 14 characters for PJ.")
        return
    # Determine client type based on document length
    if len(document) == 11:
        client_type = "pf"
    elif len(document) == 14:
        client_type = "pj"
    else:
        print("Invalid document length.")
        return
    try:
        if client_type == "pf":
            cursor.execute(
                "INSERT INTO clients_pf (document, name, email) VALUES (?, ?, ?)",
                (document, name, email),
            )
        elif client_type == "pj":
            cursor.execute(
                "INSERT INTO clients_pj (document, name, email) VALUES (?, ?, ?)",
                (document, name, email),
            )
        connection.commit()
        print("\nClient registered successfully.")
    except sqlite3.IntegrityError:
        print("Client already exists.")
    except Exception as e:
        print(f"Error registering client: {e}")
        connection.rollback()


def search_client(cursor, client_type, document):
    """
    Search for a client in the database.
    """
    try:
        if client_type == "pf":
            cursor.execute(
                "SELECT name FROM clients_pf WHERE document = ?",
                (document,),
            )
        elif client_type == "pj":
            cursor.execute(
                "SELECT name FROM clients_pj WHERE document = ?",
                (document,),
            )
        return dict(cursor.fetchone())
    except Exception as e:
        print(f"Error searching client: {e}")
        return None


def list_clients(cursor, client_type):
    """
    List all clients in the database.
    """
    try:
        if client_type == "pf":
            cursor.execute("SELECT * FROM clients_pf")
        elif client_type == "pj":
            cursor.execute("SELECT * FROM clients_pj")
        return [dict(row) for row in cursor.fetchall()]
    except Exception as e:
        print(f"Error listing clients: {e}")
        return None


def menu():
    """
    Display the menu and handle user input.
    """
    while True:
        print("\nMenu:")
        print("1. Register Client")
        print("2. Search Client")
        print("3. List Clients")
        print("4. Exit")
        choice = input("=> ")

        if choice == "1":
            document = input("Enter document (11 or 14 characters): ")
            name = input("Enter name: ")
            email = input("Enter email: ")
            register_client(connection, cursor, document, name, email)
        elif choice == "2":
            document = input("Enter document (11 or 14 characters): ")
            client_type = "pf" if len(document) == 11 else "pj"
            client = search_client(cursor, client_type, document)
            if client:
                print(
                    f"Client found:\nDocument: {client['document']}\nName: {client['name']}\nEmail: {client['email']}"
                )
            else:
                print("Client not found.")
        elif choice == "3":
            client_type = input("Enter client type (pf/pj): ")
            clients = list_clients(cursor, client_type)
            if clients:
                print(f"\nList of {client_type.upper()} clients:")
                for client in clients:
                    print(f"\nName: {client['name']}\nEmail: {client['email']}")
            else:
                print("No clients found.")
        elif choice == "4":
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    create_table(connection, cursor)
    menu()
    connection.close()
