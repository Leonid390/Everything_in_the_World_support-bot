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