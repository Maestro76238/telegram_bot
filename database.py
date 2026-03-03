import sqlite3
import datetime
import os

# Для Railway используем папку /data, которая примонтирована как Volume
# Если её нет, используем текущую папку (для локального теста)
DB_PATH = os.getenv('RAILWAY_VOLUME_PATH', '/data')
if not os.path.exists(DB_PATH):
    DB_PATH = '.'

DB_NAME = os.path.join(DB_PATH, 'salon.db')

def init_db():
    db_exists = os.path.exists(DB_NAME)
    
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            full_name TEXT,
            phone TEXT,
            registered_at TEXT
        )
    ''')
    
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
        print(f"✅ База данных создана: {DB_NAME}")
    else:
        print(f"✅ База данных подключена: {DB_NAME}")

def add_user(user_id, username, full_name):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute('''
        INSERT OR IGNORE INTO users (user_id, username, full_name, registered_at)
        VALUES (?, ?, ?, ?)
    ''', (user_id, username, full_name, datetime.datetime.now().isoformat()))
    conn.commit()
    conn.close()

def save_booking(user_id, service, date, time):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO bookings (user_id, service, date, time, created_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, service, date, time, datetime.datetime.now().isoformat()))
    conn.commit()
    booking_id = cur.lastrowid
    conn.close()
    return booking_id

def get_user_phone(user_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute('SELECT phone FROM users WHERE user_id=?', (user_id,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None

def update_user_phone(user_id, phone):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute('UPDATE users SET phone=? WHERE user_id=?', (phone, user_id))
    conn.commit()
    conn.close()

def get_all_bookings():
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
    return rows

def get_all_users():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute('SELECT user_id FROM users')
    rows = cur.fetchall()
    conn.close()
    return [row[0] for row in rows]

def get_stats():
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
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute('UPDATE bookings SET status=? WHERE id=?', (status, booking_id))
    conn.commit()
    conn.close()

def delete_booking(booking_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute('DELETE FROM bookings WHERE id=?', (booking_id,))
    conn.commit()
    conn.close()