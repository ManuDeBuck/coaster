import enum
from core.database import Database
from core.items import Items
from core.clients import Clients, Client
from core.seed import create_tables


class BarcodeType(enum.Enum):
    Client = 0
    Item = 1


def barcode_enum(barcode):
    if barcode.startswith("C_"):
        return BarcodeType.Client
    else:
        return BarcodeType.Item


def main():
    db_file = "coaster.db"  # TODO: .env
    database = Database(db_file)
    items = Items(database)
    clients = Clients(database)

    create_tables(database)

    cli = Client.create("manu")
    clients.persist(cli)

    while True:
        client_barcodes = []
        barcode = input().strip()
        while barcode_enum(barcode) is BarcodeType.Client:
            client_barcodes.append(barcode)
            barcode = input().strip()

        client_list = []
        for client_barcode in client_barcodes:
            client = clients.get_by_barcode(client_barcode)
            client_list.append(client) if client else None

        if not len(client_list):
            continue

        print("Clients: {}".format(str([str(client) for client in client_list])))
        product = items.get_by_barcode(barcode)
        print("Scanned product: {}".format(str(product)))


if __name__ == "__main__":
    main()
