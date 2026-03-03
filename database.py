import sqlite3
import datetime
import os
import sys

print("=" * 50)
print("🔍 ДИАГНОСТИКА БАЗЫ ДАННЫХ")
print("=" * 50)

# Текущая директория
current_dir = os.getcwd()
print(f"📁 Текущая директория: {current_dir}")

# Содержимое текущей директории
try:
    files = os.listdir(current_dir)
    print(f"📄 Файлы в директории: {files}")
except Exception as e:
    print(f"❌ Ошибка чтения директории: {e}")

# Права на запись
print(f"🔐 Права на запись в текущую директорию: {'✅' if os.access(current_dir, os.W_OK) else '❌'}")

# Пробуем создать тестовый файл
try:
    test_file = os.path.join(current_dir, 'test_write.txt')
    with open(test_file, 'w') as f:
        f.write('test')
    os.remove(test_file)
    print("✅ Тестовая запись успешна")
except Exception as e:
    print(f"❌ Тестовая запись не удалась: {e}")

# Используем绝对路径 для надёжности
DB_PATH = current_dir
DB_NAME = os.path.join(DB_PATH, 'salon.db')

print(f"📁 База данных будет создана: {DB_NAME}")
print("=" * 50)

def init_db():
    """Создаёт таблицы, если их нет"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        
        # Таблица пользователей
        cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                phone TEXT,
                registered_at TEXT
            )
        ''')
        
        # Таблица записей
        cur.execute('''
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                service TEXT,
                date TEXT,
                time TEXT,
                status TEXT DEFAULT 'pending',
                created_at TEXT,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )
        ''')
        
        conn.commit()
        conn.close()
        
        print(f"✅ База данных успешно создана/подключена: {DB_NAME}")
        
        # Проверяем, создался ли файл
        if os.path.exists(DB_NAME):
            size = os.path.getsize(DB_NAME)
            print(f"✅ Файл базы создан, размер: {size} байт")
        else:
            print(f"❌ Файл базы НЕ создан!")
            
    except Exception as e:
        print(f"❌ Критическая ошибка при создании БД: {e}")
        # Пробуем создать в /tmp как запасной вариант
        try:
            tmp_db = '/tmp/salon.db'
            print(f"🔄 Пробуем создать БД в /tmp: {tmp_db}")
            conn = sqlite3.connect(tmp_db)
            cur = conn.cursor()
            cur.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)')
            conn.commit()
            conn.close()
            print(f"✅ БД в /tmp создана успешно")
            global DB_NAME
            DB_NAME = tmp_db
        except Exception as e2:
            print(f"❌ И /tmp не сработал: {e2}")

def add_user(user_id, username, full_name):
    """Добавляет нового пользователя или игнорирует, если уже есть"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute('''
            INSERT OR IGNORE INTO users (user_id, username, full_name, registered_at)
            VALUES (?, ?, ?, ?)
        ''', (user_id, username, full_name, datetime.datetime.now().isoformat()))
        conn.commit()
        conn.close()
        print(f"👤 Пользователь добавлен: @{username} ({user_id})")
        return True
    except Exception as e:
        print(f"❌ Ошибка добавления пользователя: {e}")
        return False

def save_booking(user_id, service, date, time):
    """Сохраняет запись в БД и возвращает её ID"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO bookings (user_id, service, date, time, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, service, date, time, datetime.datetime.now().isoformat()))
        conn.commit()
        booking_id = cur.lastrowid
        conn.close()
        print(f"📅 Запись #{booking_id} сохранена (user:{user_id}, {service}, {date} {time})")
        return booking_id
    except Exception as e:
        print(f"❌ Ошибка сохранения записи: {e}")
        return None

def get_user_phone(user_id):
    """Возвращает телефон пользователя или None"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute('SELECT phone FROM users WHERE user_id=?', (user_id,))
        row = cur.fetchone()
        conn.close()
        return row[0] if row else None
    except Exception as e:
        print(f"❌ Ошибка получения телефона: {e}")
        return None

def update_user_phone(user_id, phone):
    """Обновляет телефон пользователя"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute('UPDATE users SET phone=? WHERE user_id=?', (phone, user_id))
        conn.commit()
        conn.close()
        print(f"📞 Телефон пользователя {user_id} обновлён: {phone}")
        return True
    except Exception as e:
        print(f"❌ Ошибка обновления телефона: {e}")
        return False

def get_all_bookings():
    """Для админа: все записи с данными клиентов (включая user_id)"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute('''
            SELECT bookings.id, users.full_name, users.phone, bookings.service, 
                   bookings.date, bookings.time, bookings.status, users.user_id
            FROM bookings
            JOIN users ON bookings.user_id = users.user_id
            ORDER BY bookings.created_at DESC
        ''')
        rows = cur.fetchall()
        conn.close()
        print(f"📋 Загружено записей: {len(rows)}")
        
        # Детальный вывод первых 3 записей
        for i, row in enumerate(rows[:3]):
            print(f"   Запись {i+1}: ID={row[0]}, Клиент={row[1]}, Услуга={row[3]}, Дата={row[4]}")
            
        return rows
    except Exception as e:
        print(f"❌ Ошибка получения записей: {e}")
        return []

def get_all_users():
    """Возвращает список всех user_id"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute('SELECT user_id FROM users')
        rows = cur.fetchall()
        conn.close()
        user_ids = [row[0] for row in rows]
        print(f"👥 Загружено пользователей: {len(user_ids)}")
        return user_ids
    except Exception as e:
        print(f"❌ Ошибка получения пользователей: {e}")
        return []

def get_stats():
    """Возвращает статистику по записям и пользователям"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        
        cur.execute('SELECT COUNT(*) FROM users')
        total_users = cur.fetchone()[0]
        
        cur.execute('SELECT COUNT(*) FROM bookings')
        total_bookings = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM bookings WHERE status='pending'")
        pending = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM bookings WHERE status='confirmed'")
        confirmed = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM bookings WHERE status='cancelled'")
        cancelled = cur.fetchone()[0]
        
        conn.close()
        
        stats = {
            'total_users': total_users,
            'total_bookings': total_bookings,
            'pending_bookings': pending,
            'confirmed_bookings': confirmed,
            'cancelled_bookings': cancelled
        }
        
        print(f"📊 Статистика: пользователей={total_users}, записей={total_bookings}")
        return stats
    except Exception as e:
        print(f"❌ Ошибка получения статистики: {e}")
        return {
            'total_users': 0,
            'total_bookings': 0,
            'pending_bookings': 0,
            'confirmed_bookings': 0,
            'cancelled_bookings': 0
        }

def update_booking_status(booking_id, status):
    """Обновляет статус записи (pending/confirmed/cancelled)"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute('UPDATE bookings SET status=? WHERE id=?', (status, booking_id))
        conn.commit()
        conn.close()
        print(f"✏️ Статус записи #{booking_id} изменён на {status}")
        return True
    except Exception as e:
        print(f"❌ Ошибка обновления статуса: {e}")
        return False

def delete_booking(booking_id):
    """Удаляет запись из базы данных"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute('DELETE FROM bookings WHERE id=?', (booking_id,))
        conn.commit()
        conn.close()
        print(f"🗑 Запись #{booking_id} удалена")
        return True
    except Exception as e:
        print(f"❌ Ошибка удаления записи: {e}")
        return False