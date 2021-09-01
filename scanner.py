import enum
import os
from math import ceil
from dotenv import load_dotenv
from core.database import Database
from core.items import Items, Item
from core.clients import Clients, Client
from core.seed import create_tables
from core.purchases import Purchases, Purchase


class BarcodeType(enum.Enum):
    Client = 0
    Item = 1


def barcode_enum(barcode):
    if barcode.startswith("C_"):
        return BarcodeType.Client
    else:
        return BarcodeType.Item


def main():
    db_file = os.getenv("db_file")
    database = Database(db_file)
    items = Items(database)
    clients = Clients(database)
    purchases = Purchases(database)

    create_tables(database)

    while True:
        client_barcodes = []
        barcode = input().strip().upper()
        while barcode_enum(barcode) is BarcodeType.Client:
            client_barcodes.append(barcode)
            barcode = input().strip().upper()

        client_list = []
        for client_barcode in client_barcodes:
            client = clients.get_by_barcode(client_barcode)
            client_list.append(client) if client else None

        if not len(client_list):
            continue

        print("Clients: {}".format(", ".join([str(client) for client in client_list])))
        product = items.get_by_barcode(barcode)
        print("Scanned product: {}".format(str(product)))

        if product:
            price_per_person = product.price
            if len(client_list) > 1:
                price_per_person = ceil(product.price * 20 / len(client_list)) / 20  # ceil with 2 decimals
            print("Price paid per person: {}".format(str(price_per_person)))

            for client in client_list:
                purchase = Purchase.create(product, client, price_per_person)
                purchases.persist(purchase)

                client.balance += price_per_person
                clients.persist(client)

                print(purchase)

            product.stock -= 1
            items.persist(product)

            print("Purchase registered")
        else:
            print("No item scanned")


if __name__ == "__main__":
    load_dotenv()
    main()
