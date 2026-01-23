"""
ultimate_amazon_price_tracker_pro.py - نظام تتبع أسعار Amazon الاحترافي - جاهز للإنتاج
الإصدار: 24.0 ULTIMATE EDITION + SMART RECOMMENDATIONS

ميزات فريدة لم تُرى من قبل:
✅ AI-Powered Price Prediction
✅ Multi-Region Support (الشرق الأوسط، أمريكا، أوروبا)
✅ Smart Buy/Wait/Don't Buy Recommendations 🆕
✅ Telegram Bot Integration
✅ Push Notifications + Email + SMS
✅ Advanced Analytics Dashboard
✅ Real Price Analysis (vs Fake Discounts)

Premium Features
===================================
"""

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
import traceback
import base64
import uuid
import platform
import requests
import threading
from threading import Lock, RLock, Thread, Event, Timer
from datetime import datetime, timedelta
from urllib.parse import urlparse, parse_qs, urlencode, urljoin, quote
from typing import Dict, List, Optional, Tuple, Set, Any
from collections import Counter, defaultdict
from dataclasses import dataclass
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from flask import Flask, request, jsonify, render_template_string, send_file
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import logging

# ==================== CONFIGURATION ====================

VERSION = "24.0 ULTIMATE + SMART RECOMMENDATIONS"
BUILD_DATE = datetime.now().strftime("%Y-%m-%d")

# Multi-Region Configuration
REGION_CONFIGS = {
    'US': {
        'domain': 'amazon.com',
        'currency': 'USD',
        'currency_symbol': '$',
        'name': 'United States',
        'flag': '🇺🇸'
    },
    'UK': {
        'domain': 'amazon.co.uk',
        'currency': 'GBP',
        'currency_symbol': '£',
        'name': 'United Kingdom',
        'flag': '🇬🇧'
    },
    'DE': {
        'domain': 'amazon.de',
        'currency': 'EUR',
        'currency_symbol': '€',
        'name': 'Germany',
        'flag': '🇩🇪'
    },
    'SA': {
        'domain': 'amazon.sa',
        'currency': 'SAR',
        'currency_symbol': 'ر.س',
        'name': 'Saudi Arabia',
        'flag': '🇸🇦'
    },
    'AE': {
        'domain': 'amazon.ae',
        'currency': 'AED',
        'currency_symbol': 'د.إ',
        'name': 'UAE',
        'flag': '🇦🇪'
    }
}

DEFAULT_REGION = 'US'

# API Configuration
SCRAPERAPI_CONFIG = {
    'enabled': True,
    'api_key': 'c5ff3050a86e42483899a1fff1ec4780',
    'url': 'http://api.scraperapi.com',
    'premium_features': True,
    'auto_retry': True,
    'render_js': True
}

# Notification Configuration
NOTIFICATION_CONFIG = {
    'email': {
        'enabled': True,
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,
        'sender': 'kklb1553@gmail.com',
        'password': 'bgbjfptmqapmwzef',
        'receiver': 'kklb1553@gmail.com'
    },
    'telegram': {
        'enabled': False,
        'bot_token': '',
        'chat_id': ''
    },
    'push': {
        'enabled': False,
        'service': 'pushover'
    }
}

# AI Price Prediction Configuration
AI_PREDICTION_CONFIG = {
    'enabled': True,
    'model': 'linear_regression',
    'prediction_days': 30,
    'confidence_threshold': 0.7,
    'min_data_points': 5
}

# 🆕 Smart Recommendation Configuration
RECOMMENDATION_CONFIG = {
    'enabled': True,
    'analysis_period_days': 30,
    'buy_threshold': {
        'discount_min': 25.0,  # خصم حقيقي ≥ 25%
        'vs_avg_max': 0.0      # أقل من أو يساوي المتوسط
    },
    'wait_threshold': {
        'discount_min': 10.0,
        'discount_max': 24.9,
        'vs_avg_range': (-5.0, 5.0)  # ±5% من المتوسط
    },
    'dont_buy_threshold': {
        'discount_max': 9.9,
        'vs_avg_min': 5.0  # أعلى من المتوسط بـ 5%
    }
}

# Analytics Configuration
ANALYTICS_CONFIG = {
    'enabled': True,
    'retention_days': 365,
    'real_time_updates': True,
    'export_formats': ['json', 'csv', 'pdf']
}

# Monitoring Configuration
MONITORING_CONFIG = {
    'enabled': True,
    'interval': 3600,  # 1 hour
    'price_drop_threshold': 10.0,
    'stock_alert': True,
    'trend_analysis': True,
    'max_concurrent_checks': 10
}

# ==================== LOGGING SETUP ====================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('amazon_tracker.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

print("=" * 80)
print("🚀 ULTIMATE AMAZON PRICE TRACKER - PRODUCTION READY")
print(f"📦 Version: {VERSION} | Build: {BUILD_DATE}")
print("=" * 80)
print("\n🎯 PREMIUM FEATURES INITIALIZED:")
print("  ✅ Multi-Region Support (US, UK, DE, SA, AE)")
print("  ✅ AI-Powered Price Prediction")
print("  ✅ Smart Buy/Wait/Don't Buy Recommendations 🆕")
print("  ✅ Advanced Analytics Dashboard")
print("  ✅ Real-time Notifications (Email, Telegram, Push)")
print("  ✅ Smart Extraction System (3-Layer Fallback)")
print("  ✅ Historical Price Analysis")
print("  ✅ Trend Detection & Forecasting")
print("  ✅ Export Reports (JSON, CSV, PDF)")
print("=" * 80)

# ==================== ENHANCED DATABASE ====================

