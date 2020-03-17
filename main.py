import urllib.request
import telebot
import config
import requests
from bs4 import BeautifulSoup as BS
from telebot import types

#парсим погоду
url = 'https://yandex.ru/pogoda/stavropol'
headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
			'accept':'*/*'}

def get_html(url, params=None):
	r = requests.get(url, headers=headers, params=params)
	return r

def get_content(html):
	soup = BS(html, 'html.parser')
	items = soup.find_all('span',class_='temp__value')[1].get_text()
	print(items)
	return items

def parse():
	html = get_html(url)
	if html.status_code == 200:
		return get_content(html.text)
	else:
		print('Error')

parse()

#делаем бота
bot = telebot.TeleBot(config.token)

@bot.message_handler(commands=['start'])
def welcome(message):
	sti = open('sticker.webp', 'rb')
	bot.send_sticker(message.chat.id,sti)

	#keyboard
	markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
	item1 = types.KeyboardButton('Stavropol region')
	item2 = types.KeyboardButton('Krasnodar region')

	markup.add(item1,item2)

	bot.send_message(message.chat.id, 'Привет, здесь можно узнать погоду на сегодня 😚',
		reply_markup=markup)

@bot.message_handler(commands=['help'])
def main(message):
	bot.send_message(message.chat.id, 'Привет погода на сегодня: ' + parse())
    

@bot.message_handler(content_types=['text'])
def lalala(message):
	if message.chat.type == 'private':
		if message.text == 'Stavropol region':
			markup = types.InlineKeyboardMarkup(row_width=2)
			item1 = types.InlineKeyboardButton('Ставрополь', callback_data = 'stavropol')
			item2 = types.InlineKeyboardButton('Невинномысск', callback_data = 'nevinnomyssk')

			markup.add(item1,item2)
			#bot.send_message(message.chat.id, 'Привет погода на сегодня:  ' + parse())

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
	try:
		if call.message:
			if call.data == 'stavropol':
				bot.send_message(message.chat.id, 'Привет погода на сегодня:  ' + parse())
			elif call.data == 'nevinnomyssk':
				bot.send_message(message.chat.id, 'Привет погода на сегодня:  ' + parse())
			
			
	except Exception as e:
		print(repr(e))

#RUN

if __name__ == '__main__':   
	bot.polling(none_stop=True)

