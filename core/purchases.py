class Purchase:

    def __init__(self, id, item, client, date):
        self.id = id
        self.item = item
        self.client = client
        self.date = date

    @staticmethod
    def create(item, client):
        return Purchase(None, item, client, None)  # TODO: Generate current date


class Purchases:

    def __init__(self, database):
        self.database = database

    def persist(self, purchase):
        query = """INSERT INTO purchases (item_id, client_id, date) VALUES (?, ?, ?)"""
        data = (purchase.item.item_id, purchase.client.client_id, purchase.date)
        generated_id = self.database.insert(query, data)
        purchase.id = generated_id
