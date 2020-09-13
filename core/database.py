import sqlite3 as sq


class Database:

    def __init__(self, db_file):
        self.db_file = db_file
        self.connection = self.create_connection()
        if not self.connection:
            raise Exception("No connection could be created with the database file.")

    def create_connection(self):
        try:
            return sq.connect(self.db_file, check_same_thread=False)
        except Exception as e:
            print(e)
        return None

    def create_table(self, query):
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
        except Exception as e:
            print(e)

    def insert(self, query, data=None):
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, data)
            self.connection.commit()
            return cursor.lastrowid
        except Exception as e:
            print(e)

    def select(self, query, data=None):
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, data)
            self.connection.commit()
            return cursor.fetchall()
        except Exception as e:
            print(e)
