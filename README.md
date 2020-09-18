# Coaster

A super lightweight, hyper modern approach to the classic coaster-to-keep-track-of-consumptions tool.

## Scanner

The `scanner.py` application can be used in combination with a barcode-scanner (you can buy it online), that will be plugged into your machine. This application keeps track of consumed drinks.

## Telegram Bot

The `bot.py` is used to control the application (add products, check your balance, get your personal barcode...).

## Usage

Run both the scanner and the bot. 
When someone wants a drink or a snack, the person scans it's own personal barcode (that is generated by the telegram bot).
If a product is shared by multiple people, all their barcodes should be scanned. 
Then, the product itself is scanned.
The price is shared (if multiple people), and the balance is stored in the database.
Afterwards everyone has the possibility to retrieve their balance via the telegram bot and pay the host-of-the-night for their expenses. 

## Installation

Need: _python_, _pip_, _sqlite3_, _barcode scanner_

Install requirements:

```bash
$ pip install -r requirements
```

Create database (with name _coaster.db_, but may be changed if wanted):

``` bash
$ mysql3 coaster.db
```

### .env file

A `.env`-file is needed to keep your secrets. See `.env_example` for the needed keys.

## License

[MIT License](LICENSE.md)
