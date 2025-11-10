import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Poll
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    PollAnswerHandler,
    ContextTypes,
    filters,
    ConversationHandler
)
from datetime import datetime, timedelta
import sqlite3
import re
import hashlib
import random
import string

#Loglamake
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

#Cevaplama
(WAITING_NAME, WAITING_STUDENT_NO, WAITING_DEPARTMENT, 
 WAITING_CLASS, WAITING_EMAIL, WAITING_VERIFICATION,
 WAITING_ANNOUNCEMENT, WAITING_POLL_QUESTION, WAITING_POLL_OPTIONS,
 WAITING_RESOURCE_TITLE, WAITING_RESOURCE_FILE,
 WAITING_QUESTION, WAITING_ANSWER,
 WAITING_EVENT_TITLE, WAITING_EVENT_DESC, WAITING_EVENT_DATE) = range(16)

#bölümler
UNIVERSITY_DEPARTMENTS = {
    'muhendislik': {
        'name': '🏗️ Mühendislik Fakültesi',
        'departments': [
            'Bilgisayar Mühendisliği',
            'Elektrik-Elektronik Mühendisliği', 
            'Makine Mühendisliği',
            'İnşaat Mühendisliği',
            'Endüstri Mühendisliği',
            'Kimya Mühendisliği',
            'Gıda Mühendisliği',
            'Çevre Mühendisliği',
            'Maden Mühendisliği',
            'Petrol ve Doğalgaz Mühendisliği'
        ]
    },
    'fen': {
        'name': '🔬 Fen Fakültesi',
        'departments': [
            'Matematik',
            'Fizik',
            'Kimya',
            'Biyoloji',
            'İstatistik',
            'Moleküler Biyoloji ve Genetik'
        ]
    },
    'saglik': {
        'name': '🏥 Sağlık Bilimleri Fakültesi',
        'departments': [
            'Tıp',
            'Diş Hekimliği',
            'Eczacılık',
            'Hemşirelik',
            'Fizyoterapi ve Rehabilitasyon',
            'Beslenme ve Diyetetik'
        ]
    },
    'sosyal': {
        'name': '📚 Sosyal Bilimler Fakültesi',
        'departments': [
            'Psikoloji',
            'Sosyoloji',
            'Tarih',
            'Coğrafya',
            'Felsefe',
            'Arkeoloji'
        ]
    },
    'ekonomi': {
        'name': '💰 İktisadi ve İdari Bilimler Fakültesi',
        'departments': [
            'İktisat',
            'İşletme',
            'Siyaset Bilimi ve Kamu Yönetimi',
            'Uluslararası İlişkiler',
            'Maliye',
            'Çalışma Ekonomisi ve Endüstri İlişkileri'
        ]
    },
    'egitim': {
        'name': '🎓 Eğitim Fakültesi',
        'departments': [
            'Sınıf Öğretmenliği',
            'Matematik Öğretmenliği',
            'Fen Bilgisi Öğretmenliği',
            'Türkçe Öğretmenliği',
            'İngilizce Öğretmenliği',
            'Rehberlik ve Psikolojik Danışmanlık'
        ]
    },
    'hukuk': {
        'name': '⚖️ Hukuk Fakültesi',
        'departments': [
            'Hukuk'
        ]
    },
    'iletisim': {
        'name': '📺 İletişim Fakültesi',
        'departments': [
            'Gazetecilik',
            'Radyo, Televizyon ve Sinema',
            'Halkla İlişkiler ve Tanıtım',
            'Reklamcılık'
        ]
    },      
    'myo': {
        'name': '🏢 Meslek Yüksekokulları',
        'departments': [
            'Tele-Sağlık Teknikerliği',
            'Ameliyathane Hizmetleri',
            'Tıbbi Veri İşleme Teknikerliği',
            'Fizyoterapi',
            'Ormancılık ve Orman Ürünleri',
            'Ortopedik Protez ve Ortez',
            'Optisyenlik',
            'Eczane Hizmetleri',
            'Bilgisayar Programcılığı',
            'Yapay Zeka Operatörlüğü',
            'Hibrid ve Elektrikli Taşıtlar Teknolojisi',
            'Sivil Savunma ve İtfaiyecilik',
            'Otonom Sistemler Teknikerliği',
            'Otomotiv Teknolojisi',
            'Mekatronik',
            'Bulut Bilişim Operatörlüğü',
            'Makine',
            'Kontrol ve Otomasyon Teknolojisi',
            'Elektrik',
            'Web Tasarımı ve Kodlama',
            'İnşaat Teknolojisi',
            'Bankacılık ve Sigortacılık',
            'Bilişim Güvenliği Teknolojisi',
            'Bilgisayar Destekli Tasarım ve Animasyon',
            'Yenilenebilir Enerji Teknikerliği',
            'Elektrik Enerjisi Üretim, İletim ve Dağıtımı',
            'Dijital Dönüşüm Elektroniği',
            'Akıllı Altyapılar Teknikerliği',
            'İnternet ve Ağ Teknolojileri',
            'Elektrikli Cihaz Teknolojisi',
            'Basım ve Yayım Teknolojileri',
            'Sanal ve Artırılmış Gerçeklik',
            'Süt ve Ürünleri Teknolojisi',
            'Akıllı Sera Teknolojileri',


        ]
    },    
}

