# Customer Registration System

This project is a simple customer registration system (Individual and Company) using Python and SQLite.

## Features

- Register individual (PF) and company (PJ) customers
- Search customers by document number
- List all registered customers
- Interactive menu interface in the terminal

## Database Structure

The `clients.sqlite` database has two tables:

- `clients_pf`: Stores individual customers (document with 11 characters)
- `clients_pj`: Stores company customers (document with 14 characters)

## How to Run

1. Make sure you have Python 3 installed.
2. Clone this repository and navigate to the project folder.
3. Run the main file:

```sh
python challenge.py
```

4. Follow the menu instructions to register, search, or list customers.

## File Structure

- `challenge.py`: Main system code.
- `clients.sqlite`: SQLite database generated automatically.
- `.gitignore`: Files and folders ignored by Git.

## Notes

- The document must have 11 characters for individuals or 14 for companies.
- The system prevents duplicate document registration.
- The database is created automatically on the first run.