import telebot
from telebot import types
from config import TOKEN, ADMIN_ID
from db_logic import DatabaseService


bot = telebot.TeleBot(TOKEN)
db = DatabaseService()

user_states = {}
STATE_WAITING_QUESTION = "waiting_question"
STATE_WAITING_ANSWER = "waiting_answer"
STATE_WAITING_FAQ_QUESTION = "waiting_faq_question"
STATE_WAITING_FAQ_ANSWER = "waiting_faq_answer"

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = """
Добро пожаловать в службу поддержки магазина 'Всё на Свете'!

Я помогу вам найти ответы на часто задаваемые вопросы или передам ваш вопрос администратору.

Доступные команды:
/faq - Посмотреть часто задаваемые вопросы
/ask - Задать свой вопрос
/help - Показать это сообщение
"""
    bot.reply_to(message, welcome_text)

@bot.message_handler(commands=['faq'])
def show_faq(message):
    faqs = db.get_all_faqs()
    
    if not faqs:
        bot.reply_to(message, "FAQ пока пуст. Задайте свой вопрос командой /ask")
        return
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    for faq_id, question, _ in faqs:
        callback_data = f"faq_{faq_id}"
        markup.add(types.InlineKeyboardButton(question, callback_data=callback_data))
    
    bot.reply_to(message, "Часто задаваемые вопросы:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('faq_'))
def handle_faq_callback(call):
    faq_id = int(call.data.split('_')[1])
    faqs = db.get_all_faqs()
    
    for f_id, question, answer in faqs:
        if f_id == faq_id:
            response = f"Вопрос: {question}\n\nОтвет: {answer}"
            bot.edit_message_text(response, call.message.chat.id, call.message.message_id)
            
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("Назад к FAQ", callback_data="back_to_faq"))
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup)
            break

@bot.callback_query_handler(func=lambda call: call.data == 'back_to_faq')
def back_to_faq(call):
    faqs = db.get_all_faqs()
    markup = types.InlineKeyboardMarkup(row_width=1)
    for faq_id, question, _ in faqs:
        callback_data = f"faq_{faq_id}"
        markup.add(types.InlineKeyboardButton(question, callback_data=callback_data))
    
    bot.edit_message_text("Часто задаваемые вопросы:", call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.message_handler(commands=['ask'])
def ask_question(message):
    user_states[message.from_user.id] = STATE_WAITING_QUESTION
    bot.reply_to(message, "Опишите ваш вопрос. Я передам его администратору:")

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "У вас нет прав администратора")
        return
    
    unanswered = db.get_unanswered_questions()
    
    text = "Панель администратора\n\n"
    if unanswered:
        text += f"Неотвеченных вопросов: {len(unanswered)}\n\n"
        
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton("Посмотреть вопросы", callback_data="admin_questions"))
        markup.add(types.InlineKeyboardButton("Добавить FAQ", callback_data="admin_add_faq"))
        
        bot.reply_to(message, text, reply_markup=markup)
    else:
        text += "Все вопросы отвечены!\n\n"
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Добавить FAQ", callback_data="admin_add_faq"))
        
        bot.reply_to(message, text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'admin_questions')
def show_admin_questions(call):
    if call.from_user.id != ADMIN_ID: # call.from_user.id not in ADMIN_IDS
        bot.answer_callback_query(call.id, "Нет прав доступа")
        return
    
    unanswered = db.get_unanswered_questions()
    
    if not unanswered:
        bot.edit_message_text("Все вопросы отвечены!", call.message.chat.id, call.message.message_id)
        return
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    for question_id, user_id, username, question in unanswered:
        user_display = f"@{username}" if username else f"ID:{user_id}"
        button_text = f"{user_display}: {question[:30]}..."
        markup.add(types.InlineKeyboardButton(button_text, callback_data=f"answer_{question_id}"))
    
    markup.add(types.InlineKeyboardButton("Назад", callback_data="back_to_admin"))
    bot.edit_message_text("Неотвеченные вопросы:", call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('answer_'))
