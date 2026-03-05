import json
from pathlib import Path
from datetime import datetime

class Database:
    """Простое хранилище данных в JSON"""
    
    def __init__(self):
        self.paid_users = set()       # ID тех, кто купил
        self.waiting_payment = set()  # ID тех, кто отправил скрин, ждет проверки
        self.user_chats = {}          # Инфо о пользователях {id: {"name": "...", "last_seen": "..."}}
        self.load()
    
    def load(self):
        """Загрузить данные из файла"""
        if Path("db.json").exists():
            try:
                with open("db.json", "r") as f:
                    data = json.load(f)
                    self.paid_users = set(data.get("paid_users", []))
                    # Остальное пока не восстанавливаем для простоты
            except:
                self.paid_users = set()
    
    def save(self):
        """Сохранить данные в файл"""
        with open("db.json", "w") as f:
            json.dump({
                "paid_users": list(self.paid_users)
            }, f)
    
    def add_user(self, user_id, username, first_name):
        """Запомнить пользователя"""
        self.user_chats[user_id] = {
            "username": username,
            "first_name": first_name,
            "last_seen": datetime.now().isoformat()
        }
    
    def is_paid(self, user_id):
        """Проверил, покупал ли пользователь"""
        return user_id in self.paid_users
    
    def add_paid(self, user_id):
        """Отметить пользователя как купившего"""
        self.paid_users.add(user_id)
        self.save()
    
    def get_stats(self):
        """Получить статистику"""
        return {
            "users": len(self.user_chats),
            "sales": len(self.paid_users),
            "revenue": len(self.paid_users) * 50,
            "waiting": len(self.waiting_payment)
        }

# Создаем глобальный экземпляр базы данных
db = Database()