def create_tables(database):
    database.create_table("""
        CREATE TABLE IF NOT EXISTS items (
            id integer PRIMARY KEY AUTOINCREMENT,
            name text NOT NULL UNIQUE,
            description text NOT NULL,
            barcode text NOT NULL UNIQUE,
            price REAL NOT NULL,
            stock INTEGER NOT NULL
        );
    """)

    database.create_table("""
        CREATE TABLE IF NOT EXISTS clients (
            id integer PRIMARY KEY AUTOINCREMENT,
            nickname text NOT NULL UNIQUE,
            telegram_id text NOT NULL UNIQUE,
            barcode text NOT NULL UNIQUE,
            balance REAL NOT NULL
        );
    """)

    database.create_table("""
        CREATE TABLE IF NOT EXISTS purchases (
            id integer PRIMARY KEY AUTOINCREMENT,
            item_id integer NOT NULL,
            client_id integer NOT NULL,
            paid_price float NOT NULL,
            date text NOT NULL,
            FOREIGN KEY (item_id) REFERENCES items (id),
            FOREIGN KEY (client_id) REFERENCES clients (id)
        );
    """)
