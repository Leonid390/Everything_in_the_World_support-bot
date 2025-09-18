import sqlite3

class DatabaseService:
    def __init__(self, db_path="support_bot.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS faqs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_questions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    username TEXT,
                    question TEXT NOT NULL,
                    answer TEXT,
                    is_answered BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    answered_at TIMESTAMP
                )
            ''')
            
            cursor.execute('SELECT COUNT(*) FROM faqs')
            if cursor.fetchone()[0] == 0:
                default_faqs = [
                    ("Как оформить заказ?", "Для оформления заказа добавьте товары в корзину и перейдите к оформлению. Укажите адрес доставки и выберите способ оплаты."),
                    ("Какие способы оплаты доступны?", "Мы принимаем оплату картой, наличными при получении, переводом на карту и через электронные кошельки."),
                    ("Сколько стоит доставка?", "Стоимость доставки зависит от региона. По городу - 200 руб., за город - от 300 руб. При заказе от 2000 руб. доставка бесплатная."),
                    ("Можно ли вернуть товар?", "Да, товар можно вернуть в течение 14 дней с момента получения при условии сохранения товарного вида и упаковки."),
                    ("Как отследить заказ?", "После отправки заказа вы получите трек-номер для отслеживания. Также можете связаться с нами для уточнения статуса заказа.")
                ]
                cursor.executemany('INSERT INTO faqs (question, answer) VALUES (?, ?)', default_faqs)
            
            conn.commit()
    
    def get_all_faqs(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, question, answer FROM faqs ORDER BY id')
            return cursor.fetchall()
    
    def add_user_question(self, user_id, username, question):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO user_questions (user_id, username, question)
                VALUES (?, ?, ?)
            ''', (user_id, username, question))
            conn.commit()
            return cursor.lastrowid or 0
    
    def get_unanswered_questions(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, user_id, username, question 
                FROM user_questions 
                WHERE is_answered = FALSE 
                ORDER BY created_at ASC
            ''')
            return cursor.fetchall()
    
    def answer_user_question(self, question_id, answer):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE user_questions 
                SET answer = ?, is_answered = TRUE, answered_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (answer, question_id))
            conn.commit()
            return cursor.rowcount > 0
    
    def get_user_question_by_id(self, question_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, user_id, username, question 
                FROM user_questions 
                WHERE id = ?
            ''', (question_id,))
            return cursor.fetchone()
    
    def add_faq(self, question, answer):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO faqs (question, answer) VALUES (?, ?)', (question, answer))
            conn.commit()
            return cursor.lastrowid or 0