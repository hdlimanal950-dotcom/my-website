"""
ultimate_smart_crawler_dashboard_fixed.py - نظام الزحف مع لوحة تحكم تراكمية ونظام مراقبة الأسعار التلقائية
الإصدار: 22.0 - نظام التمويه الذكي + وسيط ScraperAPI + نظام التحليل التاريخي الذكي
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

print("=" * 70)
print("📊 نظام الزحف الذكي - لوحة التحكم التراكمية + النظام التاريخي الذكي")
print("=" * 70)
print("\n📦 جاري تحميل المكتبات...")
print("✅ المكتبات الأساسية - جاهزة")

# ==================== إعدادات النظام الجديد ====================
MONITORING_CONFIG = {
    'enabled': True,
    'interval': 7200,
    'price_drop_threshold': 20.0,
    'monitoring_limit': 30,
    'email_notifications': True,
    'smart_rotation': True,
    'delay_between_requests': [3, 8],
    'use_proxy_fallback': True,
    'max_retries': 3,
}

# 🔥 نظام التحليل التاريخي الذكي الجديد
HISTORICAL_ANALYSIS_CONFIG = {
    'enabled': True,  # تفعيل النظام التاريخي
    'camel_api_key': '9e2a31cc365df963ee07a7084767a48c49f538fd',  # ✅ محرك الأساسي للتاريخ
    'camel_endpoint': 'https://camelcamelcamel.com',
    'fetch_on_new_product': True,  # جلب التاريخ عند إضافة منتج جديد
    'recheck_days': 7,  # إعادة التحقق كل 7 أيام
    'price_history_days': 365,  # البحث في تاريخ سنة كاملة
    'use_advanced_patterns': True,  # استخدام أنماط متقدمة للبحث
}

EMAIL_CONFIG = {
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'sender_email': 'kklb1553@gmail.com',
    'sender_password': 'b g b j f p t m q a p m w z e f',
    'receiver_email': 'kklb1553@gmail.com',
}

# ==================== إعدادات الوسيط ====================
PROXY_CONFIG = {
    'enabled': True,
    'primary_proxy': 'scraperapi',
    'scraperapi_key': 'c5ff3050a86e42483899a1fff1ec4780',
    'scraperapi_url': 'http://api.scraperapi.com',
    'use_direct_first': True,
    'retry_with_proxy': True,
    'timeout': 30,
}

# ==================== نظام التمويه الذكي مع الوسيط ====================
class SmartBrowserSimulator:
    """محاكي متصفح ذكي مع وسيط احتياطي"""
    
    def __init__(self):
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0',
            'Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36',
            'Mozilla/5.0 (Linux; Android 14; SM-S911B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/121.0.0.0 Mobile/15E148 Safari/604.1',
        ]
        
        self.cookies = {}
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
                headers = self.get_smart_headers('https://www.amazon.com/')
                self.add_natural_delay()
                
                if not self.cookies:
                    self.cookies = {
                        'session-id': str(random.randint(1000000, 9999999)),
                        'ubid-main': str(random.randint(1000000, 9999999)),
                        'session-token': hashlib.md5(str(time.time()).encode()).hexdigest()[:20],
                        'i18n-prefs': 'USD',
                        'sp-cdn': 'L5Z9:SA'
                    }
                
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
                
                attempts_log.append({
                    'attempt': attempt + 1,
                    'method': method,
                    'status': response.status_code
                })
                
                if response.status_code == 200:
                    if response.cookies:
                        self.cookies.update(response.cookies.get_dict())
                    return response, attempts_log
                
                elif response.status_code in [301, 302, 303, 307, 308]:
                    new_url = response.headers.get('Location')
                    if new_url:
                        return self.smart_get_request(new_url, max_retries, use_proxy)
                
                else:
                    self.cookies = {}
                    time.sleep(2 ** attempt)
                    
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
            encoded_url = quote(url, safe='')
            proxy_url = f"{PROXY_CONFIG['scraperapi_url']}/?api_key={PROXY_CONFIG['scraperapi_key']}&url={encoded_url}"
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

# ==================== قاعدة بيانات موسعة مع النظام التاريخي ====================
class EnhancedDatabase:
    """قاعدة بيانات موسعة مع نظام تتبع ومراقبة الأسعار والتحليل التاريخي"""
    
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
        """التأكد من وجود قاعدة البيانات وجداولها الموسعة مع النظام التاريخي"""
        print(f"\n🗄️  جاري التحقق من قاعدة البيانات مع النظام التاريخي: {self.db_path}")
        
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # ============ جدول المنتجات مع بيانات تاريخية ============
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
                    initial_price REAL,
                    price_change_count INTEGER DEFAULT 0,
                    last_monitored TIMESTAMP,
                    monitoring_enabled BOOLEAN DEFAULT 1,
                    price_drop_detected BOOLEAN DEFAULT 0,
                    extraction_method TEXT DEFAULT 'direct',
                    last_extraction_status TEXT DEFAULT 'success',
                    historical_low_price REAL DEFAULT 0.0,          -- 🔥 أقل سعر تاريخي
                    price_average REAL DEFAULT 0.0,                -- 🔥 متوسط السعر العادل
                    last_history_sync TIMESTAMP,                   -- 🔥 آخر تحديث للبيانات التاريخية
                    historical_data_available BOOLEAN DEFAULT 0,   -- 🔥 هل هناك بيانات تاريخية
                    purchase_recommendation TEXT,                  -- 🔥 توصية الشراء
                    recommendation_confidence REAL DEFAULT 0.0,    -- 🔥 ثقة التوصية
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
            
            # ============ جدول البيانات التاريخية التفصيلية ============
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS historical_price_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    asin TEXT NOT NULL,
                    historical_low REAL NOT NULL,
                    historical_high REAL,
                    price_average REAL,
                    data_source TEXT DEFAULT 'camelcamelcamel',
                    analysis_date DATE NOT NULL,
                    days_analyzed INTEGER DEFAULT 365,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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
            
            # ============ جدول توصيات الشراء ============
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS purchase_recommendations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    asin TEXT NOT NULL,
                    recommendation_type TEXT NOT NULL,
                    confidence_score REAL DEFAULT 0.0,
                    current_price REAL,
                    historical_low REAL,
                    price_average REAL,
                    price_vs_low_percentage REAL DEFAULT 0.0,
                    recommendation_text TEXT,
                    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (asin) REFERENCES dashboard_products (asin) ON DELETE CASCADE
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
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_historical_data ON historical_price_data(asin, analysis_date DESC)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_recommendations ON purchase_recommendations(asin, generated_at DESC)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_time ON update_events(created_at DESC)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_stats_date ON display_stats(created_date DESC)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_time ON price_alerts(alert_sent_at DESC)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_monitoring_time ON monitoring_logs(monitored_at DESC)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_extraction_method ON dashboard_products(extraction_method)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_extraction_stats_date ON extraction_stats(date DESC)')
                conn.commit()
            except Exception as e:
                print(f"⚠️  تحذير في إنشاء الفهارس: {e}")
            
            print("✅ قاعدة البيانات الموسعة مع النظام التاريخي جاهزة")
            self._update_display_stats()
            
        except Exception as e:
            print(f"❌ خطأ في قاعدة البيانات: {e}")
            if conn:
                conn.rollback()
            raise
    
    def _add_missing_columns(self, cursor):
        """إضافة الأعمدة المفقودة إلى الجداول"""
        try:
            cursor.execute("PRAGMA table_info(dashboard_products)")
            columns = [col[1] for col in cursor.fetchall()]
            
            # الأعمدة الجديدة للنظام التاريخي
            historical_columns = [
                'historical_low_price', 'price_average', 'last_history_sync',
                'historical_data_available', 'purchase_recommendation', 'recommendation_confidence'
            ]
            
            for col in historical_columns:
                if col not in columns:
                    try:
                        if col == 'historical_low_price':
                            cursor.execute(f'ALTER TABLE dashboard_products ADD COLUMN {col} REAL DEFAULT 0.0')
                        elif col == 'price_average':
                            cursor.execute(f'ALTER TABLE dashboard_products ADD COLUMN {col} REAL DEFAULT 0.0')
                        elif col == 'last_history_sync':
                            cursor.execute(f'ALTER TABLE dashboard_products ADD COLUMN {col} TIMESTAMP')
                        elif col == 'historical_data_available':
                            cursor.execute(f'ALTER TABLE dashboard_products ADD COLUMN {col} BOOLEAN DEFAULT 0')
                        elif col == 'purchase_recommendation':
                            cursor.execute(f'ALTER TABLE dashboard_products ADD COLUMN {col} TEXT')
                        elif col == 'recommendation_confidence':
                            cursor.execute(f'ALTER TABLE dashboard_products ADD COLUMN {col} REAL DEFAULT 0.0')
                        print(f"✅ تمت إضافة العمود التاريخي: {col}")
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
            
            # استخراج البيانات التاريخية إذا كانت موجودة
            historical_low = product_data.get('historical_low_price')
            price_average = product_data.get('price_average')
            recommendation = product_data.get('purchase_recommendation')
            confidence = product_data.get('recommendation_confidence')
            
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
                
                # بناء الاستعلام الديناميكي لتحديث الحقول التاريخية
                update_fields = []
                update_values = []
                
                # الحقول الأساسية
                update_fields.append('product_name = COALESCE(?, product_name)')
                update_values.append(product_data.get('product_name'))
                
                update_fields.append('current_price = COALESCE(?, current_price)')
                update_values.append(current_price)
                
                update_fields.append('reference_price = COALESCE(?, reference_price)')
                update_values.append(reference_price)
                
                update_fields.append('discount_percentage = COALESCE(?, discount_percentage)')
                update_values.append(discount_percentage)
                
                update_fields.append('currency = COALESCE(?, currency)')
                update_values.append(product_data.get('currency', 'USD'))
                
                update_fields.append('availability_status = COALESCE(?, availability_status)')
                update_values.append(product_data.get('availability_status', 'active'))
                
                update_fields.append('last_updated = CURRENT_TIMESTAMP')
                
                update_fields.append('source_url = COALESCE(?, source_url)')
                update_values.append(product_data.get('source_url'))
                
                update_fields.append('category = COALESCE(?, category)')
                update_values.append(product_data.get('category', 'غير مصنف'))
                
                update_fields.append('price_change_count = price_change_count + ?')
                update_values.append(1 if abs(old_price - current_price) > 0.01 else 0)
                
                update_fields.append('price_drop_detected = 0')
                
                update_fields.append('extraction_method = ?')
                update_values.append(extraction_method)
                
                update_fields.append('last_extraction_status = "success"')
                
                # تحديث الحقول التاريخية إذا كانت متوفرة
                if historical_low is not None:
                    update_fields.append('historical_low_price = ?')
                    update_values.append(historical_low)
                    update_fields.append('historical_data_available = 1')
                
                if price_average is not None:
                    update_fields.append('price_average = ?')
                    update_values.append(price_average)
                
                if recommendation:
                    update_fields.append('purchase_recommendation = ?')
                    update_values.append(recommendation)
                
                if confidence is not None:
                    update_fields.append('recommendation_confidence = ?')
                    update_values.append(confidence)
                
                # إذا تم تحديث البيانات التاريخية
                if any([historical_low is not None, price_average is not None]):
                    update_fields.append('last_history_sync = CURRENT_TIMESTAMP')
                
                # إذا لم يكن هناك سعر أولي، تعيينه الآن
                if not initial_price and current_price > 0:
                    update_fields.append('initial_price = ?')
                    update_values.append(current_price)
                
                # بناء وتنفيذ الاستعلام
                update_query = f'''
                    UPDATE dashboard_products 
                    SET {', '.join(update_fields)}
                    WHERE asin = ?
                '''
                update_values.append(asin)
                
                cursor.execute(update_query, tuple(update_values))
                
                # تسجيل حدث التحديث
                if abs(old_price - current_price) > 0.01:
                    self._log_update_event('price_change', asin, str(old_price), str(current_price), 
                                         discount_percentage - old_discount, extraction_method)
                
                # تسجيل حدث التاريخ إذا تم تحديثه
                if historical_low is not None:
                    self._log_update_event('historical_update', asin, 'N/A', f'Lowest: ${historical_low:.2f}', 
                                         0, 'historical_analyzer')
                
            else:
                # إضافة منتج جديد
                cursor.execute('''
                    INSERT INTO dashboard_products 
                    (asin, product_name, current_price, reference_price, discount_percentage, 
                     currency, availability_status, source_url, category, initial_price, 
                     extraction_method, historical_low_price, price_average, 
                     purchase_recommendation, recommendation_confidence, historical_data_available,
                     last_history_sync)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                    extraction_method,
                    historical_low or 0.0,
                    price_average or 0.0,
                    recommendation,
                    confidence or 0.0,
                    1 if historical_low is not None else 0,
                    'CURRENT_TIMESTAMP' if historical_low is not None else None
                ))
                
                event_type = 'historical_product' if historical_low is not None else 'new_product'
                self._log_update_event(event_type, asin, None, product_data.get('product_name', asin), 
                                     discount_percentage, extraction_method)
            
            # حفظ في تاريخ الأسعار
            if current_price > 0:
                cursor.execute('''
                    INSERT INTO price_history (asin, price, reference_price, discount_percentage, extraction_method)
                    VALUES (?, ?, ?, ?, ?)
                ''', (asin, current_price, reference_price, discount_percentage, extraction_method))
            
            # حفظ البيانات التاريخية التفصيلية إذا كانت متوفرة
            if historical_low is not None and historical_low > 0:
                cursor.execute('''
                    INSERT INTO historical_price_data (asin, historical_low, price_average, data_source, analysis_date, days_analyzed)
                    VALUES (?, ?, ?, ?, DATE('now'), ?)
                ''', (asin, historical_low, price_average or current_price, 'camelcamelcamel', 
                     HISTORICAL_ANALYSIS_CONFIG['price_history_days']))
            
            conn.commit()
            self._update_display_stats()
            
            logger.info(f"📊 تم تحديث المنتج: {asin} (السعر: ${current_price:.2f}, التاريخ: {'نعم' if historical_low else 'لا'})")
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
    
    def update_historical_data(self, asin: str, historical_data: Dict):
        """تحديث البيانات التاريخية لمنتج معين"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE dashboard_products 
                SET historical_low_price = ?, price_average = ?, 
                    last_history_sync = CURRENT_TIMESTAMP, historical_data_available = 1
                WHERE asin = ?
            ''', (
                historical_data.get('historical_low_price', 0),
                historical_data.get('price_average', 0),
                asin
            ))
            
            # حفظ في جدول البيانات التاريخية
            if historical_data.get('historical_low_price', 0) > 0:
                cursor.execute('''
                    INSERT INTO historical_price_data 
                    (asin, historical_low, historical_high, price_average, data_source, analysis_date, days_analyzed)
                    VALUES (?, ?, ?, ?, ?, DATE('now'), ?)
                ''', (
                    asin,
                    historical_data.get('historical_low_price', 0),
                    historical_data.get('historical_high_price', 0),
                    historical_data.get('price_average', 0),
                    historical_data.get('data_source', 'camelcamelcamel'),
                    HISTORICAL_ANALYSIS_CONFIG['price_history_days']
                ))
            
            conn.commit()
            logger.info(f"📈 تم تحديث البيانات التاريخية لـ {asin}")
            return True
            
        except Exception as e:
            logger.error(f"❌ خطأ في تحديث البيانات التاريخية: {e}")
            return False
    
    def get_historical_data(self, asin: str) -> Optional[Dict]:
        """الحصول على البيانات التاريخية لمنتج"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT historical_low_price, price_average, last_history_sync, 
                       purchase_recommendation, recommendation_confidence
                FROM dashboard_products 
                WHERE asin = ?
            ''', (asin,))
            
            row = cursor.fetchone()
            
            if row and row[0] and row[0] > 0:
                return {
                    'historical_low_price': row[0],
                    'price_average': row[1],
                    'last_history_sync': row[2],
                    'purchase_recommendation': row[3],
                    'recommendation_confidence': row[4]
                }
            
            return None
            
        except Exception as e:
            logger.error(f"❌ خطأ في جلب البيانات التاريخية: {e}")
            return None
    
    def save_purchase_recommendation(self, asin: str, recommendation_data: Dict):
        """حفظ توصية الشراء"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO purchase_recommendations 
                (asin, recommendation_type, confidence_score, current_price, 
                 historical_low, price_average, price_vs_low_percentage, recommendation_text)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                asin,
                recommendation_data.get('recommendation_type', 'unknown'),
                recommendation_data.get('confidence_score', 0),
                recommendation_data.get('current_price', 0),
                recommendation_data.get('historical_low', 0),
                recommendation_data.get('price_average', 0),
                recommendation_data.get('price_vs_low_percentage', 0),
                recommendation_data.get('recommendation_text', '')
            ))
            
            conn.commit()
        except Exception as:
            pass
    
    # ... باقي الدوال كما هي (get_products_for_monitoring, update_monitoring_time, إلخ)
    # مع التأكد من أنها تستخدم الجداول والأعمدة الجديدة

# ==================== نظام الاستخلاص المعزز مع استخراج ASIN ====================
class DiscountAwareAmazonExtractor:
    """مستخلص ذكي مع تتبع الأسعار المرجعية والخصومات والوسيط"""
    
    def __init__(self):
        try:
            import fake_useragent
            
            self.browser_simulator = SmartBrowserSimulator()
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
        """🔥 استخراج ASIN من رابط Amazon.com - التنظيف الذكي"""
        try:
            # إزالة المتغيرات الزائدة والتنظيف
            parsed_url = urlparse(url)
            clean_path = parsed_url.path
            
            # البحث في المسار أولاً
            patterns = [
                r'/dp/([A-Z0-9]{10})',  # النمط الأساسي
                r'/gp/product/([A-Z0-9]{10})',
                r'/product/([A-Z0-9]{10})',
                r'/exec/obidos/ASIN/([A-Z0-9]{10})',
                r'/d/([A-Z0-9]{10})',
                r'/([A-Z0-9]{10})(?:[/?&]|$)',  # النمط العام
            ]
            
            for pattern in patterns:
                match = re.search(pattern, clean_path, re.IGNORECASE)
                if match:
                    asin = match.group(1).upper()
                    if len(asin) == 10 and asin.isalnum():
                        return asin
            
            # البحث في استعلام URL إذا لم يتم العثور في المسار
            query_params = parse_qs(parsed_url.query)
            
            # البحث عن asin في الاستعلام
            if 'asin' in query_params:
                asin = query_params['asin'][0].upper()
                if len(asin) == 10 and asin.isalnum():
                    return asin
            
            # البحث عن أية معلمات أخرى قد تحتوي على ASIN
            for param_name in ['ASIN', 'asin', 'product_id', 'productID']:
                if param_name in query_params:
                    potential_asin = query_params[param_name][0].upper()
                    if len(potential_asin) == 10 and potential_asin.isalnum():
                        return potential_asin
            
            # البحث في الرابط الكامل كملاذ أخير
            full_pattern = r'(?:[/=])([A-Z0-9]{10})(?:[/?&]|$)'
            match = re.search(full_pattern, url, re.IGNORECASE)
            if match:
                asin = match.group(1).upper()
                if len(asin) == 10 and asin.isalnum():
                    return asin
            
            return None
            
        except Exception as e:
            logger.error(f"❌ خطأ في استخراج ASIN: {e}")
            return None
    
    # ... باقي الدوال كما هي (extract_price, _extract_with_discount_awareness, إلخ)

# ==================== نظام التحليل التاريخي الذكي ====================
class HistoricalPriceAnalyzer:
    """🔥 محلل تاريخي ذكي لجلب أقل سعر تاريخي ومتوسط الأسعار"""
    
    def __init__(self):
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        print("📈 نظام التحليل التاريخي الذكي - جاهز")
    
    def fetch_historical_data(self, asin: str) -> Optional[Dict]:
        """🔥 جلب البيانات التاريخية باستخدام المفتاح الذكي"""
        if not HISTORICAL_ANALYSIS_CONFIG['enabled']:
            logger.info(f"📊 النظام التاريخي معطل لـ {asin}")
            return None
        
        try:
            # 🔥 بناء رابط CamelCamelCamel باستخدام المفتاح كجسر عبور
            base_url = f"{HISTORICAL_ANALYSIS_CONFIG['camel_endpoint']}/product/{asin}"
            
            # 🔥 إضافة المفتاح كمعلمة للوصول
            params = {
                'api_key': HISTORICAL_ANALYSIS_CONFIG['camel_api_key'],
                'days': HISTORICAL_ANALYSIS_CONFIG['price_history_days']
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': 'https://camelcamelcamel.com/',
            }
            
            logger.info(f"🌐 جاري تحليل التاريخ للمنتج: {asin}")
            
            response = self.session.get(
                base_url, 
                params=params,
                headers=headers, 
                timeout=25
            )
            
            if response.status_code == 200:
                return self._extract_historical_from_html(response.text, asin)
            else:
                logger.warning(f"⚠️  استجابة غير متوقعة لـ {asin}: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ خطأ في جلب البيانات التاريخية لـ {asin}: {e}")
            return None
    
    def _extract_historical_from_html(self, html: str, asin: str) -> Optional[Dict]:
        """🔥 استخراج البيانات التاريخية من HTML باستخدام أنماط متقدمة"""
        try:
            historical_low = 0.0
            price_average = 0.0
            
            # 🔥 أنماط متقدمة للبحث عن "أقل سعر تاريخي"
            low_price_patterns = [
                r'Lowest Price.*?\$([\d,]+\.?\d{2})',  # Lowest Price: $123.45
                r'أقل سعر.*?\$([\d,]+\.?\d{2})',  # نمط عربي
                r'Historical Low.*?\$([\d,]+\.?\d{2})',
                r'data-lowest-price="\$([\d,]+\.?\d{2})"',
                r'"lowest_price":\s*([\d,]+\.?\d{2})',
                r'<td[^>]*>Lowest Price</td>\s*<td[^>]*>\$([\d,]+\.?\d{2})',
                r'<span[^>]*class="[^"]*low[^"]*"[^>]*>\$([\d,]+\.?\d{2})',
                r'All Time Low.*?\$([\d,]+\.?\d{2})',
            ]
            
            # 🔥 أنماط متقدمة للبحث عن "متوسط السعر"
            avg_price_patterns = [
                r'Average Price.*?\$([\d,]+\.?\d{2})',
                r'متوسط السعر.*?\$([\d,]+\.?\d{2})',
                r'data-average-price="\$([\d,]+\.?\d{2})"',
                r'"average_price":\s*([\d,]+\.?\d{2})',
                r'<td[^>]*>Average Price</td>\s*<td[^>]*>\$([\d,]+\.?\d{2})',
                r'<span[^>]*class="[^"]*avg[^"]*"[^>]*>\$([\d,]+\.?\d{2})',
                r'Price Average.*?\$([\d,]+\.?\d{2})',
            ]
            
            # البحث عن أقل سعر
            for pattern in low_price_patterns:
                match = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
                if match:
                    price_str = match.group(1).replace(',', '')
                    historical_low = self._safe_float_convert(price_str)
                    if historical_low and historical_low > 0:
                        logger.info(f"✅ تم العثور على أقل سعر تاريخي لـ {asin}: ${historical_low:.2f}")
                        break
            
            # البحث عن متوسط السعر
            for pattern in avg_price_patterns:
                match = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
                if match:
                    price_str = match.group(1).replace(',', '')
                    price_average = self._safe_float_convert(price_str)
                    if price_average and price_average > 0:
                        logger.info(f"✅ تم العثور على متوسط سعر لـ {asin}: ${price_average:.2f}")
                        break
            
            # إذا لم نجد متوسط سعر، نستخدم أقل سعر * 1.2 كتقدير
            if historical_low > 0 and price_average == 0:
                price_average = historical_low * 1.2
                logger.info(f"📊 تم تقدير متوسط السعر لـ {asin}: ${price_average:.2f}")
            
            if historical_low > 0:
                return {
                    'asin': asin,
                    'historical_low_price': historical_low,
                    'price_average': price_average,
                    'data_source': 'camelcamelcamel',
                    'fetched_at': datetime.now().isoformat()
                }
            else:
                logger.warning(f"⚠️  لم يتم العثور على بيانات تاريخية لـ {asin}")
                return None
                
        except Exception as e:
            logger.error(f"❌ خطأ في استخراج البيانات التاريخية لـ {asin}: {e}")
            return None
    
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
    
    def generate_purchase_recommendation(self, current_price: float, historical_low: float, 
                                       price_average: float) -> Dict:
        """🔥 توليد توصية شراء ذكية"""
        try:
            if historical_low == 0 or price_average == 0:
                return {
                    'recommendation_type': 'insufficient_data',
                    'confidence_score': 0.0,
                    'recommendation_text': 'لا توجد بيانات تاريخية كافية',
                    'price_vs_low_percentage': 0.0
                }
            
            # 🔥 المعادلة الذكية: (السعر الحالي - أقل سعر تاريخي) / أقل سعر تاريخي
            price_vs_low = ((current_price - historical_low) / historical_low) * 100
            
            # 🔥 المعادلة الثانية: نسبة السعر الحالي إلى المتوسط
            price_vs_avg = ((current_price - price_average) / price_average) * 100
            
            # توليد التوصية بناءً على النتائج
            if price_vs_low <= 5:  # السعر الحالي قريب جداً من الأدنى التاريخي
                recommendation = {
                    'recommendation_type': 'excellent_deal',
                    'confidence_score': 95.0,
                    'recommendation_text': '🎯 لقطة العمر! السعر في أدنى مستوياته التاريخية',
                    'price_vs_low_percentage': round(price_vs_low, 1),
                    'price_vs_avg_percentage': round(price_vs_avg, 1)
                }
            elif price_vs_low <= 15:
                recommendation = {
                    'recommendation_type': 'great_deal',
                    'confidence_score': 80.0,
                    'recommendation_text': '🔥 صفقة رائعة! السعر قريب من أدنى مستوى تاريخي',
                    'price_vs_low_percentage': round(price_vs_low, 1),
                    'price_vs_avg_percentage': round(price_vs_avg, 1)
                }
            elif price_vs_low <= 30:
                recommendation = {
                    'recommendation_type': 'good_deal',
                    'confidence_score': 65.0,
                    'recommendation_text': '👍 صفقة جيدة! السعر أقل من المتوسط التاريخي',
                    'price_vs_low_percentage': round(price_vs_low, 1),
                    'price_vs_avg_percentage': round(price_vs_avg, 1)
                }
            elif price_vs_avg < 0:  # السعر أقل من المتوسط
                recommendation = {
                    'recommendation_type': 'fair_deal',
                    'confidence_score': 50.0,
                    'recommendation_text': '👌 سعر معقول! أقل من المتوسط التاريخي',
                    'price_vs_low_percentage': round(price_vs_low, 1),
                    'price_vs_avg_percentage': round(price_vs_avg, 1)
                }
            else:
                recommendation = {
                    'recommendation_type': 'wait_better',
                    'confidence_score': 70.0,
                    'recommendation_text': '⏳ يمكنك الانتظار، السعر أعلى من المتوسط التاريخي',
                    'price_vs_low_percentage': round(price_vs_low, 1),
                    'price_vs_avg_percentage': round(price_vs_avg, 1)
                }
            
            # إضافة تفاصيل إضافية
            recommendation.update({
                'current_price': current_price,
                'historical_low': historical_low,
                'price_average': price_average,
                'savings_vs_low': current_price - historical_low,
                'savings_vs_avg': current_price - price_average
            })
            
            return recommendation
            
        except Exception as e:
            logger.error(f"❌ خطأ في توليد التوصية: {e}")
            return {
                'recommendation_type': 'error',
                'confidence_score': 0.0,
                'recommendation_text': 'خطأ في التحليل',
                'price_vs_low_percentage': 0.0
            }

# ==================== نظام التكامل المحسن ====================
class DiscountDashboardIntegrator:
    """مكامل بين نظام الزحف ولوحة التحكم مع التحليل التاريخي"""
    
    def __init__(self, dashboard_db: EnhancedDatabase):
        self.dashboard_db = dashboard_db
        self.extractor = DiscountAwareAmazonExtractor()
        self.historical_analyzer = HistoricalPriceAnalyzer()
        self.last_sync_time = datetime.now()
        
    def sync_product_with_historical_analysis(self, url: str) -> Tuple[Optional[Dict], str, str]:
        """🔥 مزامنة منتج مع التحليل التاريخي الذكي"""
        try:
            # استخلاص ASIN أولاً
            asin = self.extractor.extract_asin_from_url(url)
            if not asin:
                return None, "❌ لم يتم العثور على ASIN صالح في الرابط", "failed"
            
            logger.info(f"🔍 بدء التحليل الشامل للمنتج: {asin}")
            
            # استخلاص السعر الحالي
            price_data, message, extraction_method = self.extractor.extract_price(url)
            if not price_data:
                return None, f"❌ فشل استخلاص السعر: {message}", extraction_method
            
            current_price = price_data.get('price', 0)
            if current_price <= 0:
                return None, "❌ سعر غير صالح", extraction_method
            
            # 🔥 جلب البيانات التاريخية إذا كان النظام مفعلاً
            historical_data = None
            recommendation = None
            
            if HISTORICAL_ANALYSIS_CONFIG['enabled'] and HISTORICAL_ANALYSIS_CONFIG['fetch_on_new_product']:
                historical_data = self.historical_analyzer.fetch_historical_data(asin)
                
                if historical_data:
                    # 🔥 توليد توصية الشراء الذكية
                    recommendation = self.historical_analyzer.generate_purchase_recommendation(
                        current_price=current_price,
                        historical_low=historical_data['historical_low_price'],
                        price_average=historical_data['price_average']
                    )
            
            # تجهيز البيانات للمزامنة
            dashboard_data = {
                'asin': asin,
                'product_name': price_data.get('title', f'منتج {asin}'),
                'current_price': current_price,
                'reference_price': price_data.get('reference_price', 0.0),
                'discount_percentage': price_data.get('discount_percentage', 0.0),
                'currency': price_data.get('currency', 'USD'),
                'availability_status': self._determine_availability(price_data),
                'source_url': url,
                'category': price_data.get('category', 'غير مصنف'),
                'extraction_method': extraction_method
            }
            
            # إضافة البيانات التاريخية إذا كانت متوفرة
            if historical_data:
                dashboard_data.update({
                    'historical_low_price': historical_data['historical_low_price'],
                    'price_average': historical_data['price_average'],
                    'purchase_recommendation': recommendation['recommendation_text'] if recommendation else None,
                    'recommendation_confidence': recommendation['confidence_score'] if recommendation else 0.0
                })
            
            # المزامنة مع قاعدة البيانات
            success = self.dashboard_db.save_or_update_product(dashboard_data)
            
            if success:
                # حفظ التوصية إذا كانت متوفرة
                if recommendation:
                    self.dashboard_db.save_purchase_recommendation(asin, recommendation)
                
                response_data = {
                    'asin': asin,
                    'product_name': dashboard_data['product_name'],
                    'current_price': current_price,
                    'reference_price': dashboard_data['reference_price'],
                    'discount_percentage': dashboard_data['discount_percentage'],
                    'extraction_method': extraction_method,
                    'has_historical_data': historical_data is not None
                }
                
                # إضافة البيانات التاريخية إذا كانت متوفرة
                if historical_data:
                    response_data.update({
                        'historical_low_price': historical_data['historical_low_price'],
                        'price_average': historical_data['price_average'],
                        'purchase_recommendation': recommendation['recommendation_text'] if recommendation else None,
                        'recommendation_confidence': recommendation['confidence_score'] if recommendation else 0.0,
                        'price_vs_low_percentage': recommendation.get('price_vs_low_percentage', 0) if recommendation else 0,
                        'analysis': recommendation['recommendation_text'] if recommendation else 'لا توجد بيانات تاريخية'
                    })
                
                message_suffix = "مع تحليل تاريخي" if historical_data else "بدون تحليل تاريخي"
                return response_data, f"✅ تمت إضافة المنتج بنجاح {message_suffix}", extraction_method
            else:
                return None, "❌ فشل حفظ المنتج في قاعدة البيانات", extraction_method
                
        except Exception as e:
            logger.error(f"❌ خطأ في المزامنة: {e}")
            return None, f"❌ خطأ في المعالجة: {str(e)[:100]}", "error"
    
    def _determine_availability(self, product_data: Dict) -> str:
        """تحديد حالة التوفر"""
        price = product_data.get('price', 0)
        return 'active' if price > 0 else 'out_of_stock'

# ==================== تحديث تطبيق Flask مع الواجهة الجديدة ====================
print("\n🌐 جاري إنشاء تطبيق Flask مع النظام التاريخي...")
app = Flask(__name__)
print("✅ تطبيق Flask - تم إنشاؤه بنجاح مع النظام التاريخي")

# ==================== النظام الرئيسي مع النظام التاريخي ====================
class EnhancedDashboardSystem:
    """النظام الرئيسي مع لوحة تحكم تراكمية ونظام الوسيط الذكي والتحليل التاريخي"""
    
    def __init__(self):
        print("\n🔧 جاري تهيئة النظام المحسن مع النظام التاريخي الذكي...")
        
        # تهيئة قاعدة البيانات
        self.dashboard_db = EnhancedDatabase("dashboard_control.db")
        
        # تهيئة المكونات
        self.extractor = DiscountAwareAmazonExtractor()
        self.historical_analyzer = HistoricalPriceAnalyzer()
        self.integrator = DiscountDashboardIntegrator(self.dashboard_db)
        
        # تحميل المنتجات الحالية
        self._load_initial_products()
        
        # إعداد مسارات API
        self.setup_routes()
        
        print("\n" + "="*70)
        print("📊 نظام لوحة التحكم التراكمية - الإصدار 22.0")
        print("✅ تم التأسيس بنجاح! (نظام الوسيط الذكي + النظام التاريخي الذكي)")
        print("="*70)
        print("⚙️  ميزات النظام المحسّن:")
        print("   • 🔄 3 طبقات استخلاص (مباشر، ذكي، وسيط)")
        print("   • 📈 النظام التاريخي الذكي (CamelCamelCamel)")
        print("   • 🎯 مستشار الشراء الذكي")
        print("   • 🔑 مفتاح عبور API: 9e2a31cc365df963ee07a7084767a48c49f538fd")
        print("   • 📊 تتبع إحصائيات الاستخلاص")
        print("="*70)
    
    def _load_initial_products(self):
        """تحميل المنتجات الحالية"""
        print("\n📥 جاري تحميل المنتجات الحالية...")
        products = self.dashboard_db.get_all_products(limit=50)
        historical_count = sum(1 for p in products if p.get('historical_data_available'))
        print(f"✅ تم تحميل {len(products)} منتج ({historical_count} مع بيانات تاريخية)")
    
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
                <title>📊 لوحة تحكم الزحف الذكي - النظام التاريخي الذكي</title>
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
                    
                    .historical-panel { background: linear-gradient(135deg, #9c27b0, #673ab7); color: white; padding: 20px; border-radius: 15px; margin-bottom: 20px; }
                    
                    .search-box { margin-bottom: 20px; }
                    .url-input { width: 100%; padding: 15px; border: 2px solid #ddd; border-radius: 10px; font-size: 1rem; margin-bottom: 10px; }
                    .analyze-btn { background: linear-gradient(45deg, #2196f3, #1976d2); color: white; border: none; padding: 15px; font-size: 1.2rem; border-radius: 10px; width: 100%; cursor: pointer; font-weight: bold; }
                    
                    .stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 25px; }
                    .stat-card { background: #f5f5f5; padding: 20px; border-radius: 15px; text-align: center; border-left: 5px solid #2196f3; }
                    .stat-card.historical { border-left-color: #9c27b0; }
                    .stat-card.recommendations { border-left-color: #4caf50; }
                    .stat-card.drops { border-left-color: #f44336; }
                    .stat-card.proxy { border-left-color: #ff9800; }
                    .stat-value { font-size: 2rem; font-weight: bold; color: #1a237e; margin: 10px 0; }
                    .stat-label { color: #666; font-size: 0.9rem; }
                    
                    .products-table-container { margin-top: 25px; max-height: 600px; overflow-y: auto; border-radius: 10px; border: 1px solid #ddd; }
                    .products-table { width: 100%; border-collapse: collapse; }
                    .products-table th { background: #1a237e; color: white; padding: 15px; text-align: right; position: sticky; top: 0; }
                    .products-table td { padding: 12px 15px; border-bottom: 1px solid #eee; text-align: right; }
                    .products-table tr:hover { background: #f5f5f5; }
                    
                    .status-badge { padding: 5px 12px; border-radius: 15px; font-size: 0.8rem; font-weight: bold; }
                    .status-historical { background: linear-gradient(45deg, #9c27b0, #673ab7); color: white; }
                    .status-excellent { background: linear-gradient(45deg, #4caf50, #2e7d32); color: white; }
                    .status-good { background: linear-gradient(45deg, #8bc34a, #689f38); color: white; }
                    .status-fair { background: linear-gradient(45deg, #ff9800, #f57c00); color: white; }
                    .status-wait { background: linear-gradient(45deg, #ff5722, #d84315); color: white; }
                    
                    .recommendation-box { background: #e8f5e9; border: 2px solid #4caf50; border-radius: 10px; padding: 15px; margin: 10px 0; }
                    .recommendation-box.excellent { background: #e8f5e9; border-color: #4caf50; }
                    .recommendation-box.good { background: #fff3e0; border-color: #ff9800; }
                    .recommendation-box.wait { background: #ffebee; border-color: #f44336; }
                    
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
                        loadHistoricalStats();
                        loadProductsTable();
                        loadBestDeals();
                        
                        // تحديث تلقائي كل 30 ثانية
                        setInterval(() => {
                            loadDashboardStats();
                            loadHistoricalStats();
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
                    
                    // تحميل إحصائيات النظام التاريخي
                    async function loadHistoricalStats() {
                        try {
                            const response = await fetch('/api/historical-stats');
                            const data = await response.json();
                            
                            if (data.status === 'success') {
                                updateHistoricalDisplay(data);
                            }
                        } catch (error) {
                            console.error('Error loading historical stats:', error);
                        }
                    }
                    
                    // تحميل جدول المنتجات
                    async function loadProductsTable() {
                        const tableBody = document.getElementById('productsTableBody');
                        tableBody.innerHTML = '<tr><td colspan="12" style="text-align: center; padding: 30px;">جاري تحميل البيانات...</td></tr>';
                        
                        try {
                            const response = await fetch('/api/dashboard-products?limit=30');
                            const data = await response.json();
                            
                            if (data.status === 'success') {
                                updateProductsTable(data.products);
                            }
                        } catch (error) {
                            tableBody.innerHTML = '<tr><td colspan="12" style="text-align: center; padding: 30px; color: #f44336;">خطأ في تحميل البيانات</td></tr>';
                        }
                    }
                    
                    // تحميل أفضل العروض
                    async function loadBestDeals() {
                        try {
                            const response = await fetch('/api/best-historical-deals');
                            const data = await response.json();
                            
                            if (data.status === 'success') {
                                updateBestDeals(data.deals);
                            }
                        } catch (error) {
                            console.error('Error loading best deals:', error);
                        }
                    }
                    
                    // تحديث عرض الإحصائيات
                    function updateStatsDisplay(stats) {
                        document.getElementById('totalProducts').textContent = stats.total_products.toLocaleString();
                        document.getElementById('activeProducts').textContent = stats.active_products.toLocaleString();
                        document.getElementById('avgPrice').textContent = '$' + stats.avg_price.toLocaleString();
                        document.getElementById('avgDiscount').textContent = stats.avg_discount.toLocaleString() + '%';
                    }
                    
                    // تحديث عرض الإحصائيات التاريخية
                    function updateHistoricalDisplay(data) {
                        const stats = data.stats;
                        
                        document.getElementById('historicalProducts').textContent = stats.historical_products.toLocaleString();
                        document.getElementById('excellentDeals').textContent = stats.excellent_deals.toLocaleString();
                        document.getElementById('goodDeals').textContent = stats.good_deals.toLocaleString();
                        document.getElementById('avgSavings').textContent = '$' + stats.avg_savings.toLocaleString();
                    }
                    
                    // تحديث جدول المنتجات
                    function updateProductsTable(products) {
                        const tableBody = document.getElementById('productsTableBody');
                        
                        if (products.length === 0) {
                            tableBody.innerHTML = '<tr><td colspan="12" style="text-align: center; padding: 30px;">لا توجد منتجات بعد. ابدأ بإضافة منتج جديد!</td></tr>';
                            return;
                        }
                        
                        let html = '';
                        
                        products.forEach(product => {
                            let historicalBadge = '';
                            let recommendationBadge = '';
                            let historicalInfo = '';
                            
                            if (product.historical_data_available) {
                                historicalBadge = '<span class="status-badge status-historical">📈 تاريخي</span>';
                                
                                if (product.purchase_recommendation) {
                                    let recClass = 'status-fair';
                                    if (product.purchase_recommendation.includes('لقطة العمر')) {
                                        recClass = 'status-excellent';
                                    } else if (product.purchase_recommendation.includes('صفقة رائعة')) {
                                        recClass = 'status-good';
                                    } else if (product.purchase_recommendation.includes('يمكنك الانتظار')) {
                                        recClass = 'status-wait';
                                    }
                                    
                                    recommendationBadge = `<span class="status-badge ${recClass}">${product.purchase_recommendation.substring(0, 15)}...</span>`;
                                }
                                
                                if (product.historical_low_price > 0) {
                                    const vsLow = ((product.current_price - product.historical_low_price) / product.historical_low_price * 100).toFixed(1);
                                    historicalInfo = `
                                        <div style="font-size: 0.8rem; color: #666; margin-top: 5px;">
                                            <div>أدنى تاريخي: $${product.historical_low_price.toFixed(2)}</div>
                                            <div>فرق: ${vsLow}%</div>
                                        </div>
                                    `;
                                }
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
                            
                            html += `
                                <tr>
                                    <td>${product.product_name}</td>
                                    <td><code style="background: #f5f5f5; padding: 3px 8px; border-radius: 4px;">${product.asin}</code></td>
                                    <td>
                                        <div style="font-weight: bold; color: #d32f2f;">$${product.current_price.toFixed(2)}</div>
                                        ${historicalInfo}
                                    </td>
                                    <td><span class="discount-badge ${discountClass}">${discountText}</span></td>
                                    <td>${historicalBadge}</td>
                                    <td>${recommendationBadge}</td>
                                    <td>${product.category}</td>
                                    <td>${product.price_change_count || 0}</td>
                                    <td>${new Date(product.last_updated).toLocaleDateString('ar-SA')}</td>
                                </tr>
                            `;
                        });
                        
                        tableBody.innerHTML = html;
                    }
                    
                    // تحديث أفضل العروض
                    function updateBestDeals(deals) {
                        const dealsContainer = document.getElementById('bestDeals');
                        
                        if (deals.length === 0) {
                            dealsContainer.innerHTML = '<div style="text-align: center; padding: 20px; color: #666;">لا توجد عروض تاريخية مميزة</div>';
                            return;
                        }
                        
                        let html = '';
                        
                        deals.slice(0, 3).forEach(deal => {
                            const vsLow = deal.price_vs_low_percentage || 0;
                            let recClass = 'fair';
                            let recIcon = '👌';
                            
                            if (vsLow <= 5) {
                                recClass = 'excellent';
                                recIcon = '🎯';
                            } else if (vsLow <= 15) {
                                recClass = 'good';
                                recIcon = '🔥';
                            } else if (vsLow > 30) {
                                recClass = 'wait';
                                recIcon = '⏳';
                            }
                            
                            html += `
                                <div class="recommendation-box ${recClass}">
                                    <div style="display: flex; justify-content: space-between; align-items: start;">
                                        <div>
                                            <strong>${recIcon} ${deal.product_name.substring(0, 40)}...</strong>
                                            <div style="font-size: 0.9rem; color: #666; margin-top: 5px;">
                                                السعر: <span style="color: #d32f2f; font-weight: bold;">$${deal.current_price.toFixed(2)}</span>
                                            </div>
                                        </div>
                                        <span class="status-badge status-${recClass}">${deal.recommendation_type}</span>
                                    </div>
                                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin: 10px 0;">
                                        <div>
                                            <div style="font-size: 0.8rem; color: #666;">أدنى تاريخي</div>
                                            <div style="font-size: 0.9rem;">$${deal.historical_low.toFixed(2)}</div>
                                        </div>
                                        <div>
                                            <div style="font-size: 0.8rem; color: #666;">الفرق</div>
                                            <div style="font-size: 0.9rem; color: ${vsLow <= 15 ? '#4caf50' : '#f57c00'}; font-weight: bold;">
                                                ${vsLow.toFixed(1)}%
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            `;
                        });
                        
                        dealsContainer.innerHTML = html;
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
                                    loadHistoricalStats();
                                    loadProductsTable();
                                    loadBestDeals();
                                }, 1500);
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
                        
                        let historicalSection = '';
                        let recommendationSection = '';
                        
                        if (product.has_historical_data && product.historical_low_price > 0) {
                            const vsLow = product.price_vs_low_percentage || 0;
                            let recClass = 'fair';
                            let recColor = '#ff9800';
                            
                            if (vsLow <= 5) {
                                recClass = 'excellent';
                                recColor = '#4caf50';
                            } else if (vsLow <= 15) {
                                recClass = 'good';
                                recColor = '#8bc34a';
                            } else if (vsLow > 30) {
                                recClass = 'wait';
                                recColor = '#f44336';
                            }
                            
                            historicalSection = `
                                <div style="margin: 20px 0; padding: 15px; background: #f5f5f5; border-radius: 10px;">
                                    <h4 style="color: #673ab7; margin-bottom: 15px;">📈 التحليل التاريخي الذكي</h4>
                                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                                        <div style="text-align: center;">
                                            <div style="font-size: 0.9rem; color: #666;">أقل سعر تاريخي</div>
                                            <div style="font-size: 1.5rem; color: #f44336; font-weight: bold;">
                                                $${product.historical_low_price.toFixed(2)}
                                            </div>
                                        </div>
                                        <div style="text-align: center;">
                                            <div style="font-size: 0.9rem; color: #666;">متوسط السعر</div>
                                            <div style="font-size: 1.3rem; color: #2196f3;">
                                                $${product.price_average.toFixed(2)}
                                            </div>
                                        </div>
                                    </div>
                                    <div style="text-align: center; margin-top: 15px; padding: 10px; background: ${recColor}; color: white; border-radius: 8px;">
                                        <strong>${product.purchase_recommendation || 'جاري التحليل...'}</strong>
                                        <div style="font-size: 0.9rem; margin-top: 5px;">
                                            الثقة: ${product.recommendation_confidence || 0}%
                                        </div>
                                    </div>
                                </div>
                            `;
                        } else {
                            historicalSection = `
                                <div style="margin: 20px 0; padding: 15px; background: #fff3e0; border-radius: 10px;">
                                    <p style="color: #f57c00;">⚠️ لم يتم العثور على بيانات تاريخية لهذا المنتج</p>
                                    <p style="font-size: 0.9rem; color: #666;">النظام سيحاول تحديث البيانات تلقائياً في المرة القادمة</p>
                                </div>
                            `;
                        }
                        
                        let html = `
                            <div style="background: #e8f5e9; border-left: 5px solid #4caf50; padding: 20px; border-radius: 10px; margin-top: 20px;">
                                <h3 style="color: #2e7d32;">✅ تمت إضافة المنتج بنجاح</h3>
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
                                        <span style="margin-top: 5px; display: inline-block; padding: 5px 12px; background: #2196f3; color: white; border-radius: 15px;">
                                            ${product.discount_percentage.toFixed(1)}%
                                        </span>
                                    </div>
                                </div>
                                ${historicalSection}
                                <p style="margin-top: 15px; color: #666; font-size: 0.9rem;">
                                    ✅ تم تفعيل المراقبة التلقائية مع النظام التاريخي الذكي
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
                                    جرب إضافة المنتج مرة أخرى، النظام سيستخدم الوسيط والنظام التاريخي تلقائياً
                                </p>
                            </div>
                        `;
                        result.style.display = 'block';
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
                        <p>نظام تراكمي مع التحليل التاريخي الذكي ومستشار الشراء</p>
                        <div class="dashboard-badge">الإصدار 22.0 - النظام التاريخي الذكي ✅</div>
                    </div>
                    
                    <div class="main-content">
                        <!-- الشريط الجانبي -->
                        <div class="sidebar">
                            <h3 style="color: #1a237e; margin-bottom: 20px; border-bottom: 2px solid #eee; padding-bottom: 10px;">🔍 إضافة منتج جديد</h3>
                            
                            <div style="background: #e3f2fd; padding: 15px; border-radius: 10px; margin-bottom: 20px;">
                                <strong>🎯 النظام التاريخي الذكي:</strong><br>
                                <span style="font-size: 0.9rem; color: #666;">
                                    النظام يحلل التاريخ من CamelCamelCamel ويقدم توصيات شراء ذكية
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
                                <p>جاري تحليل السعر والتاريخ والتوصيات...</p>
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
                                <h4 style="color: #1a237e; margin-bottom: 15px;">🎯 أفضل العروض التاريخية</h4>
                                <div id="bestDeals">
                                    <!-- سيتم ملؤه بالبيانات -->
                                </div>
                            </div>
                        </div>
                        
                        <!-- اللوحة الرئيسية -->
                        <div class="main-panel">
                            <!-- لوحة النظام التاريخي -->
                            <div class="historical-panel">
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <div>
                                        <h2 style="margin: 0;">🎯 النظام التاريخي الذكي</h2>
                                        <p style="margin: 5px 0 0 0; opacity: 0.9;">
                                            محلل تاريخي لمقارنة الأسعار وتقديم توصيات شراء ذكية
                                        </p>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- إحصائيات النظام التاريخي -->
                            <div class="stats-grid">
                                <div class="stat-card historical">
                                    <div class="stat-label">المنتجات مع تاريخ</div>
                                    <div class="stat-value" id="historicalProducts">0</div>
                                    <div style="font-size: 0.8rem; color: #666;">بيانات تاريخية متوفرة</div>
                                </div>
                                
                                <div class="stat-card recommendations">
                                    <div class="stat-label">عروض ممتازة</div>
                                    <div class="stat-value" id="excellentDeals">0</div>
                                    <div style="font-size: 0.8rem; color: #666;">لقطات العمر</div>
                                </div>
                                
                                <div class="stat-card drops">
                                    <div class="stat-label">عروض جيدة</div>
                                    <div class="stat-value" id="goodDeals">0</div>
                                    <div style="font-size: 0.8rem; color: #666;">صفقات رائعة</div>
                                </div>
                                
                                <div class="stat-card proxy">
                                    <div class="stat-label">متوسط التوفير</div>
                                    <div class="stat-value" id="avgSavings">$0</div>
                                    <div style="font-size: 0.8rem; color: #666;">مقارنة بالتاريخ</div>
                                </div>
                            </div>
                            
                            <!-- إحصائيات النظام الأساسية -->
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
                                    <div class="stat-label">متوسط الخصم</div>
                                    <div class="stat-value" id="avgDiscount">0%</div>
                                    <div style="font-size: 0.8rem; color: #666;">الخصومات الحالية</div>
                                </div>
                            </div>
                            
                            <!-- جدول المنتجات -->
                            <div style="margin: 30px 0 20px 0;">
                                <h3 style="color: #1a237e; border-bottom: 2px solid #eee; padding-bottom: 10px;">
                                    📋 جميع المنتجات مع التحليل التاريخي
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
                                            <th>بيانات تاريخية</th>
                                            <th>توصية الشراء</th>
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
                        <p>© 2024 نظام التحليل التاريخي الذكي - الإصدار 22.0</p>
                        <p>🎯 مستشار الشراء الذكي | 📈 تحليل تاريخي من CamelCamelCamel | 🔑 مفتاح عبور API</p>
                    </div>
                </div>
            </body>
            </html>
            ''')
        
        @app.route('/api/dashboard-stats', methods=['GET'])
        def get_dashboard_stats():
            """الحصول على إحصائيات لوحة التحكم"""
            try:
                # الحصول على إحصائيات أساسية
                conn = system.dashboard_db.get_connection()
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT 
                        COUNT(*) as total,
                        COUNT(CASE WHEN availability_status = 'active' THEN 1 END) as active,
                        AVG(current_price) as avg_price,
                        AVG(discount_percentage) as avg_discount
                    FROM dashboard_products
                    WHERE current_price > 0
                ''')
                
                row = cursor.fetchone()
                
                stats = {
                    'total_products': row[0] if row else 0,
                    'active_products': row[1] if row else 0,
                    'avg_price': round(row[2], 2) if row and row[2] else 0.0,
                    'avg_discount': round(row[3], 2) if row and row[3] else 0.0,
                }
                
                return jsonify({'status': 'success', 'stats': stats})
            except Exception as e:
                return jsonify({'status': 'error', 'error': str(e)}), 500
        
        @app.route('/api/historical-stats', methods=['GET'])
        def get_historical_stats():
            """الحصول على إحصائيات النظام التاريخي"""
            try:
                conn = system.dashboard_db.get_connection()
                cursor = conn.cursor()
                
                # عدد المنتجات مع بيانات تاريخية
                cursor.execute('''
                    SELECT COUNT(*) FROM dashboard_products 
                    WHERE historical_data_available = 1 AND historical_low_price > 0
                ''')
                historical_products = cursor.fetchone()[0] or 0
                
                # عدد التوصيات الممتازة
                cursor.execute('''
                    SELECT COUNT(*) FROM dashboard_products 
                    WHERE purchase_recommendation LIKE '%لقطة العمر%' 
                    OR purchase_recommendation LIKE '%excellent%'
                ''')
                excellent_deals = cursor.fetchone()[0] or 0
                
                # عدد التوصيات الجيدة
                cursor.execute('''
                    SELECT COUNT(*) FROM dashboard_products 
                    WHERE purchase_recommendation LIKE '%صفقة رائعة%' 
                    OR purchase_recommendation LIKE '%great%'
                ''')
                good_deals = cursor.fetchone()[0] or 0
                
                # متوسط التوفير مقارنة بأقل سعر تاريخي
                cursor.execute('''
                    SELECT AVG(current_price - historical_low_price) 
                    FROM dashboard_products 
                    WHERE historical_low_price > 0 AND current_price > historical_low_price
                ''')
                avg_savings_row = cursor.fetchone()
                avg_savings = round(avg_savings_row[0], 2) if avg_savings_row and avg_savings_row[0] else 0.0
                
                stats = {
                    'historical_products': historical_products,
                    'excellent_deals': excellent_deals,
                    'good_deals': good_deals,
                    'avg_savings': avg_savings,
                    'historical_enabled': HISTORICAL_ANALYSIS_CONFIG['enabled'],
                    'api_key_configured': bool(HISTORICAL_ANALYSIS_CONFIG['camel_api_key'])
                }
                
                return jsonify({'status': 'success', 'stats': stats})
            except Exception as e:
                return jsonify({'status': 'error', 'error': str(e)}), 500
        
        @app.route('/api/dashboard-products', methods=['GET'])
        def get_dashboard_products():
            """الحصول على المنتجات للعرض"""
            try:
                limit = request.args.get('limit', 50, type=int)
                offset = request.args.get('offset', 0, type=int)
                
                conn = system.dashboard_db.get_connection()
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT asin, product_name, current_price, reference_price, discount_percentage,
                           currency, availability_status, last_updated, source_url, category,
                           price_change_count, initial_price, monitoring_enabled, price_drop_detected,
                           extraction_method, last_extraction_status, historical_low_price,
                           price_average, last_history_sync, historical_data_available,
                           purchase_recommendation, recommendation_confidence
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
                        'historical_low_price': row[16] or 0.0,
                        'price_average': row[17] or 0.0,
                        'last_history_sync': row[18],
                        'historical_data_available': bool(row[19]) if row[19] is not None else False,
                        'purchase_recommendation': row[20],
                        'recommendation_confidence': row[21] or 0.0,
                        'has_discount': row[3] and row[3] > row[2] and row[2] > 0
                    })
                
                return jsonify({
                    'status': 'success',
                    'products': products,
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                return jsonify({'status': 'error', 'error': str(e)}), 500
        
        @app.route('/api/analyze-product', methods=['GET'])
        def analyze_product():
            """🔥 تحليل منتج جديد مع النظام التاريخي"""
            url = request.args.get('url')
            
            if not url:
                return jsonify({'status': 'error', 'error': 'رابط المنتج مطلوب'}), 400
            
            if 'amazon.com' not in url.lower():
                return jsonify({'status': 'error', 'error': 'النظام يدعم Amazon.com فقط'}), 400
            
            logger.info(f"🎯 بدء تحليل منتج جديد مع النظام التاريخي: {url[:80]}...")
            
            try:
                # استخدام المكامل المحسن مع النظام التاريخي
                product_data, message, extraction_method = system.integrator.sync_product_with_historical_analysis(url)
                
                if not product_data:
                    return jsonify({'status': 'error', 'error': message}), 400
                
                response = {
                    'status': 'success',
                    'product': product_data,
                    'message': message
                }
                
                logger.info(f"✅ تمت إضافة المنتج {product_data['asin']} مع النظام التاريخي")
                return jsonify(response)
                
            except Exception as e:
                logger.error(f"❌ خطأ في تحليل المنتج: {e}")
                return jsonify({'status': 'error', 'error': str(e)}), 500
        
        @app.route('/api/search-products', methods=['GET'])
        def search_products():
            """البحث في المنتجات"""
            query = request.args.get('q', '')
            
            try:
                conn = system.dashboard_db.get_connection()
                cursor = conn.cursor()
                
                if not query.strip():
                    cursor.execute('''
                        SELECT asin, product_name, current_price, reference_price, discount_percentage,
                               currency, availability_status, last_updated, category, extraction_method,
                               historical_low_price, purchase_recommendation
                        FROM dashboard_products
                        ORDER BY last_updated DESC
                        LIMIT 50
                    ''')
                else:
                    search_term = f"%{query}%"
                    cursor.execute('''
                        SELECT asin, product_name, current_price, reference_price, discount_percentage,
                               currency, availability_status, last_updated, category, extraction_method,
                               historical_low_price, purchase_recommendation
                        FROM dashboard_products
                        WHERE asin LIKE ? OR product_name LIKE ? OR category LIKE ?
                        ORDER BY last_updated DESC
                        LIMIT 50
                    ''', (search_term, search_term, search_term))
                
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
                        'historical_low_price': row[10] or 0.0,
                        'purchase_recommendation': row[11],
                        'has_discount': row[3] and row[3] > row[2] and row[2] > 0
                    })
                
                return jsonify({
                    'status': 'success',
                    'products': products,
                    'query': query,
                    'count': len(products)
                })
            except Exception as e:
                return jsonify({'status': 'error', 'error': str(e)}), 500
        
        @app.route('/api/best-historical-deals', methods=['GET'])
        def get_best_historical_deals():
            """🔥 الحصول على أفضل العروض بناءً على التحليل التاريخي"""
            try:
                conn = system.dashboard_db.get_connection()
                cursor = conn.cursor()
                
                # جلب المنتجات مع بيانات تاريخية وتوصيات
                cursor.execute('''
                    SELECT asin, product_name, current_price, historical_low_price,
                           price_average, purchase_recommendation, recommendation_confidence
                    FROM dashboard_products
                    WHERE historical_data_available = 1 
                    AND historical_low_price > 0
                    AND purchase_recommendation IS NOT NULL
                    ORDER BY recommendation_confidence DESC, 
                             (current_price - historical_low_price) / historical_low_price ASC
                    LIMIT 10
                ''')
                
                deals = []
                for row in cursor.fetchall():
                    current_price = row[2] or 0
                    historical_low = row[3] or 0
                    
                    if historical_low > 0 and current_price > 0:
                        price_vs_low = ((current_price - historical_low) / historical_low * 100)
                        
                        # تحديد نوع التوصية
                        recommendation_type = 'fair'
                        if price_vs_low <= 5:
                            recommendation_type = 'excellent'
                        elif price_vs_low <= 15:
                            recommendation_type = 'great'
                        elif price_vs_low > 30:
                            recommendation_type = 'wait'
                        
                        deals.append({
                            'asin': row[0],
                            'product_name': row[1] or f"منتج {row[0]}",
                            'current_price': current_price,
                            'historical_low': historical_low,
                            'price_average': row[4] or 0.0,
                            'purchase_recommendation': row[5] or 'لا توجد توصية',
                            'recommendation_confidence': row[6] or 0.0,
                            'price_vs_low_percentage': price_vs_low,
                            'recommendation_type': recommendation_type,
                            'savings': current_price - historical_low
                        })
                
                return jsonify({
                    'status': 'success',
                    'deals': deals,
                    'count': len(deals)
                })
            except Exception as e:
                return jsonify({'status': 'error', 'error': str(e)}), 500
        
        @app.route('/api/update-historical', methods=['POST'])
        def update_historical():
            """🔥 تحديث البيانات التاريخية لمنتج معين"""
            data = request.json
            asin = data.get('asin')
            
            if not asin:
                return jsonify({'status': 'error', 'error': 'ASIN مطلوب'}), 400
            
            try:
                # جلب البيانات التاريخية
                historical_data = system.historical_analyzer.fetch_historical_data(asin)
                
                if historical_data:
                    # تحديث قاعدة البيانات
                    system.dashboard_db.update_historical_data(asin, historical_data)
                    
                    # جلب السعر الحالي
                    conn = system.dashboard_db.get_connection()
                    cursor = conn.cursor()
                    cursor.execute('SELECT current_price FROM dashboard_products WHERE asin = ?', (asin,))
                    row = cursor.fetchone()
                    
                    if row and row[0]:
                        current_price = row[0]
                        # توليد توصية جديدة
                        recommendation = system.historical_analyzer.generate_purchase_recommendation(
                            current_price=current_price,
                            historical_low=historical_data['historical_low_price'],
                            price_average=historical_data['price_average']
                        )
                        
                        # تحديث التوصية
                        cursor.execute('''
                            UPDATE dashboard_products 
                            SET purchase_recommendation = ?, recommendation_confidence = ?
                            WHERE asin = ?
                        ''', (recommendation['recommendation_text'], recommendation['confidence_score'], asin))
                        
                        conn.commit()
                    
                    return jsonify({
                        'status': 'success',
                        'message': 'تم تحديث البيانات التاريخية',
                        'historical_data': historical_data
                    })
                else:
                    return jsonify({'status': 'error', 'error': 'فشل جلب البيانات التاريخية'}), 400
                    
            except Exception as e:
                return jsonify({'status': 'error', 'error': str(e)}), 500
        
        @app.route('/system-status')
        def system_status():
            """🔥 صفحة حالة النظام مع النظام التاريخي"""
            return jsonify({
                'status': 'active',
                'version': '22.0',
                'features': {
                    'smart_extraction': True,
                    'proxy_system': True,
                    'scraperapi_integration': True,
                    'historical_analysis': HISTORICAL_ANALYSIS_CONFIG['enabled'],
                    'historical_api_key_configured': bool(HISTORICAL_ANALYSIS_CONFIG['camel_api_key']),
                    'purchase_recommendations': True,
                    'smart_rotation': MONITORING_CONFIG['smart_rotation']
                },
                'timestamp': datetime.now().isoformat(),
                'historical_config': HISTORICAL_ANALYSIS_CONFIG,
                'message': 'النظام يعمل مع النظام التاريخي الذكي بنسبة نجاح عالية'
            })
        
        @app.route('/ping')
        def ping():
            """صفحة البقاء حياً"""
            return jsonify({
                'status': 'alive',
                'timestamp': datetime.now().isoformat(),
                'historical_system': HISTORICAL_ANALYSIS_CONFIG['enabled'],
                'proxy_available': bool(PROXY_CONFIG.get('scraperapi_key'))
            }), 200

# ==================== تشغيل النظام ====================
def main():
    """الدالة الرئيسية"""
    print("\n" + "="*70)
    print("🚀 بدء تشغيل النظام التاريخي الذكي")
    print("="*70)
    
    system = None
    try:
        system = EnhancedDashboardSystem()
        
        print("\n✨ النظام يعمل الآن!")
        print(f"🌐 رابط الواجهة: http://localhost:9090")
        print(f"📡 واجهات API الرئيسية:")
        print(f"   • /                      - الواجهة الرئيسية مع النظام التاريخي")
        print(f"   • /ping                  - صفحة البقاء حياً")
        print(f"   • /system-status         - حالة النظام")
        print(f"   • /api/historical-stats  - إحصائيات النظام التاريخي")
        print(f"   • /api/best-historical-deals - أفضل العروض التاريخية")
        print("="*70)
        print("\n🎯 تفاصيل النظام التاريخي الذكي:")
        print(f"   • ✅ CamelCamelCamel API: مفعل (مفتاح: {HISTORICAL_ANALYSIS_CONFIG['camel_api_key'][:15]}...)")
        print(f"   • 📈 تحليل التاريخ: {HISTORICAL_ANALYSIS_CONFIG['price_history_days']} يوم")
        print(f"   • 🎯 مستشار الشراء: مفعل مع خوارزمية ذكية")
        print(f"   • 🔥 المعادلة: (السعر الحالي - أقل سعر تاريخي) / أقل سعر تاريخي")
        print("="*70)
        
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
        print("\n✅ تم إغلاق النظام بشكل آمن")

if __name__ == '__main__':
    main()
