import os
import sys

print("🔧 Loading configuration...")

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

print(f"BOT_TOKEN exists: {'yes' if BOT_TOKEN else 'no'}")
print(f"ADMIN_ID exists: {'yes' if ADMIN_ID else 'no'}")

if not BOT_TOKEN:
    print("❌ CRITICAL: BOT_TOKEN is missing!")
    sys.exit(1)

if not ADMIN_ID:
    print("❌ CRITICAL: ADMIN_ID is missing!")
    sys.exit(1)

try:
    ADMIN_ID = int(ADMIN_ID)
    print(f"✅ Admin ID: {ADMIN_ID}")
except ValueError:
    print(f"❌ ADMIN_ID must be a number, got: {ADMIN_ID}")
    sys.exit(1)

print("✅ Configuration loaded successfully")