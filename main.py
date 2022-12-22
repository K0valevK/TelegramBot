import telebot
from telebot import types
from telebot import async_telebot
import requests
from bs4 import BeautifulSoup
import asyncio

bot = telebot.async_telebot.AsyncTeleBot('5914144117:AAHWTI71J5Okefex0s0RTGMGG3GK6J-0JL8')


@bot.message_handler(commands=['start'])
async def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    help_button = types.KeyboardButton('/help')
    markup.add(help_button)
    await bot.send_message(message.chat.id, 'Чем могу помочь?', reply_markup=markup)


@bot.message_handler(commands=['help'])
async def bot_help(message):
    await bot.send_message(message.chat.id,
                           'Ну вообще пока не так уж много всего и могу 👉👈\n'
                           'Однако точно тебе скажу, если нужно найти какого-то преподавателя из ВШЭ, '
                           'посмотреть на рейтинг или узнать последние новости любимого универститета (ВШЭ), '
                           'то тут я в деле!\n')
    await bot.send_message(message.chat.id,
                           'Напиши Найти и ФИО преподавателя или Рейтинг и '
                           'инициалы образовательной программы с номером курса, или просто новости')


@bot.message_handler(func=lambda
        message: message.text[:5].lower() == 'найти')
async def find_person(message):
    args = message.text.split()
    if len(args) == 1:
        await bot.send_message(message.chat.id, 'А кого искать-то?)')
        return
    search_param = args[1]
    for i in range(2, len(args)):
        search_param += '+' + args[i]
    r = requests.get(f"https://www.hse.ru/org/persons/?search_person={search_param}")
    soup = BeautifulSoup(r.content, 'html.parser')
    ref_list = []
    for link in soup.find_all('a'):
        ref_list.append(link.get('href'))
    ref_list = [i for i in ref_list if (i.startswith('/org/persons/') and i[13].isnumeric())]
    if len(ref_list) == 0:
        await bot.send_message(message.chat.id, 'Увы! Такого преподавателя нет. Попробуешь ещё раз?')
    elif len(ref_list) == 1:
        await bot.send_message(message.chat.id, 'Нашёл!')
        await bot.send_message(message.chat.id, f"https://www.hse.ru" + ref_list[0])
    else:
        await bot.send_message(message.chat.id,
                               'Таких людей довольно много, может сформулируешь запрос поточнее? '
                               'Ну или тебе повезёт найти нужного человека среди первых пяти)')
        for i in range(5):
            await bot.send_message(message.chat.id, f"https://www.hse.ru" + ref_list[i])


@bot.message_handler(func=lambda
        message: message.text[:7].lower() == 'рейтинг')
async def check_ratings(message):
    args = message.text.split()
    if len(args) == 1:
        await bot.send_message(message.chat.id, 'А кого искать-то?)')
        return
    link_code = {'пми': 'ami', 'пи': 'se'}
    if len(args) == 2:
        await bot.send_message(message.chat.id, f"https://www.hse.ru/ba/{link_code[args[1]]}/ratings")
    else:
        await bot.send_message(message.chat.id, f"https://www.hse.ru/ba/{link_code[args[1]]}/ratings?course={args[2]}")


@bot.message_handler(func=lambda
        message: message.text.lower() == 'новости')
async def latest_news(message):
    r = requests.get(f"https://www.hse.ru/our/news/new/")
    soup = BeautifulSoup(r.content, 'html.parser')
    ref_list = []
    for link in soup.find_all('a'):
        ref_list.append(link.get('href'))
    ref_list = [i for i in ref_list if
                (i.startswith('https://www.hse.ru/our/news/') and len(i) > 28 and i[28].isnumeric())]
    await bot.send_message(message.chat.id, 'Последние новости ВШЭ:')
    await bot.send_message(message.chat.id, f"{ref_list[0]}")


asyncio.run(bot.polling(none_stop=True, interval=0))
