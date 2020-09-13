def create_tables(database):
    database.create_table("""
            CREATE TABLE IF NOT EXISTS item_groups (
                id integer PRIMARY KEY AUTOINCREMENT,
                name text NOT NULL
            );
        """)

    database.create_table("""
        CREATE TABLE IF NOT EXISTS items (
            id integer PRIMARY KEY AUTOINCREMENT,
            name text NOT NULL,
            description text NOT NULL,
            group_id integer NOT NULL,
            barcode text NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL,
            FOREIGN KEY (group_id) REFERENCES item_groups (id)
        );
    """)

    database.create_table("""
        CREATE TABLE IF NOT EXISTS clients (
            id integer PRIMARY KEY AUTOINCREMENT,
            nickname text NOT NULL,
            barcode text NOT NULL,
            balance REAL NOT NULL,
            UNIQUE (barcode)
        );
    """)

    database.create_table("""
        CREATE TABLE IF NOT EXISTS purchases (
            id integer PRIMARY KEY AUTOINCREMENT,
            item_id integer NOT NULL,
            client_id integer NOT NULL,
            date text NOT NULL,
            FOREIGN KEY (item_id) REFERENCES items (id),
            FOREIGN KEY (client_id) REFERENCES clients (id)
        );
    """)
