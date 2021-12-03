#!env/bin/python3
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import settings
import ephem
from datetime import date
import re

logging.basicConfig(filename='bot.log', level=logging.INFO)

def greet_user(update, context):
    logging.info('Вызван /start')
    update.message.reply_text('Привет, пользователь! Ты вызвал команду /start')

def talk_to_me(update, context):
    user_text = update.message.text 
    logging.info(user_text)
    update.message.reply_text(user_text)

def where_is_planet(update, context):
    logging.info('Вызван /planet')
    planet = update.message.text.split()[1]
    constellation = ephem.constellation
    p = getattr(ephem, planet)
    constellation = ephem.constellation(p(date.today()))
    update.message.reply_text(f'{planet} in {constellation[1]}')

def check_word_count(update, context):
    user_text = update.message.text.replace('/wordcount','',1)
    user_text = re.sub(r"[^a-zA-Zа-яА-Я_]+$","",user_text)
    wcount = len(user_text.split())
    if wcount == 0:
        update.message.reply_text('В запросе должно быть минимум одно слово на русском или английском языке')
        return
    logging.info(user_text)
    update.message.reply_text(f'Количество слов: {wcount}')

def main():
    mybot = Updater(settings.API_KEY, use_context=True)
    dp = mybot.dispatcher
    dp.add_handler(CommandHandler("start", greet_user))
    dp.add_handler(CommandHandler("planet", where_is_planet))
    dp.add_handler(CommandHandler("wordcount", check_word_count))
    dp.add_handler(MessageHandler(Filters.text, talk_to_me))
    logging.info("Бот стартовал")
    mybot.start_polling()
    mybot.idle()

if __name__ == "__main__":
    main()
