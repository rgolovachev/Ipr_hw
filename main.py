import telebot
import re
import os
from telebot import types
from bs4 import BeautifulSoup
import requests
import asyncio

PATH_TO_YOUR_TOKEN = "token.txt"
file = open(PATH_TO_YOUR_TOKEN, "r")
TOKEN = file.readline()
file.close()
bot = telebot.TeleBot(TOKEN)
main_url = 'https://www.euro-football.ru/'
url = 'https://www.euro-football.ru/champ/england/premier-league'
dates = dict()
help_msg = '''
```
Этот бот позволяет смотреть результаты, новости и статистику Английской Премьер лиги по футболу

Данные парсятся с сайта www.euro-football.ru

Команды, которые воспринимает этот бот:

/help - показать это сообщение
/table - показать таблицу результатов
/news - показать новости АПЛ
/schedule - показать расписание предстоящих матчей
/results - показать результаты прошедших матчей
/bombardiers - показать топ-10 бомбардиров АПЛ
```
'''


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.from_user.id, help_msg, parse_mode="Markdown")


async def print_table(message):
    global url
    query_ans = ""
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    tab = soup.findAll('div', class_='block__content block__turnir-table')
    arr = str(tab[0]).split('<tr>')
    arr2 = []
    for val in arr:
        arr2.extend(val.split("</tr>"))
    left = 2
    right = 21
    for i in range(1, 22):
        # print(arr[i])
        kek = arr[i].split(">")
        lol = []
        for value in kek:
            lol.extend(value.split("<"))
        # print(lol)
        cols = ["table__place", "href", "table__game", "table__result"]
        to_print = []
        for j in range(len(lol)):
            if lol[j] == "/tbody":
                break
            for col in cols:
                if col in lol[j]:
                    to_print.append(lol[j + 1].strip())
                    break
        for val in to_print:
            query_ans += val + " "
        query_ans += "\n"
    await bot.send_message(message.from_user.id, "```\n# Команда И В Н П Мячи Разн О." + query_ans + "\n```",
                           parse_mode="Markdown")
    # file.write(soup.prettify())
    # print(soup.prettify())
    # file.close()


async def print_news(message):
    global url
    global main_url
    query_ans = ""
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    tab = soup.findAll('div', class_='main-news__items')
    soup = BeautifulSoup(str(tab[0]), "html.parser")
    # print(soup.prettify())
    # print("=======")
    arr = soup.find_all("img")
    titles = []
    for elem in arr:
        match = re.search('alt=".*" ', str(elem))
        titles.append((match[0])[5:-17])
    # print("=======")
    raw_links = re.findall('<a class="main-news__item-link" href=".*">', str(tab[0]))
    links = []
    for elem in raw_links:
        match = re.search('href=".*"', str(elem))
        links.append(main_url + str(match[0][6:-1]))
    # print(titles)
    # print(links)
    msg = "Новости АПЛ: \n\n"
    for i in range(len(titles)):
        msg += "[" + titles[i] + "](" + links[i] + ")"
        msg += "\n\n"
    await bot.send_message(message.from_user.id, msg, parse_mode="Markdown")
    # print()
    # print(soup.find_all())
    # match = re.findall('alt=".*"', str(tab[0]))
    # print(match)


async def print_schedule(message):
    global url
    global main_url
    global dates
    page = requests.get(main_url + "champ/england/premier-league/calendar")
    soup = BeautifulSoup(page.text, "html.parser")
    tab = soup.findAll('div', class_='turnir-match__group turnir-match__group_date')
    dates = dict()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for day in tab:
        cur_day = str(day)
        cur_soup = BeautifulSoup(cur_day, "html.parser")
        title = cur_soup.find('div', class_='turnir-match__group-title').get_text()
        time = cur_soup.findAll('div', class_='turnir-match-list__item-status')
        team1 = cur_soup.findAll('div', class_='turnir-match-list__item-team1')
        team2 = cur_soup.findAll('div', class_='turnir-match-list__item-team2')
        # print(title)
        markup.add(types.KeyboardButton(title))
        dates[title] = "``` Расписание матчей на " + title + "\n\n"
        for i in range(len(time)):
            dates[title] += time[i].get_text().strip() + " " + team1[i].get_text().strip() + " vs " + team2[
                i].get_text().strip() + "\n"
        dates[title] += "```"
    await bot.send_message(message.from_user.id, "Выбери дату", reply_markup=markup)


