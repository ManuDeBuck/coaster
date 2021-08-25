import random


class Client:
    def __init__(self, client_id, nickname, telegram_id, barcode, balance):
        self.client_id = client_id
        self.nickname = nickname
        self.telegram_id = telegram_id
        self.barcode = barcode
        self.balance = balance

    def __str__(self):
        return "Client({}, {}, {}, {}, {})".format(self.client_id, self.nickname, self.telegram_id, self.barcode,
                                                   self.balance)

    @staticmethod
    def create(name, telegram_id):
        return Client(None, name, telegram_id, "C_{}{:02d}".format(name.lower()[:2], random.randint(0, 99)), 0.0)


class Clients:

    def __init__(self, database):
        self.database = database

    def persist(self, client):
        query = """REPLACE INTO clients (nickname, telegram_id, barcode, balance) VALUES (?, ?, ?, ?)"""
        data = (client.nickname, client.telegram_id, client.barcode, client.balance)
        generated_id = self.database.insert(query, data)
        client.id = generated_id

    def get_by_barcode(self, barcode):
        query = """
        SELECT  s.id,
                s.nickname,
                s.telegram_id,
                s.barcode,
                s.balance
            FROM clients AS s WHERE s.barcode = ?"""
        data = (barcode,)
        results = self.database.select(query, data)
        if len(results):
            return Client(*results[0])

    def get_by_telegram_id(self, telegram_id):
        query = """
                SELECT  s.id,
                        s.nickname,
                        s.telegram_id,
                        s.barcode,
                        s.balance
                    FROM clients AS s WHERE s.telegram_id = ?"""
        data = (telegram_id,)
        results = self.database.select(query, data)
        if len(results):
            return Client(*results[0])

    def get_by_nickname(self, name):
        query = """
                SELECT  s.id,
                        s.nickname,
                        s.telegram_id,
                        s.barcode,
                        s.balance
                    FROM clients AS s WHERE s.nickname = ?"""
        data = (name,)
        results = self.database.select(query, data)
        if len(results):
            return Client(*results[0])

    def list(self):
        query = """
                SELECT  s.id,
                        s.nickname,
                        s.telegram_id,
                        s.barcode,
                        s.balance
                    FROM clients AS s"""
        results = self.database.select(query)
        clients = []
        for result in results:
            clients.append(Client(*result))
        return clients

    def remove(self, nickname):
        query = """
                DELETE FROM clients WHERE nickname = ?
                """
        data = (nickname,)
        self.database.delete(query, data)
