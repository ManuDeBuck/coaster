from datetime import datetime


class Purchase:

    def __init__(self, purchase_id, item, client, paid_price, timestamp):
        self.purchase_id = purchase_id
        self.item_id = item
        self.client_id = client
        self.paid_price = paid_price
        self.timestamp = timestamp

    def __str__(self):
        return "Purchase({}, {}, {}, {}, {})".format(self.purchase_id, self.item_id, self.client_id,
                                                     self.paid_price, self.timestamp)

    @staticmethod
    def create(item, client, paid_price):
        return Purchase(None, item.item_id, client.client_id, paid_price, datetime.now().isoformat())  # TODO: Generate current date


class Purchases:

    def __init__(self, database):
        self.database = database

    def persist(self, purchase):
        query = """INSERT INTO purchases (item_id, client_id, paid_price, date) VALUES (?, ?, ?, ?)"""
        data = (purchase.item.item_id, purchase.client.client_id, purchase.paid_price, purchase.timestamp)
        generated_id = self.database.insert(query, data)
        purchase.purchase_id = generated_id

    def get_by_user_id(self, client_id):
        query = """SELECT   s.id,
                            s.item_id,
                            s.client_id,
                            s.paid_price,
                            s.date FROM purchases AS s WHERE s.client_id = ? ORDER BY date"""
        data = (client_id, )
        results = self.database.select(query, data)
        purchases = []
        for result in results:
            purchases.append(Purchase(*result))
        return purchases
