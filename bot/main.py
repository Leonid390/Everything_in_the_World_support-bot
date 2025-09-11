from config import TOKEN 
import telebot
from logic import *
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['help'])
def handle_start(message):
    bot.send_message(message.chat.id, "Я Бот поддержки интернет магазина 'Всё на свете'.")
    bot.send_message(message.chat.id, "Спрашивайте ниже, что вам непонятно по заказам или темам, имеющим отношение к нашему магазину")

@bot.message_handler(func=lambda m: True)
def handle_message(message):
    question = message.text.strip()

    conn = sqlite3.connect('qa_bot.db')
    cursor = conn.cursor()
    answer = cursor.execute("SELECT answer FROM qa WHERE question = ?", (question,)).fetchone()

    if answer:
        bot.send_message(message.chat.id, answer[0])
    else:
        bot.send_message(message.chat.id, "Вопрос не имеет ответа, но добавлен в базу данных и может получить ответ через время. Попробуйте спросить позже")
        cursor.execute("INSERT INTO qa (question, answer) VALUES (?, ?)", (question, ""))
        conn.commit()

    conn.close()




bot.infinity_polling()