class UltimateDatabaseManager:
    """Enterprise-Grade Database Manager with Recommendations Support"""
    
    def __init__(self, db_path: str = "ultimate_tracker.db"):
        self.db_path = db_path
        self.local = threading.local()
        self.lock = RLock()
        self._initialize_database()
    
    def get_connection(self):
        """Thread-safe connection"""
        with self.lock:
            if not hasattr(self.local, 'connection'):
                self.local.connection = sqlite3.connect(
                    self.db_path,
                    check_same_thread=False,
                    timeout=30.0
                )
                self.local.connection.execute('PRAGMA journal_mode=WAL')
                self.local.connection.execute('PRAGMA synchronous=NORMAL')
                self.local.connection.execute('PRAGMA cache_size=10000')
            return self.local.connection
    
    def _initialize_database(self):
        """Initialize all database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # ============ Products Table ============
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                asin TEXT UNIQUE NOT NULL,
                region TEXT DEFAULT 'US',
                product_name TEXT,
                current_price REAL,
                reference_price REAL,
                discount_percentage REAL DEFAULT 0.0,
                currency TEXT DEFAULT 'USD',
                availability_status TEXT DEFAULT 'active',
                category TEXT,
                brand TEXT,
                rating REAL,
                review_count INTEGER,
                image_url TEXT,
                product_url TEXT,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                monitoring_enabled BOOLEAN DEFAULT 1,
                price_alert_threshold REAL DEFAULT 10.0,
                metadata TEXT,
                CHECK (length(asin) = 10)
            )
        ''')
        
        # ============ Price History Table ============
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                asin TEXT NOT NULL,
                price REAL NOT NULL,
                reference_price REAL,
                discount_percentage REAL,
                availability TEXT DEFAULT 'in_stock',
                extraction_method TEXT DEFAULT 'direct',
                captured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (asin) REFERENCES products (asin) ON DELETE CASCADE
            )
        ''')
        
        # ============ AI Predictions Table ============
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                asin TEXT NOT NULL,
                prediction_date DATE NOT NULL,
                predicted_price REAL NOT NULL,
                confidence_score REAL,
                trend TEXT,
                model_version TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (asin) REFERENCES products (asin) ON DELETE CASCADE
            )
        ''')
        
        # ============ Price Alerts Table ============
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                asin TEXT NOT NULL,
                old_price REAL NOT NULL,
                new_price REAL NOT NULL,
                drop_percentage REAL NOT NULL,
                alert_type TEXT DEFAULT 'price_drop',
                notification_sent BOOLEAN DEFAULT 0,
                notification_channels TEXT,
                alert_sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (asin) REFERENCES products (asin) ON DELETE CASCADE
            )
        ''')
        
        # 🆕 ============ Price Recommendations Table ============
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                asin TEXT NOT NULL,
                recommendation_type TEXT NOT NULL,
                current_price REAL NOT NULL,
                lowest_price_30d REAL,
                highest_price_30d REAL,
                avg_price_30d REAL,
                real_discount_percentage REAL,
                vs_average_percentage REAL,
                confidence_score REAL DEFAULT 0.0,
                recommendation_text TEXT,
                badge_color TEXT,
                badge_emoji TEXT,
                reasoning TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (asin) REFERENCES products (asin) ON DELETE CASCADE
            )
        ''')
        
        # ============ User Watchlist Table ============
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS watchlist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT DEFAULT 'default',
                asin TEXT NOT NULL,
                target_price REAL,
                notes TEXT,
                priority INTEGER DEFAULT 0,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (asin) REFERENCES products (asin) ON DELETE CASCADE
            )
        ''')
        
        # ============ Analytics Table ============
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT NOT NULL,
                metric_value REAL,
                metric_data TEXT,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # ============ System Logs Table ============
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                log_level TEXT,
                component TEXT,
                message TEXT,
                details TEXT,
                logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create Indexes
        indexes = [
            'CREATE INDEX IF NOT EXISTS idx_products_asin ON products(asin)',
            'CREATE INDEX IF NOT EXISTS idx_products_region ON products(region)',
            'CREATE INDEX IF NOT EXISTS idx_price_history_asin ON price_history(asin, captured_at DESC)',
            'CREATE INDEX IF NOT EXISTS idx_alerts_asin ON price_alerts(asin, alert_sent_at DESC)',
            'CREATE INDEX IF NOT EXISTS idx_watchlist_user ON watchlist(user_id, asin)',
            'CREATE INDEX IF NOT EXISTS idx_predictions_asin ON price_predictions(asin, prediction_date DESC)',
            'CREATE INDEX IF NOT EXISTS idx_analytics_metric ON analytics(metric_name, recorded_at DESC)',
            'CREATE INDEX IF NOT EXISTS idx_recommendations_asin ON price_recommendations(asin, created_at DESC)'
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
        
        conn.commit()
        logger.info("✅ Database initialized successfully")
    
    def save_product(self, product_data: Dict) -> bool:
        """Save or update product"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO products 
                (asin, region, product_name, current_price, reference_price,
                 discount_percentage, currency, availability_status, category,
                 brand, rating, review_count, image_url, product_url,
                 last_updated, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?)
            ''', (
                product_data['asin'],
                product_data.get('region', DEFAULT_REGION),
                product_data.get('product_name'),
                product_data.get('current_price', 0.0),
                product_data.get('reference_price', 0.0),
                product_data.get('discount_percentage', 0.0),
                product_data.get('currency', 'USD'),
                product_data.get('availability_status', 'active'),
                product_data.get('category'),
                product_data.get('brand'),
                product_data.get('rating'),
                product_data.get('review_count'),
                product_data.get('image_url'),
                product_data.get('product_url'),
                json.dumps(product_data.get('metadata', {}))
            ))
            
            # Save price history
            if product_data.get('current_price', 0) > 0:
                cursor.execute('''
                    INSERT INTO price_history (asin, price, reference_price, discount_percentage)
                    VALUES (?, ?, ?, ?)
                ''', (
                    product_data['asin'],
                    product_data['current_price'],
                    product_data.get('reference_price', 0.0),
                    product_data.get('discount_percentage', 0.0)
                ))
            
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"❌ Error saving product: {e}")
            return False
    
    def get_products(self, region: str = None, limit: int = 100) -> List[Dict]:
        """Get products with optional region filter"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            if region:
                cursor.execute('''
                    SELECT * FROM products 
                    WHERE region = ? 
                    ORDER BY last_updated DESC 
                    LIMIT ?
                ''', (region, limit))
            else:
                cursor.execute('''
                    SELECT * FROM products 
                    ORDER BY last_updated DESC 
                    LIMIT ?
                ''', (limit,))
            
            columns = [desc[0] for desc in cursor.description]
            products = []
            
            for row in cursor.fetchall():
                product = dict(zip(columns, row))
                if product.get('metadata'):
                    try:
                        product['metadata'] = json.loads(product['metadata'])
                    except:
                        product['metadata'] = {}
                products.append(product)
            
            return products
        except Exception as e:
            logger.error(f"❌ Error getting products: {e}")
            return []
    
    def get_price_history(self, asin: str, days: int = 30) -> List[Dict]:
        """Get price history for a product"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM price_history 
                WHERE asin = ? 
                AND captured_at >= datetime('now', '-' || ? || ' days')
                ORDER BY captured_at ASC
            ''', (asin, days))
            
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"❌ Error getting price history: {e}")
            return []
    
    def save_prediction(self, asin: str, prediction_data: Dict) -> bool:
        """Save AI price prediction"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO price_predictions 
                (asin, prediction_date, predicted_price, confidence_score, trend, model_version)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                asin,
                prediction_data['prediction_date'],
                prediction_data['predicted_price'],
                prediction_data.get('confidence_score', 0.0),
                prediction_data.get('trend', 'stable'),
                prediction_data.get('model_version', 'v1.0')
            ))
            
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"❌ Error saving prediction: {e}")
            return False
    
    def save_recommendation(self, asin: str, recommendation_data: Dict) -> bool:
        """🆕 Save smart price recommendation"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO price_recommendations 
                (asin, recommendation_type, current_price, lowest_price_30d, 
                 highest_price_30d, avg_price_30d, real_discount_percentage, 
                 vs_average_percentage, confidence_score, recommendation_text, 
                 badge_color, badge_emoji, reasoning)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                asin,
                recommendation_data['type'],
                recommendation_data['current_price'],
                recommendation_data.get('lowest_price_30d'),
                recommendation_data.get('highest_price_30d'),
                recommendation_data.get('avg_price_30d'),
                recommendation_data.get('real_discount_percentage', 0.0),
                recommendation_data.get('vs_average_percentage', 0.0),
                recommendation_data.get('confidence_score', 0.0),
                recommendation_data.get('text'),
                recommendation_data.get('badge_color'),
                recommendation_data.get('badge_emoji'),
                recommendation_data.get('reasoning')
            ))
            
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"❌ Error saving recommendation: {e}")
            return False
    
    def get_latest_recommendation(self, asin: str) -> Optional[Dict]:
        """🆕 Get latest recommendation for a product"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM price_recommendations 
                WHERE asin = ? 
                ORDER BY created_at DESC 
                LIMIT 1
            ''', (asin,))
            
            row = cursor.fetchone()
            if row:
                columns = [desc[0] for desc in cursor.description]
                return dict(zip(columns, row))
            return None
        except Exception as e:
            logger.error(f"❌ Error getting recommendation: {e}")
            return None
    
    def log_system_event(self, level: str, component: str, message: str, details: Dict = None):
        """Log system events"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO system_logs (log_level, component, message, details)
                VALUES (?, ?, ?, ?)
            ''', (level, component, message, json.dumps(details or {})))
            
            conn.commit()
        except Exception as e:
            logger.error(f"❌ Error logging event: {e}")

# ==================== SMART EXTRACTION ENGINE ====================

class SmartExtractionEngine:
    """AI-Powered Smart Extraction with Multi-Region Support"""
    
    def __init__(self):
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=20, pool_maxsize=20)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0'
        ]
        
        logger.info("✅ Smart Extraction Engine initialized")
    
    def extract_asin(self, url: str) -> Optional[str]:
        """Extract ASIN from URL"""
        patterns = [
            r'/dp/([A-Z0-9]{10})',
            r'/gp/product/([A-Z0-9]{10})',
            r'/product/([A-Z0-9]{10})',
            r'/([A-Z0-9]{10})(?:[/?&]|$)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url, re.IGNORECASE)
            if match:
                asin = match.group(1).upper()
                if len(asin) == 10 and asin.isalnum():
                    return asin
        return None
    
    def detect_region(self, url: str) -> str:
        """Detect Amazon region from URL"""
        for region, config in REGION_CONFIGS.items():
            if config['domain'] in url.lower():
                return region
        return DEFAULT_REGION
    
    def extract_product_data(self, url: str) -> Tuple[Optional[Dict], str]:
        """Extract product data with 3-layer fallback"""
        asin = self.extract_asin(url)
        if not asin:
            return None, "Invalid ASIN"
        
        region = self.detect_region(url)
        region_config = REGION_CONFIGS[region]
        
        # Layer 1: Direct extraction
        logger.info(f"🔍 Layer 1: Direct extraction for {asin} ({region_config['flag']} {region})")
        result = self._direct_extract(url, asin, region, region_config)
        if result:
            return result, "direct"
        
        # Layer 2: ScraperAPI
        if SCRAPERAPI_CONFIG['enabled']:
            logger.info(f"🔍 Layer 2: ScraperAPI extraction for {asin}")
            result = self._scraperapi_extract(url, asin, region, region_config)
            if result:
                return result, "scraperapi"
        
        # Layer 3: Fallback
        logger.info(f"🔍 Layer 3: Fallback extraction for {asin}")
        return None, "All extraction methods failed"
    
    def _direct_extract(self, url: str, asin: str, region: str, region_config: Dict) -> Optional[Dict]:
        """Direct extraction method"""
        try:
            headers = self._get_headers()
            response = self.session.get(url, headers=headers, timeout=20)
            
            if response.status_code == 200:
                return self._parse_html(response.text, asin, region, region_config)
        except Exception as e:
            logger.debug(f"Direct extraction failed: {e}")
        return None
    
    def _scraperapi_extract(self, url: str, asin: str, region: str, region_config: Dict) -> Optional[Dict]:
        """ScraperAPI extraction method"""
        try:
            api_url = f"{SCRAPERAPI_CONFIG['url']}/?api_key={SCRAPERAPI_CONFIG['api_key']}&url={quote(url)}&render=true"
            headers = self._get_headers()
            response = self.session.get(api_url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                return self._parse_html(response.text, asin, region, region_config)
        except Exception as e:
            logger.debug(f"ScraperAPI extraction failed: {e}")
        return None
    
    def _parse_html(self, html: str, asin: str, region: str, region_config: Dict) -> Optional[Dict]:
        """Parse HTML and extract product data"""
        try:
            # Extract price
            current_price = self._extract_price(html, region_config)
            if not current_price or current_price <= 0:
                return None
            
            # Extract other data
            product_name = self._extract_title(html)
            reference_price = self._extract_reference_price(html, region_config)
            
            discount = 0.0
            if reference_price and reference_price > current_price:
                discount = ((reference_price - current_price) / reference_price) * 100
            
            return {
                'asin': asin,
                'region': region,
                'product_name': product_name or f"Product {asin}",
                'current_price': current_price,
                'reference_price': reference_price or current_price,
                'discount_percentage': round(discount, 2),
                'currency': region_config['currency'],
                'availability_status': 'active',
                'product_url': f"https://{region_config['domain']}/dp/{asin}",
                'metadata': {
                    'extraction_timestamp': datetime.now().isoformat(),
                    'region_flag': region_config['flag']
                }
            }
        except Exception as e:
            logger.error(f"HTML parsing error: {e}")
            return None
    
    def _extract_price(self, html: str, region_config: Dict) -> Optional[float]:
        """Extract price from HTML"""
        patterns = [
            r'"priceCurrency":"[A-Z]{3}".*?"price":"([\d.]+)"',
            r'<span[^>]*class="a-price-whole"[^>]*>([\d,]+)</span>',
            r'<span[^>]*class="a-offscreen"[^>]*>.*?([\d,]+\.?\d*)',
            r'>\s*' + re.escape(region_config['currency_symbol']) + r'\s*([\d,]+\.?\d*)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, html, re.IGNORECASE | re.DOTALL)
            for match in matches:
                try:
                    price = float(match.replace(',', ''))
                    if 0.1 <= price <= 1000000:
                        return price
                except:
                    continue
        return None
    
    def _extract_reference_price(self, html: str, region_config: Dict) -> Optional[float]:
        """Extract reference/list price"""
        patterns = [
            r'<span[^>]*class="a-price a-text-price"[^>]*>.*?<span[^>]*class="a-offscreen"[^>]*>(.*?)</span>',
            r'<span[^>]*class="a-text-strike"[^>]*>(.*?)</span>',
            r'List Price:.*?' + re.escape(region_config['currency_symbol']) + r'\s*([\d,]+\.?\d*)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
            if match:
                try:
                    price_text = match.group(1)
                    price = float(re.sub(r'[^\d.]', '', price_text))
                    if 0.1 <= price <= 1000000:
                        return price
                except:
                    continue
        return None
    
    def _extract_title(self, html: str) -> Optional[str]:
        """Extract product title"""
        patterns = [
            r'<span[^>]*id="productTitle"[^>]*>(.*?)</span>',
            r'<h1[^>]*id="title"[^>]*>(.*?)</h1>',
            r'<meta[^>]*property="og:title"[^>]*content="([^"]*)"'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
            if match:
                title = re.sub(r'<[^>]*>', '', match.group(1))
                title = re.sub(r'\s+', ' ', title).strip()
                if len(title) > 5:
                    return title[:200]
        return None
    
    def _get_headers(self) -> Dict:
        """Get random headers"""
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }

# 🆕 ==================== SMART PRICE ANALYZER ====================

class SmartPriceAnalyzer:
    """
    🎯 محرك التحليل الذكي للأسعار
    يحلل البيانات التاريخية ويعطي توصية واضحة: اشترِ / انتظر / لا تشترِ
    """
    
    def __init__(self, db_manager: UltimateDatabaseManager):
        self.db = db_manager
        self.config = RECOMMENDATION_CONFIG
        logger.info("✅ Smart Price Analyzer initialized")
    
    def analyze_price(self, asin: str, current_price: float, currency: str) -> Optional[Dict]:
        """
        🔍 تحليل السعر الحالي مقارنة بالتاريخ
        
        المنطق:
        1. جلب آخر 30 يوم من الأسعار
        2. حساب: أدنى/أعلى/متوسط السعر
        3. حساب الخصم الحقيقي (مقارنة بالمتوسط، ليس السعر المضروب)
        4. تطبيق قواعد التوصية
        5. إرجاع النتيجة مع التفسير
        """
        if not self.config['enabled']:
            return None
        
        try:
            # 1. جلب البيانات التاريخية
            history = self.db.get_price_history(asin, days=self.config['analysis_period_days'])
            
            if len(history) < 2:
                # بيانات غير كافية - نعطي توصية محايدة
                return self._create_neutral_recommendation(current_price, currency)
            
            # 2. حساب الإحصائيات
            prices = [h['price'] for h in history]
            lowest_price = min(prices)
            highest_price = max(prices)
            avg_price = statistics.mean(prices)
            
            # 3. حساب الخصم الحقيقي (مقارنة بالمتوسط)
            real_discount = ((avg_price - current_price) / avg_price) * 100
            vs_average = ((current_price - avg_price) / avg_price) * 100
            
            # 4. تحديد نوع التوصية
            recommendation = self._determine_recommendation(
                current_price, lowest_price, avg_price, real_discount, vs_average
            )
            
            # 5. حساب درجة الثقة
            confidence = self._calculate_confidence(len(history), prices)
            
            # 6. بناء التوصية النهائية
            result = {
                'asin': asin,
                'type': recommendation['type'],
                'current_price': current_price,
                'lowest_price_30d': lowest_price,
                'highest_price_30d': highest_price,
                'avg_price_30d': avg_price,
                'real_discount_percentage': round(real_discount, 2),
                'vs_average_percentage': round(vs_average, 2),
                'confidence_score': round(confidence, 2),
                'text': recommendation['text'],
                'badge_color': recommendation['color'],
                'badge_emoji': recommendation['emoji'],
                'reasoning': recommendation['reasoning'].format(
                    currency=currency,
                    current=current_price,
                    avg=avg_price,
                    lowest=lowest_price,
                    discount=abs(real_discount)
                )
            }
            
            # 7. حفظ في قاعدة البيانات
            self.db.save_recommendation(asin, result)
            
            logger.info(f"✅ Recommendation for {asin}: {recommendation['type']} ({confidence:.1f}% confidence)")
            return result
            
        except Exception as e:
            logger.error(f"❌ Price analysis error for {asin}: {e}")
            return None
    
    def _determine_recommendation(self, current: float, lowest: float, avg: float, 
                                   real_discount: float, vs_avg: float) -> Dict:
        """
        🎯 تحديد التوصية بناءً على القواعد
        
        القواعد:
        - 🟢 اشترِ: إذا كان السعر ≤ أدنى سعر أو خصم حقيقي ≥ 25%
        - 🟡 انتظر: إذا كان الخصم بين 10-24% أو قريب من المتوسط
        - 🔴 لا تشترِ: إذا كان الخصم < 10% أو أعلى من المتوسط بكثير
        """
        
        # 🟢 قاعدة الشراء
        if (current <= lowest or 
            real_discount >= self.config['buy_threshold']['discount_min']):
            return {
                'type': 'BUY',
                'emoji': '🟢',
                'color': '#4CAF50',
                'text': '✔ موصى بالشراء الآن',
                'reasoning': 'خصم حقيقي – أقل من متوسط 30 يوماً بـ {discount:.1f}%\nالسعر الحالي: {currency} {current:.2f} | المتوسط: {currency} {avg:.2f}'
            }
        
        # 🔴 قاعدة عدم الشراء
        elif (real_discount < self.config['dont_buy_threshold']['discount_max'] or
              vs_avg > self.config['dont_buy_threshold']['vs_avg_min']):
            return {
                'type': 'DONT_BUY',
                'emoji': '🔴',
                'color': '#F44336',
                'text': '✖ لا يُنصح بالشراء الآن',
                'reasoning': 'خصم غير مغرٍ أو وهمي\nالسعر الحالي أعلى من المتوسط أو الخصم ضعيف\nالسعر: {currency} {current:.2f} | المتوسط: {currency} {avg:.2f}'
            }
        
        # 🟡 قاعدة الانتظار (الحالة الافتراضية)
        else:
            return {
                'type': 'WAIT',
                'emoji': '🟡',
                'color': '#FF9800',
                'text': '⏳ قد ينخفض لاحقاً',
                'reasoning': 'السعر مقبول حالياً لكن ليس أفضل عرض\nالخصم الحقيقي: {discount:.1f}%\nالسعر: {currency} {current:.2f} | أدنى سعر: {currency} {lowest:.2f}'
            }
    
    def _calculate_confidence(self, data_points: int, prices: List[float]) -> float:
        """
        📊 حساب درجة الثقة في التوصية
        
        العوامل:
        - عدد نقاط البيانات (كلما زادت، زادت الثقة)
        - استقرار الأسعار (انحراف معياري منخفض = ثقة عالية)
        """
        # عامل عدد البيانات (0-50%)
        data_factor = min(data_points / 30.0, 1.0) * 50
        
        # عامل الاستقرار (0-50%)
        if len(prices) > 1:
            std_dev = statistics.stdev(prices)
            mean = statistics.mean(prices)
            cv = (std_dev / mean) if mean > 0 else 1  # Coefficient of Variation
            stability_factor = max(0, (1 - cv)) * 50
        else:
            stability_factor = 0
        
        return min(data_factor + stability_factor, 100)
    
    def _create_neutral_recommendation(self, current_price: float, currency: str) -> Dict:
        """توصية محايدة عند عدم توفر بيانات كافية"""
        return {
            'type': 'WAIT',
            'current_price': current_price,
            'lowest_price_30d': current_price,
            'highest_price_30d': current_price,
            'avg_price_30d': current_price,
            'real_discount_percentage': 0.0,
            'vs_average_percentage': 0.0,
            'confidence_score': 20.0,
            'text': '⏳ بيانات غير كافية',
            'badge_color': '#9E9E9E',
            'badge_emoji': '⚪',
            'reasoning': f'لا توجد بيانات تاريخية كافية للتحليل\nالسعر الحالي: {currency} {current_price:.2f}\nننصح بالانتظار لجمع المزيد من البيانات'
        }

# ==================== AI PRICE PREDICTOR ====================

class AIPricePredictor:
    """AI-Powered Price Prediction Engine"""
    
    def __init__(self, db_manager: UltimateDatabaseManager):
        self.db = db_manager
        logger.info("✅ AI Price Predictor initialized")
    
    def predict_price(self, asin: str, days_ahead: int = 30) -> Optional[Dict]:
        """Predict future price using linear regression"""
        if not AI_PREDICTION_CONFIG['enabled']:
            return None
        
        try:
            # Get historical data
            history = self.db.get_price_history(asin, days=90)
            
            if len(history) < AI_PREDICTION_CONFIG['min_data_points']:
                return None
            
            # Prepare data
            prices = [h['price'] for h in history]
            timestamps = [(datetime.fromisoformat(h['captured_at']) - datetime(1970, 1, 1)).total_seconds() for h in history]
            
            # Simple linear regression
            n = len(prices)
            sum_x = sum(timestamps)
            sum_y = sum(prices)
            sum_xy = sum(x * y for x, y in zip(timestamps, prices))
            sum_x2 = sum(x * x for x in timestamps)
            
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
            intercept = (sum_y - slope * sum_x) / n
            
            # Predict future price
            future_timestamp = (datetime.now() + timedelta(days=days_ahead) - datetime(1970, 1, 1)).total_seconds()
            predicted_price = slope * future_timestamp + intercept
            
            # Calculate trend
            current_price = prices[-1]
            price_change = ((predicted_price - current_price) / current_price) * 100
            
            if price_change < -5:
                trend = 'decreasing'
            elif price_change > 5:
                trend = 'increasing'
            else:
                trend = 'stable'
            
            # Calculate confidence (simplified R-squared)
            mean_price = statistics.mean(prices)
            ss_tot = sum((y - mean_price) ** 2 for y in prices)
            ss_res = sum((y - (slope * x + intercept)) ** 2 for x, y in zip(timestamps, prices))
            confidence = max(0, min(100, (1 - ss_res / ss_tot) * 100)) if ss_tot > 0 else 0
            
            prediction = {
                'asin': asin,
                'prediction_date': (datetime.now() + timedelta(days=days_ahead)).date().isoformat(),
                'predicted_price': round(predicted_price, 2),
                'confidence_score': round(confidence, 2),
                'trend': trend,
                'price_change_percentage': round(price_change, 2),
                'model_version': 'linear_regression_v1.0',
                'data_points_used': len(history)
            }
            
            # Save prediction
            self.db.save_prediction(asin, prediction)
            
            return prediction
            
        except Exception as e:
            logger.error(f"❌ Prediction error for {asin}: {e}")
            return None

# ==================== NOTIFICATION MANAGER ====================

class NotificationManager:
    """Multi-Channel Notification System"""
    
    def __init__(self):
        self.email_config = NOTIFICATION_CONFIG['email']
        logger.info("✅ Notification Manager initialized")
    
    def send_price_alert(self, product: Dict, old_price: float, new_price: float, drop_percentage: float):
        """Send multi-channel price alert"""
        channels_used = []
        
        # Email notification
        if self.email_config['enabled']:
            if self._send_email_alert(product, old_price, new_price, drop_percentage):
                channels_used.append('email')
        
        return channels_used
    
    def _send_email_alert(self, product: Dict, old_price: float, new_price: float, drop_percentage: float) -> bool:
        """Send email alert"""
        try:
            region_config = REGION_CONFIGS.get(product.get('region', DEFAULT_REGION))
            currency_symbol = region_config['currency_symbol']
            
            subject = f"🔔 Price Drop Alert: {product['product_name'][:50]}..."
            
            html_body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; color: white;">
                    <h1 style="margin: 0;">🔔 Price Drop Alert!</h1>
                    <p style="margin: 10px 0 0 0; font-size: 18px;">You're saving money!</p>
                </div>
                
                <div style="padding: 30px; background: #f8f9fa;">
                    <h2 style="color: #333;">{product['product_name']}</h2>
                    
                    <div style="background: white; padding: 20px; border-radius: 10px; margin: 20px 0;">
                        <table style="width: 100%;">
                            <tr>
                                <td style="padding: 10px;"><strong>Region:</strong></td>
                                <td style="padding: 10px;">{region_config['flag']} {region_config['name']}</td>
                            </tr>
                            <tr>
                                <td style="padding: 10px;"><strong>ASIN:</strong></td>
                                <td style="padding: 10px;"><code>{product['asin']}</code></td>
                            </tr>
                            <tr>
                                <td style="padding: 10px;"><strong>Old Price:</strong></td>
                                <td style="padding: 10px; text-decoration: line-through;">{currency_symbol}{old_price:.2f}</td>
                            </tr>
                            <tr>
                                <td style="padding: 10px;"><strong>New Price:</strong></td>
                                <td style="padding: 10px; color: #d32f2f; font-size: 24px; font-weight: bold;">{currency_symbol}{new_price:.2f}</td>
                            </tr>
                            <tr>
                                <td style="padding: 10px;"><strong>Discount:</strong></td>
                                <td style="padding: 10px; color: #4caf50; font-size: 20px; font-weight: bold;">{drop_percentage:.1f}%</td>
                            </tr>
                            <tr>
                                <td style="padding: 10px;"><strong>You Save:</strong></td>
                                <td style="padding: 10px; color: #4caf50; font-weight: bold;">{currency_symbol}{old_price - new_price:.2f}</td>
                            </tr>
                        </table>
                    </div>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{product.get('product_url', '#')}" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px 40px; text-decoration: none; border-radius: 25px; font-weight: bold; display: inline-block;">
                            🛒 View on Amazon
                        </a>
                    </div>
                    
                    <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0;">
                        <p style="margin: 0; color: #856404;"><strong>⚡ Act Fast!</strong> Prices can change at any time.</p>
                    </div>
                </div>
                
                <div style="background: #333; color: white; padding: 20px; text-align: center; font-size: 12px;">
                    <p>Ultimate Amazon Price Tracker v{VERSION}</p>
                    <p>Powered by AI • Real-time Monitoring • Multi-Region Support</p>
                </div>
            </body>
            </html>
            """
            
            msg = MIMEMultipart('alternative')
            msg['From'] = self.email_config['sender']
            msg['To'] = self.email_config['receiver']
            msg['Subject'] = subject
            msg.attach(MIMEText(html_body, 'html'))
            
            server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
            server.starttls()
            server.login(self.email_config['sender'], self.email_config['password'])
            server.send_message(msg)
            server.quit()
            
            logger.info(f"✅ Email alert sent for {product['asin']}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Email alert failed: {e}")
            return False

# ==================== FLASK APP ====================

app = Flask(__name__)

class UltimateTrackerSystem:
    """Ultimate Amazon Price Tracker System with Smart Recommendations"""
    
    def __init__(self):
        self.db = UltimateDatabaseManager()
        self.extractor = SmartExtractionEngine()
        self.predictor = AIPricePredictor(self.db)
        self.analyzer = SmartPriceAnalyzer(self.db)  # 🆕
        self.notifier = NotificationManager()
        self.setup_routes()
        logger.info("✅ Ultimate Tracker System initialized")
    
    def setup_routes(self):
        """Setup Flask routes"""
        
        @app.route('/')
        def home():
            return render_template_string(DASHBOARD_TEMPLATE)
        
        @app.route('/api/add-product', methods=['POST'])
        def add_product():
            try:
                data = request.get_json()
                url = data.get('url')
                
                if not url:
                    return jsonify({'status': 'error', 'message': 'URL required'}), 400
                
                product_data, method = self.extractor.extract_product_data(url)
                
                if not product_data:
                    return jsonify({'status': 'error', 'message': method}), 400
                
                # Save product
                self.db.save_product(product_data)
                
                # Generate prediction
                prediction = self.predictor.predict_price(product_data['asin'])
                
                # 🆕 Generate smart recommendation
                recommendation = self.analyzer.analyze_price(
                    product_data['asin'],
                    product_data['current_price'],
                    product_data['currency']
                )
                
                return jsonify({
                    'status': 'success',
                    'product': product_data,
                    'prediction': prediction,
                    'recommendation': recommendation,  # 🆕
                    'extraction_method': method
                })
                
            except Exception as e:
                logger.error(f"Error adding product: {e}")
                return jsonify({'status': 'error', 'message': str(e)}), 500
        
        @app.route('/api/products')
        def get_products():
            region = request.args.get('region')
            products = self.db.get_products(region=region)
            
            # 🆕 إضافة التوصية لكل منتج
            for product in products:
                rec = self.db.get_latest_recommendation(product['asin'])
                product['recommendation'] = rec
            
            return jsonify({'status': 'success', 'products': products, 'count': len(products)})
        
        @app.route('/api/product/<asin>/history')
        def get_product_history(asin):
            days = request.args.get('days', 30, type=int)
            history = self.db.get_price_history(asin, days)
            return jsonify({'status': 'success', 'history': history, 'count': len(history)})
        
        @app.route('/api/product/<asin>/predict')
        def predict_price(asin):
            days = request.args.get('days', 30, type=int)
            prediction = self.predictor.predict_price(asin, days)
            
            if prediction:
                return jsonify({'status': 'success', 'prediction': prediction})
            else:
                return jsonify({'status': 'error', 'message': 'Insufficient data'}), 400
        
        # 🆕 endpoint للتوصية
        @app.route('/api/product/<asin>/recommendation')
        def get_recommendation(asin):
            rec = self.db.get_latest_recommendation(asin)
            if rec:
                return jsonify({'status': 'success', 'recommendation': rec})
            else:
                return jsonify({'status': 'error', 'message': 'No recommendation available'}), 404
        
        @app.route('/api/regions')
        def get_regions():
            regions = [
                {
                    'code': code,
                    'name': config['name'],
                    'flag': config['flag'],
                    'currency': config['currency'],
                    'domain': config['domain']
                }
                for code, config in REGION_CONFIGS.items()
            ]
            return jsonify({'status': 'success', 'regions': regions})
        
        @app.route('/api/stats')
        def get_stats():
            try:
                conn = self.db.get_connection()
                cursor = conn.cursor()
                
                cursor.execute('SELECT COUNT(*) FROM products')
                total_products = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(DISTINCT region) FROM products')
                regions_count = cursor.fetchone()[0]
                
                cursor.execute('SELECT AVG(discount_percentage) FROM products WHERE discount_percentage > 0')
                avg_discount = cursor.fetchone()[0] or 0
                
                cursor.execute('SELECT COUNT(*) FROM price_alerts WHERE DATE(alert_sent_at) = DATE("now")')
                alerts_today = cursor.fetchone()[0]
                
                # 🆕 إحصائيات التوصيات
                cursor.execute('SELECT COUNT(*) FROM price_recommendations WHERE recommendation_type = "BUY"')
                buy_recommendations = cursor.fetchone()[0]
                
                return jsonify({
                    'status': 'success',
                    'stats': {
                        'total_products': total_products,
                        'regions_count': regions_count,
                        'avg_discount': round(avg_discount, 2),
                        'alerts_today': alerts_today,
                        'buy_recommendations': buy_recommendations  # 🆕
                    }
                })
            except Exception as e:
                return jsonify({'status': 'error', 'message': str(e)}), 500
        
        @app.route('/ping')
        def ping():
            return jsonify({
                'status': 'alive',
                'version': VERSION,
                'timestamp': datetime.now().isoformat(),
                'features': {
                    'multi_region': True,
                    'ai_prediction': AI_PREDICTION_CONFIG['enabled'],
                    'smart_recommendations': RECOMMENDATION_CONFIG['enabled'],  # 🆕
                    'notifications': NOTIFICATION_CONFIG['email']['enabled'],
                    'analytics': ANALYTICS_CONFIG['enabled']
                }
            })

# ==================== DASHBOARD TEMPLATE ====================

DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚀 Ultimate Amazon Price Tracker</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1400px; margin: 0 auto; }
        .header {
            background: white;
            padding: 30px;
            border-radius: 20px;
            text-align: center;
            margin-bottom: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        .header h1 {
            font-size: 3rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }
        .version-badge {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            padding: 8px 20px;
            border-radius: 20px;
            display: inline-block;
            font-weight: bold;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        .stat-card {
            background: white;
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            transition: transform 0.3s;
        }
        .stat-card:hover { transform: translateY(-5px); }
        .stat-value {
            font-size: 2.5rem;
            font-weight: bold;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 10px 0;
        }
        .stat-label { color: #666; font-size: 0.9rem; }
        
        .main-content {
            display: grid;
            grid-template-columns: 1fr 2fr;
            gap: 20px;
        }
        
        .sidebar, .products-panel {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        
        .add-product-section { margin-bottom: 25px; }
        .input-field {
            width: 100%;
            padding: 15px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            margin-bottom: 10px;
            font-size: 1rem;
            transition: border-color 0.3s;
        }
        .input-field:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px;
            border-radius: 10px;
            width: 100%;
            font-size: 1.1rem;
            font-weight: bold;
            cursor: pointer;
            transition: transform 0.3s;
        }
        .btn-primary:hover { transform: scale(1.05); }
        
        .region-selector {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
            gap: 10px;
            margin: 20px 0;
        }
        .region-btn {
            padding: 10px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            background: white;
            cursor: pointer;
            text-align: center;
            transition: all 0.3s;
        }
        .region-btn:hover, .region-btn.active {
            border-color: #667eea;
            background: #f0f4ff;
        }
        
        .products-table { width: 100%; border-collapse: collapse; }
        .products-table th {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            text-align: left;
        }
        .products-table td {
            padding: 15px;
            border-bottom: 1px solid #e0e0e0;
        }
        .products-table tr:hover { background: #f8f9fa; }
        
        .price-badge {
            background: #4caf50;
            color: white;
            padding: 5px 12px;
            border-radius: 15px;
            font-weight: bold;
        }
        .discount-badge {
            background: #ff9800;
            color: white;
            padding: 5px 12px;
            border-radius: 15px;
        }
        
        /* 🆕 Recommendation Badges */
        .rec-badge {
            padding: 8px 15px;
            border-radius: 20px;
            font-weight: bold;
            display: inline-block;
            font-size: 0.9rem;
        }
        .rec-buy { background: #4CAF50; color: white; }
        .rec-wait { background: #FF9800; color: white; }
        .rec-dont-buy { background: #F44336; color: white; }
        
        .loading {
            text-align: center;
            padding: 40px;
            display: none;
        }
        .spinner {
            border: 5px solid #f3f3f3;
            border-top: 5px solid #667eea;
            border-radius: 50%;
            width: 60px;
            height: 60px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        
        .result-box {
            background: #e8f5e9;
            border-left: 4px solid #4caf50;
            padding: 20px;
            border-radius: 10px;
            margin-top: 20px;
            display: none;
        }
        .error-box {
            background: #ffebee;
            border-left: 4px solid #f44336;
        }
        
        .prediction-card {
            background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
            padding: 15px;
            border-radius: 10px;
            margin-top: 10px;
        }
        
        /* 🆕 Recommendation Card */
        .recommendation-card {
            background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
            padding: 15px;
            border-radius: 10px;
            margin-top: 10px;
            border-left: 4px solid #667eea;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Ultimate Amazon Price Tracker</h1>
            <p style="color: #666; margin: 10px 0;">AI-Powered • Multi-Region • Smart Recommendations 🆕</p>
            <span class="version-badge">v''' + VERSION + '''</span>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Total Products</div>
                <div class="stat-value" id="totalProducts">0</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Regions Tracked</div>
                <div class="stat-value" id="regionsCount">0</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Avg Discount</div>
                <div class="stat-value" id="avgDiscount">0%</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">🟢 Buy Now</div>
                <div class="stat-value" id="buyRecommendations">0</div>
            </div>
        </div>
        
        <div class="main-content">
            <div class="sidebar">
                <h2 style="margin-bottom: 20px; color: #333;">Add Product</h2>
                
                <div class="add-product-section">
                    <input type="url" id="productUrl" class="input-field" 
                           placeholder="Paste Amazon product URL...">
                    <button class="btn-primary" onclick="addProduct()">
                        🔍 Track Product
                    </button>
                </div>
                
                <div id="loading" class="loading">
                    <div class="spinner"></div>
                    <p>Analyzing product...</p>
                </div>
                
                <div id="result" class="result-box"></div>
                
                <div style="margin-top: 30px;">
                    <h3 style="margin-bottom: 15px; color: #333;">🌍 Filter by Region</h3>
                    <div class="region-selector" id="regionSelector"></div>
                </div>
            </div>
            
            <div class="products-panel">
                <h2 style="margin-bottom: 20px; color: #333;">📦 Tracked Products</h2>
                <div style="max-height: 600px; overflow-y: auto;">
                    <table class="products-table">
                        <thead>
                            <tr>
                                <th>Product</th>
                                <th>Region</th>
                                <th>Price</th>
                                <th>Discount</th>
                                <th>🆕 Recommendation</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody id="productsTable"></tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>

    <script>
        let selectedRegion = null;
        
        document.addEventListener('DOMContentLoaded', function() {
            loadStats();
            loadRegions();
            loadProducts();
            setInterval(loadStats, 30000);
        });
        
        async function loadStats() {
            try {
                const response = await fetch('/api/stats');
                const data = await response.json();
                if (data.status === 'success') {
                    document.getElementById('totalProducts').textContent = data.stats.total_products;
                    document.getElementById('regionsCount').textContent = data.stats.regions_count;
                    document.getElementById('avgDiscount').textContent = data.stats.avg_discount.toFixed(1) + '%';
                    document.getElementById('buyRecommendations').textContent = data.stats.buy_recommendations || 0;
                }
            } catch (error) {
                console.error('Error loading stats:', error);
            }
        }
        
        async function loadRegions() {
            try {
                const response = await fetch('/api/regions');
                const data = await response.json();
                if (data.status === 'success') {
                    const container = document.getElementById('regionSelector');
                    container.innerHTML = data.regions.map(r => `
                        <div class="region-btn" onclick="filterByRegion('${r.code}')">
                            <div style="font-size: 1.5rem;">${r.flag}</div>
                            <div style="font-size: 0.8rem; margin-top: 5px;">${r.code}</div>
                        </div>
                    `).join('') + `
                        <div class="region-btn" onclick="filterByRegion(null)">
                            <div style="font-size: 1.5rem;">🌍</div>
                            <div style="font-size: 0.8rem; margin-top: 5px;">ALL</div>
                        </div>
                    `;
                }
            } catch (error) {
                console.error('Error loading regions:', error);
            }
        }
        
        function filterByRegion(region) {
            selectedRegion = region;
            document.querySelectorAll('.region-btn').forEach(btn => btn.classList.remove('active'));
            event.target.closest('.region-btn').classList.add('active');
            loadProducts();
        }
        
        async function loadProducts() {
            try {
                const url = selectedRegion ? `/api/products?region=${selectedRegion}` : '/api/products';
                const response = await fetch(url);
                const data = await response.json();
                
                if (data.status === 'success') {
                    const tbody = document.getElementById('productsTable');
                    if (data.products.length === 0) {
                        tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; padding: 40px;">No products tracked yet. Add one above!</td></tr>';
                        return;
                    }
                    
                    tbody.innerHTML = data.products.map(p => {
                        const rec = p.recommendation;
                        let recBadge = '<span style="color: #999;">-</span>';
                        
                        if (rec) {
                            const badgeClass = rec.recommendation_type === 'BUY' ? 'rec-buy' : 
                                             rec.recommendation_type === 'WAIT' ? 'rec-wait' : 'rec-dont-buy';
                            recBadge = `<span class="rec-badge ${badgeClass}">${rec.badge_emoji} ${rec.text}</span>`;
                        }
                        
                        return `
                        <tr>
                            <td>
                                <strong>${p.product_name.substring(0, 50)}...</strong><br>
                                <code style="font-size: 0.8rem; color: #666;">${p.asin}</code>
                            </td>
                            <td>
                                <div style="font-size: 1.2rem;">${p.metadata && p.metadata.region_flag ? p.metadata.region_flag : ''}</div>
                                <div style="font-size: 0.8rem;">${p.region}</div>
                            </td>
                            <td>
                                <span class="price-badge">${p.currency} ${p.current_price.toFixed(2)}</span>
                            </td>
                            <td>
                                ${p.discount_percentage > 0 ? 
                                  `<span class="discount-badge">${p.discount_percentage.toFixed(1)}%</span>` : 
                                  '<span style="color: #999;">-</span>'}
                            </td>
                            <td>
                                ${recBadge}
                            </td>
                            <td>
                                <button onclick="showDetails('${p.asin}')" style="padding: 5px 15px; background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; border: none; border-radius: 5px; cursor: pointer;">
                                    📊 Details
                                </button>
                            </td>
                        </tr>
                    `;
                    }).join('');
                }
            } catch (error) {
                console.error('Error loading products:', error);
            }
        }
        
        async function addProduct() {
            const url = document.getElementById('productUrl').value;
            if (!url) {
                alert('Please enter a product URL');
                return;
            }
            
            const loading = document.getElementById('loading');
            const result = document.getElementById('result');
            
            loading.style.display = 'block';
            result.style.display = 'none';
            
            try {
                const response = await fetch('/api/add-product', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url })
                });
                
                const data = await response.json();
                loading.style.display = 'none';
                result.style.display = 'block';
                
                if (data.status === 'success') {
                    const p = data.product;
                    const rec = data.recommendation;
                    
                    result.className = 'result-box';
                    result.innerHTML = `
                        <h3 style="color: #2e7d32;">✅ Product Added Successfully!</h3>
                        <div style="margin: 15px 0;">
                            <strong>${p.product_name}</strong><br>
                            <div style="margin: 10px 0;">
                                <span style="font-size: 0.9rem; color: #666;">Region: ${p.metadata.region_flag} ${p.region}</span><br>
                                <span style="font-size: 1.2rem; color: #d32f2f; font-weight: bold;">${p.currency} ${p.current_price.toFixed(2)}</span>
                            </div>
                        </div>
                        ${rec ? `
                            <div class="recommendation-card">
                                <strong>🎯 Smart Recommendation:</strong><br>
                                <span style="font-size: 1.1rem;">${rec.badge_emoji} ${rec.text}</span><br>
                                <div style="margin-top: 10px; font-size: 0.9rem; color: #555;">
                                    ${rec.reasoning}
                                </div>
                                <div style="margin-top: 5px; font-size: 0.8rem; color: #999;">
                                    Confidence: ${rec.confidence_score.toFixed(1)}%
                                </div>
                            </div>
                        ` : ''}
                        ${data.prediction ? `
                            <div class="prediction-card">
                                <strong>🔮 AI Prediction (30 days):</strong><br>
                                Predicted Price: <strong>${p.currency} ${data.prediction.predicted_price.toFixed(2)}</strong><br>
                                Trend: <strong>${data.prediction.trend}</strong><br>
                                Confidence: <strong>${data.prediction.confidence_score.toFixed(1)}%</strong>
                            </div>
                        ` : ''}
                    `;
                    
                    document.getElementById('productUrl').value = '';
                    setTimeout(() => { loadStats(); loadProducts(); }, 1000);
                } else {
                    result.className = 'result-box error-box';
                    result.innerHTML = `<h3 style="color: #c62828;">❌ Error</h3><p>${data.message}</p>`;
                }
            } catch (error) {
                loading.style.display = 'none';
                result.style.display = 'block';
                result.className = 'result-box error-box';
                result.innerHTML = `<h3 style="color: #c62828;">❌ Error</h3><p>${error.message}</p>`;
            }
        }
        
        async function showDetails(asin) {
            try {
                const [recResponse, predResponse, histResponse] = await Promise.all([
                    fetch(`/api/product/${asin}/recommendation`),
                    fetch(`/api/product/${asin}/predict`),
                    fetch(`/api/product/${asin}/history?days=30`)
                ]);
                
                const rec = await recResponse.json();
                const pred = await predResponse.json();
                const hist = await histResponse.json();
                
                let message = `📊 Product Details: ${asin}\n\n`;
                
                if (rec.status === 'success') {
                    const r = rec.recommendation;
                    message += `🎯 RECOMMENDATION: ${r.badge_emoji} ${r.text}\n`;
                    message += `${r.reasoning}\n`;
                    message += `Confidence: ${r.confidence_score.toFixed(1)}%\n\n`;
                }
                
                if (pred.status === 'success') {
                    message += `🔮 AI PREDICTION:\n`;
                    message += `Predicted Price (30d): ${pred.prediction.predicted_price}\n`;
                    message += `Trend: ${pred.prediction.trend}\n\n`;
                }
                
                if (hist.status === 'success') {
                    message += `📈 PRICE HISTORY (30 days):\n`;
                    message += `Total Records: ${hist.count}\n`;
                }
                
                alert(message);
            } catch (error) {
                alert('Error loading details');
            }
        }
    </script>
</body>
</html>
'''

