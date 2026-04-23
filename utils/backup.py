# utils/backup.py
import shutil
import os
from datetime import datetime

async def backup_database():
    """Создание резервной копии базы данных"""
    try:
        db_path = os.getenv('DATABASE_PATH', 'db.sqlite3')
        if os.path.exists(db_path):
            backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sqlite3"
            shutil.copy(db_path, f"backups/{backup_name}")
            print(f"✅ Бэкап создан: {backup_name}")
            
            # Удаляем старые бэкапы (оставляем 5 последних)
            backups = sorted([f for f in os.listdir('backups') if f.startswith('backup_')])
            for old_backup in backups[:-5]:
                os.remove(f"backups/{old_backup}")
    except Exception as e:
        print(f"❌ Ошибка бэкапа: {e}")

# Создайте папку для бэкапов
os.makedirs('backups', exist_ok=True)