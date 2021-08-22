import os
import yfinance as yf
from telegram.ext import ConversationHandler, Filters
from telegram.ext import Updater, CommandHandler, MessageHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove

# variáveis globais
token = os.environ.get('API_KEY')
teclado = [['SIM', 'NÃO']]
reply_markup = ReplyKeyboardMarkup(teclado, one_time_keyboard=True, resize_keyboard=True)
PORT = int(os.environ.get("PORT", 5000))


def start(update, context):
    '''Define uma mensagem de boas vindas ao usuário e solicitação qual comando ira ser utilizado'''
    texto_boas_vindas = 'Olá, bem vindo ao FLR Finance, gostariad de obter informações sobre uma ação listada na IBOVESPA? '
    update.message.reply_text(texto_boas_vindas, reply_markup=reply_markup)
    return 'ESCOLHA'


def escolha(update, context):
    '''Usuário informa o ticker e caso seja informado algo não relativo ao solicitado e retornado a mensagem de fim'''
    resposta = update.message.text
    usuario = update.message.from_user
    update.message.reply_text('Obrigado pela resposta!', reply_markup=ReplyKeyboardRemove())

    if resposta == 'SIM':
        update.message.reply_text('Por favor indique qual o código da ação (Ticker) que deseja obter informações')
        return 'AÇÃO'
    else:
        texto_fim = 'No momento posso trazer somente a ultima cotação da ação. \nEm breve aprenderei novas funções'
        update.message.reply_text(texto_fim)
        return ConversationHandler.END


def preco(update, context):
    '''Pegando o preço das ações e suas informações'''
    nome_acao = update.message.text
    nome_acao = nome_acao.upper()
    try:
        ticker = yf.Ticker(f'{nome_acao}.SA')
        info = ticker.info
        var = ((float(info["ask"])) / (float(info["previousClose"])) - 1) * 100
        site = 'https://statusinvest.com.br/acoes/'+nome_acao+''
        dividendo = info["trailingAnnualDividendYield"] * 100
        update.message.reply_text(f'Aqui estão algumas informações sobre {nome_acao}:\n'
                                  f'\nCotação: R${info["currentPrice"]:.2f}\n'
                                  f'Variação: {round(var, 2)}%\n'
                                  f'Dividend Yield: {round(dividendo, 2)}%\n'
                                  f'\nPara mais infomações sobre {nome_acao} acesse: {site}\n'
                                  f'\nDeseja consultar outra ação?', reply_markup=reply_markup)
        return 'ESCOLHA'
    except:
        update.message.reply_text(f'{nome_acao} não está registrada em nossa base de dados.\nTente novamente')
        return 'AÇÃO'


def fim(update, context):
    '''Mensagem de encerramento'''
    update.message.reply_text('Espero ter te ajudado, te espero novamente!')
    return ConversationHandler.END


def main():
    updater = Updater(token, use_context=True)
    dispatcher = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            "ESCOLHA": [MessageHandler(Filters.text, escolha)],
            "AÇÃO": [MessageHandler(Filters.text, preco)]
        },
        fallbacks=[CommandHandler('fim', fim)]
    )
    dispatcher.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
