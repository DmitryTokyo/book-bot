# Book webhook bot

## About
The Book Webhook Bot searches in several resources. Bot was based on Flask framework and working via webhook. Books are sent to Telegram. 

## Requirements
- Programming language - Python 3.8.5.
- Webhook was built on - Flask.
- Telegram bot library - Python-telegram-bot.
- Cache is using - Redis database.

## Installation
1. Clone this repository `git clone https://github.com/DmitryTokyo/quotes.git`.
2. Create virtual environment `python3 -m venv venv` and activate `source venv/bin/activate`.
3. Install all dependencies `pip install -r requirements.txt`
4. Create `.env` file and put there following variables:
    - `TG_TOKEN` - telegram bot token. You can get it by using `@BotFather` bot.
    - `DATABASE_PASSWORD` - Redis database password.
    - `DATABASE_HOST` - Redis database host.
    - `DATABASE_PORT` - Redis database port.
5. Webhook method needs public IP address or domain, but in a local computer you can use `ngrok` technology. For this way you can start the `ngrok` server by the command `./ngrok http 5000` and `https` link assign to `URL` variable in `.env` file.
6. You need to tell your terminal the main flask application to work with by exporting the FLASK_APP and set debug mode by exporting the FLASK_ENV:
    ```bash
    export FLASK_APP=app.py
    export FLASK_ENV=development
    ```
    You can create `.flaskenv` instead it.

## Usage
1. Start the `./ngrok http 5000` and put to `.env` https link.
2. Start the app by command `flask run`.
3. Set up your webhook to follow the url. You can see in your browser `webhook setup ok!!!`.
4. Send your bot `/start`.

## License
Code licensed under [MIT License](https://opensource.org/licenses/MIT).