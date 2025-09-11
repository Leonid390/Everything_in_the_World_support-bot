from config import TOKEN 
import telebot
from logic import *
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['help',  'start'])
def handle_start(message):
    bot.send_message(message.chat.id, "Я Бот поддержки интернет магазина 'всё на свете'. Спрашивайте, что тебе не понятно по заказам или чему-то, имеющему отношение к нашему магазину")
    bot.send_message(message.chat.id, "Спрашивайте ниже, что вам не понятно по заказам или темам, имеющим отношение к нашему магазину")

@bot.message_handler(func=lambda m: True)
def handle_message(message):
    question = message.text.strip()
    
    # Получаем ответ из logic.py
    answer = q_and_a(question)
    
    # Такая же логика отправки сообщений
    if answer:
        bot.send_message(message.chat.id, answer)
    else:
        bot.send_message(message.chat.id, "Вопрос не имеет ответа, но добавлен в базу данных и может получить ответ позже. Попробуйте спроить позже")




bot.infinity_polling()
