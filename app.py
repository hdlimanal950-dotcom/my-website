"""
ultimate_smart_crawler_dashboard_fixed.py - نظام الزحف مع لوحة تحكم تراكمية ونظام مراقبة الأسعار التلقائية
الإصدار: 21.2 - نظام التمويه الذكي + وسيط ScraperAPI
"""

# ==================== الاستيراد العام أولاً ====================
from flask import Flask, request, jsonify, render_template_string
import os
import sys
import json
import sqlite3
import hashlib
import random
import time
import re
import statistics
import math
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from urllib.parse import urlparse, parse_qs, urlencode, urljoin, quote
import threading
from threading import Lock, RLock, Thread, Event, Timer
from typing import Dict, List, Optional, Tuple, Set, Any
from collections import Counter, defaultdict
from dataclasses import dataclass
import traceback
import base64
import uuid
import platform
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

print("=" * 60)
print("📊 نظام الزحف الذكي - لوحة التحكم التراكمية + نظام الوسيط الذكي")
print("=" * 60)
print("\n📦 جاري تحميل المكتبات...")
print("✅ المكتبات الأساسية - جاهزة")

# ==================== إعدادات النظام الجديد ====================
MONITORING_CONFIG = {
    'enabled': True,  # تفعيل/تعطيل نظام المراقبة
    'interval': 7200,  # الفترة بين عمليات المراقبة بالثواني (كل ساعتين)
    'price_drop_threshold': 20.0,  # نسبة الانخفاض لإرسال إشعار (20%)
    'monitoring_limit': 30,  # عدد المنتجات للمراقبة في كل دورة
    'email_notifications': True,  # ✅ تفعيل الإشعارات البريدية
    'smart_rotation': True,  # تدوير الهويات تلقائياً
    'delay_between_requests': [3, 8],  # تأخير بين الطلبات
    'use_proxy_fallback': True,  # استخدام الوسيط عند الفشل
    'max_retries': 3,  # عدد المحاولات
}

EMAIL_CONFIG = {
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'sender_email': 'kklb1553@gmail.com',  # ✅ تم التحديث
    'sender_password': 'b g b j f p t m q a p m w z e f',  # ✅ تم التحديث
    'receiver_email': 'kklb1553@gmail.com',  # ✅ تم التحديث
}

# ==================== إعدادات الوسيط ====================
PROXY_CONFIG = {
    'enabled': True,
    'primary_proxy': 'scraperapi',
    'scraperapi_key': 'c5ff3050a86e42483899a1fff1ec4780',
    'scraperapi_url': 'http://api.scraperapi.com',
    'use_direct_first': True,  # المحاولة المباشرة أولاً
    'retry_with_proxy': True,  # إعادة المحاولة بالوسيط
    'timeout': 30,  # وقت الانتظار للوسيط
}

# ==================== نظام التمويه الذكي مع الوسيط ====================
class SmartBrowserSimulator:
    """محاكي متصفح ذكي مع وسيط احتياطي"""
    
    def __init__(self):
        self.user_agents = [
            # Chrome على Windows
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            
            # Chrome على Mac
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            
            # Safari على Mac
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
            
            # Firefox
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
            
            # Edge
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0',
            
            # Chrome على Android (مهم: لمحاكاة الهاتف)
            'Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36',
            'Mozilla/5.0 (Linux; Android 14; SM-S911B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36',
            
            # iPhone
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/121.0.0.0 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1',
        ]
        
        self.cookies = {}
        self.session = requests.Session()
        
        # إعدادات متقدمة للجلسة
        retry_strategy = Retry(
            total=2,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=20, pool_maxsize=20)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # تأخيرات طبيعية بين الطلبات
        self.delays = [2.0, 2.5, 3.0, 3.5, 4.0, 4.5]
        
        print("🕵️‍♂️ نظام التمويه الذكي مع الوسيط - جاهز")
    
    def get_smart_headers(self, referer=None):
        """إرجاع رأسيات ذكية لمحاكاة المتصفح الحقيقي"""
        headers = {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,ar;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'Sec-Ch-Ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
        }
        
        if referer:
            headers['Referer'] = referer
        
        return headers
    
    def add_natural_delay(self):
        """إضافة تأخير طبيعي لمحاكاة السلوك البشري"""
        delay = random.choice(self.delays)
        time.sleep(delay)
    
    def smart_get_request(self, url, max_retries=3, use_proxy=True):
        """طلب ذكي مع إعادة محاولة وتغيير الهوية والوسيط"""
        attempts_log = []
        
        for attempt in range(max_retries):
            try:
                # تغيير الهوية في كل محاولة
                headers = self.get_smart_headers('https://www.amazon.com/')
                
                # إضافة تأخير قبل الطلب
                self.add_natural_delay()
                
                # إضافة كوكيز عشوائية لمحاكاة الجلسة
                if not self.cookies:
                    self.cookies = {
                        'session-id': str(random.randint(1000000, 9999999)),
                        'ubid-main': str(random.randint(1000000, 9999999)),
                        'session-token': hashlib.md5(str(time.time()).encode()).hexdigest()[:20],
                        'i18n-prefs': 'USD',
                        'sp-cdn': 'L5Z9:SA'
                    }
                
                # المحاولة 1: طلب مباشر (إذا كان مسموحاً)
                if attempt == 0 or not use_proxy:
                    response = self.session.get(
                        url,
                        headers=headers,
                        cookies=self.cookies,
                        timeout=20,
                        allow_redirects=True,
                        stream=False
                    )
                    method = "direct"
                
                # المحاولة 2+: استخدام الوسيط
                else:
                    proxy_url = self._get_proxy_url(url)
                    if proxy_url:
                        response = self.session.get(
                            proxy_url,
                            headers=headers,
                            cookies=self.cookies,
                            timeout=PROXY_CONFIG['timeout'],
                            allow_redirects=True,
                            stream=False
                        )
                        method = "proxy"
                    else:
                        continue
                
                # تسجيل محاولة
                attempts_log.append({
                    'attempt': attempt + 1,
                    'method': method,
                    'status': response.status_code
                })
                
                # إذا كان الطلب ناجحاً
                if response.status_code == 200:
                    # تحديث الكوكيز من الاستجابة
                    if response.cookies:
                        self.cookies.update(response.cookies.get_dict())
                    return response, attempts_log
                
                # إذا كان هناك تحويل، اتبع الرابط الجديد
                elif response.status_code in [301, 302, 303, 307, 308]:
                    new_url = response.headers.get('Location')
                    if new_url:
                        return self.smart_get_request(new_url, max_retries, use_proxy)
                
                # إذا فشل، حاول مرة أخرى مع هوية مختلفة
                else:
                    # إعادة ضبط الكوكيز للجلسة الجديدة
                    self.cookies = {}
                    time.sleep(2 ** attempt)  # تأخير متزايد
                    
            except requests.exceptions.Timeout:
                attempts_log.append({
                    'attempt': attempt + 1,
                    'method': method if 'method' in locals() else 'unknown',
                    'status': 'timeout'
                })
                time.sleep(2 ** attempt)
            except Exception as e:
                attempts_log.append({
                    'attempt': attempt + 1,
                    'method': method if 'method' in locals() else 'unknown',
                    'status': f'error: {str(e)[:50]}'
                })
                time.sleep(2 ** attempt)
        
        return None, attempts_log
    
    def _get_proxy_url(self, url):
        """إنشاء رابط الوسيط"""
        if not PROXY_CONFIG['enabled'] or not PROXY_CONFIG['scraperapi_key']:
            return None
        
        try:
            # تشفير الرابط
            encoded_url = quote(url, safe='')
            
            # بناء رابط ScraperAPI
            proxy_url = f"{PROXY_CONFIG['scraperapi_url']}/?api_key={PROXY_CONFIG['scraperapi_key']}&url={encoded_url}"
            
            # إضافة إعدادات إضافية لـ ScraperAPI
            proxy_url += "&render=true&country_code=us&device_type=desktop"
            
            return proxy_url
        except:
            return None

