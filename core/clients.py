import random

class Client:
    def __init__(self, client_id, nickname, barcode, balance):
        self.client_id = client_id
        self.nickname = nickname
        self.barcode = barcode
        self.balance = balance

    def __str__(self):
        return "Client({}, {}, {}, {})".format(self.client_id, self.nickname, self.barcode, self.balance)

    @staticmethod
    def create(name):
        return Client(None, name, "C_{}{:02d}".format(name.lower()[:2], random.randint(0, 99)), 0.0)


class Clients:

    def __init__(self, database):
        self.database = database

    def persist(self, client):
        query = """INSERT INTO clients (nickname, barcode, balance) VALUES (?, ?, ?)"""
        data = (client.nickname, client.barcode, client.balance)
        generated_id = self.database.insert(query, data)
        client.id = generated_id

    def get_by_barcode(self, barcode):
        query = """
        SELECT  s.id,
                s.nickname,
                s.barcode,
                s.balance
            FROM clients AS s WHERE s.barcode = ?"""
        data = (barcode, )
        results = self.database.select(query, data)
        if len(results):
            return Client(*results[0])
