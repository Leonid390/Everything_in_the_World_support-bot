import sqlite3

# Подключаемся к базе данных (файл создастся автоматически, если его нет)
conn = sqlite3.connect('qa_bot.db')
cursor = conn.cursor()

# Создаём таблицу для хранения вопросов и ответов
cursor.execute('''
CREATE TABLE IF NOT EXISTS qa (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT NOT NULL,
    answer TEXT NOT NULL
)
''')

conn.commit()
conn.close()

def q_and_a(question):
    """Обрабатывает вопрос и возвращает ответ или None"""
    conn = sqlite3.connect('qa_bot.db')
    cursor = conn.cursor()
    
    answer_row = cursor.execute("SELECT answer FROM qa WHERE question = ?", (question,)).fetchone()
    
    if answer_row:
        result = answer_row[0] 
    else:
        result = None
        cursor.execute("INSERT INTO qa (question, answer) VALUES (?, ?)", (question, ""))
        conn.commit()
    
    conn.close()
    return result