# ==================== إعدادات التسجيل ====================
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# ==================== قاعدة بيانات موسعة مع نظام المراقبة ====================
class EnhancedDatabase:
    """قاعدة بيانات موسعة مع نظام تتبع ومراقبة الأسعار"""
    
    def __init__(self, db_path: str = "crawler_dashboard.db"):
        self.db_path = db_path
        self.local = threading.local()
        self.lock = RLock()
        self._ensure_database_exists()
    
    def get_connection(self):
        """الحصول على اتصال آمن"""
        with self.lock:
            if not hasattr(self.local, 'connection'):
                self.local.connection = sqlite3.connect(
                    self.db_path,
                    check_same_thread=False,
                    timeout=30.0
                )
                self.local.connection.execute('PRAGMA journal_mode=WAL')
                self.local.connection.execute('PRAGMA synchronous=NORMAL')
            return self.local.connection
    
    def _ensure_database_exists(self):
        """التأكد من وجود قاعدة البيانات وجداولها الموسعة"""
        print(f"\n🗄️  جاري التحقق من قاعدة البيانات: {self.db_path}")
        
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # ============ جدول المنتجات الموسع ============
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS dashboard_products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    asin TEXT UNIQUE NOT NULL,
                    product_name TEXT,
                    current_price REAL,
                    reference_price REAL,
                    discount_percentage REAL DEFAULT 0.0,
                    currency TEXT DEFAULT 'USD',
                    availability_status TEXT DEFAULT 'active',
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    source_url TEXT,
                    category TEXT,
                    initial_price REAL,  -- السعر الأول المسجل
                    price_change_count INTEGER DEFAULT 0,
                    last_monitored TIMESTAMP,
                    monitoring_enabled BOOLEAN DEFAULT 1,
                    price_drop_detected BOOLEAN DEFAULT 0,
                    extraction_method TEXT DEFAULT 'direct',  -- طريقة الاستخلاص
                    last_extraction_status TEXT DEFAULT 'success',
                    CHECK (length(asin) = 10),
                    CHECK (discount_percentage >= 0 AND discount_percentage <= 100)
                )
            ''')
            
            # ============ جدول تاريخ الأسعار ============
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS price_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    asin TEXT NOT NULL,
                    price REAL NOT NULL,
                    reference_price REAL,
                    discount_percentage REAL,
                    extraction_method TEXT DEFAULT 'direct',
                    captured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (asin) REFERENCES dashboard_products (asin) ON DELETE CASCADE
                )
            ''')
            
            # ============ جدول أحداث التحديث ============
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS update_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    asin TEXT,
                    old_value TEXT,
                    new_value TEXT,
                    discount_change REAL DEFAULT 0.0,
                    extraction_method TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # ============ جدول إحصائيات العرض ============
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS display_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    total_products INTEGER DEFAULT 0,
                    active_products INTEGER DEFAULT 0,
                    avg_price REAL DEFAULT 0.0,
                    avg_discount REAL DEFAULT 0.0,
                    best_deal_percentage REAL DEFAULT 0.0,
                    last_refresh TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_date DATE UNIQUE DEFAULT CURRENT_DATE
                )
            ''')
            
            # ============ جدول تنبيهات الأسعار ============
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS price_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    asin TEXT NOT NULL,
                    old_price REAL NOT NULL,
                    new_price REAL NOT NULL,
                    drop_percentage REAL NOT NULL,
                    extraction_method TEXT DEFAULT 'direct',
                    alert_sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    notified_email TEXT,
                    FOREIGN KEY (asin) REFERENCES dashboard_products (asin) ON DELETE CASCADE
                )
            ''')
            
            # ============ جدول سجلات المراقبة ============
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS monitoring_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    asin TEXT NOT NULL,
                    old_price REAL,
                    new_price REAL,
                    price_change REAL,
                    extraction_method TEXT,
                    status TEXT,
                    message TEXT,
                    monitored_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # ============ جدول إحصائيات الاستخلاص ============
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS extraction_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE UNIQUE DEFAULT CURRENT_DATE,
                    total_attempts INTEGER DEFAULT 0,
                    direct_success INTEGER DEFAULT 0,
                    proxy_success INTEGER DEFAULT 0,
                    failed_attempts INTEGER DEFAULT 0,
                    success_rate REAL DEFAULT 0.0,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            
            # ============ إضافة الأعمدة المفقودة إذا لزم ============
            self._add_missing_columns(cursor)
            
            conn.commit()
            
            # ============ الفهارس ============
            try:
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_dashboard_asin ON dashboard_products(asin)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_dashboard_discount ON dashboard_products(discount_percentage DESC)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_dashboard_status ON dashboard_products(availability_status, last_updated DESC)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_price_history ON price_history(asin, captured_at DESC)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_time ON update_events(created_at DESC)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_stats_date ON display_stats(created_date DESC)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_time ON price_alerts(alert_sent_at DESC)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_monitoring_time ON monitoring_logs(monitored_at DESC)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_extraction_method ON dashboard_products(extraction_method)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_extraction_stats_date ON extraction_stats(date DESC)')
                conn.commit()
            except Exception as e:
                print(f"⚠️  تحذير في إنشاء الفهارس: {e}")
            
            print("✅ قاعدة البيانات الموسعة جاهزة")
            
            # تحديث الإحصائيات الأولية
            self._update_display_stats()
            
        except Exception as e:
            print(f"❌ خطأ في قاعدة البيانات: {e}")
            if conn:
                conn.rollback()
            raise
    
    def _add_missing_columns(self, cursor):
        """إضافة الأعمدة المفقودة إلى الجداول"""
        try:
            # التحقق من أعمدة جدول dashboard_products
            cursor.execute("PRAGMA table_info(dashboard_products)")
            columns = [col[1] for col in cursor.fetchall()]
            
            missing_columns = []
            
            # التحقق من الأعمدة المطلوبة
            required_columns = [
                'initial_price', 'monitoring_enabled', 'price_drop_detected', 
                'last_monitored', 'extraction_method', 'last_extraction_status'
            ]
            
            for col in required_columns:
                if col not in columns:
                    missing_columns.append(col)
            
            # إضافة الأعمدة المفقودة
            for col in missing_columns:
                try:
                    if col == 'initial_price':
                        cursor.execute(f'ALTER TABLE dashboard_products ADD COLUMN {col} REAL')
                    elif col == 'monitoring_enabled':
                        cursor.execute(f'ALTER TABLE dashboard_products ADD COLUMN {col} BOOLEAN DEFAULT 1')
                    elif col == 'price_drop_detected':
                        cursor.execute(f'ALTER TABLE dashboard_products ADD COLUMN {col} BOOLEAN DEFAULT 0')
                    elif col == 'last_monitored':
                        cursor.execute(f'ALTER TABLE dashboard_products ADD COLUMN {col} TIMESTAMP')
                    elif col == 'extraction_method':
                        cursor.execute(f'ALTER TABLE dashboard_products ADD COLUMN {col} TEXT DEFAULT "direct"')
                    elif col == 'last_extraction_status':
                        cursor.execute(f'ALTER TABLE dashboard_products ADD COLUMN {col} TEXT DEFAULT "success"')
                    print(f"✅ تمت إضافة العمود المفقود: {col}")
                except Exception as e:
                    print(f"⚠️  تحذير في إضافة العمود {col}: {e}")
            
        except Exception as e:
            print(f"⚠️  تحذير في التحقق من الأعمدة المفقودة: {e}")
    
    def save_or_update_product(self, product_data: Dict) -> bool:
        """حفظ أو تحديث منتج مع تتبع الخصومات والتغيرات وطريقة الاستخلاص"""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            asin = product_data.get('asin')
            if not asin or len(asin) != 10:
                return False
            
            current_price = product_data.get('current_price', 0.0)
            reference_price = product_data.get('reference_price', 0.0)
            discount_percentage = product_data.get('discount_percentage', 0.0)
            extraction_method = product_data.get('extraction_method', 'direct')
            
            # التحقق مما إذا كان المنتج موجوداً
            cursor.execute('''
                SELECT id, current_price, reference_price, discount_percentage, initial_price 
                FROM dashboard_products WHERE asin = ?
            ''', (asin,))
            existing = cursor.fetchone()
            
            if existing:
                product_id, old_price, old_reference, old_discount, initial_price = existing
                
                # تحديث المنتج الموجود
                cursor.execute('''
                    UPDATE dashboard_products 
                    SET product_name = COALESCE(?, product_name),
                        current_price = COALESCE(?, current_price),
                        reference_price = COALESCE(?, reference_price),
                        discount_percentage = COALESCE(?, discount_percentage),
                        currency = COALESCE(?, currency),
                        availability_status = COALESCE(?, availability_status),
                        last_updated = CURRENT_TIMESTAMP,
                        source_url = COALESCE(?, source_url),
                        category = COALESCE(?, category),
                        price_change_count = price_change_count + ?,
                        price_drop_detected = 0,  -- إعادة ضغط كاشف الانخفاض
                        extraction_method = ?,
                        last_extraction_status = 'success'
                    WHERE asin = ?
                ''', (
                    product_data.get('product_name'),
                    current_price,
                    reference_price,
                    discount_percentage,
                    product_data.get('currency', 'USD'),
                    product_data.get('availability_status', 'active'),
                    product_data.get('source_url'),
                    product_data.get('category', 'غير مصنف'),
                    1 if abs(old_price - current_price) > 0.01 else 0,
                    extraction_method,
                    asin
                ))
                
                # إذا لم يكن هناك سعر أولي، تعيينه الآن
                if not initial_price and current_price > 0:
                    cursor.execute('''
                        UPDATE dashboard_products 
                        SET initial_price = ?
                        WHERE asin = ?
                    ''', (current_price, asin))
                
                # تسجيل حدث التحديث
                if abs(old_price - current_price) > 0.01:
                    self._log_update_event('price_change', asin, str(old_price), str(current_price), 
                                         discount_percentage - old_discount, extraction_method)
                
            else:
                # إضافة منتج جديد مع تعيين السعر الأولي
                cursor.execute('''
                    INSERT INTO dashboard_products 
                    (asin, product_name, current_price, reference_price, discount_percentage, 
                     currency, availability_status, source_url, category, initial_price, extraction_method)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    asin,
                    product_data.get('product_name', f'منتج {asin}'),
                    current_price,
                    reference_price,
                    discount_percentage,
                    product_data.get('currency', 'USD'),
                    product_data.get('availability_status', 'active'),
                    product_data.get('source_url'),
                    product_data.get('category', 'غير مصنف'),
                    current_price,  # السعر الأولي
                    extraction_method
                ))
                
                self._log_update_event('new_product', asin, None, product_data.get('product_name', asin), 
                                     discount_percentage, extraction_method)
            
            # حفظ في تاريخ الأسعار
            if current_price > 0:
                cursor.execute('''
                    INSERT INTO price_history (asin, price, reference_price, discount_percentage, extraction_method)
                    VALUES (?, ?, ?, ?, ?)
                ''', (asin, current_price, reference_price, discount_percentage, extraction_method))
            
            conn.commit()
            self._update_display_stats()
            
            logger.info(f"📊 تم تحديث المنتج: {asin} (السعر: ${current_price:.2f}, الطريقة: {extraction_method})")
            return True
            
        except sqlite3.Error as e:
            logger.error(f"❌ خطأ SQL في حفظ المنتج: {e}")
            if conn:
                conn.rollback()
            return False
        except Exception as e:
            logger.error(f"❌ خطأ عام في حفظ المنتج: {e}")
            if conn:
                conn.rollback()
            return False
    
    def update_extraction_status(self, asin: str, status: str, method: str = None):
        """تحديث حالة الاستخلاص للمنتج"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            if method:
                cursor.execute('''
                    UPDATE dashboard_products 
                    SET last_extraction_status = ?, extraction_method = ?, last_updated = CURRENT_TIMESTAMP
                    WHERE asin = ?
                ''', (status, method, asin))
            else:
                cursor.execute('''
                    UPDATE dashboard_products 
                    SET last_extraction_status = ?, last_updated = CURRENT_TIMESTAMP
                    WHERE asin = ?
                ''', (status, asin))
            
            conn.commit()
        except Exception as e:
            logger.error(f"❌ خطأ في تحديث حالة الاستخلاص: {e}")
    
    def log_extraction_stat(self, success: bool, method: str = 'direct'):
        """تسجيل إحصائية استخلاص"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            today = datetime.now().date().isoformat()
            
            # التحقق من وجود سجل اليوم
            cursor.execute('SELECT id, total_attempts, direct_success, proxy_success FROM extraction_stats WHERE date = ?', (today,))
            row = cursor.fetchone()
            
            if row:
                stat_id, total_attempts, direct_success, proxy_success = row
                total_attempts += 1
                
                if success:
                    if method == 'direct':
                        direct_success += 1
                    elif method == 'proxy':
                        proxy_success += 1
                
                failed_attempts = total_attempts - (direct_success + proxy_success)
                success_rate = ((direct_success + proxy_success) / total_attempts * 100) if total_attempts > 0 else 0
                
                cursor.execute('''
                    UPDATE extraction_stats 
                    SET total_attempts = ?, direct_success = ?, proxy_success = ?, 
                        failed_attempts = ?, success_rate = ?, last_updated = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (total_attempts, direct_success, proxy_success, failed_attempts, success_rate, stat_id))
            else:
                total_attempts = 1
                direct_success = 1 if success and method == 'direct' else 0
                proxy_success = 1 if success and method == 'proxy' else 0
                failed_attempts = 0 if success else 1
                success_rate = 100 if success else 0
                
                cursor.execute('''
                    INSERT INTO extraction_stats 
                    (date, total_attempts, direct_success, proxy_success, failed_attempts, success_rate)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (today, total_attempts, direct_success, proxy_success, failed_attempts, success_rate))
            
            conn.commit()
        except Exception as e:
            logger.error(f"❌ خطأ في تسجيل إحصائية الاستخلاص: {e}")
    
    def get_extraction_stats(self) -> Dict:
        """الحصول على إحصائيات الاستخلاص"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT date, total_attempts, direct_success, proxy_success, 
                       failed_attempts, success_rate, last_updated
                FROM extraction_stats 
                ORDER BY date DESC 
                LIMIT 7
            ''')
            
            stats = []
            for row in cursor.fetchall():
                stats.append({
                    'date': row[0],
                    'total_attempts': row[1],
                    'direct_success': row[2],
                    'proxy_success': row[3],
                    'failed_attempts': row[4],
                    'success_rate': row[5],
                    'last_updated': row[6]
                })
            
            # الإحصائيات الإجمالية
            cursor.execute('''
                SELECT 
                    SUM(total_attempts) as total_attempts,
                    SUM(direct_success) as total_direct_success,
                    SUM(proxy_success) as total_proxy_success,
                    SUM(failed_attempts) as total_failed_attempts,
                    AVG(success_rate) as avg_success_rate
                FROM extraction_stats 
                WHERE date >= DATE('now', '-7 days')
            ''')
            
            row = cursor.fetchone()
            
            return {
                'recent_stats': stats,
                'summary': {
                    'total_attempts': row[0] if row[0] else 0,
                    'total_direct_success': row[1] if row[1] else 0,
                    'total_proxy_success': row[2] if row[2] else 0,
                    'total_failed_attempts': row[3] if row[3] else 0,
                    'avg_success_rate': round(row[4], 2) if row[4] else 0,
                    'direct_success_rate': round((row[1] / row[0] * 100), 2) if row[0] and row[0] > 0 else 0,
                    'proxy_success_rate': round((row[2] / row[0] * 100), 2) if row[0] and row[0] > 0 else 0
                }
            }
            
        except Exception as e:
            logger.error(f"❌ خطأ في جلب إحصائيات الاستخلاص: {e}")
            return {'recent_stats': [], 'summary': {}}
    
    def get_products_for_monitoring(self, limit: int = 50) -> List[Dict]:
        """الحصول على المنتجات للمراقبة"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # جلب المنتجات النشطة التي تم تفعيل المراقبة لها
            # مع إعطاء الأولوية للمنتجات التي فشل استخلاصها مؤخراً
            cursor.execute('''
                SELECT asin, product_name, current_price, initial_price, source_url, 
                       last_monitored, monitoring_enabled, extraction_method, last_extraction_status
                FROM dashboard_products
                WHERE availability_status = 'active' 
                AND monitoring_enabled = 1
                AND current_price > 0
                ORDER BY 
                    CASE 
                        WHEN last_extraction_status = 'failed' THEN 1
                        WHEN extraction_method = 'proxy' THEN 2
                        ELSE 3
                    END,
                    last_monitored ASC NULLS FIRST, 
                    last_updated DESC
                LIMIT ?
            ''', (limit,))
            
            products = []
            for row in cursor.fetchall():
                products.append({
                    'asin': row[0],
                    'product_name': row[1],
                    'current_price': row[2],
                    'initial_price': row[3] if row[3] else row[2],
                    'source_url': row[4] or f"https://www.amazon.com/dp/{row[0]}",
                    'last_monitored': row[5],
                    'monitoring_enabled': bool(row[6]),
                    'extraction_method': row[7] or 'direct',
                    'last_extraction_status': row[8] or 'success'
                })
            
            return products
            
        except Exception as e:
            logger.error(f"❌ خطأ في جلب المنتجات للمراقبة: {e}")
            return []
    
    def update_monitoring_time(self, asin: str):
        """تحديث وقت المراقبة الأخير"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE dashboard_products 
                SET last_monitored = CURRENT_TIMESTAMP 
                WHERE asin = ?
            ''', (asin,))
            
            conn.commit()
        except Exception as e:
            logger.error(f"❌ خطأ في تحديث وقت المراقبة: {e}")
    
    def add_price_alert(self, asin: str, old_price: float, new_price: float, 
                       drop_percentage: float, extraction_method: str = 'direct'):
        """إضافة تنبيه انخفاض السعر"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO price_alerts (asin, old_price, new_price, drop_percentage, 
                                        extraction_method, notified_email)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (asin, old_price, new_price, drop_percentage, 
                 extraction_method, EMAIL_CONFIG['receiver_email']))
            
            conn.commit()
            logger.info(f"⚠️  تم تسجيل تنبيه انخفاض السعر لـ {asin}: {drop_percentage:.1f}% (الطريقة: {extraction_method})")
            
        except Exception as e:
            logger.error(f"❌ خطأ في تسجيل تنبيه السعر: {e}")
    
    def add_monitoring_log(self, asin: str, old_price: float, new_price: float, 
                          status: str, message: str = "", extraction_method: str = None):
        """إضافة سجل مراقبة"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            price_change = new_price - old_price if old_price and new_price else 0
            
            cursor.execute('''
                INSERT INTO monitoring_logs (asin, old_price, new_price, price_change, 
                                           extraction_method, status, message)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (asin, old_price, new_price, price_change, extraction_method, status, message))
            
            conn.commit()
        except Exception as e:
            logger.error(f"❌ خطأ في تسجيل سجل المراقبة: {e}")
    
    def mark_price_drop_detected(self, asin: str):
        """تحديث حالة اكتشاف انخفاض السعر"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE dashboard_products 
                SET price_drop_detected = 1 
                WHERE asin = ?
            ''', (asin,))
            
            conn.commit()
        except Exception as e:
            logger.error(f"❌ خطأ في تحديث حالة انخفاض السعر: {e}")
    
    def get_recent_alerts(self, limit: int = 10) -> List[Dict]:
        """الحصول على التنبيهات الحديثة"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT pa.asin, dp.product_name, pa.old_price, pa.new_price, 
                       pa.drop_percentage, pa.alert_sent_at, pa.extraction_method
                FROM price_alerts pa
                LEFT JOIN dashboard_products dp ON pa.asin = dp.asin
                ORDER BY pa.alert_sent_at DESC
                LIMIT ?
            ''', (limit,))
            
            alerts = []
            for row in cursor.fetchall():
                alerts.append({
                    'asin': row[0],
                    'product_name': row[1] if row[1] else f"منتج {row[0]}",
                    'old_price': row[2],
                    'new_price': row[3],
                    'drop_percentage': row[4],
                    'alert_sent_at': row[5],
                    'extraction_method': row[6] or 'direct',
                    'savings': row[2] - row[3] if row[2] and row[3] else 0
                })
            
            return alerts
            
        except Exception as e:
            logger.error(f"❌ خطأ في جلب التنبيهات: {e}")
            return []
    
    def get_monitoring_stats(self) -> Dict:
        """الحصول على إحصائيات المراقبة"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # إحصائيات عامة
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_monitored,
                    COUNT(CASE WHEN price_drop_detected = 1 THEN 1 END) as drops_detected,
                    COUNT(CASE WHEN last_monitored IS NOT NULL THEN 1 END) as recently_monitored,
                    AVG(current_price) as avg_price,
                    COUNT(CASE WHEN extraction_method = 'proxy' THEN 1 END) as proxy_used,
                    COUNT(CASE WHEN last_extraction_status = 'failed' THEN 1 END) as failed_extractions
                FROM dashboard_products 
                WHERE monitoring_enabled = 1 AND availability_status = 'active'
            ''')
            
            row = cursor.fetchone()
            
            # آخر تنبيه
            cursor.execute('''
                SELECT COUNT(*), MAX(alert_sent_at)
                FROM price_alerts
                WHERE DATE(alert_sent_at) = DATE('now')
            ''')
            
            alerts_row = cursor.fetchone()
            
            # إحصائيات الاستخلاص
            extraction_stats = self.get_extraction_stats()
            
            return {
                'total_monitored': row[0] if row else 0,
                'drops_detected': row[1] if row else 0,
                'recently_monitored': row[2] if row else 0,
                'avg_price': round(row[3], 2) if row and row[3] else 0.0,
                'proxy_used': row[4] if row else 0,
                'failed_extractions': row[5] if row else 0,
                'alerts_today': alerts_row[0] if alerts_row else 0,
                'last_alert': alerts_row[1] if alerts_row and alerts_row[1] else None,
                'monitoring_enabled': MONITORING_CONFIG['enabled'],
                'next_monitoring': self._calculate_next_monitoring_time(),
                'extraction_stats': extraction_stats['summary']
            }
            
        except Exception as e:
            logger.error(f"❌ خطأ في جلب إحصائيات المراقبة: {e}")
            return {}
    
    def _calculate_next_monitoring_time(self) -> str:
        """حساب وقت المراقبة التالي"""
        if not MONITORING_CONFIG['enabled']:
            return "معطل"
        
        next_time = datetime.now() + timedelta(seconds=MONITORING_CONFIG['interval'])
        return next_time.strftime("%H:%M:%S")
    
    def _log_update_event(self, event_type: str, asin: str, old_value: str = None, 
                         new_value: str = None, discount_change: float = 0.0, 
                         extraction_method: str = None):
        """تسجيل حدث تحديث"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO update_events (event_type, asin, old_value, new_value, 
                                         discount_change, extraction_method)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (event_type, asin, old_value, new_value, discount_change, extraction_method))
            
            conn.commit()
        except Exception as e:
            logger.error(f"❌ خطأ في تسجيل الحدث: {e}")
    
    def _update_display_stats(self):
        """تحديث إحصائيات العرض"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    COUNT(*) as total,
                    COUNT(CASE WHEN availability_status = 'active' THEN 1 END) as active,
                    AVG(current_price) as avg_price,
                    AVG(discount_percentage) as avg_discount,
                    MAX(discount_percentage) as best_deal
                FROM dashboard_products
                WHERE current_price > 0
            ''')
            
            row = cursor.fetchone()
            
            today = datetime.now().date().isoformat()
            
            cursor.execute('''
                INSERT OR REPLACE INTO display_stats 
                (created_date, total_products, active_products, avg_price, avg_discount, best_deal_percentage, last_refresh)
                VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (
                today, 
                row[0] if row else 0, 
                row[1] if row else 0, 
                row[2] if row else 0.0,
                row[3] if row else 0.0,
                row[4] if row else 0.0
            ))
            
            conn.commit()
            
        except Exception as e:
            logger.error(f"❌ خطأ في تحديث الإحصائيات: {e}")
    
    def get_all_products(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """الحصول على جميع المنتجات"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT asin, product_name, current_price, reference_price, discount_percentage,
                       currency, availability_status, last_updated, source_url, category,
                       price_change_count, initial_price, monitoring_enabled, price_drop_detected,
                       extraction_method, last_extraction_status
                FROM dashboard_products
                ORDER BY last_updated DESC
                LIMIT ? OFFSET ?
            ''', (limit, offset))
            
            products = []
            for row in cursor.fetchall():
                products.append({
                    'asin': row[0],
                    'product_name': row[1] or f"منتج {row[0]}",
                    'current_price': row[2],
                    'reference_price': row[3],
                    'discount_percentage': row[4],
                    'currency': row[5],
                    'availability_status': row[6],
                    'last_updated': row[7],
                    'source_url': row[8],
                    'category': row[9] or 'غير مصنف',
                    'price_change_count': row[10] or 0,
                    'initial_price': row[11],
                    'monitoring_enabled': bool(row[12]) if row[12] is not None else True,
                    'price_drop_detected': bool(row[13]) if row[13] is not None else False,
                    'extraction_method': row[14] or 'direct',
                    'last_extraction_status': row[15] or 'success',
                    'has_discount': row[3] and row[3] > row[2] and row[2] > 0
                })
            
            return products
            
        except Exception as e:
            logger.error(f"❌ خطأ في جلب المنتجات: {e}")
            return []
    
    def get_product_count(self) -> Dict:
        """الحصول على عدد المنتجات"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    COUNT(*) as total,
                    COUNT(CASE WHEN availability_status = 'active' THEN 1 END) as active,
                    COUNT(CASE WHEN availability_status = 'out_of_stock' THEN 1 END) as out_of_stock,
                    COUNT(CASE WHEN availability_status = 'discontinued' THEN 1 END) as discontinued,
                    COUNT(CASE WHEN monitoring_enabled = 1 THEN 1 END) as monitored,
                    COUNT(CASE WHEN extraction_method = 'proxy' THEN 1 END) as proxy_used
                FROM dashboard_products
            ''')
            
            row = cursor.fetchone()
            return {
                'total': row[0] if row else 0,
                'active': row[1] if row else 0,
                'out_of_stock': row[2] if row else 0,
                'discontinued': row[3] if row else 0,
                'monitored': row[4] if row else 0,
                'proxy_used': row[5] if row else 0
            }
            
        except Exception as e:
            logger.error(f"❌ خطأ في جلب العدد: {e}")
            return {'total': 0, 'active': 0, 'out_of_stock': 0, 'discontinued': 0}
    
    def search_products(self, query: str, limit: int = 20) -> List[Dict]:
        """البحث عن منتجات"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            search_term = f"%{query}%"
            
            cursor.execute('''
                SELECT asin, product_name, current_price, reference_price, discount_percentage,
                       currency, availability_status, last_updated, category, extraction_method
                FROM dashboard_products
                WHERE asin LIKE ? OR product_name LIKE ? OR category LIKE ?
                ORDER BY last_updated DESC
                LIMIT ?
            ''', (search_term, search_term, search_term, limit))
            
            products = []
            for row in cursor.fetchall():
                products.append({
                    'asin': row[0],
                    'product_name': row[1] or f"منتج {row[0]}",
                    'current_price': row[2],
                    'reference_price': row[3],
                    'discount_percentage': row[4],
                    'currency': row[5],
                    'availability_status': row[6],
                    'last_updated': row[7],
                    'category': row[8] or 'غير مصنف',
                    'extraction_method': row[9] or 'direct',
                    'has_discount': row[3] and row[3] > row[2] and row[2] > 0
                })
            
            return products
            
        except Exception as e:
            logger.error(f"❌ خطأ في البحث: {e}")
            return []
    
    def get_best_deals(self, min_discount: float = 20.0, limit: int = 10) -> List[Dict]:
        """الحصول على أفضل العروض"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT asin, product_name, current_price, reference_price, discount_percentage,
                       currency, last_updated, category, extraction_method
                FROM dashboard_products
                WHERE discount_percentage >= ? AND current_price > 0 AND availability_status = 'active'
                ORDER BY discount_percentage DESC, current_price ASC
                LIMIT ?
            ''', (min_discount, limit))
            
            deals = []
            for row in cursor.fetchall():
                deals.append({
                    'asin': row[0],
                    'product_name': row[1] or f"منتج {row[0]}",
                    'current_price': row[2],
                    'reference_price': row[3],
                    'discount_percentage': row[4],
                    'currency': row[5],
                    'last_updated': row[6],
                    'category': row[7] or 'غير مصنف',
                    'extraction_method': row[8] or 'direct'
                })
            
            return deals
            
        except Exception as e:
            logger.error(f"❌ خطأ في جلب العروض: {e}")
            return []
    
    def close(self):
        """إغلاق الاتصالات"""
        with self.lock:
            if hasattr(self.local, 'connection'):
                try:
                    self.local.connection.close()
                except:
                    pass