def handle_answer_question(call):
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "Нет прав доступа")
        return
    
    question_id = int(call.data.split('_')[1])
    question_data = db.get_user_question_by_id(question_id)
    
    if not question_data:
        bot.edit_message_text("Вопрос не найден", call.message.chat.id, call.message.message_id)
        return
    
    q_id, user_id, username, question = question_data
    user_display = f"@{username}" if username else f"ID:{user_id}"
    
    text = f"Вопрос от {user_display}:\n\n{question}\n\nНапишите ваш ответ:"
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id)
    
    user_states[call.from_user.id] = f"{STATE_WAITING_ANSWER}_{question_id}"

@bot.callback_query_handler(func=lambda call: call.data == 'admin_add_faq')
def start_add_faq(call):
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "Нет прав доступа")
        return
    
    user_states[call.from_user.id] = STATE_WAITING_FAQ_QUESTION
    bot.edit_message_text("Добавление нового FAQ\n\nВведите вопрос:", call.message.chat.id, call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data == 'back_to_admin')
def back_to_admin(call):
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "Нет прав доступа")
        return
    
    unanswered = db.get_unanswered_questions()
    
    text = "Панель администратора\n\n"
    if unanswered:
        text += f"Неотвеченных вопросов: {len(unanswered)}\n\n"
        
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton("Посмотреть вопросы", callback_data="admin_questions"))
        markup.add(types.InlineKeyboardButton("Добавить FAQ", callback_data="admin_add_faq"))
    else:
        text += "Все вопросы отвечены!\n\n"
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Добавить FAQ", callback_data="admin_add_faq"))
    
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    user_id = message.from_user.id
    user_state = user_states.get(user_id)
    
    if user_state == STATE_WAITING_QUESTION:
        question_id = db.add_user_question(user_id, message.from_user.username, message.text)
        user_states.pop(user_id, None)
        
        bot.reply_to(message, "Ваш вопрос принят! Администратор ответит в ближайшее время.")
        
        if ADMIN_ID:
            try:
                user_display = f"@{message.from_user.username}" if message.from_user.username else f"ID:{user_id}"
                notification = f"Новый вопрос от {user_display}:\n\n{message.text}\n\n/admin - Перейти в панель администратора"
                bot.send_message(ADMIN_ID, notification)
            except Exception:
                pass
    
    elif user_state and user_state.startswith(STATE_WAITING_ANSWER):
        question_id = int(user_state.split('_')[2])
        question_data = db.get_user_question_by_id(question_id)
        
        if question_data:
            q_id, target_user_id, username, question = question_data
            
            db.answer_user_question(question_id, message.text)
            user_states.pop(user_id, None)
            
            try:
                response = f"Получен ответ на ваш вопрос:\n\nВопрос: {question}\n\nОтвет: {message.text}"
                bot.send_message(target_user_id, response)
                
                bot.reply_to(message, "Ответ отправлен пользователю!")
            except Exception:
                bot.reply_to(message, "Не удалось отправить ответ пользователю (возможно, он заблокировал бота)")
        else:
            bot.reply_to(message, "Вопрос не найден")
            user_states.pop(user_id, None)
    
    elif user_state == STATE_WAITING_FAQ_QUESTION:
        user_states[user_id] = f"{STATE_WAITING_FAQ_ANSWER}_{message.text}"
        bot.reply_to(message, f"Вопрос: {message.text}\n\nТеперь введите ответ:")
    
    elif user_state and user_state.startswith(STATE_WAITING_FAQ_ANSWER):
        question = user_state.split('_')[3]
        answer = message.text
        
        db.add_faq(question, answer)
        user_states.pop(user_id, None)
        
        bot.reply_to(message, f"FAQ добавлен!\n\nВопрос: {question}\nОтвет: {answer}")
    
    else:
        bot.reply_to(message, "Используйте /help для просмотра доступных команд.")


bot.infinity_polling()