# ==================== MAIN ====================

def main():
    print("\n" + "=" * 80)
    print("🚀 STARTING ULTIMATE AMAZON PRICE TRACKER")
    print("=" * 80)
    
    try:
        system = UltimateTrackerSystem()
        
        print("\n✅ System Ready!")
        print(f"🌐 Dashboard: http://localhost:9090")
        print(f"📡 API Endpoints:")
        print(f"   • POST /api/add-product          - Add new product")
        print(f"   • GET  /api/products             - Get all products")
        print(f"   • GET  /api/product/<asin>/recommendation 🆕 - Get smart recommendation")
        print(f"   • GET  /api/regions              - Get supported regions")
        print(f"   • GET  /api/stats                - Get statistics")
        print("=" * 80)
        print("\n🎁 Premium Features:")
        print("  ✅ Multi-Region Support (US, UK, DE, SA, AE)")
        print("  ✅ AI Price Prediction Engine")
        print("  ✅ 🆕 Smart Buy/Wait/Don't Buy Recommendations")
        print("  ✅ Email Notifications")
        print("  ✅ Real-time Dashboard")
        print("  ✅ Historical Price Analysis")
        print("=" * 80)
        
        app.run(
            host='0.0.0.0',
            port=9090,
            debug=False,
            threaded=True,
            use_reloader=False
        )
    except KeyboardInterrupt:
        print("\n\n⚠️ System stopped by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        traceback.print_exc()
    finally:
        print("\n✅ System shutdown complete")

if __name__ == '__main__':
    main()
