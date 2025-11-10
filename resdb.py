import sqlite3
import os

def reset_database():
    db_file = 'university_bot.db'
    
    if os.path.exists(db_file):
        # Dosyayı tamamen sil
        os.remove(db_file)
        print(f"🗑️ {db_file} silindi!")
    else:
        print("⚠️ Veritabanı dosyası bulunamadı")
    
    print("✅ Veritabanı sıfırlandı - bot yeniden oluşturacak")

if __name__ == "__main__":
    reset_database()