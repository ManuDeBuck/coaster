class Item:

    def __init__(self, item_id, name, description, barcode, price, stock):
        self.item_id = item_id
        self.name = name
        self.description = description
        self.barcode = barcode
        self.price = price
        self.stock = stock

    def __str__(self):
        return "Item({}, {}, {}, {}, {}, {})".format(self.item_id, self.name, self.description,
                                                     self.barcode, self.price, self.stock)

    @staticmethod
    def create(name, description, barcode, price):
        return Item(None, name, description, barcode, price, 0)


class Items:

    def __init__(self, database):
        self.database = database

    def persist(self, item):
        query = """REPLACE INTO items (name, description, barcode, price, stock) VALUES (?, ?, ?, ?, ?)"""
        data = (item.name, item.description, item.barcode, item.price, item.stock)
        generated_id = self.database.insert(query, data)
        item.item_id = generated_id

    def get_by_barcode(self, barcode):
        query = """
        SELECT  s.id,
                s.name,
                s.description,
                s.barcode,
                s.price,
                s.stock 
            FROM items AS s WHERE s.barcode = ?"""
        data = (barcode,)
        results = self.database.select(query, data)
        if len(results):
            return Item(*results[0])

    def list(self):
        query = """
               SELECT * FROM items"""
        results = self.database.select(query)
        items = []
        for result in results:
            items.append(Item(*result))
        return items

    def get_by_item_name(self, name):
        query = """
                SELECT  s.id,
                        s.name,
                        s.description,
                        s.barcode,
                        s.price,
                        s.stock 
                    FROM items AS s WHERE s.name = ?"""
        data = (name,)
        results = self.database.select(query, data)
        if len(results):
            return Item(*results[0])
