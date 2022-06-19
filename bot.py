import telebot
from bs4 import BeautifulSoup
import requests
from telebot import types
import json

headers = {"User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:101.0) Gecko/20100101 Firefox/101.0"}
url = "https://www.ixbt.com/news/"
token = '5392113929:AAGbGpbKew4EAcBs_rkgCXXXsmeDOiILK4Y'
bot = telebot.TeleBot(token)
news = {}

@bot.message_handler(commands=['start'])
def start_message(message):
    reply = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = "Все Новости"
    btn2 = "Свежие Новости"
    btn3 = "Последние 5 новостей"
    reply.add(btn1, btn2, btn3)
    bot.send_message(message.chat.id, "Привет, это бот с новостями", reply_markup=reply)

@bot.message_handler(content_types=['text'])
def news_choose(message):
    if message.text == "Все Новости":
        all_news(message)
    elif message.text == "Свежие новости":
        fresh_news(message)
    elif message.text == "Последние 5 новостей":
        last_news(message)

def all_news(message):
    global headers, url, news
    resp = requests.get(url=url, headers=headers)
    soup = BeautifulSoup(resp.text, "lxml")
    news_all = soup.find_all("li", class_="item")
    for n in news_all:
        title = n.find("strong").text.strip()
        desc = n.find("strong").find_next().text.strip()
        link = f'https://www.ixbt.com{n.find("a").get("href")}'.replace('#comments', '')
        id = n.find("span", class_="time_iteration_icon_light").text.replace(':', '')
        bot.send_message(message.chat.id, f"*{title}*\n\n{desc}\n\n{link}", parse_mode="Markdown")
        news[id] = {
            'title' : title,
            'description' : desc,
            'link' : link
        }
    with open("news.json", "w") as file:
        json.dump(news, file, indent=4, ensure_ascii=False)

def fresh_news(message):
    global news, headers, url
    resp = requests.get(url=url, headers=headers)
    soup = BeautifulSoup(resp.text, "lxml")
    news_all = soup.find_all("li", class_="item")
    with open("news.json", "r") as file:
        news_dict = json.load(file)
    for n in news_all:
        id = n.find("span", class_="time_iteration_icon_light").text.replace(':', '')
        print(id)
        if id in news_dict:
            bot.send_message(message.chat.id, "Свежих новостей пока нет")
            continue
        else:
         title = n.find("strong").text.strip()
         desc = n.find("strong").find_next().text.strip()
         link = f'https://www.ixbt.com{n.find("a").get("href")}'.replace('#comments', '')
         bot.send_message(message.chat.id, f"*{title}*\n\n{desc}\n\n{link}", parse_mode="Markdown")
         news[id] = {
            'title' : title,
            'description' : desc,
            'link' : link
         }
         with open("news.json", "w") as file:
           json.dump(news, file, indent=4, ensure_ascii=False)

def last_news(message):
    with open("news.json", "r") as file:
        news = json.load(file)
    for k, v in sorted(news.items())[-5:]:
        bot.send_message(message.chat.id, f"*{v['title']}*\n\n{v['description']}\n\n{v['link']}", parse_mode="Markdown")




bot.infinity_polling()