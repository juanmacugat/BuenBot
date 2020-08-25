import os
import requests

from flask import Flask, request

TELEGRAM_BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
URL = 'https://api.telegram.org/bot' + TELEGRAM_BOT_TOKEN
WEBHOOK_URL = os.environ['WEBHOOK_URL']

app = Flask(__name__)
app.config['TESTING'] = True
app.config['DEVELOPMENT'] = False
app.config['DEBUG'] = True

supported_commands = ['/daiars', '/daiusd', '/arsusd', '/btcars', '/start','/help']


def register_webhook():
    body = {'url': WEBHOOK_URL + '/webhook'}
    response = requests.request('POST', URL + '/setWebhook', json=body)
    if response.status_code == 200:
        return True

    return False


def startup():
    if register_webhook():
        app.logger.info('Callback registered successfully on %s', WEBHOOK_URL)
    else:
        exit()


def send_message(chat, message):
    body = {
        'chat_id': chat,
        'text': message
    }
    response = requests.post(url=URL + '/sendMessage', json=body)
    app.logger.info('Message sent')
    return response.status_code


@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json

    chat = data['message']['chat']['id']
    command = data['message']['text']

    if command not in supported_commands:
        app.logger.info('Unsupported command')
        send_message(chat, 'Hola! Perdon pero no entiendo tu mensaje. Intenta con los comandos definidos')
        return '200'

    if command == '/start':
        return '200'

    if command == '/help':
        send_message(chat, 'WIP')
        return '200'

    response = requests.get(url='https://be.buenbit.com/api/market/tickers')

    if response.status_code == 200:
        tickers = response.json()
        if command == '/arsusd':
            send_message(chat, f'{ars_usd(tickers)} ARS')
        if command == '/daiars':
            send_message(chat, 'COMPRA: ' + dai_ars(tickers)['purchase_price'] + ' ARS - ' +
                         'VENTA: ' + dai_ars(tickers)['selling_price'] + ' ARS')
        elif command == '/daiusd':
            send_message(chat, 'COMPRA: ' + dai_usd(tickers)['purchase_price'] + ' USD - ' +
                         'VENTA: ' + dai_usd(tickers)['selling_price'] + ' USD')
        elif command == '/btcars':
            send_message(chat, 'COMPRA: ' + btc_ars(tickers)['purchase_price'] + ' ARS - ' +
                         'VENTA: ' + btc_ars(tickers)['selling_price'] + ' ARS')
    else:
        send_message(chat, 'Intenta mas tarde, estoy muy cansado ahora')

    return '200'


def btc_ars(tickers):
    return tickers['object']['btcars']


def dai_usd(tickers):
    return tickers['object']['daiusd']


def dai_ars(tickers):
    return tickers['object']['daiars']


def ars_usd(tickers):
    ars_dai = float(tickers['object']['daiars']['selling_price'])
    dai_usd = float(tickers['object']['daiusd']['purchase_price'])
    return round(ars_dai / dai_usd, 2)


startup()

if __name__ == '__main__':
    app.run(port=443, host='0.0.0.0')
