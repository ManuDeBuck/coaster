from core.database import Database
from core.seed import create_tables
from telegram.ext import Updater, MessageHandler, CommandHandler, CallbackQueryHandler, Filters
import os
from barcode import Code128
from barcode.writer import ImageWriter
from dotenv import load_dotenv
from core.clients import Clients, Client

load_dotenv()


class CoasterBotHandler:
    def __init__(self, database):
        self.database = database
        self.clients = Clients(self.database)

    # example method handler
    @staticmethod
    def ping(update, context):
        context.bot.send_message(update.effective_chat.id,
                                 text="pong")

    def create_client(self, update, context):
        command_split = update.message.text.split(" ")
        if len(command_split) < 2:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="A name for the new client should be provided")
        new_client = Client.create(command_split[1], update.message.from_user.id)
        self.clients.persist(new_client)
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Hello, {}! Have a drink, have a snack, it's all on you tonight!".format(
                                     new_client.nickname))

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
        ping_handler = CommandHandler('ping', self.ping)
        dispatcher.add_handler(ping_handler)

        add_client_handler = CommandHandler('create_client', self.create_client)
        dispatcher.add_handler(add_client_handler)

        get_barcode_handler = CommandHandler('get_barcode', self.get_barcode)
        dispatcher.add_handler(get_barcode_handler)

        # Unknown command catchall handler
        unknown_handler = MessageHandler(Filters.command, self.unknown)
        dispatcher.add_handler(unknown_handler)

        # To poll for incoming commands
        updater.start_polling()


if __name__ == "__main__":
    # Create database
    database = Database(os.getenv("db_file"))
    # Make sure all tables are instantiated
    create_tables(database)
    # Create bot handler
    handler = CoasterBotHandler(database)
    # Run the bot
    handler.run()
