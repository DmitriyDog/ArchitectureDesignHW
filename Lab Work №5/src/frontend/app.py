import requests
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    try:
        # Важно! backend - это имя сервиса из docker-compose.yml
        response = requests.get('http://backend:5000/', timeout=5)
        backend_message = response.text
        return f'Frontend получил ответ от: <br> {backend_message}'
    except requests.exceptions.RequestException as e:
        return f'Frontend не смог достучаться до backend. Ошибка: {e}'

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
