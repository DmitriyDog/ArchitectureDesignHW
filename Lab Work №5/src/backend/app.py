import os
import psycopg2
from flask import Flask
from psycopg2 import sql
import time

app = Flask(__name__)

# Функция для подключения к БД с повторными попытками
def get_db_connection():
    max_retries = 5
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            conn = psycopg2.connect(
                host=os.getenv('POSTGRES_HOST', 'db'),  # 'db' - имя сервиса в docker-compose
                database=os.getenv('POSTGRES_DB', 'labdb'),
                user=os.getenv('POSTGRES_USER', 'user'),
                password=os.getenv('POSTGRES_PASSWORD', 'password'),
                port=5432
            )
            return conn
        except psycop2.OperationalError as e:
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                continue
            else:
                raise e

@app.route('/')
def hello():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Увеличиваем счетчик
        cur.execute("""
            UPDATE hits 
            SET counter = counter + 1, last_updated = CURRENT_TIMESTAMP 
            WHERE id = 1 
            RETURNING counter
        """)
        
        # Если запись еще не существует (на всякий случай)
        if cur.rowcount == 0:
            cur.execute("INSERT INTO hits (id, counter) VALUES (1, 1) RETURNING counter")
        
        count = cur.fetchone()[0]
        conn.commit()

        # Закрываем соединение с БД
        cur.close()
        conn.close()
        
        return f'Backend с PostgreSQL: Этот запрос виден {count} раз.\n'
        
    except Exception as e:
        return f'Backend: Ошибка подключения к PostgreSQL: {str(e)}\n'

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