async def print_results(message):
    global url
    global main_url
    global dates
    page = requests.get(main_url + "champ/england/premier-league/result")
    soup = BeautifulSoup(page.text, "html.parser")
    tab = soup.findAll('div', class_='turnir-match__group turnir-match__group_date')
    dates = dict()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for day in tab:
        cur_day = str(day)
        cur_soup = BeautifulSoup(cur_day, "html.parser")
        title = cur_soup.find('div', class_='turnir-match__group-title').get_text()
        time = cur_soup.findAll('div', class_='turnir-match-list__item-status')
        team1 = cur_soup.findAll('div', class_='turnir-match-list__item-team1')
        res = cur_soup.findAll('a', class_='match-score match-score_finish')
        team2 = cur_soup.findAll('div', class_='turnir-match-list__item-team2')
        # print(title)
        markup.add(types.KeyboardButton(title))
        dates[title] = "``` Результаты матчей " + title + "\n\n"
        for i in range(len(time)):
            dates[title] += time[i].get_text().strip() + " " + team1[i].get_text().strip() + " " + res[
                i].get_text().strip() + " " + team2[i].get_text().strip() + "\n"
        dates[title] += "```"
    await bot.send_message(message.from_user.id, "Выбери дату", reply_markup=markup)


async def print_bombardiers(message):
    global main_url
    page = requests.get(main_url + "champ/england/premier-league/statistic")
    soup = BeautifulSoup(page.text, "html.parser")
    tab = str(soup.find('tbody', class_='bombardiers-list-tbody'))
    soup2 = BeautifulSoup(tab, "html.parser")
    place = soup2.findAll('td', class_='place')
    person = soup2.findAll('td', class_='person')
    team = soup2.findAll('td', class_='team')
    goals = soup2.findAll('td', class_='goals')
    minutes = soup2.findAll('td', class_='minutes')
    games = soup2.findAll('td', class_='game')
    msg = "``` Топ-10 бомбардиров АПЛ:\n\n"
    msg += "#  Name          Team Goals Mins Games\n\n"
    for i in range(10):
        msg += place[i].get_text().strip() + " " + person[i].get_text().strip() + " " + team[
            i].get_text().strip() + " " + goals[i].get_text().strip() + " " + minutes[i].get_text().strip() + " " + \
               games[i].get_text().strip() + "\n"
    msg += "```"
    await bot.send_message(message.from_user.id, msg, parse_mode="Markdown")


async def print_help(message):
    await bot.send_message(message.from_user.id, help_msg, parse_mode="Markdown")


async def print_dict_elem(message):
    await bot.send_message(message.from_user.id, dates[message.text], parse_mode="Markdown")


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    global help_msg
    global dates
    if message.text == "/help":
        asyncio.run(print_help(message))
    if message.text == "/table":
        dates = dict()
        asyncio.run(print_table(message))
    if message.text == "/news":
        dates = dict()
        asyncio.run(print_news(message))
    if message.text == "/schedule":
        dates = dict()
        asyncio.run(print_schedule(message))
    if message.text == "/results":
        dates = dict()
        asyncio.run(print_results(message))
    if message.text == "/bombardiers":
        dates = dict()
        asyncio.run(print_bombardiers(message))
    if (len(dates) > 0) and (message.text in dates):
        asyncio.run(print_dict_elem(message))


while True:
    try:
        bot.polling(none_stop=True, interval=0)
    except:
        continue
