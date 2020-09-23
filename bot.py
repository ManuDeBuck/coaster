import os
from core.database import Database
from core.seed import create_tables
from telegram.ext import Updater, MessageHandler, CommandHandler, CallbackQueryHandler, Filters
from barcode import Code128
from barcode.writer import ImageWriter
from dotenv import load_dotenv
from core.clients import Clients, Client
from core.items import Items, Item
from core.purchases import Purchases
from datetime import datetime


class CoasterBotHandler:
    def __init__(self, database, admin_telegram_id):
        self.database = database
        self.admin_telegram_id = admin_telegram_id
        self.clients = Clients(self.database)
        self.items = Items(self.database)
        self.purchases = Purchases(self.database)

    def is_admin(self, update, context):
        if int(update.message.from_user.id) != int(self.admin_telegram_id):
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="Only admin is allowed to perform this action.")
            return False
        return True

    def add_product(self, update, context):
        if not self.is_admin(update, context):
            return
        command_split = update.message.text.split(" ")
        if len(command_split) < 5:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="format: /add_product product description EAN_code price")
            return
        product_name = command_split[1].strip()
        product_description = command_split[2].strip()
        product_ean = command_split[3].strip()
        product_price = command_split[4].strip()
        product = Item.create(product_name, product_description, product_ean, product_price)
        self.items.persist(product)
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="The product {} is added.".format(product_name))

    def remove_product(self, update, context):
        if not self.is_admin(update, context):
            return
        command_split = update.message.text.split(" ")
        if len(command_split) < 2:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="format: /remove_product productname")
            return
        product_name = command_split[1].strip()
        product = self.items.get_by_item_name(product_name)
        self.items.remove(product)
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=f"The product {product_name} is removed.")

    def change_price(self, update, context):
        if not self.is_admin(update, context):
            return
        command_split = update.message.text.split(" ")
        if len(command_split) < 3:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="format: /change_price productname new_price")
            return
        product_name = command_split[1].strip()
        product_new_price = command_split[1].strip()
        product = self.items.get_by_item_name(product_name)
        product.price = product_new_price
        self.items.persist(product)
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=f"The product {product_name}'s new price is {product_new_price}.")

    def get_balance(self, update, context):
        telegram_id = update.message.from_user.id
        client = self.clients.get_by_telegram_id(telegram_id)
        if client:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="Hello, {}, your balance is: {}".format(client.nickname,
                                                                                  round(client.balance, 2)))
        else:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="No client with telegram id {} can be found".format(telegram_id))

    def reset_balance(self, update, context):
        if not self.is_admin(update, context):
            return
        command_split = update.message.text.split(" ")
        if len(command_split) < 2:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="Format: /reset_balance nickname")
            return
        client_name = command_split[1]
        client = self.clients.get_by_nickname(client_name)
        if client is not None:
            client.balance = 0
            self.clients.persist(client)
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text=f"Balance of {client_name} is reset.")
        else:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text=f"No client with name {client_name}.")

    def create_client(self, update, context):
        if not self.is_admin(update, context):
            return
        command_split = update.message.text.split(" ")
        if len(command_split) < 3:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="Format: /create_client nickname telegram_id")
            return
        client_name = command_split[1]
        client_telegram_id = command_split[2]
        new_client = Client.create(client_name, client_telegram_id)
        self.clients.persist(new_client)
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Hello, {}! Have a drink, have a snack, it's all on you tonight!".format(
                                     new_client.nickname))

    @staticmethod
    def get_telegram_id(update, context):
        telegram_id = update.message.from_user.id
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Your telegram ID is: {}".format(telegram_id))

    def get_barcode(self, update, context):
        telegram_id = update.message.from_user.id
        client = self.clients.get_by_telegram_id(telegram_id)
        if client is not None:
            filename = "barcodes/{}.png".format(client.barcode)
            if not os.path.isfile(filename):
                code = Code128(client.barcode, writer=ImageWriter())
                code.save("barcodes/{}".format(client.barcode))
            context.bot.send_photo(chat_id=update.effective_chat.id,
                                   photo=open("barcodes/{}.png".format(client.barcode), "rb"))
        else:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="You currently are not a client.")

    def list_stock(self, update, context):
        if not self.is_admin(update, context):
            return
        items_list = self.items.list()
        if not len(items_list):
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="No products yet.")
            return
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="\n".join(["{}: {}".format(item.name, item.stock) for item in items_list]))

    def list_balances(self, update, context):
        if not self.is_admin(update, context):
            return
        client_list = self.clients.list()
        if not len(client_list):
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="No clients yet.")
            return
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="\n".join([f"Client {client.nickname}: {round(client.balance, 2)}" for client in
                                                 client_list]))

    def list_purchases(self, update, context):
        telegram_id = update.message.from_user.id
        client = self.clients.get_by_telegram_id(telegram_id)
        if client is not None:
            all_items = self.items.list()
            purchases_by_client = self.purchases.get_by_user_id(client.client_id)
            if not len(purchases_by_client):
                context.bot.send_message(chat_id=update.effective_chat.id,
                                         text="You currently don't have any purchases.")
                return
            item_names = [list(filter(lambda x: x.item_id == purchase.item_id, all_items)) for purchase in
                          purchases_by_client]
            item_names = ["product unknown" if not len(items) else items[0] for items in item_names]
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="\n".join([
                                         f"{purchase.timestamp[:purchase.timestamp.find('T')]}:"
                                         f" {item_name}, {purchase.paid_price}"
                                         for
                                         (item_name, purchase) in zip(item_names, purchases_by_client)]))
        else:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="You currently are not a client.")

    def get_item_barcode(self, update, context):
        command_split = update.message.text.split(" ")
        if len(command_split) < 2:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="Format: /get_item_barcode item")
            return
        item_name = command_split[1]
        item = self.items.get_by_item_name(item_name)
        if item is not None:
            filename = "barcodes/{}.png".format(item.barcode)
            if not os.path.isfile(filename):
                code = Code128(item.barcode, writer=ImageWriter())
                code.save("barcodes/{}".format(item.barcode))
            context.bot.send_photo(chat_id=update.effective_chat.id,
                                   photo=open("barcodes/{}.png".format(item.barcode), "rb"))
        else:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text=f"The item with name {item_name} currently does not exist.")

    def list_item_prices(self, update, context):
        if not self.is_admin(update, context):
            return
        items_list = self.items.list()
        if not len(items_list):
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="No products yet.")
            return
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="\n".join(["{}: {}".format(item.name, item.price) for item in items_list]))

    def add_stock(self, update, context):
        if not self.is_admin(update, context):
            return
        command_split = update.message.text.split(" ")
        if len(command_split) < 3:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="Format: /add_stock product_name quantity")
            return
        item_name = command_split[1]
        item_add_stock = int(command_split[2])
        item = self.items.get_by_item_name(item_name)
        if not item:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="No product with name {} was found.".format(item_name))
        item.stock += item_add_stock
        self.items.persist(item)
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Item {} has current stock: {}".format(item.name, item.stock))

    def remove_stock(self, update, context):
        if not self.is_admin(update, context):
            return
        command_split = update.message.text.split(" ")
        if len(command_split) < 3:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="Format: /remove_stock product_name quantity")
            return
        item_name = command_split[1]
        item_remove_stock = int(command_split[2])
        item = self.items.get_by_item_name(item_name)
        if not item:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="No product with name {} was found.".format(item_name))
        item.stock -= item_remove_stock
        self.items.persist(item)
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Item {} has current stock: {}".format(item.name, item.stock))

    @staticmethod
    def help(update, context):
        public_commands = ["/get_balance", "/telegram_id", "/get_barcode", "/get_item_barcode", "/list_purchases",
                           "/help", "/list_prices"]
        admin_commands = ["/add_product", "/create_client", "/list_stock", "/add_stock", "/reset_balance",
                          "/remove_product", "/list_balances", "/remove_stock"]
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Current public commands are: {}\nCurrent admin-only commands are: {}".format(
                                     ", ".join(public_commands), ", ".join(admin_commands)))

    @staticmethod
    def unknown(update, context):
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Sorry I don't know this command. "
                                      "Enter /help for more information on how to use this bot.")

    def run(self):
        # Updater and dispatcher for Telegram bot
        updater = Updater(os.getenv("telegram_token"), use_context=True)
        dispatcher = updater.dispatcher

        # Add handlers for commands
        add_client_handler = CommandHandler('create_client', self.create_client)
        dispatcher.add_handler(add_client_handler)

        get_barcode_handler = CommandHandler('get_barcode', self.get_barcode)
        dispatcher.add_handler(get_barcode_handler)

        add_product_handler = CommandHandler('add_product', self.add_product)
        dispatcher.add_handler(add_product_handler)

        balance_handler = CommandHandler('balance', self.get_balance)
        dispatcher.add_handler(balance_handler)

        telegram_id_handler = CommandHandler('telegram_id', self.get_telegram_id)
        dispatcher.add_handler(telegram_id_handler)

        list_stock_handler = CommandHandler('list_stock', self.list_stock)
        dispatcher.add_handler(list_stock_handler)

        add_stock_handler = CommandHandler('add_stock', self.add_stock)
        dispatcher.add_handler(add_stock_handler)

        reset_balance_handler = CommandHandler('reset_balance', self.reset_balance)
        dispatcher.add_handler(reset_balance_handler)

        remove_product_handler = CommandHandler('remove_product', self.remove_product)
        dispatcher.add_handler(remove_product_handler)

        change_price_handler = CommandHandler('change_price', self.change_price)
        dispatcher.add_handler(change_price_handler)

        list_balances_handler = CommandHandler('list_balances', self.list_balances)
        dispatcher.add_handler(list_balances_handler)

        list_purchases_handler = CommandHandler('list_purchases', self.list_purchases)
        dispatcher.add_handler(list_purchases_handler)

        item_barcode_handler = CommandHandler('get_item_barcode', self.get_item_barcode)
        dispatcher.add_handler(item_barcode_handler)

        remove_stock_handler = CommandHandler('remove_stock', self.remove_product)
        dispatcher.add_handler(remove_stock_handler)

        list_prices_handler = CommandHandler('list_prices', self.list_item_prices)
        dispatcher.add_handler(list_prices_handler)

        help_handler = CommandHandler('help', self.help)
        dispatcher.add_handler(help_handler)

        # Unknown command catchall handler
        unknown_handler = MessageHandler(Filters.command, self.unknown)
        dispatcher.add_handler(unknown_handler)

        # To poll for incoming commands
        updater.start_polling()


if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    # Create database, retrieve admin id
    db = Database(os.getenv("db_file"))
    admin_id = os.getenv("admin_telegram_id")
    # Make sure all tables are instantiated
    create_tables(db)
    # Create bot handler
    handler = CoasterBotHandler(db, admin_id)
    # Run the bot
    handler.run()
