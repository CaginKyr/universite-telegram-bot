import sqlite3
import sys

def make_user_admin(username):
    """
    Kullanıcı adına göre kullanıcıyı admin yapar
    
    Args:
        username (str): Admin yapılacak kullanıcının Telegram kullanıcı adı
    """
    
    # Veritabanına bağlan
    conn = sqlite3.connect('university_bot.db')
    cursor = conn.cursor()
    
    try:
        # Kullanıcıyı bul
        cursor.execute('SELECT user_id, full_name FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        
        if not user:
            print(f"❌ Kullanıcı '{username}' bulunamadı!")
            return False
        
        user_id, full_name = user
        
        # Kullanıcının zaten admin olup olmadığını kontrol et
        cursor.execute('SELECT role FROM users WHERE user_id = ?', (user_id,))
        current_role = cursor.fetchone()[0]
        
        if current_role == 'admin':
            print(f"✅ Kullanıcı '{username}' zaten admin!")
            return True
        
        # Kullanıcıyı admin yap
        cursor.execute('UPDATE users SET role = ? WHERE user_id = ?', ('admin', user_id))
        
        # User roles tablosuna da ekle
        cursor.execute('''
            INSERT OR REPLACE INTO user_roles (user_id, role_name, permissions, assigned_by, assigned_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, 'admin', 
              '["view_resources", "ask_questions", "join_events", "manage_questions", "view_stats", "create_announcements", "create_polls", "create_events", "manage_users"]',
              user_id, '2024-01-01T00:00:00'))
        
        conn.commit()
        
        print(f"✅ Kullanıcı '{username}' ({full_name}) başarıyla admin yapıldı!")
        print(f"👤 User ID: {user_id}")
        print(f"🎯 Yeni Rol: Admin")
        
        return True
        
    except Exception as e:
        print(f"❌ Hata oluştu: {e}")
        conn.rollback()
        return False
    
    finally:
        conn.close()

def list_admins():
    """Tüm adminleri listeler"""
    conn = sqlite3.connect('university_bot.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT u.username, u.full_name, u.user_id, u.role 
            FROM users u 
            WHERE u.role = 'admin' OR u.user_id IN (
                SELECT user_id FROM user_roles WHERE role_name = 'admin'
            )
        ''')
        
        admins = cursor.fetchall()
        
        if not admins:
            print("❌ Hiç admin bulunamadı!")
            return
        
        print("👑 MEVCUT ADMİNLER:")
        print("-" * 50)
        for admin in admins:
            username, full_name, user_id, role = admin
            print(f"👤 @{username} ({full_name})")
            print(f"   ID: {user_id}")
            print(f"   Rol: {role}")
            print()
            
    except Exception as e:
        print(f"❌ Hata oluştu: {e}")
    
    finally:
        conn.close()

def remove_admin(username):
    """Kullanıcının admin yetkisini kaldırır"""
    conn = sqlite3.connect('university_bot.db')
    cursor = conn.cursor()
    
    try:
        # Kullanıcıyı bul
        cursor.execute('SELECT user_id, full_name FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        
        if not user:
            print(f"❌ Kullanıcı '{username}' bulunamadı!")
            return False
        
        user_id, full_name = user
        
        # Admin yetkisini kaldır
        cursor.execute('UPDATE users SET role = ? WHERE user_id = ?', ('student', user_id))
        cursor.execute('DELETE FROM user_roles WHERE user_id = ? AND role_name = ?', (user_id, 'admin'))
        
        conn.commit()
        
        print(f"✅ Kullanıcı '{username}' ({full_name}) admin yetkisi kaldırıldı!")
        print(f"👤 User ID: {user_id}")
        print(f"🎯 Yeni Rol: Student")
        
        return True
        
    except Exception as e:
        print(f"❌ Hata oluştu: {e}")
        conn.rollback()
        return False
    
    finally:
        conn.close()

if __name__ == "__main__":
    print("🤖 Telegram Bot Admin Yönetim Aracı")
    print("=" * 40)
    
    if len(sys.argv) < 2:
        print("Kullanım:")
        print("  python admin_yap.py <kullanici_adi>     - Kullanıcıyı admin yap")
        print("  python admin_yap.py list                - Adminleri listele")
        print("  python admin_yap.py remove <kullanici_adi> - Admin yetkisini kaldır")
        print()
        print("Örnek:")
        print("  python admin_yap.py john_doe")
        print("  python admin_yap.py list")
        print("  python admin_yap.py remove john_doe")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "list":
        list_admins()
    elif command == "remove":
        if len(sys.argv) < 3:
            print("❌ Kullanıcı adı belirtin!")
            print("Kullanım: python admin_yap.py remove <kullanici_adi>")
            sys.exit(1)
        username = sys.argv[2]
        remove_admin(username)
    else:
        # Admin yapma komutu
        username = sys.argv[1]
        if not username.startswith('@'):
            username = username  # @ işareti yoksa ekleme
        
        make_user_admin(username)