#db
class Database:
    def __init__(self, db_name='university_bot.db'):
        self.db_name = db_name
        self.init_db()
    
    def get_connection(self):
        return sqlite3.connect(self.db_name)
    
    def init_db(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Kullanıcılar tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                student_no TEXT UNIQUE,
                department TEXT,
                class_year TEXT,
                email TEXT,
                verification_code TEXT,
                is_verified INTEGER DEFAULT 0,
                role TEXT DEFAULT 'student',
                join_date TEXT,
                is_banned INTEGER DEFAULT 0,
                warning_count INTEGER DEFAULT 0
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS announcements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                content TEXT,
                category TEXT,
                created_by INTEGER,
                created_at TEXT,
                message_id INTEGER
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS polls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                poll_id TEXT UNIQUE,
                question TEXT,
                created_by INTEGER,
                created_at TEXT,
                is_active INTEGER DEFAULT 1
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS resources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                description TEXT,
                file_id TEXT,
                file_type TEXT,
                department TEXT,
                uploaded_by INTEGER,
                uploaded_at TEXT,
                download_count INTEGER DEFAULT 0
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT,
                asked_by INTEGER,
                asked_at TEXT,
                answer TEXT,
                answered_by INTEGER,
                answered_at TEXT,
                is_answered INTEGER DEFAULT 0,
                category TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                description TEXT,
                event_date TEXT,
                created_by INTEGER,
                created_at TEXT,
                is_active INTEGER DEFAULT 1
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS event_participants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER,
                user_id INTEGER,
                joined_at TEXT,
                FOREIGN KEY (event_id) REFERENCES events (id),
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS spam_tracker (
                user_id INTEGER,
                message_time TEXT,
                PRIMARY KEY (user_id, message_time)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_roles (
                user_id INTEGER PRIMARY KEY,
                role_name TEXT DEFAULT 'student',
                permissions TEXT,
                assigned_by INTEGER,
                assigned_at TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_user(self, user_id, username, full_name, student_no, department, class_year, email):
        conn = self.get_connection()
        cursor = conn.cursor()
        verification_code = ''.join(random.choices(string.digits, k=6))
        
        try:
            cursor.execute('''
                INSERT INTO users (user_id, username, full_name, student_no, department, 
                                 class_year, email, verification_code, join_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, username, full_name, student_no, department, class_year, 
                  email, verification_code, datetime.now().isoformat()))
            conn.commit()
            conn.close()
            return verification_code
        except sqlite3.IntegrityError:
            conn.close()
            return None
    
    def verify_user(self, user_id, code):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT verification_code FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        
        if result and result[0] == code:
            cursor.execute('UPDATE users SET is_verified = 1 WHERE user_id = ?', (user_id,))
            conn.commit()
            conn.close()
            return True
        conn.close()
        return False
    
    def get_user(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result
    
    def is_verified(self, user_id):
        user = self.get_user(user_id)
        return user and user[8] == 1
    
    def is_admin(self, user_id):
        user = self.get_user(user_id)
        return user and user[9] in ['admin', 'moderator']
    
    def get_pending_users(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT user_id, username, full_name, student_no, department, class_year 
            FROM users WHERE is_verified = 0
        ''')
        results = cursor.fetchall()
        conn.close()
        return results
    
    def assign_role(self, user_id, role_name, assigned_by):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        #izinler
        permissions = {
            'student': ['view_resources', 'ask_questions', 'join_events'],
            'moderator': ['view_resources', 'ask_questions', 'join_events', 'manage_questions', 'view_stats'],
            'admin': ['view_resources', 'ask_questions', 'join_events', 'manage_questions', 'view_stats', 'create_announcements', 'create_polls', 'create_events', 'manage_users']
        }
        
        import json
        permissions_json = json.dumps(permissions.get(role_name, permissions['student']))
        
        cursor.execute('''
            INSERT OR REPLACE INTO user_roles (user_id, role_name, permissions, assigned_by, assigned_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, role_name, permissions_json, assigned_by, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def get_user_role(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT role_name FROM user_roles WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else 'student'
    
    def has_permission(self, user_id, permission):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT permissions FROM user_roles WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return False
        
        import json
        permissions = json.loads(result[0])
        return permission in permissions

#bot
class UniversityBot:
    def __init__(self, token, channel_id, group_id):
        self.db = Database()
        self.token = token
        self.channel_id = channel_id
        self.group_id = group_id
        self.user_data = {}
        self.bad_words = ['küfür1', 'küfür2']
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        
        if self.db.is_verified(user.id):
            keyboard = [
                [InlineKeyboardButton("📋 Profilim", callback_data='profile'),
                 InlineKeyboardButton("❓ Yardım", callback_data='help')],
                [InlineKeyboardButton("📚 Kaynaklar", callback_data='resources'),
                 InlineKeyboardButton("❓ Sorular", callback_data='questions')],
                [InlineKeyboardButton("🎉 Etkinlikler", callback_data='events'),
                 InlineKeyboardButton("📊 İstatistikler", callback_data='stats')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                f"🎓 <b>Hoş geldin {user.first_name}!</b>\n\n"
                f"Üniversite Telegram Bot'a hoş geldin!\n"
                f"Ana menüden istediğin işlemi seçebilirsin.\n\n"
                f"💡 <b>Hızlı Komutlar:</b>\n"
                f"• /profil - Profilini görüntüle\n"
                f"• /kaynaklar - Kaynakları listele\n"
                f"• /sorular - Soruları görüntüle\n"
                f"• /etkinlikler - Etkinlikleri listele\n"
                f"• /yardim - Yardım menüsü",
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
        else:
            keyboard = [[InlineKeyboardButton("✅ Kayıt Ol", callback_data='register')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                f"👋 <b>Merhaba {user.first_name}!</b>\n\n"
                f"🎓 Üniversite Telegram Bot'a hoş geldin!\n\n"
                f"Bu bot ile:\n"
                f"• 📚 Ders kaynaklarını paylaşabilirsin\n"
                f"• ❓ Sorular sorabilirsin\n"
                f"• 🎉 Etkinliklere katılabilirsin\n"
                f"• 📢 Duyuruları takip edebilirsin\n\n"
                f"Gruba katılmak için önce kayıt olman gerekiyor!",
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
        return ConversationHandler.END
    
    async def register_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        #kanala katılmış mı check
        user_id = query.from_user.id
        is_channel_member = False
        is_group_member = False
        
        try:
            #kanala katılmış mı check
            if self.channel_id:
                channel_member = await context.bot.get_chat_member(self.channel_id, user_id)
                is_channel_member = channel_member.status in ['member', 'administrator', 'creator']
        except Exception as e:
            print(f"Error checking channel membership: {e}")
            is_channel_member = False
        
        try:
            #kanala katılmış mı check
            if self.group_id:
                group_member = await context.bot.get_chat_member(self.group_id, user_id)
                is_group_member = group_member.status in ['member', 'administrator', 'creator']
        except Exception as e:
            print(f"Error checking group membership: {e}")
            is_group_member = False
        
        if not is_channel_member:  # Sadece kanal kontrolü yap
            missing_channels = []
            if not is_channel_member:
                missing_channels.append(f"📢 Duyuru Kanalı: {self.channel_id}")
            if not is_group_member:
                missing_channels.append(f"💬 Sohbet Grubu: {self.group_id}")
            
            keyboard = [
                [InlineKeyboardButton("📢 Duyuru Kanalına Katıl", url=f"https://t.me/{self.channel_id.replace('@', '')}")],
                [InlineKeyboardButton("💬 Sohbet Grubuna Katıl", url=f"https://t.me/{self.group_id.replace('@', '')}")],
                [InlineKeyboardButton("✅ Kontrol Et", callback_data='register')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            try:
                await query.edit_message_text(
                    f"❌ <b>Kayıt İçin Gerekli Kanallara Katılın!</b>\n\n"
                    f"Botu kullanabilmek için aşağıdaki kanallara katılmanız gerekiyor:\n\n"
                    f"{chr(10).join(missing_channels)}\n\n"
                    f"Kanallara katıldıktan sonra 'Kontrol Et' butonuna tıklayın.",
                    reply_markup=reply_markup,
                    parse_mode='HTML',
                )
            except Exception as e:
                # Eğer mesaj aynıysa, yeni bir mesaj gönder
                if "Message is not modified" in str(e):
                    await query.message.reply_text(
                        f"❌ <b>Kayıt İçin Gerekli Kanallara Katılın!</b>\n\n"
                        f"Botu kullanabilmek için aşağıdaki kanallara katılmanız gerekiyor:\n\n"
                        f"{chr(10).join(missing_channels)}\n\n"
                        f"Kanallara katıldıktan sonra 'Kontrol Et' butonuna tıklayın.",
                        reply_markup=reply_markup,
                        parse_mode='HTML',
                    )
                else:
                    raise e
            return ConversationHandler.END
        
        self.user_data[user_id] = {}
        try:
            await query.edit_message_text("✅ Kanallara üye olduğunuz doğrulandı!\n\n📝 Kayıt İşlemi Başlatıldı\n\nLütfen tam adını ve soyadını yaz:\nÖrnek: Ahmet Yılmaz")
        except Exception as e:
            # Eğer mesaj aynıysa, yeni bir mesaj gönder
            if "Message is not modified" in str(e):
                await query.message.reply_text("✅ Kanallara üye olduğunuz doğrulandı!\n\n📝 Kayıt İşlemi Başlatıldı\n\nLütfen tam adını ve soyadını yaz:\nÖrnek: Ahmet Yılmaz")
            else:
                raise e
        return WAITING_NAME
    
    async def get_name(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        self.user_data[user_id]['full_name'] = update.message.text
        await update.message.reply_text("✅ Teşekkürler!\n\nŞimdi öğrenci numaranı yaz:\nÖrnek: 2021010101")
        return WAITING_STUDENT_NO
    
    async def get_student_no(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        student_no = update.message.text
        
        if not re.match(r'^\d{10}$', student_no):
            await update.message.reply_text("❌ Geçersiz öğrenci numarası!\nLütfen 10 haneli öğrenci numaranı gir:")
            return WAITING_STUDENT_NO
        
        self.user_data[user_id]['student_no'] = student_no
        
        # Fakülte seçim 
        keyboard = []
        for faculty_key, faculty_data in UNIVERSITY_DEPARTMENTS.items():
            keyboard.append([InlineKeyboardButton(faculty_data['name'], callback_data=f'faculty_{faculty_key}')])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("✅ Harika!\n\nFakülteni seç:", reply_markup=reply_markup)
        return WAITING_DEPARTMENT
    
    
    
    async def show_department_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        user_id = query.from_user.id
        faculty_key = query.data.split('_')[1]
        
        if faculty_key not in UNIVERSITY_DEPARTMENTS:
            await query.edit_message_text("❌ Geçersiz fakülte seçimi!")
            return WAITING_DEPARTMENT
        
        faculty_data = UNIVERSITY_DEPARTMENTS[faculty_key]
        self.user_data[user_id]['faculty'] = faculty_data['name']
        
        # Bölüm seçim 
        keyboard = []
        for dept in faculty_data['departments']:
            keyboard.append([InlineKeyboardButton(dept, callback_data=f'dept_{dept}')])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(f"✅ {faculty_data['name']} seçildi!\n\nBölümünü seç:", reply_markup=reply_markup)
        return WAITING_DEPARTMENT
    
    async def select_department(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        user_id = query.from_user.id
        department = query.data.replace('dept_', '')
        
        self.user_data[user_id]['department'] = department
        
        keyboard = [          
            [InlineKeyboardButton("1. Sınıf", callback_data='class_1')],
            [InlineKeyboardButton("2. Sınıf", callback_data='class_2')],
            [InlineKeyboardButton("3. Sınıf", callback_data='class_3')],
            [InlineKeyboardButton("4. Sınıf", callback_data='class_4')],
            [InlineKeyboardButton("Yüksek Lisans", callback_data='class_master')],
            [InlineKeyboardButton("Doktora", callback_data='class_phd')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(f"✅ {department} seçildi!\n\nSınıfını seç:", reply_markup=reply_markup)
        return WAITING_CLASS
    
    async def get_class(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        user_id = query.from_user.id
        class_map = {'class_1': '1', 'class_2': '2', 'class_3': '3', 'class_4': '4', 'class_master': 'Yüksek Lisans', 'class_phd': 'Doktora'}
        self.user_data[user_id]['class_year'] = class_map[query.data]
        await query.edit_message_text("✅ Mükemmel!\n\nSon olarak üniversite e-posta adresini yaz:\nÖrnek: ahmet.yilmaz@universite.edu.tr")
        return WAITING_EMAIL
    
    async def get_email(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        email = update.message.text
        
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            await update.message.reply_text("❌ Geçersiz e-posta adresi!\nLütfen geçerli bir e-posta adresi gir:")
            return WAITING_EMAIL
        
        self.user_data[user_id]['email'] = email
        verification_code = self.db.add_user(
            user_id, update.effective_user.username, self.user_data[user_id]['full_name'],
            self.user_data[user_id]['student_no'], self.user_data[user_id]['department'],
            self.user_data[user_id]['class_year'], email
        )
        
        if verification_code:
            await update.message.reply_text(
                f"✅ Kayıt başarıyla oluşturuldu!\n\n📧 E-posta adresine gönderilen 6 haneli doğrulama kodunu gir:\n\n(Simülasyon için kod: {verification_code})\n\nNot: Gerçek uygulamada e-posta gönderilecek."
            )
            return WAITING_VERIFICATION
        else:
            await update.message.reply_text("❌ Bu öğrenci numarası zaten kayıtlı!\nYardım için /yardim komutunu kullan.")
            return ConversationHandler.END
    
    async def verify_code(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        code = update.message.text
        
        if self.db.verify_user(user_id, code):
            # Otomatik rol atama
            self.db.assign_role(user_id, 'student', user_id)
            
            # Telegram gruplarında rol verme
            user_info = self.user_data[user_id]
            
            # Telegram gruplarında rol verme (sadece kullanıcı zaten grupta ise)
            if self.group_id:
                try:
                    # Önce kullanıcının grupta olup olmadığını kontrol et
                    member = await context.bot.get_chat_member(self.group_id, user_id)
                    if member.status in ['member', 'administrator', 'creator']:
                        # Kullanıcı zaten grupta, rol verebiliriz
                        await context.bot.promote_chat_member(
                            chat_id=self.group_id,
                            user_id=user_id,
                            can_send_messages=True,
                            can_send_media_messages=True,
                            can_send_other_messages=True,
                            can_add_web_page_previews=True,
                            can_invite_users=False,
                            can_restrict_members=False,
                            can_pin_messages=False,
                            can_manage_chat=False,
                            can_manage_video_chats=False,
                            can_manage_topics=False
                        )
                        
                        # Kullanıcıya öğrenci rolü ver
                        try:
                            await context.bot.set_chat_administrator_custom_title(
                                chat_id=self.group_id,
                                user_id=user_id,
                                custom_title="🎓 Öğrenci"
                            )
                            logger.info(f"Successfully assigned role to user {user_id} in group")
                        except Exception as title_error:
                            logger.info(f"Custom title not supported for user {user_id} in group: {title_error}")
                    else:
                        logger.info(f"User {user_id} is not a member of group {self.group_id}")
                        
                except Exception as e:
                    logger.warning(f"Could not promote user {user_id} in group: {e}")
            
            # Duyuru kanalında rol verme (sadece kullanıcı zaten kanalda ise)
            if self.channel_id:
                try:
                    # Önce kullanıcının kanalda olup olmadığını kontrol et
                    member = await context.bot.get_chat_member(self.channel_id, user_id)
                    if member.status in ['member', 'administrator', 'creator']:
                        # Kullanıcı zaten kanalda, rol verebiliriz
                        await context.bot.promote_chat_member(
                            chat_id=self.channel_id,
                            user_id=user_id,
                            can_send_messages=True,
                            can_send_media_messages=True,
                            can_send_other_messages=True,
                            can_add_web_page_previews=True,
                            can_invite_users=False,
                            can_restrict_members=False,
                            can_pin_messages=False,
                            can_manage_chat=False,
                            can_manage_video_chats=False,
                            can_manage_topics=False
                        )
                        
                        # Kullanıcıya öğrenci rolü ver
                        try:
                            await context.bot.set_chat_administrator_custom_title(
                                chat_id=self.channel_id,
                                user_id=user_id,
                                custom_title="🎓 Öğrenci"
                            )
                            logger.info(f"Successfully assigned role to user {user_id} in channel")
                        except Exception as title_error:
                            logger.info(f"Custom title not supported for user {user_id} in channel: {title_error}")
                    else:
                        logger.info(f"User {user_id} is not a member of channel {self.channel_id}")
                        
                except Exception as e:
                    logger.warning(f"Could not promote user {user_id} in channel: {e}")
            
            await update.message.reply_text(
                f"🎉 <b>Tebrikler! Hesabın doğrulandı!</b>\n\n"
                f"✅ Artık gruba katılabilir ve tüm özellikleri kullanabilirsin.\n"
                f"🎓 Öğrenci rolü atandı.\n\n"
                f"📱 <b>Hızlı Erişim:</b>\n"
                f"• Gruba katıl: {self.group_id}\n"
                f"• Duyuru kanalı: {self.channel_id}\n\n"
                f"💡 <b>Komutlar için:</b> /yardim\n"
                f"📋 <b>Profil için:</b> /profil",
                parse_mode='HTML'
            )
            
            if self.group_id:
                try:
                    user_info = self.user_data[user_id]
                    await context.bot.send_message(
                        chat_id=self.group_id,
                        text=f"🎓 <b>Yeni Üye Katıldı!</b>\n\n"
                        f"👤 <b>{user_info['full_name']}</b>\n"
                        f"🎒 <b>{user_info['department']}</b>\n"
                        f"📚 <b>{user_info['class_year']}. Sınıf</b>\n\n"
                        f"Hoş geldin! 👋",
                        parse_mode='HTML'
                    )
                except:
                    pass
            return ConversationHandler.END
        else:
            await update.message.reply_text("❌ Geçersiz doğrulama kodu!\nLütfen tekrar dene veya /start ile baştan başla.")
            return WAITING_VERIFICATION
    
    async def announcement(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if not self.db.is_admin(user_id):
            if update.message:
                await update.message.reply_text("❌ Bu komutu kullanma yetkiniz yok!")
            else:
                await update.callback_query.answer("❌ Bu komutu kullanma yetkiniz yok!", show_alert=True)
            return ConversationHandler.END
        
        keyboard = [
            [InlineKeyboardButton("📚 Akademik", callback_data='ann_academic')],
            [InlineKeyboardButton("🎉 Sosyal", callback_data='ann_social')],
            [InlineKeyboardButton("🏢 İdari", callback_data='ann_administrative')],
            [InlineKeyboardButton("⚠️ Acil", callback_data='ann_urgent')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.message:
            await update.message.reply_text("📢 Duyuru kategorisini seç:", reply_markup=reply_markup)
        else:
            await update.callback_query.edit_message_text("📢 Duyuru kategorisini seç:", reply_markup=reply_markup)
        return WAITING_ANNOUNCEMENT
    
    async def announcement_category(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        category_map = {'ann_academic': 'Akademik', 'ann_social': 'Sosyal', 'ann_administrative': 'İdari', 'ann_urgent': 'Acil'}
        context.user_data['ann_category'] = category_map[query.data]
        await query.edit_message_text(f"📝 {category_map[query.data]} duyurusu oluşturuyorsun.\n\nDuyuru başlığını ve içeriğini şu formatta yaz:\n\nBaşlık: ...\nİçerik: ...")
        return WAITING_ANNOUNCEMENT
    
    async def send_announcement(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = update.message.text
        try:
            parts = text.split('\n', 1)
            title = parts[0].replace('Başlık:', '').strip()
            content = parts[1].replace('İçerik:', '').strip() if len(parts) > 1 else ''
            category = context.user_data.get('ann_category', 'Genel')
            emoji_map = {'Akademik': '📚', 'Sosyal': '🎉', 'İdari': '🏢', 'Acil': '⚠️'}
            announcement_text = f"{emoji_map.get(category, '📢')} **{category.upper()} DUYURU**\n\n**{title}**\n\n{content}\n\n📅 {datetime.now().strftime('%d.%m.%Y %H:%M')}"
            
            if self.channel_id:
                msg = await context.bot.send_message(chat_id=self.channel_id, text=announcement_text, )
                conn = self.db.get_connection()
                cursor = conn.cursor()
                cursor.execute('INSERT INTO announcements (title, content, category, created_by, created_at, message_id) VALUES (?, ?, ?, ?, ?, ?)',
                             (title, content, category, update.effective_user.id, datetime.now().isoformat(), msg.message_id))
                conn.commit()
                conn.close()
                await update.message.reply_text("✅ Duyuru başarıyla yayınlandı!")
            else:
                await update.message.reply_text("⚠️ Kanal ID ayarlanmamış!")
        except Exception as e:
            await update.message.reply_text(f"❌ Hata: {str(e)}")
        return ConversationHandler.END
    
    async def create_poll(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if not self.db.is_admin(user_id):
            if update.message:
                await update.message.reply_text("❌ Bu komutu kullanma yetkiniz yok!")
            else:
                await update.callback_query.answer("❌ Bu komutu kullanma yetkiniz yok!", show_alert=True)
            return ConversationHandler.END
        
        if update.message:
            await update.message.reply_text("📊 Anket oluşturuyorsun!\n\nAnket sorusunu yaz:")
        else:
            await update.callback_query.edit_message_text("📊 Anket oluşturuyorsun!\n\nAnket sorusunu yaz:")
        return WAITING_POLL_QUESTION
    
    async def get_poll_question(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.user_data['poll_question'] = update.message.text
        await update.message.reply_text("✅ Soru alındı!\n\nŞimdi seçenekleri her satıra bir tane gelecek şekilde yaz:\n\nÖrnek:\nSeçenek 1\nSeçenek 2\nSeçenek 3")
        return WAITING_POLL_OPTIONS
    
    async def send_poll(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        options = [opt.strip() for opt in update.message.text.split('\n') if opt.strip()]
        
        if len(options) < 2:
            await update.message.reply_text("❌ En az 2 seçenek gerekli!\nLütfen tekrar dene:")
            return WAITING_POLL_OPTIONS
        
        question = context.user_data['poll_question']
        try:
            if self.group_id:
                poll_message = await context.bot.send_poll(
                    chat_id=self.group_id, question=question, options=options,
                    is_anonymous=False, allows_multiple_answers=False
                )
                conn = self.db.get_connection()
                cursor = conn.cursor()
                cursor.execute('INSERT INTO polls (poll_id, question, created_by, created_at) VALUES (?, ?, ?, ?)',
                             (poll_message.poll.id, question, update.effective_user.id, datetime.now().isoformat()))
                conn.commit()
                conn.close()
                await update.message.reply_text("✅ Anket başarıyla oluşturuldu!")
            else:
                await update.message.reply_text("⚠️ Grup ID ayarlanmamış!")
        except Exception as e:
            await update.message.reply_text(f"❌ Hata: {str(e)}")
        return ConversationHandler.END
    
    async def share_resource(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if not self.db.is_verified(user_id):
            if update.message:
                await update.message.reply_text("❌ Önce kayıt olmalısın!")
            else:
                await update.callback_query.answer("❌ Önce kayıt olmalısın!", show_alert=True)
            return ConversationHandler.END
        
        text = "📚 Kaynak Paylaşımı\n\nPaylaşacağın kaynağın başlığını ve açıklamasını yaz:\n\nBaşlık: ...\nAçıklama: ...\nBölüm: ..."
        
        if update.message:
            await update.message.reply_text(text)
        else:
            await update.callback_query.edit_message_text(text)
        return WAITING_RESOURCE_TITLE
    
    async def get_resource_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = update.message.text
        try:
            lines = text.split('\n')
            
            # Başlık, açıklama ve bölüm bilgilerini ayıkla
            title = ""
            desc = ""
            dept = ""
            
            for line in lines:
                line = line.strip()
                if line.startswith('Başlık:'):
                    title = line.replace('Başlık:', '').strip()
                elif line.startswith('Açıklama:'):
                    desc = line.replace('Açıklama:', '').strip()
                elif line.startswith('Bölüm:'):
                    dept = line.replace('Bölüm:', '').strip()
            
            # Eğer format doğru değilse, kullanıcıdan tekrar iste
            if not title or not desc or not dept:
                await update.message.reply_text(
                    "❌ Lütfen bilgileri doğru formatta yazın:\n\n"
                    "Başlık: Kaynak başlığı\n"
                    "Açıklama: Kaynak açıklaması\n"
                    "Bölüm: Bölüm adı\n\n"
                    "Örnek:\n"
                    "Başlık: Matematik Ders Notları\n"
                    "Açıklama: 1. sınıf matematik ders notları\n"
                    "Bölüm: Bilgisayar Mühendisliği"
                )
                return WAITING_RESOURCE_TITLE
            
            context.user_data['resource_title'] = title
            context.user_data['resource_desc'] = desc
            context.user_data['resource_dept'] = dept
            
            await update.message.reply_text("✅ Bilgiler alındı!\n\nŞimdi dosyayı gönder (PDF, Word, PowerPoint, vb.)")
            return WAITING_RESOURCE_FILE
        except Exception as e:
            await update.message.reply_text(
                "❌ Hata oluştu! Lütfen bilgileri doğru formatta yazın:\n\n"
                "Başlık: Kaynak başlığı\n"
                "Açıklama: Kaynak açıklaması\n"
                "Bölüm: Bölüm adı"
            )
            return WAITING_RESOURCE_TITLE
    
    async def save_resource(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        document = update.message.document
        if not document:
            await update.message.reply_text("❌ Lütfen bir dosya gönder!")
            return WAITING_RESOURCE_FILE
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO resources (title, description, file_id, file_type, department, uploaded_by, uploaded_at) VALUES (?, ?, ?, ?, ?, ?, ?)',
                     (context.user_data['resource_title'], context.user_data['resource_desc'], document.file_id,
                      document.mime_type, context.user_data['resource_dept'], update.effective_user.id, datetime.now().isoformat()))
        conn.commit()
        conn.close()
        await update.message.reply_text("✅ Kaynak başarıyla paylaşıldı!\n\nTeşekkürler! 🙏")
        return ConversationHandler.END
    
    async def list_resources(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        if query:
            await query.answer()
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, title, description, department, uploaded_at, download_count FROM resources ORDER BY uploaded_at DESC LIMIT 10')
        resources = cursor.fetchall()
        conn.close()
        
        if not resources:
            text = "📚 Henüz paylaşılmış kaynak yok."
        else:
            text = "📚 SON PAYLAŞILAN KAYNAKLAR\n\n"
            for res in resources:
                # Tüm özel karakterleri temizle
                title = str(res[1]).replace('*', '').replace('_', '').replace('`', '').replace('[', '').replace(']', '').replace('(', '').replace(')', '')
                desc = str(res[2]).replace('*', '').replace('_', '').replace('`', '').replace('[', '').replace(']', '').replace('(', '').replace(')', '')
                dept = str(res[3]).replace('*', '').replace('_', '').replace('`', '').replace('[', '').replace(']', '').replace('(', '').replace(')', '')
                text += f"🔹 {title}\n   📖 {desc}\n   🎒 {dept}\n   📥 {res[5]} indirme\n   /kaynak_{res[0]}\n\n"
        
        # Geri dönüş butonu ekle
        keyboard = [[InlineKeyboardButton("🔙 Geri", callback_data='help')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if query:
            await query.edit_message_text(text, reply_markup=reply_markup)
        else:
            await update.message.reply_text(text, reply_markup=reply_markup)
    
    async def download_resource(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Kaynak dosyasını indirme fonksiyonu"""
        user_id = update.effective_user.id
        
        # Kullanıcının doğrulanmış olup olmadığını kontrol et
        if not self.db.is_verified(user_id):
            await update.message.reply_text("❌ Önce kayıt olmalısın!")
            return
        
        # Komuttan kaynak ID'sini çıkar
        command = update.message.text
        if not command.startswith('/kaynak_'):
            await update.message.reply_text("❌ Geçersiz komut formatı! /kaynak_X formatında kullanın.")
            return
        
        try:
            resource_id = int(command.split('_')[1])
        except (IndexError, ValueError):
            await update.message.reply_text("❌ Geçersiz kaynak numarası!")
            return
        
        # Kaynağı veritabanından al
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT r.id, r.title, r.description, r.file_id, r.file_type, r.department, 
                   r.uploaded_at, r.download_count, u.full_name
            FROM resources r 
            JOIN users u ON r.uploaded_by = u.user_id 
            WHERE r.id = ?
        ''', (resource_id,))
        resource = cursor.fetchone()
        
        if not resource:
            await update.message.reply_text("❌ Bu kaynak bulunamadı!")
            conn.close()
            return
        
        # İndirme sayısını artır
        cursor.execute('UPDATE resources SET download_count = download_count + 1 WHERE id = ?', (resource_id,))
        conn.commit()
        conn.close()
        
        # Kaynak bilgilerini göster
        resource_info = f"""📚 <b>KAYNAK DETAYI</b>

🔹 <b>Başlık:</b> {resource[1]}
📖 <b>Açıklama:</b> {resource[2]}
🎒 <b>Bölüm:</b> {resource[5]}
👤 <b>Yükleyen:</b> {resource[8]}
📅 <b>Yüklenme Tarihi:</b> {resource[6][:10]}
📥 <b>İndirme Sayısı:</b> {resource[7] + 1}

Dosya gönderiliyor... ⬇️"""
        
        await update.message.reply_text(resource_info, parse_mode='HTML')
        
        # Dosyayı gönder
        try:
            await context.bot.send_document(
                chat_id=user_id,
                document=resource[3],  # file_id
                caption=f"📚 {resource[1]}\n\n📖 {resource[2]}\n\n🎒 {resource[5]}"
            )
        except Exception as e:
            await update.message.reply_text(f"❌ Dosya gönderilirken hata oluştu: {str(e)}")
            logger.error(f"Error sending document: {e}")
    
    async def get_resource_details(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Kaynak detaylarını görüntüleme fonksiyonu (etkinlik detayları için)"""
        command = update.message.text
        if not command.startswith('/etkinlik_'):
            return
        
        try:
            event_id = int(command.split('_')[1])
        except (IndexError, ValueError):
            return
        
        # Etkinlik detaylarını göster (mevcut kod)
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT e.id, e.title, e.description, e.event_date, COUNT(ep.id) as participant_count
            FROM events e LEFT JOIN event_participants ep ON e.id = ep.event_id
            WHERE e.id = ? AND e.is_active = 1
            GROUP BY e.id
        ''', (event_id,))
        event = cursor.fetchone()
        conn.close()
        
        if event:
            text = f"""🎉 <b>ETKİNLİK DETAYI</b>

📌 <b>{event[1]}</b>
📝 {event[2]}
📅 {event[3]}
👥 {event[4]} katılımcı

Katılmak için: /katil_{event[0]}"""
            await update.message.reply_text(text, parse_mode='HTML')
    
    async def ask_question(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if not self.db.is_verified(user_id):
            if update.message:
                await update.message.reply_text("❌ Önce kayıt olmalısın!")
            else:
                await update.callback_query.answer("❌ Önce kayıt olmalısın!", show_alert=True)
            return ConversationHandler.END
        
        keyboard = [
            [InlineKeyboardButton("📚 Akademik", callback_data='q_academic')],
            [InlineKeyboardButton("💻 Teknik", callback_data='q_technical')],
            [InlineKeyboardButton("🏢 Genel", callback_data='q_general')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.message:
            await update.message.reply_text("❓ Soru kategorisini seç:", reply_markup=reply_markup)
        else:
            await update.callback_query.edit_message_text("❓ Soru kategorisini seç:", reply_markup=reply_markup)
        return WAITING_QUESTION
    
    async def get_question_category(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        category_map = {'q_academic': 'Akademik', 'q_technical': 'Teknik', 'q_general': 'Genel'}
        context.user_data['q_category'] = category_map[query.data]
        await query.edit_message_text(f"❓ {category_map[query.data]} kategorisinde soru soruyorsun.\n\nSorunu yaz:")
        return WAITING_ANSWER
    
    async def save_question(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        question = update.message.text
        category = context.user_data.get('q_category', 'Genel')
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO questions (question, asked_by, asked_at, category) VALUES (?, ?, ?, ?)',
                     (question, update.effective_user.id, datetime.now().isoformat(), category))
        question_id = cursor.lastrowid
        conn.commit()
        conn.close()
        await update.message.reply_text(f"✅ Sorun kaydedildi! (#{question_id})\n\nBir yönetici veya öğretim üyesi en kısa sürede cevaplayacak.")
        
        if self.group_id:
            try:
                user = self.db.get_user(update.effective_user.id)
                await context.bot.send_message(
                    chat_id=self.group_id,
                    text=f"❓ <b>YENİ SORU</b> (#{question_id})\n\n👤 {user[2]} ({user[4]})\n📁 <b>Kategori:</b> {category}\n\n<b>Soru:</b> {question}\n\nCevaplamak için: /soru_{question_id}",
                    parse_mode='HTML'
                )
            except:
                pass
        return ConversationHandler.END
    
    async def list_questions(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        if query:
            await query.answer()
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT q.id, q.question, q.category, q.is_answered, u.full_name FROM questions q JOIN users u ON q.asked_by = u.user_id ORDER BY q.asked_at DESC LIMIT 15')
        questions = cursor.fetchall()
        conn.close()
        
        if not questions:
            text = "❓ Henüz soru sorulmamış."
        else:
            text = "❓ SON SORULAR\n\n"
            for q in questions:
                status = "✅" if q[3] else "⏳"
                # Özel karakterleri temizle
                question_text = str(q[1]).replace('*', '').replace('_', '').replace('`', '').replace('[', '').replace(']', '').replace('(', '').replace(')', '')
                category = str(q[2]).replace('*', '').replace('_', '').replace('`', '').replace('[', '').replace(']', '').replace('(', '').replace(')', '')
                full_name = str(q[4]).replace('*', '').replace('_', '').replace('`', '').replace('[', '').replace(']', '').replace('(', '').replace(')', '')
                text += f"{status} #{q[0]} - {category}\n   {question_text[:100]}...\n   👤 {full_name}\n   /soru_{q[0]}\n\n"
        
        # Geri dönüş butonu ekle
        keyboard = [[InlineKeyboardButton("🔙 Geri", callback_data='help')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if query:
            await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='HTML')
        else:
            await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='HTML')
    
    async def list_announcements(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        if query:
            await query.answer()
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT a.id, a.title, a.content, a.category, a.created_at, u.full_name FROM announcements a JOIN users u ON a.created_by = u.user_id ORDER BY a.created_at DESC LIMIT 10')
        announcements = cursor.fetchall()
        conn.close()
        
        if not announcements:
            text = "📢 Henüz duyuru yayınlanmamış."
        else:
            text = "📢 <b>SON DUYURULAR</b>\n\n"
            for ann in announcements:
                emoji_map = {'Akademik': '📚', 'Sosyal': '🎉', 'İdari': '🏢', 'Acil': '⚠️'}
                emoji = emoji_map.get(ann[3], '📢')
                text += f"{emoji} <b>{ann[1]}</b>\n   {ann[2][:100]}...\n   📁 {ann[3]}\n   👤 {ann[5]}\n   📅 {ann[4][:10]}\n\n"
        
        # Geri dönüş butonu ekle
        keyboard = [[InlineKeyboardButton("🔙 Geri", callback_data='help')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if query:
            await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='HTML')
        else:
            await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='HTML')
    
    async def answer_question(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Sorulara cevap verme fonksiyonu"""
        user_id = update.effective_user.id
        
        # Admin veya moderator kontrolü
        if not self.db.is_admin(user_id):
            await update.message.reply_text("❌ Bu komutu kullanma yetkiniz yok! Sadece yöneticiler sorulara cevap verebilir.")
            return
        
        # Komuttan soru ID'sini çıkar
        command = update.message.text
        if not command.startswith('/soru_'):
            await update.message.reply_text("❌ Geçersiz komut formatı! /soru_X formatında kullanın.")
            return
        
        try:
            question_id = int(command.split('_')[1])
        except (IndexError, ValueError):
            await update.message.reply_text("❌ Geçersiz soru numarası!")
            return
        
        # Soruyu veritabanından al
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, question, asked_by, is_answered FROM questions WHERE id = ?', (question_id,))
        question = cursor.fetchone()
        
        if not question:
            await update.message.reply_text("❌ Bu soru bulunamadı!")
            conn.close()
            return
        
        if question[3]:  # is_answered
            await update.message.reply_text("❌ Bu soru zaten cevaplanmış!")
            conn.close()
            return
        
        # Soru bilgilerini göster ve cevap iste
        cursor.execute('SELECT full_name FROM users WHERE user_id = ?', (question[2],))
        asker = cursor.fetchone()
        asker_name = asker[0] if asker else "Bilinmeyen"
        
        conn.close()
        
        # Context'e soru ID'sini kaydet
        context.user_data['answering_question_id'] = question_id
        
        await update.message.reply_text(
            f"❓ <b>SORU #{question_id}</b>\n\n"
            f"👤 <b>Soran:</b> {asker_name}\n"
            f"📝 <b>Soru:</b> {question[1]}\n\n"
            f"💬 Cevabınızı yazın:",
            parse_mode='HTML'
        )
        
        return WAITING_ANSWER
    
    async def save_answer(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cevabı kaydetme fonksiyonu"""
        user_id = update.effective_user.id
        answer_text = update.message.text
        question_id = context.user_data.get('answering_question_id')
        
        if not question_id:
            await update.message.reply_text("❌ Hata: Soru ID bulunamadı!")
            return ConversationHandler.END
        
        # Cevabı veritabanına kaydet
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE questions 
            SET answer = ?, answered_by = ?, answered_at = ?, is_answered = 1 
            WHERE id = ?
        ''', (answer_text, user_id, datetime.now().isoformat(), question_id))
        
        # Soruyu soran kişiyi bul
        cursor.execute('SELECT asked_by FROM questions WHERE id = ?', (question_id,))
        asked_by = cursor.fetchone()[0]
        
        conn.commit()
        conn.close()
        
        # Soruyu soran kişiye bildirim gönder
        try:
            await context.bot.send_message(
                chat_id=asked_by,
                text=f"✅ <b>SORUNUZA CEVAP GELDİ!</b>\n\n"
                f"❓ <b>Soru #{question_id}</b>\n"
                f"💬 <b>Cevap:</b> {answer_text}\n\n"
                f"Teşekkürler! 🙏",
                parse_mode='HTML'
            )
        except:
            pass  # Kullanıcı botu engellemiş olabilir
        
        await update.message.reply_text(
            f"✅ Cevap başarıyla kaydedildi!\n\n"
            f"❓ Soru #{question_id} cevaplandı.\n"
            f"👤 Soruyu soran kişiye bildirim gönderildi."
        )
        
        # Context'i temizle
        context.user_data.pop('answering_question_id', None)
        return ConversationHandler.END
    
    async def create_event(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if not self.db.is_admin(user_id):
            if update.message:
                await update.message.reply_text("❌ Bu komutu kullanma yetkiniz yok!")
            else:
                await update.callback_query.answer("❌ Bu komutu kullanma yetkiniz yok!", show_alert=True)
            return ConversationHandler.END
        
        if update.message:
            await update.message.reply_text("🎉 Etkinlik oluşturuyorsun!\n\nEtkinlik başlığını yaz:")
        else:
            await update.callback_query.edit_message_text("🎉 Etkinlik oluşturuyorsun!\n\nEtkinlik başlığını yaz:")
        return WAITING_EVENT_TITLE
    
    async def get_event_title(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.user_data['event_title'] = update.message.text
        await update.message.reply_text("✅ Başlık alındı!\n\nEtkinlik açıklamasını yaz:")
        return WAITING_EVENT_DESC
    
    async def get_event_desc(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.user_data['event_desc'] = update.message.text
        await update.message.reply_text("✅ Açıklama alındı!\n\nEtkinlik tarih ve saatini yaz:\nFormat: GG.AA.YYYY SS:DD\nÖrnek: 25.12.2024 14:00")
        return WAITING_EVENT_DATE
    
    async def save_event(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        event_date = update.message.text
        try:
            datetime.strptime(event_date, '%d.%m.%Y %H:%M')
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute('INSERT INTO events (title, description, event_date, created_by, created_at) VALUES (?, ?, ?, ?, ?)',
                         (context.user_data['event_title'], context.user_data['event_desc'], event_date,
                          update.effective_user.id, datetime.now().isoformat()))
            event_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            if self.channel_id:
                keyboard = [[InlineKeyboardButton("✅ Katılıyorum", callback_data=f'join_event_{event_id}')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await context.bot.send_message(
                    chat_id=self.channel_id,
                    text=f"🎉 <b>YENİ ETKİNLİK</b>\n\n<b>{context.user_data['event_title']}</b>\n\n{context.user_data['event_desc']}\n\n📅 {event_date}\n\nKatılmak için butona tıkla!",
                    reply_markup=reply_markup,
                    parse_mode='HTML'
                )
            await update.message.reply_text("✅ Etkinlik başarıyla oluşturuldu!")
        except ValueError:
            await update.message.reply_text("❌ Geçersiz tarih formatı!\nLütfen belirtilen formatta yaz: GG.AA.YYYY SS:DD")
            return WAITING_EVENT_DATE
        except Exception as e:
            await update.message.reply_text(f"❌ Hata: {str(e)}")
        return ConversationHandler.END
    
    async def join_event(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        user_id = query.from_user.id
        event_id = int(query.data.split('_')[-1])
        
        if not self.db.is_verified(user_id):
            await query.answer("❌ Önce kayıt olmalısın!", show_alert=True)
            return
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM event_participants WHERE event_id = ? AND user_id = ?', (event_id, user_id))
        
        if cursor.fetchone():
            await query.answer("ℹ️ Zaten bu etkinliğe katıldın!", show_alert=True)
            conn.close()
            return
        
        cursor.execute('INSERT INTO event_participants (event_id, user_id, joined_at) VALUES (?, ?, ?)',
                     (event_id, user_id, datetime.now().isoformat()))
        conn.commit()
        cursor.execute('SELECT COUNT(*) FROM event_participants WHERE event_id = ?', (event_id,))
        count = cursor.fetchone()[0]
        conn.close()
        await query.answer("✅ Etkinliğe kaydoldun!", show_alert=True)
        
        try:
            current_text = query.message.text
            # Eğer zaten katılımcı sayısı varsa, onu güncelle
            if "👥 Katılımcı sayısı:" in current_text:
                # Mevcut katılımcı sayısını bul ve güncelle
                import re
                updated_text = re.sub(r'👥 Katılımcı sayısı: \d+', f'👥 Katılımcı sayısı: {count}', current_text)
            else:
                # İlk katılımcı ise ekle
                updated_text = current_text + f"\n\n👥 Katılımcı sayısı: {count}"
            await query.edit_message_text(text=updated_text, reply_markup=query.message.reply_markup, parse_mode='HTML')
        except:
            pass
    
    async def list_events(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        if query:
            await query.answer()
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT e.id, e.title, e.description, e.event_date, COUNT(ep.id) as participant_count
            FROM events e LEFT JOIN event_participants ep ON e.id = ep.event_id
            WHERE e.is_active = 1 GROUP BY e.id ORDER BY e.event_date ASC
        ''')
        events = cursor.fetchall()
        conn.close()
        
        if not events:
            text = "🎉 Yaklaşan etkinlik yok."
        else:
            text = "🎉 <b>YAKINLAŞAN ETKİNLİKLER</b>\n\n"
            for event in events:
                text += f"📌 <b>{event[1]}</b>\n   {event[2][:100]}...\n   📅 {event[3]}\n   👥 {event[4]} katılımcı\n   /etkinlik_{event[0]}\n\n"
        
        # Geri dönüş butonu ekle
        keyboard = [[InlineKeyboardButton("🔙 Geri", callback_data='help')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if query:
            await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='HTML')
        else:
            await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='HTML')
    
    async def check_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            user_id = update.effective_user.id
            message = update.message
            
            # Kullanıcının doğrulanmış olup olmadığını kontrol et
            if not self.db.is_verified(user_id):
                # Mesajı silmeye çalış
                try:
                    await message.delete()
                    logger.info(f"Deleted message from unverified user {user_id}")
                except Exception as e:
                    logger.warning(f"Could not delete message from user {user_id}: {e}")
                
                # Kullanıcıya özelden uyarı mesajı göndermeye çalış
                try:
                    await context.bot.send_message(
                        chat_id=user_id, 
                        text="❌ Gruba mesaj atabilmek için önce kayıt olmalısın!\nKayıt olmak için: /start"
                    )
                    logger.info(f"Sent warning message to user {user_id}")
                except Exception as send_error:
                    logger.error(f"Could not send message to user {user_id}: {send_error}")
                    # Kullanıcıya mesaj gönderilemiyorsa, gruba bilgilendirici mesaj gönder ve 10 saniye sonra sil
                    try:
                        info_message = await context.bot.send_message(
                            chat_id=update.effective_chat.id,
                            text=f"⚠️ @{update.effective_user.username} gruba mesaj atabilmek için önce @{context.bot.username} botuna gidip /start komutu çalıştırmanız gerek!"
                        )
                        logger.info(f"Sent group info message for user {user_id}")
                        
                        # 10 saniye sonra mesajı sil
                        import asyncio
                        async def delete_after_delay():
                            await asyncio.sleep(10)
                            try:
                                await context.bot.delete_message(
                                    chat_id=update.effective_chat.id,
                                    message_id=info_message.message_id
                                )
                                logger.info(f"Deleted info message for user {user_id}")
                            except Exception as delete_error:
                                logger.warning(f"Could not delete info message: {delete_error}")
                        
                        # Arka planda silme işlemini başlat
                        asyncio.create_task(delete_after_delay())
                        
                    except Exception as group_error:
                        logger.error(f"Could not send group message: {group_error}")
                return
            
            conn = self.db.get_connection()
            cursor = conn.cursor()
            one_minute_ago = (datetime.now() - timedelta(minutes=1)).isoformat()
            cursor.execute('SELECT COUNT(*) FROM spam_tracker WHERE user_id = ? AND message_time > ?', (user_id, one_minute_ago))
            message_count = cursor.fetchone()[0]
            
            if message_count >= 5:
                cursor.execute('UPDATE users SET warning_count = warning_count + 1 WHERE user_id = ?', (user_id,))
                conn.commit()
                
                # Spam mesajını sil
                try:
                    await message.delete()
                    logger.info(f"Deleted spam message from user {user_id}")
                except Exception as e:
                    logger.warning(f"Could not delete spam message from user {user_id}: {e}")
                
                # Kullanıcıya spam uyarısı gönder
                try:
                    await context.bot.send_message(chat_id=user_id, text="⚠️ Spam tespit edildi! Lütfen yavaşla.")
                    logger.info(f"Sent spam warning to user {user_id}")
                except Exception as e:
                    logger.error(f"Could not send spam warning to user {user_id}: {e}")
                
                cursor.execute('SELECT warning_count FROM users WHERE user_id = ?', (user_id,))
                warnings = cursor.fetchone()[0]
                
                if warnings >= 3:
                    try:
                        await context.bot.ban_chat_member(chat_id=self.group_id, user_id=user_id)
                        cursor.execute('UPDATE users SET is_banned = 1 WHERE user_id = ?', (user_id,))
                        conn.commit()
                        await context.bot.send_message(chat_id=self.group_id, text=f"🚫 Kullanıcı yasaklandı: {update.effective_user.mention_html()}", parse_mode='HTML')
                        logger.info(f"Banned user {user_id} for spam")
                    except Exception as e:
                        logger.error(f"Could not ban user {user_id}: {e}")
                conn.close()
                return
            
            cursor.execute('INSERT INTO spam_tracker (user_id, message_time) VALUES (?, ?)', (user_id, datetime.now().isoformat()))
            conn.commit()
            cursor.execute('DELETE FROM spam_tracker WHERE message_time < ?', (one_minute_ago,))
            conn.commit()
            
            message_text = message.text.lower() if message.text else ""
            for bad_word in self.bad_words:
                if bad_word in message_text:
                    # Uygunsuz içerik mesajını sil
                    try:
                        await message.delete()
                        logger.info(f"Deleted bad word message from user {user_id}")
                    except Exception as e:
                        logger.warning(f"Could not delete bad word message from user {user_id}: {e}")
                    
                    cursor.execute('UPDATE users SET warning_count = warning_count + 1 WHERE user_id = ?', (user_id,))
                    conn.commit()
                    
                    # Kullanıcıya uyarı gönder
                    try:
                        await context.bot.send_message(chat_id=user_id, text="⚠️ Mesajınız uygunsuz içerik nedeniyle silindi!")
                        logger.info(f"Sent bad word warning to user {user_id}")
                    except Exception as e:
                        logger.error(f"Could not send bad word warning to user {user_id}: {e}")
                    
                    conn.close()
                    return
            conn.close()
            
        except Exception as e:
            logger.error(f"Error in check_message: {e}")
            # Hata durumunda sessizce devam et, botu durdurma
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        user_id = update.effective_user.id if update.effective_user else None
        is_admin = self.db.is_admin(user_id) if user_id else False
        
        help_text = """📚 <b>YARDIM MENÜSÜ</b>

Aşağıdaki butonları kullanarak bot özelliklerine erişebilirsin:

<b>Özellikler:</b>
✅ Güvenli kayıt sistemi
📢 Kategorize duyurular
📊 Anket sistemi
📚 Kaynak paylaşımı
❓ Soru-cevap sistemi
🎉 Etkinlik yönetimi
🛡️ Spam ve küfür koruması
"""
        
        # Genel komutlar için butonlar
        keyboard = [
            [InlineKeyboardButton("🏠 Ana Menü", callback_data='start_menu'),
             InlineKeyboardButton("👤 Profilim", callback_data='profile')],
            [InlineKeyboardButton("📚 Kaynaklar", callback_data='resources'),
             InlineKeyboardButton("📤 Kaynak Paylaş", callback_data='share_resource')],
            [InlineKeyboardButton("❓ Sorular", callback_data='questions'),
             InlineKeyboardButton("❓ Soru Sor", callback_data='ask_question')],
            [InlineKeyboardButton("🎉 Etkinlikler", callback_data='events'),
             InlineKeyboardButton("📢 Duyurular", callback_data='announcements')]
        ]
        
        # Admin komutları için butonlar
        if is_admin:
            keyboard.extend([
                [InlineKeyboardButton("📢 Duyuru Yayınla", callback_data='create_announcement'),
                 InlineKeyboardButton("📊 Anket Oluştur", callback_data='create_poll')],
                [InlineKeyboardButton("🎉 Etkinlik Oluştur", callback_data='create_event'),
                 InlineKeyboardButton("📊 İstatistikler", callback_data='stats')],
                [InlineKeyboardButton("⏳ Bekleyen Kayıtlar", callback_data='pending_users')]
            ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if query:
            await query.answer()
            await query.edit_message_text(help_text, reply_markup=reply_markup, parse_mode='HTML')
        else:
            await update.message.reply_text(help_text, reply_markup=reply_markup, parse_mode='HTML')
    
    async def profile(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        user_id = query.from_user.id if query else update.effective_user.id
        if query:
            await query.answer()
        
        user = self.db.get_user(user_id)
        if not user:
            text = "❌ Profil bulunamadı! Kayıt olmak için /start"
        else:
            role = self.db.get_user_role(user_id)
            role_emoji = {
                'student': '🎓',
                'moderator': '🛡️', 
                'admin': '👑'
            }
            
            text = f"""👤 <b>PROFİL BİLGİLERİ</b>

📛 <b>Ad Soyad:</b> {user[2]}
🎓 <b>Öğrenci No:</b> {user[3]}
🏫 <b>Bölüm:</b> {user[4]}
📚 <b>Sınıf:</b> {user[5]}
📧 <b>E-posta:</b> {user[6]}
✅ <b>Durum:</b> {"Onaylı" if user[8] else "Onay Bekliyor"}
{role_emoji.get(role, '🎓')} <b>Rol:</b> {role.title()}
📅 <b>Kayıt Tarihi:</b> {user[10][:10]}

💡 <b>İzinler:</b>
{self._get_permissions_text(user_id)}
"""
        
        # Geri dönüş butonu ekle
        keyboard = [[InlineKeyboardButton("🔙 Geri", callback_data='help')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if query:
            await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='HTML')
        else:
            await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='HTML')
    
    def _get_permissions_text(self, user_id):
        permissions = {
            'view_resources': '📚 Kaynakları görüntüleme',
            'ask_questions': '❓ Soru sorma',
            'join_events': '🎉 Etkinliklere katılma',
            'manage_questions': '🛠️ Soruları yönetme',
            'view_stats': '📊 İstatistikleri görme',
            'create_announcements': '📢 Duyuru oluşturma',
            'create_polls': '📊 Anket oluşturma',
            'create_events': '🎉 Etkinlik oluşturma',
            'manage_users': '👥 Kullanıcı yönetimi'
        }
        
        user_permissions = []
        for perm, desc in permissions.items():
            if self.db.has_permission(user_id, perm):
                user_permissions.append(f"✅ {desc}")
        
        return '\n'.join(user_permissions) if user_permissions else "❌ Hiçbir özel izin yok"
    
    async def statistics(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        user_id = query.from_user.id if query else update.effective_user.id
        if not self.db.is_admin(user_id):
            if query:
                await query.answer("❌ Bu komutu kullanma yetkiniz yok!", show_alert=True)
            else:
                await update.message.reply_text("❌ Bu komutu kullanma yetkiniz yok!")
            return
        
        if query:
            await query.answer()
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM users')
        total_users = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM users WHERE is_verified = 1')
        verified_users = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM users WHERE is_verified = 0')
        pending_users = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM announcements')
        total_announcements = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM resources')
        total_resources = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM questions')
        total_questions = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM questions WHERE is_answered = 1')
        answered_questions = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM events WHERE is_active = 1')
        active_events = cursor.fetchone()[0]
        conn.close()
        
        stats_text = f"""📊 <b>BOT İSTATİSTİKLERİ</b>

👥 <b>Kullanıcılar:</b>
   • Toplam: {total_users}
   • Onaylı: {verified_users}
   • Bekleyen: {pending_users}

📢 <b>Duyurular:</b> {total_announcements}
📚 <b>Kaynaklar:</b> {total_resources}
❓ <b>Sorular:</b> {total_questions} (✅ {answered_questions})
🎉 <b>Aktif Etkinlikler:</b> {active_events}

📅 Güncelleme: {datetime.now().strftime('%d.%m.%Y %H:%M')}
"""
        
        # Geri dönüş butonu ekle
        keyboard = [[InlineKeyboardButton("🔙 Geri", callback_data='help')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if query:
            await query.edit_message_text(stats_text, reply_markup=reply_markup, parse_mode='HTML')
        else:
            await update.message.reply_text(stats_text, reply_markup=reply_markup, parse_mode='HTML')
    
    async def pending_users(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        user_id = query.from_user.id if query else update.effective_user.id
        if not self.db.is_admin(user_id):
            if query:
                await query.answer("❌ Bu komutu kullanma yetkiniz yok!", show_alert=True)
            else:
                await update.message.reply_text("❌ Bu komutu kullanma yetkiniz yok!")
            return
        
        if query:
            await query.answer()
        
        pending = self.db.get_pending_users()
        if not pending:
            text = "✅ Bekleyen kayıt yok!"
        else:
            text = "⏳ **BEKLEYEN KAYITLAR**\n\n"
            for user in pending:
                text += f"👤 {user[2]} (@{user[1]})\n   🎓 {user[3]}\n   🏫 {user[4]} - {user[5]}\n   /onayla_{user[0]}\n\n"
        
        # Geri dönüş butonu ekle
        keyboard = [[InlineKeyboardButton("🔙 Geri", callback_data='help')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if query:
            await query.edit_message_text(text, reply_markup=reply_markup, )
        else:
            await update.message.reply_text(text, reply_markup=reply_markup, )
    
    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        if query.data == 'register':
            return await self.register_start(update, context)
        elif query.data == 'start_menu':
            return await self.start(update, context)
        elif query.data == 'profile':
            return await self.profile(update, context)
        elif query.data == 'resources':
            return await self.list_resources(update, context)
        elif query.data == 'share_resource':
            # Kaynak paylaşımı için conversation başlat
            return await self.share_resource(update, context)
        elif query.data == 'questions':
            return await self.list_questions(update, context)
        elif query.data == 'ask_question':
            # Soru sorma için conversation başlat
            return await self.ask_question(update, context)
        elif query.data == 'events':
            return await self.list_events(update, context)
        elif query.data == 'announcements':
            return await self.list_announcements(update, context)
        elif query.data == 'stats':
            return await self.statistics(update, context)
        elif query.data == 'help':
            return await self.help_command(update, context)
        elif query.data == 'create_announcement':
            # Duyuru oluşturma için conversation başlat
            return await self.announcement(update, context)
        elif query.data == 'create_poll':
            # Anket oluşturma için conversation başlat
            return await self.create_poll(update, context)
        elif query.data == 'create_event':
            # Etkinlik oluşturma için conversation başlat
            return await self.create_event(update, context)
        elif query.data == 'pending_users':
            return await self.pending_users(update, context)
        elif query.data.startswith('join_event_'):
            return await self.join_event(update, context)
        elif query.data.startswith('faculty_'):
            return await self.show_department_menu(update, context)
        elif query.data.startswith('dept_'):
            return await self.select_department(update, context)
    
    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("❌ İşlem iptal edildi.\nYeni işlem başlatmak için /start")
        return ConversationHandler.END
    
    def run(self):
        app = Application.builder().token(self.token).build()
        
        register_conv = ConversationHandler(
            entry_points=[CallbackQueryHandler(self.register_start, pattern='^register$')],
            states={
                WAITING_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.get_name)],
                WAITING_STUDENT_NO: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.get_student_no)],
                WAITING_DEPARTMENT: [
                    CallbackQueryHandler(self.show_department_menu, pattern='^faculty_'),
                    CallbackQueryHandler(self.select_department, pattern='^dept_')
                ],
                WAITING_CLASS: [CallbackQueryHandler(self.get_class, pattern='^class_')],
                WAITING_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.get_email)],
                WAITING_VERIFICATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.verify_code)]
            },
            fallbacks=[CommandHandler('cancel', self.cancel)],
            per_chat=True
        )
        
        answer_conv = ConversationHandler(
            entry_points=[MessageHandler(filters.Regex(r'^/soru_\d+$'), self.answer_question)],
            states={
                WAITING_ANSWER: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.save_answer)]
            },
            fallbacks=[CommandHandler('cancel', self.cancel)],
            per_chat=True
        )
        
        announcement_conv = ConversationHandler(
            entry_points=[
                CommandHandler('duyuru', self.announcement),
                CallbackQueryHandler(self.announcement, pattern='^create_announcement$')
            ],
            states={
                WAITING_ANNOUNCEMENT: [
                    CallbackQueryHandler(self.announcement_category, pattern='^ann_'),
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.send_announcement)
                ]
            },
            fallbacks=[CommandHandler('cancel', self.cancel)],
            per_chat=True
        )
        
        poll_conv = ConversationHandler(
            entry_points=[
                CommandHandler('anket', self.create_poll),
                CallbackQueryHandler(self.create_poll, pattern='^create_poll$')
            ],
            states={
                WAITING_POLL_QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.get_poll_question)],
                WAITING_POLL_OPTIONS: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.send_poll)]
            },
            fallbacks=[CommandHandler('cancel', self.cancel)],
            per_chat=True
        )
        
        resource_conv = ConversationHandler(
            entry_points=[
                CommandHandler('kaynak_paylas', self.share_resource),
                CallbackQueryHandler(self.share_resource, pattern='^share_resource$')
            ],
            states={
                WAITING_RESOURCE_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.get_resource_info)],
                WAITING_RESOURCE_FILE: [MessageHandler(filters.Document.ALL, self.save_resource)]
            },
            fallbacks=[CommandHandler('cancel', self.cancel)],
            per_chat=True
        )
        
        question_conv = ConversationHandler(
            entry_points=[
                CommandHandler('soru_sor', self.ask_question),
                CallbackQueryHandler(self.ask_question, pattern='^ask_question$')
            ],
            states={
                WAITING_QUESTION: [
                    CallbackQueryHandler(self.get_question_category, pattern='^q_')
                ],
                WAITING_ANSWER: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.save_question)
                ]
            },
            fallbacks=[CommandHandler('cancel', self.cancel)],
            per_chat=True
        )
        
        event_conv = ConversationHandler(
            entry_points=[
                CommandHandler('etkinlik', self.create_event),
                CallbackQueryHandler(self.create_event, pattern='^create_event$')
            ],
            states={
                WAITING_EVENT_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.get_event_title)],
                WAITING_EVENT_DESC: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.get_event_desc)],
                WAITING_EVENT_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.save_event)]
            },
            fallbacks=[CommandHandler('cancel', self.cancel)],
            per_chat=True
        )
        
        # Bot komutlarını ayarla
        commands = [
            ('start', 'Botu başlat'),
            ('profil', 'Profilini görüntüle'),
            ('kaynaklar', 'Paylaşılan kaynakları listele'),
            ('kaynak_paylas', 'Yeni kaynak paylaş'),
            ('sorular', 'Soruları listele'),
            ('soru_sor', 'Yeni soru sor'),
            ('etkinlikler', 'Etkinlikleri listele'),
            ('yardim', 'Yardım menüsü'),
            ('istatistik', 'Bot istatistikleri'),
            ('duyuru', 'Duyuru yayınla (Admin)'),
            ('anket', 'Anket oluştur (Admin)'),
            ('etkinlik', 'Etkinlik oluştur (Admin)'),
            ('onay_bekleyenler', 'Bekleyen kayıtları göster (Admin)')
        ]
        
        app.add_handler(CommandHandler('start', self.start))
        app.add_handler(register_conv)
        app.add_handler(answer_conv)
        app.add_handler(announcement_conv)
        app.add_handler(poll_conv)
        app.add_handler(resource_conv)
        app.add_handler(question_conv)
        app.add_handler(event_conv)
        app.add_handler(CommandHandler('profil', self.profile))
        app.add_handler(CommandHandler('kaynaklar', self.list_resources))
        app.add_handler(CommandHandler('sorular', self.list_questions))
        app.add_handler(CommandHandler('etkinlikler', self.list_events))
        app.add_handler(CommandHandler('yardim', self.help_command))
        app.add_handler(CommandHandler('istatistik', self.statistics))
        app.add_handler(CommandHandler('onay_bekleyenler', self.pending_users))
        # Kaynak indirme komutları
        app.add_handler(MessageHandler(filters.Regex(r'^/kaynak_\d+$'), self.download_resource))
        app.add_handler(MessageHandler(filters.Regex(r'^/etkinlik_\d+$'), self.get_resource_details))
        app.add_handler(CallbackQueryHandler(self.button_handler))
        app.add_handler(MessageHandler(filters.ChatType.GROUPS & filters.TEXT & ~filters.COMMAND, self.check_message))
        
        print("Bot baslatiliyor...")
        app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    BOT_TOKEN = 'botun tokeni'
    CHANNEL_ID = 'duyuru kanalının @ ile başlayan tagı(@tag)'
    GROUP_ID = 'sohbet grubunun @ ile başlayan tagı(@tag)'
    
    bot = UniversityBot(BOT_TOKEN, CHANNEL_ID, GROUP_ID)
    
    try:
        bot.run()
    except KeyboardInterrupt:
        print("Bot durduruldu.")
    except Exception as e:
        print(f"Hata: {e}")