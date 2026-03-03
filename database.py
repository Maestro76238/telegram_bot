import sqlite3
import datetime
import os

# Простое локальное хранилище — в той же папке, где лежит бот
DB_NAME = 'salon.db'

def init_db():
    """Создаёт таблицы, если их нет"""
    db_exists = os.path.exists(DB_NAME)
    
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
    
    if not db_exists:
        print(f"✅ Новая база данных создана: {DB_NAME}")
    else:
        print(f"✅ База данных подключена: {DB_NAME}")

def add_user(user_id, username, full_name):
    """Добавляет нового пользователя или игнорирует, если уже есть"""
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute('''
        INSERT OR IGNORE INTO users (user_id, username, full_name, registered_at)
        VALUES (?, ?, ?, ?)
    ''', (user_id, username, full_name, datetime.datetime.now().isoformat()))
    conn.commit()
    conn.close()
    print(f"👤 Пользователь добавлен: @{username}")

def save_booking(user_id, service, date, time):
    """Сохраняет запись в БД и возвращает её ID"""
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO bookings (user_id, service, date, time, created_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, service, date, time, datetime.datetime.now().isoformat()))
    conn.commit()
    booking_id = cur.lastrowid
    conn.close()
    print(f"📅 Запись #{booking_id} сохранена")
    return booking_id

def get_user_phone(user_id):
    """Возвращает телефон пользователя или None"""
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute('SELECT phone FROM users WHERE user_id=?', (user_id,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None

def update_user_phone(user_id, phone):
    """Обновляет телефон пользователя"""
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute('UPDATE users SET phone=? WHERE user_id=?', (phone, user_id))
    conn.commit()
    conn.close()
    print(f"📞 Телефон пользователя {user_id} обновлён")

def get_all_bookings():
    """Для админа: все записи с данными клиентов (включая user_id)"""
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
    return rows

def get_all_users():
    """Возвращает список всех user_id"""
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute('SELECT user_id FROM users')
    rows = cur.fetchall()
    conn.close()
    user_ids = [row[0] for row in rows]
    print(f"👥 Загружено пользователей: {len(user_ids)}")
    return user_ids

def get_stats():
    """Возвращает статистику по записям и пользователям"""
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
    
    return {
        'total_users': total_users,
        'total_bookings': total_bookings,
        'pending_bookings': pending,
        'confirmed_bookings': confirmed,
        'cancelled_bookings': cancelled
    }

def update_booking_status(booking_id, status):
    """Обновляет статус записи (pending/confirmed/cancelled)"""
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute('UPDATE bookings SET status=? WHERE id=?', (status, booking_id))
    conn.commit()
    conn.close()
    print(f"✏️ Статус записи #{booking_id} изменён на {status}")

def delete_booking(booking_id):
    """Удаляет запись из базы данных"""
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute('DELETE FROM bookings WHERE id=?', (booking_id,))
    conn.commit()
    conn.close()
    print(f"🗑 Запись #{booking_id} удалена")