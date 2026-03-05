import json
from pathlib import Path
from datetime import datetime

class Database:
    """Простое хранилище данных в JSON"""
    
    def __init__(self):
        self.paid_users = set()       # ID тех, кто купил
        self.payments = {}            # Платежи {payment_id: {"user_id": id, "status": "pending/approved/rejected", "photo": "path", "date": "..."}}
        self.user_chats = {}           # Инфо о пользователях {id: {"name": "...", "last_seen": "..."}}
        self.payment_counter = 0       # Счетчик для ID платежей
        self.load()
    
    def load(self):
        """Загрузить данные из файла"""
        if Path("db.json").exists():
            try:
                with open("db.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.paid_users = set(data.get("paid_users", []))
                    self.payments = data.get("payments", {})
                    self.payment_counter = data.get("payment_counter", 0)
                    self.user_chats = data.get("user_chats", {})
                print(f"✅ База данных загружена. Продаж: {len(self.paid_users)}")
            except Exception as e:
                print(f"⚠️ Ошибка загрузки БД: {e}")
                self.paid_users = set()
                self.payments = {}
                self.payment_counter = 0
                self.user_chats = {}
    
    def save(self):
        """Сохранить данные в файл"""
        try:
            with open("db.json", "w", encoding="utf-8") as f:
                json.dump({
                    "paid_users": list(self.paid_users),
                    "payments": self.payments,
                    "payment_counter": self.payment_counter,
                    "user_chats": self.user_chats
                }, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"❌ Ошибка сохранения БД: {e}")
            return False
    
    def add_user(self, user_id, username, first_name):
        """Запомнить пользователя"""
        self.user_chats[str(user_id)] = {
            "username": username,
            "first_name": first_name,
            "last_seen": datetime.now().isoformat()
        }
        self.save()
    
    def create_payment(self, user_id, username, first_name, photo_path):
        """Создать запись о платеже"""
        self.payment_counter += 1
        payment_id = f"PAY-{self.payment_counter:06d}"
        
        self.payments[payment_id] = {
            "user_id": user_id,
            "username": username,
            "first_name": first_name,
            "photo": photo_path,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "processed_at": None,
            "reject_reason": None
        }
        self.save()
        return payment_id
    
    def approve_payment(self, payment_id):
        """Подтвердить платеж"""
        if payment_id in self.payments:
            self.payments[payment_id]["status"] = "approved"
            self.payments[payment_id]["processed_at"] = datetime.now().isoformat()
            user_id = self.payments[payment_id]["user_id"]
            self.paid_users.add(user_id)
            self.save()
            return True
        return False
    
    def reject_payment(self, payment_id, reason):
        """Отклонить платеж с причиной"""
        if payment_id in self.payments:
            self.payments[payment_id]["status"] = "rejected"
            self.payments[payment_id]["processed_at"] = datetime.now().isoformat()
            self.payments[payment_id]["reject_reason"] = reason
            self.save()
            return True
        return False
    
    def get_pending_payments(self):
        """Получить все ожидающие платежи"""
        return {k: v for k, v in self.payments.items() if v["status"] == "pending"}
    
    def is_paid(self, user_id):
        """Проверил, покупал ли пользователь"""
        return user_id in self.paid_users
    
    def get_stats(self):
        """Получить статистику"""
        pending = len([p for p in self.payments.values() if p["status"] == "pending"])
        approved = len([p for p in self.payments.values() if p["status"] == "approved"])
        rejected = len([p for p in self.payments.values() if p["status"] == "rejected"])
        
        return {
            "users": len(self.user_chats),
            "sales": len(self.paid_users),
            "revenue": len(self.paid_users) * 50,
            "pending": pending,
            "approved": approved,
            "rejected": rejected,
            "total_payments": len(self.payments)
        }

# Создаем глобальный экземпляр базы данных
db = Database()