# ==================== نظام الإشعارات البريدية ====================
class EmailNotifier:
    """نظام إرسال الإشعارات البريدية"""
    
    @staticmethod
    def send_price_drop_alert(asin: str, product_name: str, old_price: float, 
                            new_price: float, drop_percentage: float, 
                            product_url: str = None, extraction_method: str = 'direct'):
        """إرسال إشعار انخفاض السعر"""
        if not MONITORING_CONFIG['email_notifications']:
            print(f"📧 (محاكاة) إشعار انخفاض السعر لـ {asin}: {drop_percentage:.1f}% (الطريقة: {extraction_method})")
            return True
        
        try:
            # تنظيف كلمة المرور من المسافات
            cleaned_password = EMAIL_CONFIG['sender_password'].replace(' ', '')
            
            # إنشاء الرسالة
            subject = f"🚨 انخفاض كبير في السعر! {product_name[:50]}..."
            body = f"""
            اكتشف نظام المراقبة انخفاضاً كبيراً في سعر المنتج:
            
            📦 المنتج: {product_name}
            🔢 كود المنتج: {asin}
            
            💰 السعر السابق: ${old_price:.2f}
            💰 السعر الحالي: ${new_price:.2f}
            
            📉 نسبة الانخفاض: {drop_percentage:.1f}%
            💵 التوفير: ${old_price - new_price:.2f}
            
            🛠️  طريقة الاستخلاص: {extraction_method}
            
            🔗 رابط المنتج: {product_url or f"https://www.amazon.com/dp/{asin}"}
            
            ⏰ وقت الاكتشاف: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            
            هذا الإشعار تلقائي من نظام مراقبة الأسعار.
            """
            
            html_body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; direction: rtl; text-align: right;">
                <h2 style="color: #d32f2f;">🚨 انخفاض كبير في السعر!</h2>
                <div style="background: #f5f5f5; padding: 20px; border-radius: 10px; margin: 15px 0;">
                    <h3>📦 {product_name}</h3>
                    <p><strong>🔢 كود المنتج:</strong> {asin}</p>
                    
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin: 20px 0;">
                        <div style="background: white; padding: 15px; border-radius: 8px; text-align: center;">
                            <div style="color: #666; font-size: 0.9rem;">السعر السابق</div>
                            <div style="text-decoration: line-through; color: #999; font-size: 1.2rem;">${old_price:.2f}</div>
                        </div>
                        <div style="background: #e8f5e9; padding: 15px; border-radius: 8px; text-align: center;">
                            <div style="color: #666; font-size: 0.9rem;">السعر الحالي</div>
                            <div style="color: #4caf50; font-size: 1.5rem; font-weight: bold;">${new_price:.2f}</div>
                        </div>
                    </div>
                    
                    <div style="background: linear-gradient(45deg, #ff6b6b, #ee5a24); color: white; 
                                padding: 15px; border-radius: 8px; text-align: center; margin: 20px 0;">
                        <div style="font-size: 2rem; font-weight: bold;">{drop_percentage:.1f}%</div>
                        <div>نسبة الانخفاض</div>
                    </div>
                    
                    <div style="background: #4caf50; color: white; padding: 15px; border-radius: 8px; 
                                text-align: center; font-size: 1.2rem; margin: 15px 0;">
                        💵 توفير: ${old_price - new_price:.2f}
                    </div>
                    
                    <div style="background: #2196f3; color: white; padding: 10px; border-radius: 8px; 
                                text-align: center; font-size: 0.9rem; margin: 10px 0;">
                        🛠️  طريقة الاستخلاص: {extraction_method}
                    </div>
                    
                    <p>
                        <strong>🔗 رابط المنتج:</strong><br>
                        <a href="{product_url or f'https://www.amazon.com/dp/{asin}'}" 
                           style="color: #2196f3; word-break: break-all;">
                            {product_url or f"https://www.amazon.com/dp/{asin}"}
                        </a>
                    </p>
                    
                    <p style="color: #666; font-size: 0.9rem; margin-top: 20px;">
                        ⏰ وقت الاكتشاف: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                    </p>
                </div>
                <p style="color: #999; font-size: 0.8rem; border-top: 1px solid #eee; padding-top: 10px;">
                    هذا الإشعار تلقائي من نظام مراقبة الأسعار.
                </p>
            </body>
            </html>
            """
            
            # إنشاء الرسالة
            msg = MIMEMultipart('alternative')
            msg['From'] = EMAIL_CONFIG['sender_email']
            msg['To'] = EMAIL_CONFIG['receiver_email']
            msg['Subject'] = subject
            
            # إضافة النص العادي والHTML
            part1 = MIMEText(body, 'plain')
            part2 = MIMEText(html_body, 'html')
            
            msg.attach(part1)
            msg.attach(part2)
            
            # إرسال البريد
            server = smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port'])
            server.starttls()
            server.login(EMAIL_CONFIG['sender_email'], cleaned_password)
            server.send_message(msg)
            server.quit()
            
            logger.info(f"📧 تم إرسال إشعار انخفاض السعر لـ {asin} إلى {EMAIL_CONFIG['receiver_email']}")
            return True
            
        except Exception as e:
            logger.error(f"❌ فشل إرسال الإشعار البريدية: {e}")
            print(f"📧 (محاكاة) إشعار انخفاض السعر لـ {asin}: {drop_percentage:.1f}%")
            return True
    
    @staticmethod
    def send_monitoring_summary(monitored_count: int, alerts_count: int, drops_detected: int,
                               extraction_stats: Dict = None):
        """إرسال ملخص المراقبة"""
        if not MONITORING_CONFIG['email_notifications']:
            print(f"📧 (محاكاة) ملخص المراقبة: {monitored_count} منتج، {drops_detected} انخفاضات")
            return True
        
        try:
            # تنظيف كلمة المرور من المسافات
            cleaned_password = EMAIL_CONFIG['sender_password'].replace(' ', '')
            
            # إضافة إحصائيات الاستخلاص إذا موجودة
            extraction_info = ""
            if extraction_stats:
                extraction_info = f"""
                
            📊 إحصائيات الاستخلاص:
            • إجمالي المحاولات: {extraction_stats.get('total_attempts', 0)}
            • نجاح مباشر: {extraction_stats.get('total_direct_success', 0)}
            • نجاح بالوسيط: {extaration_stats.get('total_proxy_success', 0)}
            • نسبة النجاح: {extraction_stats.get('avg_success_rate', 0)}%
            """
            
            subject = f"📊 ملخص مراقبة الأسعار - {datetime.now().strftime('%Y-%m-%d')}"
            body = f"""
            ملخص مراقبة الأسعار:
            
            📅 التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            
            📈 الإحصائيات:
            • عدد المنتجات المراقبة: {monitored_count}
            • عدد المنتجات التي تمت زيارتها: {monitored_count}
            • عدد التنبيهات المكتشفة: {alerts_count}
            • عدد الانخفاضات الكبيرة: {drops_detected}
            {extraction_info}
            
            تمت المراقبة تلقائياً بواسطة النظام مع الوسيط الذكي.
            """
            
            msg = MIMEText(body, 'plain')
            msg['From'] = EMAIL_CONFIG['sender_email']
            msg['To'] = EMAIL_CONFIG['receiver_email']
            msg['Subject'] = subject
            
            server = smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port'])
            server.starttls()
            server.login(EMAIL_CONFIG['sender_email'], cleaned_password)
            server.send_message(msg)
            server.quit()
            
            logger.info(f"📧 تم إرسال ملخص المراقبة")
            return True
            
        except Exception as e:
            logger.error(f"❌ فشل إرسال ملخص المراقبة: {e}")
            print(f"📧 (محاكاة) ملخص المراقبة: {monitored_count} منتج، {drops_detected} انخفاضات")
            return True

# ==================== نظام استخلاص مع الوسيط الذكي ====================
class DiscountAwareAmazonExtractor:
    """مستخلص ذكي مع تتبع الأسعار المرجعية والخصومات والوسيط"""
    
    def __init__(self):
        try:
            import fake_useragent
            
            # إضافة المدير الذكي مع الوسيط
            self.browser_simulator = SmartBrowserSimulator()
            
            # الحفاظ على الجلسة القديمة للتوافق
            self.session = requests.Session()
            
            retry_strategy = Retry(
                total=2,
                backoff_factor=1,
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=["GET"]
            )
            adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=20, pool_maxsize=20)
            self.session.mount("http://", adapter)
            self.session.mount("https://", adapter)
            
            self.ua_generator = fake_useragent.UserAgent()
            
            print("✅ مكتبات الاستخلاص - جاهزة مع الوسيط الذكي")
        except ImportError as e:
            print(f"⚠️  خطأ في استيراد مكتبات الاستخلاص: {e}")
            self.session = None
            self.ua_generator = None
            self.browser_simulator = None
        
    def extract_asin_from_url(self, url: str) -> Optional[str]:
        """استخراج ASIN من رابط Amazon.com"""
        patterns = [
            r'/dp/([A-Z0-9]{10})',
            r'/gp/product/([A-Z0-9]{10})',
            r'/product/([A-Z0-9]{10})',
            r'/d/([A-Z0-9]{10})',
            r'/exec/obidos/ASIN/([A-Z0-9]{10})',
            r'/([A-Z0-9]{10})(?:[/?&]|$)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url, re.IGNORECASE)
            if match:
                asin = match.group(1).upper()
                if len(asin) == 10 and asin.isalnum():
                    return asin
        
        return None
    
    def extract_price(self, url: str) -> Tuple[Optional[Dict], str, str]:
        """استخلاص السعر مع تتبع الأسعار المرجعية والخصومات"""
        extraction_method = "direct"
        attempts_log = []
        
        try:
            if not self.session:
                return None, "مكتبات الاستخلاص غير مثبتة", extraction_method
            
            if 'amazon.com' not in url.lower():
                return None, "النظام يدعم Amazon.com فقط", extraction_method
            
            asin = self.extract_asin_from_url(url)
            if not asin:
                return None, "لم يتم العثور على ASIN في الرابط", extraction_method
            
            # المحاولة 1: الاستخلاص المباشر (إذا كان مفعلاً)
            if PROXY_CONFIG.get('use_direct_first', True):
                logger.info(f"🔍 المحاولة 1: استخلاص مباشر لـ {asin}")
                
                headers = self._get_global_headers()
                parsed_url = urlparse(url)
                headers['Referer'] = f"{parsed_url.scheme}://{parsed_url.netloc}/"
                
                # تأخير عشوائي قبل المحاولة
                time.sleep(random.uniform(2, 4))
                
                try:
                    response = self.session.get(
                        url, 
                        headers=headers, 
                        timeout=20, 
                        allow_redirects=True
                    )
                    
                    if response.status_code == 200:
                        html_content = response.text
                        product_data = self._extract_with_discount_awareness(html_content, asin)
                        
                        if product_data:
                            product_data['url'] = url
                            extraction_method = "direct"
                            logger.info(f"✅ نجاح الاستخلاص المباشر لـ {asin}")
                            return product_data, "تم الاستخلاص بنجاح (مباشر)", extraction_method
                    else:
                        logger.warning(f"⚠️  فشل مباشر لـ {asin}: {response.status_code}")
                        attempts_log.append(f"مباشر: {response.status_code}")
                except Exception as e:
                    logger.warning(f"⚠️  خطأ في الاستخلاص المباشر لـ {asin}: {str(e)[:100]}")
                    attempts_log.append(f"مباشر خطأ: {str(e)[:50]}")
            
            # المحاولة 2: استخدام النظام الذكي
            if self.browser_simulator:
                logger.info(f"🔍 المحاولة 2: استخلاص ذكي لـ {asin}")
                
                response, smart_attempts = self.browser_simulator.smart_get_request(
                    url, 
                    max_retries=2,
                    use_proxy=False
                )
                
                if response and response.status_code == 200:
                    html_content = response.text
                    product_data = self._extract_with_discount_awareness(html_content, asin)
                    
                    if product_data:
                        product_data['url'] = url
                        extraction_method = "smart"
                        logger.info(f"✅ نجاح الاستخلاص الذكي لـ {asin}")
                        return product_data, "تم الاستخلاص بنجاح (ذكي)", extraction_method
                else:
                    logger.warning(f"⚠️  فشل ذكي لـ {asin}")
                    attempts_log.extend([f"ذكي: {a['status']}" for a in smart_attempts])
            
            # المحاولة 3: استخدام الوسيط (ScraperAPI)
            if PROXY_CONFIG.get('retry_with_proxy', True) and PROXY_CONFIG.get('scraperapi_key'):
                logger.info(f"🔍 المحاولة 3: استخلاص بالوسيط لـ {asin}")
                
                proxy_url = self._get_proxy_url(url)
                if proxy_url:
                    try:
                        headers = self._get_global_headers()
                        time.sleep(random.uniform(3, 6))
                        
                        response = self.session.get(
                            proxy_url,
                            headers=headers,
                            timeout=PROXY_CONFIG['timeout'],
                            allow_redirects=True
                        )
                        
                        if response.status_code == 200:
                            html_content = response.text
                            product_data = self._extract_with_discount_awareness(html_content, asin)
                            
                            if product_data:
                                product_data['url'] = url
                                extraction_method = "proxy"
                                logger.info(f"✅ نجاح الاستخلاص بالوسيط لـ {asin}")
                                return product_data, "تم الاستخلاص بنجاح (وسيط)", extraction_method
                        else:
                            logger.warning(f"⚠️  فشل وسيط لـ {asin}: {response.status_code}")
                            attempts_log.append(f"وسيط: {response.status_code}")
                    except Exception as e:
                        logger.warning(f"⚠️  خطأ في الاستخلاص بالوسيط لـ {asin}: {str(e)[:100]}")
                        attempts_log.append(f"وسيط خطأ: {str(e)[:50]}")
            
            # جميع المحاولات فشلت
            error_msg = f"فشل جميع طرق الاستخلاص. المحاولات: {', '.join(attempts_log)}"
            logger.error(f"❌ {error_msg}")
            return None, error_msg, "failed"
            
        except Exception as e:
            error_msg = f"خطأ عام في الاستخلاص: {str(e)[:200]}"
            logger.error(f"❌ {error_msg}")
            return None, error_msg, extraction_method
    
    def _get_proxy_url(self, url):
        """إنشاء رابط الوسيط"""
        if not PROXY_CONFIG.get('scraperapi_key'):
            return None
        
        try:
            encoded_url = quote(url, safe='')
            proxy_url = f"{PROXY_CONFIG['scraperapi_url']}/?api_key={PROXY_CONFIG['scraperapi_key']}&url={encoded_url}"
            
            # إضافة إعدادات متقدمة لـ ScraperAPI
            proxy_url += "&render=true&country_code=us&device_type=desktop&session_number=1"
            
            return proxy_url
        except:
            return None
    
    def _get_global_headers(self) -> Dict:
        """إرجاع رأسيات موحدة"""
        try:
            user_agent = self.ua_generator.random if self.ua_generator else 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
        except:
            user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
        
        return {
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
            'TE': 'trailers'
        }
    
    def _extract_with_discount_awareness(self, html: str, asin: str) -> Optional[Dict]:
        """استخراج البيانات مع وعي الخصومات"""
        
        current_price_data = self._extract_current_price(html, asin)
        if not current_price_data:
            return None
        
        reference_price_data = self._extract_reference_price(html, asin)
        
        current_price = current_price_data.get('price', 0.0)
        reference_price = reference_price_data.get('reference_price', 0.0)
        discount_percentage = 0.0
        
        if reference_price > current_price > 0:
            discount_percentage = ((reference_price - current_price) / reference_price) * 100
        
        title = self._extract_product_title(html)
        
        return {
            'asin': asin,
            'price': current_price,
            'reference_price': reference_price,
            'discount_percentage': round(discount_percentage, 1),
            'currency': 'USD',
            'title': title or f'منتج {asin}'
        }
    
    def _extract_current_price(self, html: str, asin: str) -> Optional[Dict]:
        """استخراج السعر الحالي"""
        try:
            # أنماط محسنة للبحث عن السعر
            price_patterns = [
                (r'"priceCurrency":"USD".*?"price":"([\d.]+)"', 1),  # JSON-LD
                (r'data-a-price="\d*\.?\d*".*?>\s*([\$\d.,]+)\s*<', 0),
                (r'<span[^>]*id="price_inside_buybox"[^>]*>\s*([\$\d.,]+)\s*</span>', 0),
                (r'<span[^>]*id="priceblock_ourprice"[^>]*>\s*([\$\d.,]+)\s*</span>', 0),
                (r'<span[^>]*id="priceblock_dealprice"[^>]*>\s*([\$\d.,]+)\s*</span>', 0),
                (r'<span[^>]*class="a-price-whole"[^>]*>([\d,]+)</span>', 0),
                (r'<span[^>]*class="a-price[^"]*"[^>]*>.*?<span[^>]*class="a-offscreen"[^>]*>(.*?)</span>', 0),
                (r'<span[^>]*class="apexPriceToPay"[^>]*>.*?<span[^>]*class="a-offscreen"[^>]*>(.*?)</span>', 0),
                (r'\$\s*([\d,]+\.?\d*)(?![^<]*?</span>)', 1),
                (r'>\s*\$\s*([\d,]+\.?\d*)\s*<', 1),
                (r'"displayPrice":"\$([\d.]+)"', 1),  # نمط جديد
                (r'"formattedPrice":"\$([\d.]+)"', 1),  # نمط جديد
            ]
            
            for pattern, group_idx in price_patterns:
                matches = re.findall(pattern, html, re.IGNORECASE | re.DOTALL)
                for match in matches:
                    if isinstance(match, tuple):
                        price_text = match[group_idx]
                    else:
                        price_text = match
                    
                    price = self._extract_usd_price_from_text(price_text)
                    
                    if price and self._is_valid_usd_price(price):
                        return {'price': price}
                        
        except Exception:
            pass
        
        return None
    
    def _extract_reference_price(self, html: str, asin: str) -> Optional[Dict]:
        """استخراج السعر المرجعي"""
        try:
            reference_patterns = [
                (r'<span[^>]*class="a-price a-text-price"[^>]*>.*?<span[^>]*class="a-offscreen"[^>]*>(.*?)</span>', 0),
                (r'<span[^>]*class="a-text-strike"[^>]*>(.*?)</span>', 0),
                (r'<s[^>]*class="a-text-strike"[^>]*>(.*?)</s>', 0),
                (r'<span[^>]*style="text-decoration: line-through"[^>]*>(.*?)</span>', 0),
                (r'>\s*List Price:\s*</span>.*?\$\s*([\d,]+\.?\d*)', 1),
                (r'>\s*MSRP:\s*</span>.*?\$\s*([\d,]+\.?\d*)', 1),
                (r'>\s*Was:\s*</span>.*?\$\s*([\d,]+\.?\d*)', 1),
                (r'>\s*Original price:\s*</span>.*?\$\s*([\d,]+\.?\d*)', 1),
                (r'>\s*Price Was:\s*</span>.*?\$\s*([\d,]+\.?\d*)', 1),
                (r'>\s*Suggested Retail Price:\s*</span>.*?\$\s*([\d,]+\.?\d*)', 1),
                (r'"priceCurrency":"USD".*?"price":"([\d.]+)"', 1),
                (r'"highPrice":\s*([\d.]+)', 1),
                (r'"listPrice":\s*([\d.]+)', 1),
                (r'"strikePrice":\s*([\d.]+)', 1),  # نمط جديد
            ]
            
            best_reference_price = 0.0
            
            for pattern, group_idx in reference_patterns:
                match = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
                if match:
                    price_text = match.group(group_idx).strip()
                    price = self._extract_usd_price_from_text(price_text)
                    
                    if price and self._is_valid_usd_price(price):
                        if price > best_reference_price:
                            best_reference_price = price
            
            if best_reference_price > 0:
                return {'reference_price': best_reference_price}
                
        except Exception:
            pass
        
        return {'reference_price': 0.0}
    
    def _extract_product_title(self, html: str) -> Optional[str]:
        """استخراج عنوان المنتج"""
        try:
            title_patterns = [
                r'<h1[^>]*id="title"[^>]*>(.*?)</h1>',
                r'<span[^>]*id="productTitle"[^>]*>(.*?)</span>',
                r'<meta[^>]*property="og:title"[^>]*content="([^"]*)"',
                r'<title[^>]*>(.*?)</title>',
                r'"title":"([^"]+)"',  # نمط جديد
            ]
            
            for pattern in title_patterns:
                match = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
                if match:
                    title = match.group(1).strip()
                    title = re.sub(r'<[^>]*>', '', title)
                    title = re.sub(r'\s+', ' ', title).strip()
                    title = title.replace('Amazon.com', '').strip()
                    
                    if title and len(title) > 5:
                        return title[:200]
                        
        except Exception:
            pass
        
        return None
    
    def _extract_usd_price_from_text(self, text: str) -> Optional[float]:
        """استخراج السعر USD من نص معين"""
        try:
            text = re.sub(r'<[^>]*>', '', text)
            text = re.sub(r'\s+', ' ', text).strip()
            
            usd_patterns = [
                r'\$\s*([\d,]+\.?\d*)',
                r'USD\s*([\d,]+\.?\d*)',
                r'([\d,]+\.?\d*)\s*\$',
                r'([\d,]+\.?\d*)\s*USD',
            ]
            
            for pattern in usd_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    price_str = match.group(1).replace(',', '')
                    return self._safe_float_convert(price_str)
                    
        except Exception:
            pass
        
        return None
    
    def _is_valid_usd_price(self, price: float) -> bool:
        """التحقق من صحة السعر USD"""
        if not price or price <= 0:
            return False
        
        if price < 0.5:
            return False
        
        if price > 100000:
            return False
        
        return True
    
    def _safe_float_convert(self, value: Any) -> Optional[float]:
        """تحويل آمن للقيمة إلى عدد عشري"""
        try:
            if value is None:
                return None
            
            str_value = str(value).strip()
            cleaned = re.sub(r'[^\d.,]', '', str_value)
            
            if ',' in cleaned and '.' in cleaned:
                cleaned = cleaned.replace(',', '')
            elif ',' in cleaned:
                if cleaned.count(',') == 1 and len(cleaned.split(',')[1]) <= 2:
                    cleaned = cleaned.replace(',', '.')
                else:
                    cleaned = cleaned.replace(',', '')
            
            result = float(cleaned) if cleaned else None
            
            if result and 0.1 <= result <= 1000000:
                return result
            else:
                return None
                
        except (ValueError, TypeError, AttributeError):
            return None

# ==================== نظام التكامل مع الخصومات ====================
class DiscountDashboardIntegrator:
    """مكامل بين نظام الزحف ولوحة التحكم"""
    
    def __init__(self, dashboard_db: EnhancedDatabase):
        self.dashboard_db = dashboard_db
        self.last_sync_time = datetime.now()
        self.sync_interval = 5
        
    def sync_product_to_dashboard(self, product_data: Dict, extraction_method: str = "direct"):
        """مزامنة منتج إلى لوحة التحكم"""
        try:
            dashboard_data = {
                'asin': product_data.get('asin'),
                'product_name': product_data.get('title', f"منتج {product_data.get('asin')}"),
                'current_price': product_data.get('price', 0.0),
                'reference_price': product_data.get('reference_price', 0.0),
                'discount_percentage': product_data.get('discount_percentage', 0.0),
                'currency': product_data.get('currency', 'USD'),
                'availability_status': self._determine_availability(product_data),
                'source_url': product_data.get('url'),
                'category': product_data.get('category', 'غير مصنف'),
                'extraction_method': extraction_method
            }
            
            success = self.dashboard_db.save_or_update_product(dashboard_data)
            
            if success:
                discount = dashboard_data['discount_percentage']
                if discount > 0:
                    logger.info(f"🔄 تم مزامنة المنتج {dashboard_data['asin']} مع خصم {discount:.1f}% (الطريقة: {extraction_method})")
                else:
                    logger.info(f"🔄 تم مزامنة المنتج {dashboard_data['asin']} (الطريقة: {extraction_method})")
            else:
                logger.warning(f"⚠️  فشل مزامنة المنتج {dashboard_data['asin']}")
                
        except Exception as e:
            logger.error(f"❌ خطأ في مزامنة المنتج: {e}")
    
    def _determine_availability(self, product_data: Dict) -> str:
        """تحديد حالة التوفر"""
        price = product_data.get('price', 0)
        
        if price <= 0:
            return 'out_of_stock'
        
        return 'active'
    
    def sync_batch_to_dashboard(self, products_list: List[Dict]):
        """مزامنة مجموعة منتجات"""
        success_count = 0
        for product in products_list:
            try:
                self.sync_product_to_dashboard(product)
                success_count += 1
            except:
                continue
        
        logger.info(f"📊 تم مزامنة {success_count}/{len(products_list)} منتج")
        return success_count

# ==================== نظام المراقبة التلقائي مع الوسيط ====================
class PriceMonitoringSystem:
    """نظام مراقبة الأسعار التلقائي مع الوسيط الذكي"""
    
    def __init__(self, dashboard_db: EnhancedDatabase, extractor: DiscountAwareAmazonExtractor):
        self.dashboard_db = dashboard_db
        self.extractor = extractor
        self.is_monitoring = False
        self.monitoring_thread = None
        self.monitoring_stats = {
            'total_monitored': 0,
            'price_drops_detected': 0,
            'last_monitoring': None,
            'next_monitoring': None,
            'extraction_stats': {}
        }
        
        # بدء المراقبة إذا كانت مفعلة
        if MONITORING_CONFIG['enabled']:
            self.start_monitoring()
    
    def start_monitoring(self):
        """بدء نظام المراقبة"""
        if self.is_monitoring:
            logger.warning("⚠️  نظام المراقبة يعمل بالفعل")
            return
        
        self.is_monitoring = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        logger.info("🚀 بدأ نظام المراقبة التلقائية مع الوسيط الذكي")
    
    def stop_monitoring(self):
        """إيقاف نظام المراقبة"""
        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        
        logger.info("🛑 توقف نظام المراقبة التلقائية")
    
    def _monitoring_loop(self):
        """حلقة المراقبة الرئيسية"""
        while self.is_monitoring:
            try:
                self.run_monitoring_cycle()
                
                # انتظار الفترة المحددة
                time.sleep(MONITORING_CONFIG['interval'])
                
            except Exception as e:
                logger.error(f"❌ خطأ في حلقة المراقبة: {e}")
                time.sleep(60)  # انتظار دقيقة ثم إعادة المحاولة
    
    def run_monitoring_cycle(self):
        """تشغيل دورة مراقبة واحدة مع الوسيط الذكي"""
        try:
            logger.info("🔄 بدء دورة مراقبة جديدة...")
            
            # جلب المنتجات للمراقبة
            products = self.dashboard_db.get_products_for_monitoring(
                limit=MONITORING_CONFIG['monitoring_limit']
            )
            
            if not products:
                logger.info("⚠️  لا توجد منتجات للمراقبة")
                return
            
            logger.info(f"📊 جاري مراقبة {len(products)} منتج...")
            
            drops_detected = 0
            monitored_count = 0
            successful_extractions = 0
            failed_extractions = 0
            
            # ترتيب عشوائي للمنتجات لتجنب الأنماط الثابتة
            random.shuffle(products)
            
            for product in products:
                try:
                    monitored_count += 1
                    asin = product['asin']
                    
                    # اختيار طريقة الاستخلاص بناءً على السجل السابق
                    preferred_method = product.get('extraction_method', 'direct')
                    if product.get('last_extraction_status') == 'failed':
                        # إذا فشلت آخر محاولة، جرب طريقة مختلفة
                        preferred_method = 'proxy' if preferred_method == 'direct' else 'direct'
                    
                    # تغيير الهوية بشكل دوري
                    if MONITORING_CONFIG['smart_rotation'] and monitored_count % 5 == 0:
                        time.sleep(random.uniform(5, 10))  # استراحة أطول
                    
                    # إضافة تأخير ذكي (متغير)
                    delay_range = MONITORING_CONFIG['delay_between_requests']
                    delay = random.uniform(delay_range[0], delay_range[1])
                    time.sleep(delay)
                    
                    # محاولة استخراج السعر
                    extraction, message, extraction_method = self.extractor.extract_price(product['source_url'])
                    
                    if extraction:
                        successful_extractions += 1
                        current_price = extraction['price']
                        old_price = product['current_price']
                        initial_price = product['initial_price']
                        
                        # تسجيل نجاح الاستخلاص
                        self.dashboard_db.log_extraction_stat(success=True, method=extraction_method)
                        self.dashboard_db.update_extraction_status(asin, 'success', extraction_method)
                        
                        # تحديث وقت المراقبة
                        self.dashboard_db.update_monitoring_time(asin)
                        
                        # التحقق من انخفاض السعر
                        price_drop_detected = False
                        
                        if initial_price > 0 and current_price > 0:
                            # حساب نسبة الانخفاض من السعر الأولي
                            drop_percentage = ((initial_price - current_price) / initial_price) * 100
                            
                            if drop_percentage >= MONITORING_CONFIG['price_drop_threshold']:
                                # إشعار انخفاض السعر
                                price_drop_detected = True
                                drops_detected += 1
                                
                                logger.info(f"⚠️  اكتشاف انخفاض سعر لـ {asin}: {drop_percentage:.1f}% (الطريقة: {extraction_method})")
                                
                                # إضافة تنبيه
                                self.dashboard_db.add_price_alert(
                                    asin=asin,
                                    old_price=initial_price,
                                    new_price=current_price,
                                    drop_percentage=drop_percentage,
                                    extraction_method=extraction_method
                                )
                                
                                # تحديث حالة المنتج
                                self.dashboard_db.mark_price_drop_detected(asin)
                                
                                # إرسال إشعار بريدي
                                EmailNotifier.send_price_drop_alert(
                                    asin=asin,
                                    product_name=product['product_name'],
                                    old_price=initial_price,
                                    new_price=current_price,
                                    drop_percentage=drop_percentage,
                                    product_url=product['source_url'],
                                    extraction_method=extraction_method
                                )
                        
                        # تسجيل سجل المراقبة
                        self.dashboard_db.add_monitoring_log(
                            asin=asin,
                            old_price=old_price,
                            new_price=current_price,
                            status="success" if not price_drop_detected else "price_drop",
                            message=f"السعر الحالي: ${current_price:.2f}" + 
                                   (f" (انخفاض: {drop_percentage:.1f}%)" if price_drop_detected else ""),
                            extraction_method=extraction_method
                        )
                        
                        # تحديث السعر في قاعدة البيانات
                        if current_price != old_price:
                            self.dashboard_db.save_or_update_product({
                                'asin': asin,
                                'current_price': current_price,
                                'product_name': product['product_name'],
                                'extraction_method': extraction_method
                            })
                        
                    else:
                        failed_extractions += 1
                        # تسجيل فشل الاستخلاص
                        self.dashboard_db.log_extraction_stat(success=False, method=extraction_method)
                        self.dashboard_db.update_extraction_status(asin, 'failed', extraction_method)
                        
                        self.dashboard_db.add_monitoring_log(
                            asin=asin,
                            old_price=product['current_price'],
                            new_price=0,
                            status="failed",
                            message=message,
                            extraction_method=extraction_method
                        )
                    
                except Exception as e:
                    failed_extractions += 1
                    logger.error(f"❌ خطأ في مراقبة المنتج {product.get('asin', 'unknown')}: {e}")
                    self.dashboard_db.log_extraction_stat(success=False, method='error')
                    continue
            
            # تحديث الإحصائيات
            self.monitoring_stats = {
                'total_monitored': monitored_count,
                'price_drops_detected': drops_detected,
                'last_monitoring': datetime.now().isoformat(),
                'next_monitoring': (datetime.now() + 
                                  timedelta(seconds=MONITORING_CONFIG['interval'])).isoformat(),
                'extraction_stats': {
                    'successful': successful_extractions,
                    'failed': failed_extractions,
                    'success_rate': (successful_extractions / monitored_count * 100) if monitored_count > 0 else 0
                }
            }
            
            logger.info(f"✅ انتهت دورة المراقبة: {monitored_count} منتج، {drops_detected} انخفاضات، {successful_extractions}/{monitored_count} نجاح")
            
            # إرسال ملخص المراقبة إذا كان هناك انخفاضات أو فشل كبير
            if drops_detected > 0 or failed_extractions > monitored_count * 0.5:
                extraction_stats = self.dashboard_db.get_extraction_stats()['summary']
                EmailNotifier.send_monitoring_summary(
                    monitored_count=monitored_count,
                    alerts_count=drops_detected,
                    drops_detected=drops_detected,
                    extraction_stats=extraction_stats
                )
                
        except Exception as e:
            logger.error(f"❌ خطأ جسيم في دورة المراقبة: {e}")
    
    def get_monitoring_status(self) -> Dict:
        """الحصول على حالة المراقبة"""
        db_stats = self.dashboard_db.get_monitoring_stats()
        return {
            'is_monitoring': self.is_monitoring,
            'stats': {**self.monitoring_stats, **db_stats},
            'config': MONITORING_CONFIG,
            'proxy_config': PROXY_CONFIG
        }

# ==================== إنشاء تطبيق Flask هنا ====================
print("\n🌐 جاري إنشاء تطبيق Flask...")
app = Flask(__name__)
print("✅ تطبيق Flask - تم إنشاؤه بنجاح")

# ==================== النظام الرئيسي مع نظام المراقبة والوسيط ====================
class EnhancedDashboardSystem:
    """النظام الرئيسي مع لوحة تحكم تراكمية ونظام الوسيط الذكي"""
    
    def __init__(self):
        print("\n🔧 جاري تهيئة النظام المحسن مع الوسيط الذكي...")
        
        # تهيئة قاعدة البيانات
        self.dashboard_db = EnhancedDatabase("dashboard_control.db")
        
        # تهيئة المكونات
        self.extractor = DiscountAwareAmazonExtractor()
        self.integrator = DiscountDashboardIntegrator(self.dashboard_db)
        
        # تهيئة نظام المراقبة
        self.monitoring_system = PriceMonitoringSystem(self.dashboard_db, self.extractor)
        
        # تحميل المنتجات الحالية
        self._load_initial_products()
        
        # إعداد مسارات API
        self.setup_routes()
        
        print("\n" + "="*60)
        print("📊 نظام لوحة التحكم التراكمية - الإصدار 21.2")
        print("✅ تم التأسيس بنجاح! (نظام الوسيط الذكي + ScraperAPI)")
        print("="*60)
        print("⚙️  ميزات النظام المحسّن:")
        print("   • 🔄 3 طبقات استخلاص (مباشر، ذكي، وسيط)")
        print("   • 🛡️  ScraperAPI كوسيط احتياطي")
        print("   • 📊 تتبع إحصائيات الاستخلاص")
        print("   • ⚡ استخلاص ذكي بناءً على السجل السابق")
        print("="*60)
    
    def _load_initial_products(self):
        """تحميل المنتجات الحالية"""
        print("\n📥 جاري تحميل المنتجات الحالية...")
        products = self.dashboard_db.get_all_products(limit=50)
        print(f"✅ تم تحميل {len(products)} منتج في الذاكرة")
    
    def setup_routes(self):
        """إعداد مسارات API"""
        
        @app.route('/')
        def home():
            """الصفحة الرئيسية مع لوحة التحكم المحسنة"""
            return render_template_string('''
            <!DOCTYPE html>
            <html lang="ar" dir="rtl">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>📊 لوحة تحكم الزحف الذكي - نظام الوسيط الذكي</title>
                <style>
                    * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Segoe UI', Arial, sans-serif; }
                    body { background: linear-gradient(135deg, #1a237e, #283593); min-height: 100vh; padding: 20px; color: white; }
                    .container { max-width: 1600px; margin: 0 auto; }
                    .header { background: rgba(255, 255, 255, 0.95); padding: 25px; border-radius: 20px; text-align: center; margin-bottom: 20px; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3); }
                    .header h1 { color: #1a237e; margin-bottom: 10px; font-size: 2.5rem; }
                    .dashboard-badge { background: linear-gradient(45deg, #ff6b6b, #ee5a24); color: white; padding: 8px 20px; border-radius: 20px; display: inline-block; margin-top: 10px; font-weight: bold; }
                    
                    .main-content { display: grid; grid-template-columns: 1fr 3fr; gap: 20px; margin-bottom: 20px; }
                    
                    .sidebar { background: white; padding: 25px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2); color: #333; }
                    .main-panel { background: white; padding: 25px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2); color: #333; }
                    
                    .monitoring-panel { background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 20px; border-radius: 15px; margin-bottom: 20px; }
                    
                    .search-box { margin-bottom: 20px; }
                    .url-input { width: 100%; padding: 15px; border: 2px solid #ddd; border-radius: 10px; font-size: 1rem; margin-bottom: 10px; }
                    .analyze-btn { background: linear-gradient(45deg, #2196f3, #1976d2); color: white; border: none; padding: 15px; font-size: 1.2rem; border-radius: 10px; width: 100%; cursor: pointer; font-weight: bold; }
                    
                    .stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 25px; }
                    .stat-card { background: #f5f5f5; padding: 20px; border-radius: 15px; text-align: center; border-left: 5px solid #2196f3; }
                    .stat-card.monitoring { border-left-color: #9c27b0; }
                    .stat-card.alerts { border-left-color: #ff9800; }
                    .stat-card.drops { border-left-color: #f44336; }
                    .stat-card.proxy { border-left-color: #4caf50; }
                    .stat-value { font-size: 2rem; font-weight: bold; color: #1a237e; margin: 10px 0; }
                    .stat-label { color: #666; font-size: 0.9rem; }
                    
                    .products-table-container { margin-top: 25px; max-height: 600px; overflow-y: auto; border-radius: 10px; border: 1px solid #ddd; }
                    .products-table { width: 100%; border-collapse: collapse; }
                    .products-table th { background: #1a237e; color: white; padding: 15px; text-align: right; position: sticky; top: 0; }
                    .products-table td { padding: 12px 15px; border-bottom: 1px solid #eee; text-align: right; }
                    .products-table tr:hover { background: #f5f5f5; }
                    
                    .status-badge { padding: 5px 12px; border-radius: 15px; font-size: 0.8rem; font-weight: bold; }
                    .status-active { background: #4caf50; color: white; }
                    .status-monitoring { background: #9c27b0; color: white; }
                    .status-drop { background: #f44336; color: white; }
                    .status-direct { background: #2196f3; color: white; }
                    .status-proxy { background: #4caf50; color: white; }
                    .status-smart { background: #9c27b0; color: white; }
                    .status-failed { background: #ff5722; color: white; }
                    
                    .discount-badge { padding: 5px 12px; border-radius: 15px; font-size: 0.9rem; font-weight: bold; text-align: center; }
                    .discount-high { background: linear-gradient(45deg, #4caf50, #2e7d32); color: white; }
                    .discount-medium { background: linear-gradient(45deg, #ff9800, #f57c00); color: white; }
                    .discount-low { background: linear-gradient(45deg, #ff5722, #d84315); color: white; }
                    
                    .monitoring-controls { display: flex; gap: 10px; margin: 15px 0; }
                    .monitoring-btn { padding: 10px 20px; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; }
                    .btn-start { background: #4caf50; color: white; }
                    .btn-stop { background: #f44336; color: white; }
                    .btn-run { background: #2196f3; color: white; }
                    
                    .loading { text-align: center; padding: 40px; display: none; }
                    .spinner { border: 5px solid #f3f3f3; border-top: 5px solid #2196f3; border-radius: 50%; width: 60px; height: 60px; animation: spin 1s linear infinite; margin: 0 auto 20px; }
                    @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
                    
                    .alert-card { background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 10px; padding: 15px; margin: 10px 0; }
                    .alert-title { color: #856404; font-weight: bold; }
                    
                    .footer { text-align: center; margin-top: 30px; color: rgba(255, 255, 255, 0.8); font-size: 0.9rem; }
                    
                    @media (max-width: 1200px) {
                        .main-content { grid-template-columns: 1fr; }
                        .stats-grid { grid-template-columns: repeat(2, 1fr); }
                    }
                </style>
                <script>
                    // تحميل البيانات الأولية
                    document.addEventListener('DOMContentLoaded', function() {
                        loadDashboardStats();
                        loadMonitoringStatus();
                        loadProductsTable();
                        loadRecentAlerts();
                        
                        // تحديث تلقائي كل 30 ثانية
                        setInterval(() => {
                            loadDashboardStats();
                            loadMonitoringStatus();
                        }, 30000);
                    });
                    
                    // تحميل إحصائيات النظام
                    async function loadDashboardStats() {
                        try {
                            const response = await fetch('/api/dashboard-stats');
                            const data = await response.json();
                            
                            if (data.status === 'success') {
                                updateStatsDisplay(data.stats);
                            }
                        } catch (error) {
                            console.error('Error loading stats:', error);
                        }
                    }
                    
                    // تحميل حالة المراقبة
                    async function loadMonitoringStatus() {
                        try {
                            const response = await fetch('/api/monitoring-status');
                            const data = await response.json();
                            
                            if (data.status === 'success') {
                                updateMonitoringDisplay(data);
                            }
                        } catch (error) {
                            console.error('Error loading monitoring status:', error);
                        }
                    }
                    
                    // تحميل جدول المنتجات
                    async function loadProductsTable() {
                        const tableBody = document.getElementById('productsTableBody');
                        tableBody.innerHTML = '<tr><td colspan="11" style="text-align: center; padding: 30px;">جاري تحميل البيانات...</td></tr>';
                        
                        try {
                            const response = await fetch('/api/dashboard-products?limit=30');
                            const data = await response.json();
                            
                            if (data.status === 'success') {
                                updateProductsTable(data.products);
                            }
                        } catch (error) {
                            tableBody.innerHTML = '<tr><td colspan="11" style="text-align: center; padding: 30px; color: #f44336;">خطأ في تحميل البيانات</td></tr>';
                        }
                    }
                    
                    // تحميل التنبيهات الحديثة
                    async function loadRecentAlerts() {
                        try {
                            const response = await fetch('/api/recent-alerts');
                            const data = await response.json();
                            
                            if (data.status === 'success') {
                                updateRecentAlerts(data.alerts);
                            }
                        } catch (error) {
                            console.error('Error loading alerts:', error);
                        }
                    }
                    
                    // تحديث عرض الإحصائيات
                    function updateStatsDisplay(stats) {
                        document.getElementById('totalProducts').textContent = stats.total_products.toLocaleString();
                        document.getElementById('activeProducts').textContent = stats.active_products.toLocaleString();
                        document.getElementById('avgPrice').textContent = '$' + stats.avg_price.toLocaleString();
                        document.getElementById('avgDiscount').textContent = stats.avg_discount.toLocaleString() + '%';
                        document.getElementById('proxyUsed').textContent = stats.proxy_used.toLocaleString();
                    }
                    
                    // تحديث عرض حالة المراقبة
                    function updateMonitoringDisplay(data) {
                        const stats = data.stats;
                        
                        document.getElementById('monitoredProducts').textContent = stats.total_monitored.toLocaleString();
                        document.getElementById('dropsDetected').textContent = stats.drops_detected.toLocaleString();
                        document.getElementById('alertsToday').textContent = stats.alerts_today.toLocaleString();
                        document.getElementById('successRate').textContent = stats.extraction_stats?.success_rate?.toFixed(1) || '0';
                        
                        if (stats.last_monitoring) {
                            const lastTime = new Date(stats.last_monitoring);
                            document.getElementById('lastMonitoring').textContent = lastTime.toLocaleTimeString('ar-SA');
                        }
                        
                        if (stats.next_monitoring) {
                            const nextTime = new Date(stats.next_monitoring);
                            document.getElementById('nextMonitoring').textContent = nextTime.toLocaleTimeString('ar-SA');
                        }
                        
                        // تحديث حالة زر المراقبة
                        const startBtn = document.getElementById('startMonitoring');
                        const stopBtn = document.getElementById('stopMonitoring');
                        const runBtn = document.getElementById('runMonitoring');
                        
                        if (data.is_monitoring) {
                            startBtn.disabled = true;
                            stopBtn.disabled = false;
                            document.getElementById('monitoringStatus').textContent = '🟢 نشط';
                            document.getElementById('monitoringStatus').style.color = '#4caf50';
                        } else {
                            startBtn.disabled = false;
                            stopBtn.disabled = true;
                            document.getElementById('monitoringStatus').textContent = '🔴 متوقف';
                            document.getElementById('monitoringStatus').style.color = '#f44336';
                        }
                    }
                    
                    // تحديث جدول المنتجات
                    function updateProductsTable(products) {
                        const tableBody = document.getElementById('productsTableBody');
                        
                        if (products.length === 0) {
                            tableBody.innerHTML = '<tr><td colspan="11" style="text-align: center; padding: 30px;">لا توجد منتجات بعد. ابدأ بإضافة منتج جديد!</td></tr>';
                            return;
                        }
                        
                        let html = '';
                        
                        products.forEach(product => {
                            let monitoringStatus = product.monitoring_enabled ? 
                                '<span class="status-badge status-monitoring">🔍 مراقَب</span>' : 
                                '<span class="status-badge">غير مراقَب</span>';
                            
                            let dropStatus = product.price_drop_detected ? 
                                '<span class="status-badge status-drop">📉 انخفاض</span>' : '';
                            
                            let extractionStatus = '';
                            if (product.extraction_method === 'direct') {
                                extractionStatus = '<span class="status-badge status-direct">مباشر</span>';
                            } else if (product.extraction_method === 'proxy') {
                                extractionStatus = '<span class="status-badge status-proxy">وسيط</span>';
                            } else if (product.extraction_method === 'smart') {
                                extractionStatus = '<span class="status-badge status-smart">ذكي</span>';
                            }
                            
                            if (product.last_extraction_status === 'failed') {
                                extractionStatus += ' <span class="status-badge status-failed">فشل</span>';
                            }
                            
                            let discountClass = 'discount-none';
                            let discountText = '0%';
                            
                            if (product.discount_percentage > 0) {
                                discountText = product.discount_percentage.toFixed(1) + '%';
                                
                                if (product.discount_percentage >= 30) {
                                    discountClass = 'discount-high';
                                } else if (product.discount_percentage >= 10) {
                                    discountClass = 'discount-medium';
                                } else {
                                    discountClass = 'discount-low';
                                }
                            }
                            
                            let initialPriceHtml = '';
                            if (product.initial_price && product.initial_price > product.current_price) {
                                const dropPercent = ((product.initial_price - product.current_price) / product.initial_price * 100).toFixed(1);
                                initialPriceHtml = `
                                    <div style="font-size: 0.8rem; color: #666;">
                                        <div>السعر الأولي: $${product.initial_price.toFixed(2)}</div>
                                        <div style="color: #4caf50;">انخفاض: ${dropPercent}%</div>
                                    </div>
                                `;
                            }
                            
                            html += `
                                <tr>
                                    <td>${product.product_name}</td>
                                    <td><code style="background: #f5f5f5; padding: 3px 8px; border-radius: 4px;">${product.asin}</code></td>
                                    <td>
                                        <div style="font-weight: bold; color: #d32f2f;">$${product.current_price.toFixed(2)}</div>
                                        ${initialPriceHtml}
                                    </td>
                                    <td><span class="discount-badge ${discountClass}">${discountText}</span></td>
                                    <td>${extractionStatus}</td>
                                    <td>${monitoringStatus} ${dropStatus}</td>
                                    <td>${product.category}</td>
                                    <td>${product.price_change_count || 0}</td>
                                    <td>${new Date(product.last_updated).toLocaleDateString('ar-SA')}</td>
                                </tr>
                            `;
                        });
                        
                        tableBody.innerHTML = html;
                    }
                    
                    // تحديث التنبيهات الحديثة
                    function updateRecentAlerts(alerts) {
                        const alertsContainer = document.getElementById('recentAlerts');
                        
                        if (alerts.length === 0) {
                            alertsContainer.innerHTML = '<div style="text-align: center; padding: 20px; color: #666;">لا توجد تنبيهات حديثة</div>';
                            return;
                        }
                        
                        let html = '';
                        
                        alerts.slice(0, 3).forEach(alert => {
                            let methodBadge = alert.extraction_method === 'proxy' ? 
                                '<span class="status-badge status-proxy">وسيط</span>' : 
                                '<span class="status-badge status-direct">مباشر</span>';
                            
                            html += `
                                <div class="alert-card">
                                    <div class="alert-title">📉 انخفاض سعر: ${alert.product_name} ${methodBadge}</div>
                                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin: 10px 0;">
                                        <div>
                                            <div style="font-size: 0.9rem; color: #666;">السعر القديم</div>
                                            <div style="text-decoration: line-through; color: #999;">$${alert.old_price.toFixed(2)}</div>
                                        </div>
                                        <div>
                                            <div style="font-size: 0.9rem; color: #666;">السعر الجديد</div>
                                            <div style="color: #4caf50; font-weight: bold;">$${alert.new_price.toFixed(2)}</div>
                                        </div>
                                    </div>
                                    <div style="display: flex; justify-content: space-between; align-items: center;">
                                        <span style="color: #f57c00; font-weight: bold;">${alert.drop_percentage.toFixed(1)}% انخفاض</span>
                                        <span style="font-size: 0.8rem; color: #666;">${new Date(alert.alert_sent_at).toLocaleTimeString('ar-SA')}</span>
                                    </div>
                                </div>
                            `;
                        });
                        
                        alertsContainer.innerHTML = html;
                    }
                    
                    // تحليل منتج جديد
                    async function analyzeProduct() {
                        const url = document.getElementById('productUrl').value;
                        const loading = document.getElementById('loading');
                        const result = document.getElementById('result');
                        
                        if (!url.includes('amazon.com')) {
                            alert('⚠️ هذا النظام مخصص لـ Amazon.com فقط');
                            return;
                        }
                        
                        loading.style.display = 'block';
                        result.style.display = 'none';
                        
                        try {
                            const response = await fetch(`/api/analyze-product?url=${encodeURIComponent(url)}`);
                            const data = await response.json();
                            
                            loading.style.display = 'none';
                            
                            if (data.status === 'success') {
                                displayResult(data);
                                setTimeout(() => {
                                    loadDashboardStats();
                                    loadProductsTable();
                                }, 1000);
                            } else {
                                displayError(data.error || 'خطأ غير معروف');
                            }
                        } catch (error) {
                            loading.style.display = 'none';
                            displayError('خطأ في الاتصال: ' + error.message);
                        }
                    }
                    
                    // عرض نتيجة التحليل
                    function displayResult(data) {
                        const result = document.getElementById('result');
                        const product = data.product;
                        
                        let methodBadge = product.extraction_method === 'proxy' ? 
                            '<span class="status-badge status-proxy">وسيط</span>' : 
                            '<span class="status-badge status-direct">مباشر</span>';
                        
                        let discountClass = 'discount-none';
                        if (product.discount_percentage > 0) {
                            if (product.discount_percentage >= 30) {
                                discountClass = 'discount-high';
                            } else if (product.discount_percentage >= 10) {
                                discountClass = 'discount-medium';
                            } else {
                                discountClass = 'discount-low';
                            }
                        }
                        
                        let html = `
                            <div style="background: #e8f5e9; border-left: 5px solid #4caf50; padding: 20px; border-radius: 10px; margin-top: 20px;">
                                <h3 style="color: #2e7d32;">✅ تمت إضافة المنتج بنجاح ${methodBadge}</h3>
                                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top: 15px;">
                                    <div>
                                        <strong>اسم المنتج:</strong><br>
                                        ${product.product_name}
                                    </div>
                                    <div>
                                        <strong>ASIN:</strong><br>
                                        <code>${product.asin}</code>
                                    </div>
                                    <div>
                                        <strong>السعر الحالي:</strong><br>
                                        <span style="font-size: 1.5rem; color: #d32f2f; font-weight: bold;">$${product.current_price.toFixed(2)}</span>
                                    </div>
                                    <div>
                                        <strong>نسبة الخصم:</strong><br>
                                        <span class="discount-badge ${discountClass}" style="margin-top: 5px; display: inline-block;">
                                            ${product.discount_percentage.toFixed(1)}%
                                        </span>
                                    </div>
                                </div>
                                <p style="margin-top: 15px; color: #666; font-size: 0.9rem;">
                                    ✅ تم تفعيل المراقبة التلقائية مع الوسيط الذكي
                                </p>
                            </div>
                        `;
                        
                        result.innerHTML = html;
                        result.style.display = 'block';
                        document.getElementById('productUrl').value = '';
                    }
                    
                    // عرض خطأ
                    function displayError(message) {
                        const result = document.getElementById('result');
                        result.innerHTML = `
                            <div style="background: #ffebee; border-left: 5px solid #f44336; padding: 20px; border-radius: 10px; margin-top: 20px;">
                                <h3 style="color: #d32f2f;">❌ فشل التحليل</h3>
                                <p>${message}</p>
                                <p style="color: #666; font-size: 0.9rem; margin-top: 10px;">
                                    جرب إضافة المنتج مرة أخرى، النظام سيستخدم الوسيط تلقائياً
                                </p>
                            </div>
                        `;
                        result.style.display = 'block';
                    }
                    
                    // التحكم في نظام المراقبة
                    async function startMonitoring() {
                        try {
                            const response = await fetch('/api/monitoring/start', { method: 'POST' });
                            const data = await response.json();
                            
                            if (data.status === 'success') {
                                alert('✅ بدأ نظام المراقبة مع الوسيط الذكي');
                                loadMonitoringStatus();
                            } else {
                                alert('❌ فشل بدء المراقبة: ' + data.error);
                            }
                        } catch (error) {
                            alert('❌ خطأ في الاتصال');
                        }
                    }
                    
                    async function stopMonitoring() {
                        try {
                            const response = await fetch('/api/monitoring/stop', { method: 'POST' });
                            const data = await response.json();
                            
                            if (data.status === 'success') {
                                alert('✅ توقف نظام المراقبة');
                                loadMonitoringStatus();
                            } else {
                                alert('❌ فشل إيقاف المراقبة: ' + data.error);
                            }
                        } catch (error) {
                            alert('❌ خطأ في الاتصال');
                        }
                    }
                    
                    async function runMonitoringNow() {
                        try {
                            const response = await fetch('/api/monitoring/run-now', { method: 'POST' });
                            const data = await response.json();
                            
                            if (data.status === 'success') {
                                alert('✅ بدأت دورة مراقبة فورية مع الوسيط الذكي');
                                setTimeout(() => {
                                    loadDashboardStats();
                                    loadMonitoringStatus();
                                    loadRecentAlerts();
                                    loadProductsTable();
                                }, 5000);
                            } else {
                                alert('❌ فشل تشغيل المراقبة: ' + data.error);
                            }
                        } catch (error) {
                            alert('❌ خطأ في الاتصال');
                        }
                    }
                    
                    // البحث في المنتجات
                    async function searchProducts() {
                        const query = document.getElementById('searchInput').value;
                        
                        if (!query.trim()) {
                            loadProductsTable();
                            return;
                        }
                        
                        try {
                            const response = await fetch(`/api/search-products?q=${encodeURIComponent(query)}`);
                            const data = await response.json();
                            
                            if (data.status === 'success') {
                                updateProductsTable(data.products);
                            }
                        } catch (error) {
                            console.error('Search error:', error);
                        }
                    }
                    
                    // إضافة حدث Enter للبحث
                    document.getElementById('searchInput')?.addEventListener('keypress', function(e) {
                        if (e.key === 'Enter') {
                            searchProducts();
                        }
                    });
                </script>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>📊 لوحة تحكم الزحف الذكي</h1>
                        <p>نظام تراكمي مع مراقبة تلقائية ونظام الوسيط الذكي</p>
                        <div class="dashboard-badge">الإصدار 21.2 - نظام الوسيط الذكي ✅ ScraperAPI</div>
                    </div>
                    
                    <div class="main-content">
                        <!-- الشريط الجانبي -->
                        <div class="sidebar">
                            <h3 style="color: #1a237e; margin-bottom: 20px; border-bottom: 2px solid #eee; padding-bottom: 10px;">🔍 إضافة منتج جديد</h3>
                            
                            <div style="background: #e3f2fd; padding: 15px; border-radius: 10px; margin-bottom: 20px;">
                                <strong>🛡️  نظام الوسيط الذكي:</strong><br>
                                <span style="font-size: 0.9rem; color: #666;">
                                    النظام يحاول 3 طرق: مباشر → ذكي → وسيط (ScraperAPI)
                                </span>
                            </div>
                            
                            <div class="search-box">
                                <input type="url" id="productUrl" class="url-input" 
                                       placeholder="https://www.amazon.com/..." 
                                       required>
                                <button class="analyze-btn" onclick="analyzeProduct()">
                                    🚀 إضافة وتحليل المنتج
                                </button>
                            </div>
                            
                            <div id="result"></div>
                            
                            <div id="loading" class="loading">
                                <div class="spinner"></div>
                                <h3>جاري تحليل المنتج...</h3>
                                <p>جاري تجربة طرق الاستخلاص المختلفة...</p>
                            </div>
                            
                            <div style="margin-top: 30px;">
                                <h4 style="color: #1a237e; margin-bottom: 15px;">🔍 البحث في المنتجات</h4>
                                <input type="text" id="searchInput" class="url-input" 
                                       placeholder="ابحث بالاسم أو ASIN أو الفئة...">
                                <button class="analyze-btn" onclick="searchProducts()" style="background: #673ab7;">
                                    🔎 بحث في المنتجات
                                </button>
                            </div>
                            
                            <div style="margin-top: 30px; padding: 20px; background: #f5f5f5; border-radius: 10px;">
                                <h4 style="color: #1a237e; margin-bottom: 15px;">🛡️  نظام الوسيط الذكي ✅ مفعل</h4>
                                <p style="color: #666; font-size: 0.9rem;">
                                    <strong>ميزات النظام:</strong><br>
                                    • 3 طبقات استخلاص (مباشر، ذكي، وسيط)<br>
                                    • ScraperAPI كوسيط احتياطي<br>
                                    • تتبع إحصائيات النجاح<br>
                                    • استخلاص ذكي بناءً على السجل
                                </p>
                                <p style="color: #4caf50; font-size: 0.8rem; margin-top: 10px; font-weight: bold;">
                                    ✅ معدل النجاح المتوقع: 95%
                                </p>
                            </div>
                        </div>
                        
                        <!-- اللوحة الرئيسية -->
                        <div class="main-panel">
                            <!-- لوحة المراقبة -->
                            <div class="monitoring-panel">
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <div>
                                        <h2 style="margin: 0;">🛡️  نظام المراقبة مع الوسيط الذكي</h2>
                                        <p style="margin: 5px 0 0 0; opacity: 0.9;">
                                            الحالة: <span id="monitoringStatus">🔄 جاري التحميل...</span>
                                        </p>
                                    </div>
                                    <div class="monitoring-controls">
                                        <button class="monitoring-btn btn-start" id="startMonitoring" onclick="startMonitoring()">▶ بدء</button>
                                        <button class="monitoring-btn btn-stop" id="stopMonitoring" onclick="stopMonitoring()" disabled>⏹ إيقاف</button>
                                        <button class="monitoring-btn btn-run" id="runMonitoring" onclick="runMonitoringNow()">⚡ تشغيل الآن</button>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- إحصائيات المراقبة -->
                            <div class="stats-grid">
                                <div class="stat-card monitoring">
                                    <div class="stat-label">المنتجات المراقبة</div>
                                    <div class="stat-value" id="monitoredProducts">0</div>
                                    <div style="font-size: 0.8rem; color: #666;">مراقبة نشطة</div>
                                </div>
                                
                                <div class="stat-card drops">
                                    <div class="stat-label">انخفاضات مكتشفة</div>
                                    <div class="stat-value" id="dropsDetected">0</div>
                                    <div style="font-size: 0.8rem; color: #666;">إجمالي الانخفاضات</div>
                                </div>
                                
                                <div class="stat-card alerts">
                                    <div class="stat-label">تنبيهات اليوم</div>
                                    <div class="stat-value" id="alertsToday">0</div>
                                    <div style="font-size: 0.8rem; color: #666;">مرسلة بالبريد</div>
                                </div>
                                
                                <div class="stat-card proxy">
                                    <div class="stat-label">معدل النجاح</div>
                                    <div class="stat-value" id="successRate">0%</div>
                                    <div style="font-size: 0.8rem; color: #666;">نجاح الاستخلاص</div>
                                </div>
                            </div>
                            
                            <div class="stats-grid">
                                <div class="stat-card">
                                    <div class="stat-label">إجمالي المنتجات</div>
                                    <div class="stat-value" id="totalProducts">0</div>
                                    <div style="font-size: 0.8rem; color: #666;">منتجات في النظام</div>
                                </div>
                                
                                <div class="stat-card">
                                    <div class="stat-label">المنتجات النشطة</div>
                                    <div class="stat-value" id="activeProducts">0</div>
                                    <div style="font-size: 0.8rem; color: #666;">متاحة للشراء</div>
                                </div>
                                
                                <div class="stat-card">
                                    <div class="stat-label">المتوسط السعري</div>
                                    <div class="stat-value" id="avgPrice">$0</div>
                                    <div style="font-size: 0.8rem; color: #666;">متوسط الأسعار</div>
                                </div>
                                
                                <div class="stat-card">
                                    <div class="stat-label">الوسيط المستخدم</div>
                                    <div class="stat-value" id="proxyUsed">0</div>
                                    <div style="font-size: 0.8rem; color: #666;">منتجات بالوسيط</div>
                                </div>
                            </div>
                            
                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin: 20px 0;">
                                <div style="background: #f5f5f5; padding: 15px; border-radius: 10px; text-align: center;">
                                    <div style="color: #666; font-size: 0.9rem;">آخر مراقبة</div>
                                    <div class="stat-value" id="lastMonitoring" style="font-size: 1.5rem;">--:--</div>
                                </div>
                                <div style="background: #f5f5f5; padding: 15px; border-radius: 10px; text-align: center;">
                                    <div style="color: #666; font-size: 0.9rem;">المراقبة التالية</div>
                                    <div class="stat-value" id="nextMonitoring" style="font-size: 1.5rem;">--:--</div>
                                </div>
                            </div>
                            
                            <!-- التنبيهات الحديثة -->
                            <div style="margin: 25px 0;">
                                <h3 style="color: #1a237e; border-bottom: 2px solid #eee; padding-bottom: 10px;">
                                    ⚠️ التنبيهات الحديثة
                                </h3>
                                <div id="recentAlerts">
                                    <!-- سيتم ملؤه بالبيانات -->
                                </div>
                            </div>
                            
                            <!-- جدول المنتجات -->
                            <div style="margin: 30px 0 20px 0;">
                                <h3 style="color: #1a237e; border-bottom: 2px solid #eee; padding-bottom: 10px;">
                                    📋 جميع المنتجات مع طريقة الاستخلاص
                                </h3>
                            </div>
                            
                            <div class="products-table-container">
                                <table class="products-table">
                                    <thead>
                                        <tr>
                                            <th>اسم المنتج</th>
                                            <th>ASIN</th>
                                            <th>السعر الحالي</th>
                                            <th>الخصم</th>
                                            <th>طريقة الاستخلاص</th>
                                            <th>حالة المراقبة</th>
                                            <th>الفئة</th>
                                            <th>التغيرات</th>
                                            <th>آخر تحديث</th>
                                        </tr>
                                    </thead>
                                    <tbody id="productsTableBody">
                                        <!-- سيتم ملؤه بالبيانات -->
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                    
                    <div class="footer">
                        <p>© 2024 نظام مراقبة الأسعار التلقائي - الإصدار 21.2</p>
                        <p>🛡️  نظام الوسيط الذكي (ScraperAPI) | 📡 مراقبة تلقائية كل ساعتين | 📧 إشعارات بريدية فورية</p>
                    </div>
                </div>
            </body>
            </html>
            ''')
        
        @app.route('/api/dashboard-stats', methods=['GET'])
        def get_dashboard_stats():
            """الحصول على إحصائيات لوحة التحكم"""
            try:
                stats = self.dashboard_db.get_display_stats()
                return jsonify({'status': 'success', 'stats': stats})
            except Exception as e:
                return jsonify({'status': 'error', 'error': str(e)}), 500
        
        @app.route('/api/dashboard-products', methods=['GET'])
        def get_dashboard_products():
            """الحصول على المنتجات للعرض"""
            try:
                limit = request.args.get('limit', 50, type=int)
                offset = request.args.get('offset', 0, type=int)
                
                products = self.dashboard_db.get_all_products(limit=limit, offset=offset)
                
                return jsonify({
                    'status': 'success',
                    'products': products,
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                return jsonify({'status': 'error', 'error': str(e)}), 500
        
        @app.route('/api/monitoring-status', methods=['GET'])
        def get_monitoring_status():
            """الحصول على حالة نظام المراقبة"""
            try:
                monitoring_status = self.monitoring_system.get_monitoring_status()
                return jsonify({
                    'status': 'success',
                    'is_monitoring': monitoring_status['is_monitoring'],
                    'stats': monitoring_status['stats'],
                    'config': monitoring_status['config'],
                    'proxy_config': monitoring_status['proxy_config']
                })
            except Exception as e:
                return jsonify({'status': 'error', 'error': str(e)}), 500
        
        @app.route('/api/recent-alerts', methods=['GET'])
        def get_recent_alerts():
            """الحصول على التنبيهات الحديثة"""
            try:
                alerts = self.dashboard_db.get_recent_alerts(limit=10)
                return jsonify({'status': 'success', 'alerts': alerts})
            except Exception as e:
                return jsonify({'status': 'error', 'error': str(e)}), 500
        
        @app.route('/api/analyze-product', methods=['GET'])
        def analyze_product():
            """تحليل منتج جديد وإضافته"""
            url = request.args.get('url')
            
            if not url:
                return jsonify({'status': 'error', 'error': 'رابط المنتج مطلوب'}), 400
            
            if 'amazon.com' not in url.lower():
                return jsonify({'status': 'error', 'error': 'النظام يدعم Amazon.com فقط'}), 400
            
            logger.info(f"🎯 بدء تحليل منتج جديد: {url[:80]}...")
            
            try:
                # استخلاص البيانات
                extraction, message, extraction_method = self.extractor.extract_price(url)
                
                if not extraction:
                    return jsonify({'status': 'error', 'error': message}), 400
                
                # مزامنة إلى لوحة التحكم
                self.integrator.sync_product_to_dashboard(extraction, extraction_method)
                
                # جلب بيانات المنتج المحدثة
                products = self.dashboard_db.search_products(extraction['asin'], limit=1)
                
                response = {
                    'status': 'success',
                    'product': products[0] if products else {
                        'asin': extraction['asin'],
                        'product_name': extraction.get('title', f'منتج {extraction["asin"]}'),
                        'current_price': extraction['price'],
                        'reference_price': extraction.get('reference_price', 0.0),
                        'discount_percentage': extraction.get('discount_percentage', 0.0),
                        'currency': extraction.get('currency', 'USD'),
                        'availability_status': 'active',
                        'extraction_method': extraction_method
                    },
                    'message': f'تمت إضافة المنتج باستخدام {extraction_method}'
                }
                
                logger.info(f"✅ تمت إضافة المنتج {extraction['asin']} باستخدام {extraction_method}")
                return jsonify(response)
                
            except Exception as e:
                logger.error(f"❌ خطأ في تحليل المنتج: {e}")
                return jsonify({'status': 'error', 'error': str(e)}), 500
        
        @app.route('/api/search-products', methods=['GET'])
        def search_products():
            """البحث في المنتجات"""
            query = request.args.get('q', '')
            
            try:
                if not query.strip():
                    products = self.dashboard_db.get_all_products(limit=50)
                else:
                    products = self.dashboard_db.search_products(query, limit=50)
                
                return jsonify({
                    'status': 'success',
                    'products': products,
                    'query': query,
                    'count': len(products)
                })
            except Exception as e:
                return jsonify({'status': 'error', 'error': str(e)}), 500
        
        @app.route('/api/monitoring/start', methods=['POST'])
        def start_monitoring():
            """بدء نظام المراقبة"""
            try:
                if MONITORING_CONFIG['enabled']:
                    self.monitoring_system.start_monitoring()
                    return jsonify({'status': 'success', 'message': 'بدأ نظام المراقبة مع الوسيط الذكي'})
                else:
                    return jsonify({'status': 'error', 'error': 'نظام المراقبة معطل في الإعدادات'}), 400
            except Exception as e:
                return jsonify({'status': 'error', 'error': str(e)}), 500
        
        @app.route('/api/monitoring/stop', methods=['POST'])
        def stop_monitoring():
            """إيقاف نظام المراقبة"""
            try:
                self.monitoring_system.stop_monitoring()
                return jsonify({'status': 'success', 'message': 'توقف نظام المراقبة'})
            except Exception as e:
                return jsonify({'status': 'error', 'error': str(e)}), 500
        
        @app.route('/api/monitoring/run-now', methods=['POST'])
        def run_monitoring_now():
            """تشغيل دورة مراقبة فورية"""
            try:
                if not MONITORING_CONFIG['enabled']:
                    return jsonify({'status': 'error', 'error': 'نظام المراقبة معطل'}), 400
                
                # تشغيل دورة مراقبة في خيط منفصل
                threading.Thread(target=self.monitoring_system.run_monitoring_cycle, daemon=True).start()
                
                return jsonify({'status': 'success', 'message': 'بدأت دورة مراقبة فورية مع الوسيط الذكي'})
            except Exception as e:
                return jsonify({'status': 'error', 'error': str(e)}), 500
        
        @app.route('/api/best-deals', methods=['GET'])
        def get_best_deals():
            """الحصول على أفضل العروض"""
            try:
                min_discount = request.args.get('min_discount', 10.0, type=float)
                limit = request.args.get('limit', 20, type=int)
                
                deals = self.dashboard_db.get_best_deals(min_discount=min_discount, limit=limit)
                
                return jsonify({
                    'status': 'success',
                    'deals': deals,
                    'min_discount': min_discount,
                    'count': len(deals)
                })
            except Exception as e:
                return jsonify({'status': 'error', 'error': str(e)}), 500
        
        @app.route('/system-status')
        def system_status():
            """صفحة حالة النظام"""
            extraction_stats = self.dashboard_db.get_extraction_stats()
            return jsonify({
                'status': 'active',
                'version': '21.2',
                'features': {
                    'smart_extraction': True,
                    'proxy_system': True,
                    'scraperapi_integration': True,
                    'smart_monitoring': True,
                    'email_notifications': MONITORING_CONFIG['email_notifications'],
                    'smart_rotation': MONITORING_CONFIG['smart_rotation']
                },
                'timestamp': datetime.now().isoformat(),
                'extraction_stats': extraction_stats,
                'message': 'النظام يعمل مع الوسيط الذكي بنسبة نجاح عالية'
            })
        
        @app.route('/ping')
        def ping():
            """صفحة البقاء حياً"""
            return jsonify({
                'status': 'alive',
                'timestamp': datetime.now().isoformat(),
                'smart_system': True,
                'proxy_available': bool(PROXY_CONFIG.get('scraperapi_key'))
            }), 200
        
        @app.route('/api/extraction-stats')
        def get_extraction_stats():
            """الحصول على إحصائيات الاستخلاص"""
            try:
                stats = self.dashboard_db.get_extraction_stats()
                return jsonify({
                    'status': 'success',
                    'stats': stats
                })
            except Exception as e:
                return jsonify({'status': 'error', 'error': str(e)}), 500

# ==================== تشغيل النظام ====================
def main():
    """الدالة الرئيسية"""
    print("\n" + "="*60)
    print("🚀 بدء تشغيل نظام الوسيط الذكي (ScraperAPI ✅ مفعل)")
    print("="*60)
    
    system = None
    try:
        system = EnhancedDashboardSystem()
        
        print("\n✨ النظام يعمل الآن!")
        print(f"🌐 رابط الواجهة: http://localhost:9090")
        print(f"📡 واجهات API الرئيسية:")
        print(f"   • /                      - الواجهة الرئيسية مع الوسيط الذكي")
        print(f"   • /ping                  - صفحة البقاء حياً")
        print(f"   • /system-status         - حالة النظام")
        print(f"   • /api/extraction-stats  - إحصائيات الاستخلاص")
        print(f"   • /api/monitoring-status - حالة نظام المراقبة")
        print("="*60)
        print("\n🛡️  تفاصيل نظام الوسيط الذكي:")
        print("   • ✅ ScraperAPI: مفعل (مفتاح: c5ff3050a86e42483899a1fff1ec4780)")
        print("   • 🔄 3 طبقات استخلاص: مباشر → ذكي → وسيط")
        print("   • 📊 تتبع إحصائيات النجاح لكل طريقة")
        print("   • ⚡ استخلاص ذكي بناءً على السجل السابق")
        print("="*60)
        
        app.run(
            host='0.0.0.0',
            port=9090,
            debug=False,
            threaded=True,
            use_reloader=False
        )
    except KeyboardInterrupt:
        print("\n\n🛑 تم إيقاف النظام بواسطة المستخدم")
    except Exception as e:
        print(f"\n❌ خطأ غير متوقع: {e}")
        traceback.print_exc()
    finally:
        if system:
            system.dashboard_db.close()
            system.monitoring_system.stop_monitoring()
        print("\n✅ تم إغلاق النظام بشكل آمن")

if __name__ == '__main__':
    main()
