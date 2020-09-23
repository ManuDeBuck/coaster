from datetime import datetime


class Purchase:

    def __init__(self, purchase_id, item_name, client_name, paid_price, timestamp):
        self.purchase_id = purchase_id
        self.item_name = item_name
        self.client_name = client_name
        self.paid_price = paid_price
        self.timestamp = timestamp

    def __str__(self):
        return "Purchase({}, {}, {}, {}, {})".format(self.purchase_id, self.item_name, self.client_name,
                                                     self.paid_price, self.timestamp)

    @staticmethod
    def create(item, client, paid_price):
        return Purchase(None, item.name, client.nickname, paid_price, datetime.now().isoformat())


class Purchases:

    def __init__(self, database):
        self.database = database

    def persist(self, purchase):
        query = """INSERT INTO purchases (item_name, client_name, paid_price, date) VALUES (?, ?, ?, ?)"""
        data = (purchase.item_name, purchase.client_name, purchase.paid_price, purchase.timestamp)
        generated_id = self.database.insert(query, data)
        purchase.purchase_id = generated_id

    def get_by_user_name(self, client_id):
        query = """SELECT   s.id,
                            s.item_name,
                            s.client_name,
                            s.paid_price,
                            s.date FROM purchases AS s WHERE s.client_id = ? ORDER BY date"""
        data = (client_id,)
        results = self.database.select(query, data)
        purchases = []
        for result in results:
            purchases.append(Purchase(*result))
        return purchases
