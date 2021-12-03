#!env/bin/python3
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import settings
import ephem
from datetime import date, datetime
import re
import os.path
from shutil import copyfile

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

def get_next_full_moon(update, context):
    logging.info('Вызван /next_full_moon')
    input_date = update.message.text.split()[1]
    try:
        input_ddate = datetime.strptime(input_date, '%Y-%m-%d')
    except:
        update.message.reply_text('В запросе должна быть указана дата в формате %Y-%m-%d, например /next_full_moon 2019-01-01')
        return
    next_date = ephem.next_full_moon(input_ddate)
    update.message.reply_text(f'Следующее полнолуние {next_date}')

def play_cities(update, context):
    logging.info('Вызван /play_cities')
    logging.info(update.message.chat.id)
    
    orig_citiesfile_path = 'rcities.txt'
    input_city = update.message.text.split()[1].lower()
    user_citiesfile_path = f'rcities.{update.message.chat.id}.temp'

    if not os.path.isfile(user_citiesfile_path):
        copyfile(orig_citiesfile_path, user_citiesfile_path)
    
    with open(orig_citiesfile_path, 'r', encoding='utf-8') as orig_citiesfile:
        orig_cities_raw = orig_citiesfile.read()
    allcities = orig_cities_raw.split()

    with open(user_citiesfile_path, 'r', encoding='utf-8') as user_citiesfile:
        citiesraw = user_citiesfile.read()
    remaincities = citiesraw.split()

    if input_city in remaincities:
        remaincities.remove(input_city)
        currletter = input_city[-1]
        update.message.reply_text(f'Мой город на букву {currletter.capitalize()}')
        r = re.compile('^(%s)'%currletter)
        for city in remaincities:
            if r.match(city):
                update.message.reply_text(f'Выбираю {city.capitalize()}, твой город на букву {city[-1].capitalize()}')
                remaincities.remove(city)
                with open(user_citiesfile_path, 'w', encoding='utf-8') as user_citiesfile:
                    for city in remaincities:
                        user_citiesfile.write(city + "\n")
                return
        update.message.reply_text(f'Городов на букву {currletter.capitalize()} не осталось, ты победил! Теперь можно начать заново :)')
        os.remove(user_citiesfile_path)
    else:
        if input_city in allcities:
            update.message.reply_text(f'Город {input_city.capitalize()} уже назывался')
        else:
            update.message.reply_text(f'Города {input_city.capitalize()} в России нет')


def main():
    mybot = Updater(settings.API_KEY, use_context=True)
    dp = mybot.dispatcher
    dp.add_handler(CommandHandler("start", greet_user))
    dp.add_handler(CommandHandler("planet", where_is_planet))
    dp.add_handler(CommandHandler("wordcount", check_word_count))
    dp.add_handler(CommandHandler("next_full_moon", get_next_full_moon))
    dp.add_handler(CommandHandler("cities", play_cities))
    dp.add_handler(MessageHandler(Filters.text, talk_to_me))
    logging.info("Бот стартовал")
    mybot.start_polling()
    mybot.idle()

if __name__ == "__main__":
    main()
