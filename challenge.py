import sqlite3
from pathlib import Path

ROOT_DIR = Path(__file__).parent

connection = sqlite3.connect(ROOT_DIR / "clients.sqlite")
print(connection)
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
                email VARCHAR(150) NOT NULL,
                balance REAL DEFAULT 0.0
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS clients_pj (
                document VARCHAR(14) PRIMARY KEY UNIQUE,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(150) NOT NULL,
                balance REAL DEFAULT 0.0
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


def deposit(cursor, client_type, document, amount):
    """
    Deposit money into a client's account.
    """
    try:
        if client_type == "pf":
            cursor.execute(
                "UPDATE clients_pf SET balance = balance + ? WHERE document = ?",
                (amount, document),
            )
        elif client_type == "pj":
            cursor.execute(
                "UPDATE clients_pj SET balance = balance + ? WHERE document = ?",
                (amount, document),
            )
        connection.commit()
        return True
    except Exception as e:
        print(f"\nError depositing money: {e}")
        return False


def withdraw(cursor, client_type, document, amount):
    """
    Withdraw money from a client's account.
    """
    try:
        if client_type == "pf":
            if amount <= 0:
                print("Withdrawal amount must be positive.")
                return False
            cursor.execute(
                "SELECT balance FROM clients_pf WHERE document = ?",
                (document,),
            )
            current_balance = cursor.fetchone()
            if current_balance and current_balance[0] >= amount:
                cursor.execute(
                    "UPDATE clients_pf SET balance = balance - ? WHERE document = ?",
                    (amount, document),
                )
            else:
                print("Insufficient funds.")
                return False
        elif client_type == "pj":
            if amount <= 0:
                print("Withdrawal amount must be positive.")
                return False
            cursor.execute(
                "SELECT balance FROM clients_pj WHERE document = ?",
                (document,),
            )
            current_balance = cursor.fetchone()
            if current_balance and current_balance[0] >= amount:
                cursor.execute(
                    "UPDATE clients_pj SET balance = balance - ? WHERE document = ?",
                    (amount, document),
                )
            else:
                print("Insufficient funds.")
                return False
        connection.commit()
        return True
    except Exception as e:
        print(f"Error withdrawing money: {e}")
        return False


def transfer(
    cursor, client_type_from, document_from, client_type_to, document_to, amount
):
    """
    Transfer money between clients.
    """
    if withdraw(cursor, client_type_from, document_from, amount):
        deposit(cursor, client_type_to, document_to, amount)
        print("\nTransfer successful.")
    else:
        print("\nTransfer failed.")


def menu():
    """
    Display the menu and handle user input.
    """
    while True:
        print("\nMenu:")
        print("1. Register Client")
        print("2. Search Client")
        print("3. List Clients")
        print("4. Deposit")
        print("5. Withdraw")
        print("6. Transfer")
        print("7. Exit")
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
            document = input("Enter document (11 or 14 characters): ")
            client_type = "pf" if len(document) == 11 else "pj"
            amount = float(input("Enter amount to deposit: "))
            if deposit(cursor, client_type, document, amount):
                print("\nDeposit successful.")
            else:
                print("\nDeposit failed.")
        elif choice == "5":
            document = input("Enter document (11 or 14 characters): ")
            client_type = "pf" if len(document) == 11 else "pj"
            amount = float(input("Enter amount to withdraw: "))
            if withdraw(cursor, client_type, document, amount):
                print("\nWithdrawal successful.")
            else:
                print("\nWithdrawal failed.")
        elif choice == "6":
            document_from = input("Enter document (11 or 14 characters) of sender: ")
            client_type_from = "pf" if len(document_from) == 11 else "pj"
            document_to = input("Enter document (11 or 14 characters) of receiver: ")
            client_type_to = "pf" if len(document_to) == 11 else "pj"
            amount = float(input("Enter amount to transfer: "))
            transfer(
                cursor,
                client_type_from,
                document_from,
                client_type_to,
                document_to,
                amount,
            )
        elif choice == "7":
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    create_table(connection, cursor)
    menu()
    connection.close()
