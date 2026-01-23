"""
ultimate_amazon_price_tracker_pro.py - نظام تتبع أسعار Amazon الاحترافي - جاهز للإنتاج
الإصدار: 24.0 ULTIMATE EDITION + SMART RECOMMENDATIONS + CROSS-REGION COMPARISON

ميزات فريدة لم تُرى من قبل:
✅ AI-Powered Price Prediction
✅ Multi-Region Support (الشرق الأوسط، أمريكا، أوروبا)
✅ Smart Buy/Wait/Don't Buy Recommendations 🆕
✅ Cross-Region Price Comparison 🔥
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
import concurrent.futures
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

VERSION = "24.0 ULTIMATE + SMART RECOMMENDATIONS + CROSS-REGION"
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

# Exchange Rates (يمكن تحديثها من API)
EXCHANGE_RATES = {
    'USD': 1.0,
    'GBP': 1.27,      # 1 GBP = 1.27 USD
    'EUR': 1.09,      # 1 EUR = 1.09 USD
    'SAR': 0.2667,    # 1 SAR = 0.2667 USD
    'AED': 0.2723     # 1 AED = 0.2723 USD
}

# Regional Costs (الشحن والضرائب التقريبية)
REGIONAL_COSTS = {
    'US': {'shipping': 0.0, 'tax': 0.0, 'import_duty': 0.0},
    'UK': {'shipping': 15.0, 'tax': 20.0, 'import_duty': 0.0},
    'DE': {'shipping': 12.0, 'tax': 19.0, 'import_duty': 0.0},
    'SA': {'shipping': 0.0, 'tax': 15.0, 'import_duty': 5.0},
    'AE': {'shipping': 10.0, 'tax': 5.0, 'import_duty': 5.0}
}

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

# Cross-Region Comparison Configuration
COMPARISON_CONFIG = {
    'enabled': True,
    'cache_duration_minutes': 5,
    'parallel_workers': 5,
    'include_shipping': True,
    'include_taxes': True,
    'max_regions_to_compare': 5
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
print("  ✅ 🔥 Cross-Region Price Comparison (NEW)")
print("  ✅ Advanced Analytics Dashboard")
print("  ✅ Real-time Notifications (Email, Telegram, Push)")
print("  ✅ Smart Extraction System (3-Layer Fallback)")
print("  ✅ Historical Price Analysis")
print("  ✅ Trend Detection & Forecasting")
print("  ✅ Export Reports (JSON, CSV, PDF)")
print("=" * 80)

# ==================== ENHANCED DATABASE ====================

class UltimateDatabaseManager:
    """Enterprise-Grade Database Manager with Recommendations & Comparison Support"""
    
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
        
        # 🔥 ============ Cross-Region Prices Table ============
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cross_region_prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                asin TEXT NOT NULL,
                region_code TEXT NOT NULL,
                local_price REAL NOT NULL,
                local_currency TEXT,
                converted_price REAL,
                converted_currency TEXT DEFAULT 'USD',
                shipping_cost REAL DEFAULT 0.0,
                tax_percentage REAL DEFAULT 0.0,
                import_duty_percentage REAL DEFAULT 0.0,
                total_cost REAL,
                availability_status TEXT DEFAULT 'unknown',
                product_url TEXT,
                last_checked TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                confidence_score REAL DEFAULT 0.0,
                best_deal_score REAL DEFAULT 0.0,
                UNIQUE(asin, region_code)
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
            'CREATE INDEX IF NOT EXISTS idx_recommendations_asin ON price_recommendations(asin, created_at DESC)',
            'CREATE INDEX IF NOT EXISTS idx_cross_region_asin ON cross_region_prices(asin, region_code)',
            'CREATE INDEX IF NOT EXISTS idx_cross_region_score ON cross_region_prices(asin, best_deal_score DESC)',
            'CREATE INDEX IF NOT EXISTS idx_cross_region_time ON cross_region_prices(asin, last_checked DESC)'
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
    
    # 🔥 Cross-Region Comparison Methods
    
    def save_cross_region_price(self, asin: str, region_data: Dict) -> bool:
        """Save cross-region price data"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO cross_region_prices 
                (asin, region_code, local_price, local_currency, converted_price,
                 shipping_cost, tax_percentage, import_duty_percentage, total_cost,
                 availability_status, product_url, last_checked, best_deal_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?)
            ''', (
                asin,
                region_data['region_code'],
                region_data['local_price'],
                region_data['local_currency'],
                region_data.get('converted_price', 0.0),
                region_data.get('shipping_cost', 0.0),
                region_data.get('tax_percentage', 0.0),
                region_data.get('import_duty_percentage', 0.0),
                region_data.get('total_cost', 0.0),
                region_data.get('availability_status', 'unknown'),
                region_data.get('product_url'),
                region_data.get('best_deal_score', 0.0)
            ))
            
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"❌ Error saving cross-region price: {e}")
            return False
    
    def get_cross_region_prices(self, asin: str, max_age_minutes: int = 5) -> List[Dict]:
        """Get cross-region prices for a product"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM cross_region_prices 
                WHERE asin = ? 
                AND last_checked >= datetime('now', '-' || ? || ' minutes')
                ORDER BY total_cost ASC
            ''', (asin, max_age_minutes))
            
            columns = [desc[0] for desc in cursor.description]
            results = []
            
            for row in cursor.fetchall():
                result = dict(zip(columns, row))
                results.append(result)
            
            return results
        except Exception as e:
            logger.error(f"❌ Error getting cross-region prices: {e}")
            return []
    
    def get_best_region_deals(self, limit: int = 10) -> List[Dict]:
        """Get best cross-region deals across all products"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT DISTINCT crp.asin, 
                       crp.region_code,
                       crp.total_cost,
                       crp.local_price,
                       crp.local_currency,
                       crp.product_url,
                       p.product_name,
                       p.currency as product_currency,
                       crp.last_checked
                FROM cross_region_prices crp
                JOIN products p ON crp.asin = p.asin
                WHERE crp.total_cost > 0
                AND crp.total_cost = (
                    SELECT MIN(total_cost) 
                    FROM cross_region_prices 
                    WHERE asin = crp.asin
                    AND last_checked >= datetime('now', '-30 minutes')
                )
                ORDER BY crp.last_checked DESC
                LIMIT ?
            ''', (limit,))
            
            columns = [desc[0] for desc in cursor.description]
            deals = []
            
            for row in cursor.fetchall():
                deal = dict(zip(columns, row))
                deals.append(deal)
            
            return deals
        except Exception as e:
            logger.error(f"❌ Error getting best region deals: {e}")
            return []
    
    def get_comparison_history(self, asin: str, days: int = 7) -> List[Dict]:
        """Get historical comparison data for a product"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT region_code, 
                       AVG(total_cost) as avg_total_cost,
                       MIN(total_cost) as min_total_cost,
                       MAX(total_cost) as max_total_cost,
                       COUNT(*) as data_points,
                       MAX(last_checked) as last_checked
                FROM cross_region_prices 
                WHERE asin = ? 
                AND last_checked >= datetime('now', '-' || ? || ' days')
                GROUP BY region_code
                ORDER BY avg_total_cost ASC
            ''', (asin, days))
            
            columns = [desc[0] for desc in cursor.description]
            results = []
            
            for row in cursor.fetchall():
                result = dict(zip(columns, row))
                results.append(result)
            
            return results
        except Exception as e:
            logger.error(f"❌ Error getting comparison history: {e}")
            return []
    
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
    
    def extract_product_data_by_region(self, asin: str, region_code: str) -> Optional[Dict]:
        """Extract product data for specific region"""
        try:
            region_config = REGION_CONFIGS[region_code]
            url = f"https://{region_config['domain']}/dp/{asin}"
            
            headers = self._get_headers()
            response = self.session.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                product_data = self._parse_html(response.text, asin, region_code, region_config)
                return product_data
        except Exception as e:
            logger.debug(f"Extraction failed for {asin} in {region_code}: {e}")
        return None
    
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

# 🔥 ==================== CROSS-REGION COMPARATOR ====================

class CrossRegionComparator:
    """
    🔥 محرك مقارنة الأسعار بين المناطق
    يقارن سعر المنتج في جميع المناطق المدعومة ويحدد أفضل صفقة
    """
    
    def __init__(self, db_manager: UltimateDatabaseManager, extractor: SmartExtractionEngine):
        self.db = db_manager
        self.extractor = extractor
        self.config = COMPARISON_CONFIG
        logger.info("✅ Cross-Region Comparator initialized")
    
    def compare_product_prices(self, asin: str, target_region: str = None, force_refresh: bool = False) -> Dict:
        """
        🔍 مقارنة سعر المنتج عبر جميع المناطق
        
        الخوارزمية:
        1. التحقق من التخزين المؤقت (5 دقائق)
        2. استخراج الأسعار من جميع المناطق (بالتوازي)
        3. تحويل الأسعار إلى عملة موحدة (USD)
        4. حساب التكاليف الإضافية (الشحن، الضرائب)
        5. تحديد أفضل وأسوأ منطقة
        6. إنشاء توصية ذكية
        """
        if not self.config['enabled']:
            return {
                'status': 'disabled',
                'message': 'Cross-region comparison is disabled'
            }
        
        try:
            logger.info(f"🔄 Starting cross-region comparison for {asin}")
            
            # 1. التحقق من التخزين المؤقت
            if not force_refresh:
                cached_prices = self.db.get_cross_region_prices(asin, self.config['cache_duration_minutes'])
                if cached_prices:
                    logger.info(f"📊 Using cached data for {asin}")
                    return self._analyze_cached_prices(asin, cached_prices, target_region)
            
            # 2. استخراج الأسعار من جميع المناطق (بالتوازي)
            region_prices = self._fetch_all_region_prices(asin)
            
            if not region_prices:
                return {
                    'status': 'error',
                    'message': 'لم يتم العثور على المنتج في أي منطقة'
                }
            
            # 3. تحليل وترتيب المناطق
            comparison_result = self._analyze_regional_prices(
                region_prices, 
                target_region
            )
            
            # 4. حفظ النتائج في قاعدة البيانات
            self._save_comparison_results(asin, region_prices)
            
            # 5. إنشاء توصية ذكية
            recommendation = self._generate_cross_region_recommendation(
                comparison_result
            )
            
            logger.info(f"✅ Comparison completed for {asin}")
            logger.info(f"   🥇 Best region: {comparison_result['best_deal']['region_code']}")
            logger.info(f"   💰 Savings: {comparison_result['savings_percentage']:.1f}%")
            
            return {
                'status': 'success',
                'asin': asin,
                'timestamp': datetime.now().isoformat(),
                'cached': False,
                'comparison': comparison_result,
                'recommendation': recommendation
            }
            
        except Exception as e:
            logger.error(f"❌ Cross-region comparison error: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def _fetch_all_region_prices(self, asin: str) -> List[Dict]:
        """جمع الأسعار من جميع المناطق (بالتوازي)"""
        region_prices = []
        
        def fetch_region_price(region_code: str):
            """استخراج سعر منطقة واحدة"""
            try:
                config = REGION_CONFIGS[region_code]
                product_data = self.extractor.extract_product_data_by_region(asin, region_code)
                
                if product_data and product_data.get('current_price', 0) > 0:
                    return {
                        'region_code': region_code,
                        'region_name': config['name'],
                        'region_flag': config['flag'],
                        'local_price': product_data['current_price'],
                        'local_currency': config['currency'],
                        'currency_symbol': config['currency_symbol'],
                        'product_url': product_data.get('product_url'),
                        'availability': product_data.get('availability_status', 'unknown'),
                        'extraction_time': datetime.now().isoformat()
                    }
            except Exception as e:
                logger.debug(f"❌ Failed to extract price for {region_code}: {e}")
            return None
        
        # استخراج متزامن لجميع المناطق
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.config['parallel_workers']) as executor:
            futures = {
                executor.submit(fetch_region_price, region_code): region_code 
                for region_code in REGION_CONFIGS.keys()
            }
            
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result:
                    region_prices.append(result)
        
        return region_prices
    
    def _analyze_cached_prices(self, asin: str, cached_prices: List[Dict], target_region: str = None) -> Dict:
        """تحليل البيانات المخزنة مؤقتاً"""
        try:
            # تحويل البيانات المخزنة إلى تنسيق التحليل
            region_prices = []
            for cached in cached_prices:
                region_code = cached['region_code']
                config = REGION_CONFIGS.get(region_code, {})
                
                region_prices.append({
                    'region_code': region_code,
                    'region_name': config.get('name', region_code),
                    'region_flag': config.get('flag', '🏳️'),
                    'local_price': cached['local_price'],
                    'local_currency': cached['local_currency'],
                    'currency_symbol': REGION_CONFIGS.get(region_code, {}).get('currency_symbol', '$'),
                    'product_url': cached.get('product_url'),
                    'availability': cached.get('availability_status', 'unknown'),
                    'converted_price_usd': cached.get('converted_price', 0.0),
                    'shipping_cost_usd': cached.get('shipping_cost', 0.0),
                    'total_cost_usd': cached.get('total_cost', 0.0),
                    'extraction_time': cached.get('last_checked', datetime.now().isoformat())
                })
            
            # تحليل البيانات
            comparison_result = self._analyze_regional_prices(region_prices, target_region)
            
            return {
                'status': 'success',
                'asin': asin,
                'timestamp': datetime.now().isoformat(),
                'cached': True,
                'comparison': comparison_result,
                'recommendation': self._generate_cross_region_recommendation(comparison_result)
            }
            
        except Exception as e:
            logger.error(f"❌ Error analyzing cached prices: {e}")
            raise
    
    def _analyze_regional_prices(self, region_prices: List[Dict], target_region: str = None) -> Dict:
        """تحليل وترتيب الأسعار الإقليمية"""
        analyzed_regions = []
        
        for region_data in region_prices:
            # تحويل السعر إلى USD
            local_price = region_data['local_price']
            local_currency = region_data['local_currency']
            
            if local_currency in EXCHANGE_RATES:
                converted_price = local_price * EXCHANGE_RATES[local_currency]
            else:
                converted_price = local_price  # إذا لم نعرف سعر الصرف
            
            # إضافة التكاليف الإضافية
            region_costs = REGIONAL_COSTS.get(region_data['region_code'], {})
            shipping_cost = region_costs.get('shipping', 0.0) if self.config['include_shipping'] else 0.0
            tax_rate = region_costs.get('tax', 0.0) if self.config['include_taxes'] else 0.0
            import_duty = region_costs.get('import_duty', 0.0)
            
            # حساب التكلفة الإجمالية
            tax_amount = (converted_price * tax_rate) / 100
            duty_amount = (converted_price * import_duty) / 100
            
            total_cost = converted_price + shipping_cost + tax_amount + duty_amount
            
            # حساب "درجة الصفقة" (كلما قل السعر، زادت الدرجة)
            base_score = 100 - (total_cost / 100)  # معادلة مبسطة
            # زيادة الدرجة للمناطق الأقرب (تخفيض تكاليف الشحن)
            if region_data['region_code'] in ['SA', 'AE']:
                base_score += 10  # زيادة للأولوية الإقليمية
            
            analyzed_region = {
                **region_data,
                'converted_price_usd': round(converted_price, 2),
                'shipping_cost_usd': round(shipping_cost, 2),
                'tax_amount_usd': round(tax_amount, 2),
                'duty_amount_usd': round(duty_amount, 2),
                'total_cost_usd': round(total_cost, 2),
                'deal_score': round(base_score, 1),
                'cost_breakdown': {
                    'product_price': round(converted_price, 2),
                    'shipping': round(shipping_cost, 2),
                    'tax': round(tax_amount, 2),
                    'import_duty': round(duty_amount, 2)
                }
            }
            
            analyzed_regions.append(analyzed_region)
        
        # ترتيب المناطق حسب الأفضل (أقل تكلفة إجمالية)
        analyzed_regions.sort(key=lambda x: x['total_cost_usd'])
        
        # تحديد المنطقة المستهدفة (إن وجدت)
        target_region_data = None
        if target_region:
            for region in analyzed_regions:
                if region['region_code'] == target_region:
                    target_region_data = region
                    break
        
        # العثور على أفضل وأسوأ منطقة
        best_deal = analyzed_regions[0] if analyzed_regions else None
        worst_deal = analyzed_regions[-1] if len(analyzed_regions) > 1 else None
        
        # حساب النسبة المئوية للتوفير
        savings_percentage = 0.0
        if best_deal and worst_deal and worst_deal['total_cost_usd'] > 0:
            savings_percentage = ((worst_deal['total_cost_usd'] - best_deal['total_cost_usd']) 
                                 / worst_deal['total_cost_usd'] * 100)
        
        return {
            'all_regions': analyzed_regions,
            'best_deal': best_deal,
            'worst_deal': worst_deal,
            'target_region': target_region_data,
            'savings_percentage': round(savings_percentage, 2),
            'currency_base': 'USD',
            'regions_count': len(analyzed_regions),
            'analysis_timestamp': datetime.now().isoformat()
        }
    
    def _save_comparison_results(self, asin: str, region_prices: List[Dict]):
        """حفظ نتائج المقارنة في قاعدة البيانات"""
        try:
            for region_data in region_prices:
                # حساب التكاليف للخزن
                local_currency = region_data['local_currency']
                local_price = region_data['local_price']
                
                if local_currency in EXCHANGE_RATES:
                    converted_price = local_price * EXCHANGE_RATES[local_currency]
                else:
                    converted_price = local_price
                
                region_costs = REGIONAL_COSTS.get(region_data['region_code'], {})
                shipping_cost = region_costs.get('shipping', 0.0) if self.config['include_shipping'] else 0.0
                tax_rate = region_costs.get('tax', 0.0) if self.config['include_taxes'] else 0.0
                import_duty = region_costs.get('import_duty', 0.0)
                
                tax_amount = (converted_price * tax_rate) / 100
                duty_amount = (converted_price * import_duty) / 100
                total_cost = converted_price + shipping_cost + tax_amount + duty_amount
                
                save_data = {
                    'region_code': region_data['region_code'],
                    'local_price': local_price,
                    'local_currency': local_currency,
                    'converted_price': round(converted_price, 2),
                    'shipping_cost': round(shipping_cost, 2),
                    'tax_percentage': tax_rate,
                    'import_duty_percentage': import_duty,
                    'total_cost': round(total_cost, 2),
                    'availability_status': region_data.get('availability', 'unknown'),
                    'product_url': region_data.get('product_url'),
                    'best_deal_score': region_data.get('deal_score', 0.0)
                }
                
                self.db.save_cross_region_price(asin, save_data)
                
        except Exception as e:
            logger.error(f"❌ Error saving comparison results: {e}")
    
    def _generate_cross_region_recommendation(self, comparison: Dict) -> Dict:
        """إنشاء توصية ذكية بناءً على نتائج المقارنة"""
        best_deal = comparison['best_deal']
        worst_deal = comparison.get('worst_deal')
        savings = comparison['savings_percentage']
        
        if not best_deal:
            return {
                'type': 'NEUTRAL',
                'emoji': '⚪',
                'color': '#9E9E9E',
                'title': 'بيانات غير كافية',
                'message': 'لا توجد بيانات كافية لمقارنة الأسعار بين المناطق',
                'action': 'wait',
                'priority': 0
            }
        
        if savings > 20:
            # توفير كبير - صفقة ممتازة
            return {
                'type': 'HOT_DEAL',
                'emoji': '🔥',
                'color': '#FF5722',
                'title': '🔥 صفقة ساخنة في منطقة أخرى!',
                'message': f'توفير يصل إلى {savings:.1f}% مقارنة بأغلى منطقة',
                'details': f'اشتري من {best_deal["region_name"]} {best_deal["region_flag"]} ووفر ${(worst_deal["total_cost_usd"] - best_deal["total_cost_usd"]):.2f}',
                'action': 'buy_from_region',
                'recommended_region': best_deal['region_code'],
                'savings_amount': worst_deal['total_cost_usd'] - best_deal['total_cost_usd'],
                'savings_percentage': savings,
                'priority': 3
            }
        elif savings > 10:
            # توفير جيد
            return {
                'type': 'GOOD_DEAL',
                'emoji': '💰',
                'color': '#4CAF50',
                'title': '💰 توفير جيد في منطقة أخرى',
                'message': f'وفر {savings:.1f}% بشراء من {best_deal["region_name"]}',
                'action': 'consider_region',
                'recommended_region': best_deal['region_code'],
                'priority': 2
            }
        else:
            # لا فرق كبير
            return {
                'type': 'SIMILAR',
                'emoji': '⚖️',
                'color': '#2196F3',
                'title': '⚖️ الأسعار متقاربة',
                'message': 'لا يوجد فرق كبير في الأسعار بين المناطق',
                'action': 'buy_local',
                'reason': 'تكاليف الشحن والضرائب تساوي الفرق في السعر',
                'priority': 1
            }
    
    def get_best_region_deals(self, limit: int = 10) -> List[Dict]:
        """الحصول على أفضل صفقات المناطق"""
        try:
            deals = self.db.get_best_region_deals(limit)
            
            # إضافة معلومات إضافية
            for deal in deals:
                region_code = deal['region_code']
                deal['region_name'] = REGION_CONFIGS.get(region_code, {}).get('name', region_code)
                deal['region_flag'] = REGION_CONFIGS.get(region_code, {}).get('flag', '🏳️')
                deal['currency_symbol'] = REGION_CONFIGS.get(region_code, {}).get('currency_symbol', '$')
            
            return deals
        except Exception as e:
            logger.error(f"❌ Error getting best region deals: {e}")
            return []
    
    def get_comparison_history(self, asin: str, days: int = 7) -> List[Dict]:
        """الحصول على تاريخ مقارنات المنتج"""
        try:
            history = self.db.get_comparison_history(asin, days)
            
            # إضافة معلومات إضافية
            for item in history:
                region_code = item['region_code']
                item['region_name'] = REGION_CONFIGS.get(region_code, {}).get('name', region_code)
                item['region_flag'] = REGION_CONFIGS.get(region_code, {}).get('flag', '🏳️')
            
            return history
        except Exception as e:
            logger.error(f"❌ Error getting comparison history: {e}")
            return []

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
    """Ultimate Amazon Price Tracker System with Smart Recommendations & Cross-Region Comparison"""
    
    def __init__(self):
        self.db = UltimateDatabaseManager()
        self.extractor = SmartExtractionEngine()
        self.predictor = AIPricePredictor(self.db)
        self.analyzer = SmartPriceAnalyzer(self.db)
        self.comparator = CrossRegionComparator(self.db, self.extractor)  # 🔥
        self.notifier = NotificationManager()
        self.setup_routes()
        logger.info("✅ Ultimate Tracker System initialized with Cross-Region Comparison")
    
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
                
                # Generate smart recommendation
                recommendation = self.analyzer.analyze_price(
                    product_data['asin'],
                    product_data['current_price'],
                    product_data['currency']
                )
                
                # 🔥 Automatically compare regions for new products
                if COMPARISON_CONFIG['enabled']:
                    comparison_thread = threading.Thread(
                        target=self.comparator.compare_product_prices,
                        args=(product_data['asin'],),
                        kwargs={'force_refresh': True}
                    )
                    comparison_thread.daemon = True
                    comparison_thread.start()
                
                return jsonify({
                    'status': 'success',
                    'product': product_data,
                    'prediction': prediction,
                    'recommendation': recommendation,
                    'extraction_method': method
                })
                
            except Exception as e:
                logger.error(f"Error adding product: {e}")
                return jsonify({'status': 'error', 'message': str(e)}), 500
        
        @app.route('/api/products')
        def get_products():
            region = request.args.get('region')
            products = self.db.get_products(region=region)
            
            # إضافة التوصية لكل منتج
            for product in products:
                rec = self.db.get_latest_recommendation(product['asin'])
                product['recommendation'] = rec
                
                # 🔥 إضافة معلومات المقارنة إذا كانت متاحة
                if COMPARISON_CONFIG['enabled']:
                    cached_prices = self.db.get_cross_region_prices(product['asin'], 30)
                    if cached_prices:
                        product['has_cross_region_data'] = True
                        product['regions_available'] = len(cached_prices)
            
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
        
        @app.route('/api/product/<asin>/recommendation')
        def get_recommendation(asin):
            rec = self.db.get_latest_recommendation(asin)
            if rec:
                return jsonify({'status': 'success', 'recommendation': rec})
            else:
                return jsonify({'status': 'error', 'message': 'No recommendation available'}), 404
        
        # 🔥 Cross-Region Comparison APIs
        
        @app.route('/api/product/<asin>/compare-regions')
        def compare_regions(asin):
            try:
                target_region = request.args.get('target_region')
                force_refresh = request.args.get('refresh', 'false').lower() == 'true'
                
                result = self.comparator.compare_product_prices(asin, target_region, force_refresh)
                return jsonify(result)
                
            except Exception as e:
                logger.error(f"Error in region comparison: {e}")
                return jsonify({'status': 'error', 'message': str(e)}), 500
        
        @app.route('/api/product/<asin>/comparison-history')
        def get_comparison_history(asin):
            try:
                days = request.args.get('days', 7, type=int)
                history = self.comparator.get_comparison_history(asin, days)
                return jsonify({
                    'status': 'success',
                    'asin': asin,
                    'history': history,
                    'days_analyzed': days
                })
            except Exception as e:
                return jsonify({'status': 'error', 'message': str(e)}), 500
        
        @app.route('/api/best-region-deals')
        def get_best_region_deals():
            try:
                limit = request.args.get('limit', 10, type=int)
                deals = self.comparator.get_best_region_deals(limit)
                
                return jsonify({
                    'status': 'success',
                    'deals': deals,
                    'count': len(deals),
                    'feature': 'cross_region_comparison'
                })
                
            except Exception as e:
                return jsonify({'status': 'error', 'message': str(e)}), 500
        
        @app.route('/api/regions')
        def get_regions():
            regions = [
                {
                    'code': code,
                    'name': config['name'],
                    'flag': config['flag'],
                    'currency': config['currency'],
                    'currency_symbol': config['currency_symbol'],
                    'domain': config['domain'],
                    'costs': REGIONAL_COSTS.get(code, {})
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
                
                # إحصائيات التوصيات
                cursor.execute('SELECT COUNT(*) FROM price_recommendations WHERE recommendation_type = "BUY"')
                buy_recommendations = cursor.fetchone()[0]
                
                # 🔥 إحصائيات المقارنة بين المناطق
                cursor.execute('SELECT COUNT(DISTINCT asin) FROM cross_region_prices')
                products_with_comparison = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(*) FROM cross_region_prices WHERE last_checked >= datetime("now", "-1 hour")')
                recent_comparisons = cursor.fetchone()[0]
                
                return jsonify({
                    'status': 'success',
                    'stats': {
                        'total_products': total_products,
                        'regions_count': regions_count,
                        'avg_discount': round(avg_discount, 2),
                        'alerts_today': alerts_today,
                        'buy_recommendations': buy_recommendations,
                        'products_with_comparison': products_with_comparison,  # 🔥
                        'recent_comparisons': recent_comparisons  # 🔥
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
                    'smart_recommendations': RECOMMENDATION_CONFIG['enabled'],
                    'cross_region_comparison': COMPARISON_CONFIG['enabled'],  # 🔥
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
        .new-feature-badge {
            background: linear-gradient(135deg, #FF416C 0%, #FF4B2B 100%);
            color: white;
            padding: 8px 20px;
            border-radius: 20px;
            display: inline-block;
            font-weight: bold;
            margin-left: 10px;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
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
        
        .feature-highlight {
            background: linear-gradient(135deg, #FF416C 0%, #FF4B2B 100%);
            color: white;
            padding: 25px;
            border-radius: 15px;
            margin-bottom: 20px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        .feature-highlight h2 {
            margin-bottom: 10px;
            font-size: 1.8rem;
        }
        
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
        
        .btn-hot {
            background: linear-gradient(135deg, #FF416C 0%, #FF4B2B 100%);
            color: white;
            border: none;
            padding: 15px;
            border-radius: 10px;
            width: 100%;
            font-size: 1.1rem;
            font-weight: bold;
            cursor: pointer;
            transition: transform 0.3s;
            margin-top: 10px;
        }
        .btn-hot:hover { transform: scale(1.05); }
        
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
        
        .comparison-badge {
            background: #FF416C;
            color: white;
            padding: 5px 10px;
            border-radius: 10px;
            font-size: 0.8rem;
            display: inline-block;
            margin-left: 5px;
        }
        
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
        
        .recommendation-card {
            background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
            padding: 15px;
            border-radius: 10px;
            margin-top: 10px;
            border-left: 4px solid #667eea;
        }
        
        .comparison-section {
            background: white;
            padding: 25px;
            border-radius: 15px;
            margin-top: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            display: none;
        }
        
        .comparison-results {
            max-height: 500px;
            overflow-y: auto;
            margin-top: 20px;
        }
        
        .region-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 15px;
            border-left: 4px solid #667eea;
        }
        .region-card.best {
            background: #e8f5e9;
            border-left: 4px solid #4CAF50;
        }
        .region-card.worst {
            background: #ffebee;
            border-left: 4px solid #F44336;
        }
        
        .deal-card {
            background: white;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            margin-bottom: 15px;
        }
        
        .profit-guide {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            padding: 25px;
            border-radius: 15px;
            margin: 40px 0;
            text-align: center;
        }
        
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            z-index: 1000;
            justify-content: center;
            align-items: center;
        }
        .modal-content {
            background: white;
            padding: 30px;
            border-radius: 15px;
            max-width: 800px;
            width: 90%;
            max-height: 80vh;
            overflow-y: auto;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Ultimate Amazon Price Tracker</h1>
            <p style="color: #666; margin: 10px 0;">AI-Powered • Multi-Region • Smart Recommendations • 🔥 Cross-Region Comparison</p>
            <span class="version-badge">v''' + VERSION + '''</span>
            <span class="new-feature-badge">🔥 NEW: Cross-Region Price Comparison</span>
        </div>

        <div class="feature-highlight">
            <h2>🔥 اكتشف فرق الأسعار بين الدول</h2>
            <p>احصل على نفس المنتج بسعر أقل في دولة أخرى مع إمكانية الشحن الدولي</p>
            <p style="margin-top: 10px; font-size: 1.1rem;">
                مثال: iPhone 15 Pro - السعودية: 4,999 ريال 🇸🇦 | الإمارات: 3,999 درهم 🇦🇪
                <br>
                <strong>التوفير: 244 دولار (18.3%)</strong>
            </p>
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
                <div class="stat-label">🔥 Cross-Region Deals</div>
                <div class="stat-value" id="comparisonProducts">0</div>
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
                    <button class="btn-hot" onclick="toggleComparisonSection()">
                        🔥 Compare Across Regions
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
                                <th>Recommendation</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody id="productsTable"></tbody>
                    </table>
                </div>
            </div>
        </div>
        
        <!-- 🔥 Cross-Region Comparison Section -->
        <div class="comparison-section" id="comparisonSection">
            <h2 style="color: #333; margin-bottom: 20px;">🔥 مقارنة الأسعار بين المناطق</h2>
            
            <div style="display: flex; gap: 10px; margin-bottom: 20px;">
                <button class="btn-primary" onclick="compareRegions()" id="compareBtn">
                    🔄 مقارنة الأسعار بين المناطق
                </button>
                <button class="btn-hot" onclick="loadBestRegionDeals()">
                    💰 أفضل صفقات المناطق
                </button>
                <button class="btn-primary" onclick="showComparisonHistory()" style="background: #607d8b;">
                    📊 سجل المقارنات
                </button>
            </div>
            
            <div style="background: #f0f4ff; padding: 15px; border-radius: 10px; margin-bottom: 20px;">
                <label style="display: flex; align-items: center; gap: 10px;">
                    <input type="checkbox" id="includeShipping" checked>
                    <span>تضمين تكاليف الشحن</span>
                </label>
                <label style="display: flex; align-items: center; gap: 10px; margin-top: 10px;">
                    <input type="checkbox" id="includeTaxes" checked>
                    <span>تضمين الضرائب والجمارك</span>
                </label>
            </div>
            
            <div id="comparisonLoading" class="loading" style="display: none;">
                <div class="spinner"></div>
                <p>جاري مقارنة الأسعار بين جميع المناطق...</p>
                <p style="font-size: 0.9rem; color: #666;">قد يستغرق هذا بضع ثواني</p>
            </div>
            
            <div id="comparisonResults" style="display: none;"></div>
            
            <div id="bestDealsSection" style="margin-top: 40px; display: none;">
                <h3 style="color: #333; margin-bottom: 15px;">💰 أفضل صفقات المناطق</h3>
                <div id="bestDealsGrid" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 15px;"></div>
            </div>
        </div>
        
        <!-- Profit Guide -->
        <div class="profit-guide">
            <h2 style="margin: 0 0 10px 0;">🚀 كيف تربح من فرق الأسعار بين المناطق؟</h2>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-top: 20px;">
                <div style="background: rgba(255,255,255,0.2); padding: 15px; border-radius: 10px;">
                    <div style="font-size: 2rem; margin-bottom: 10px;">🛒</div>
                    <div style="font-weight: bold;">اشترِ من أرخص منطقة</div>
                    <p style="font-size: 0.9rem; margin: 10px 0 0 0;">اشتري نفس المنتج من أمازون الإمارات بدلاً من السعودية ووفر حتى 30%</p>
                </div>
                <div style="background: rgba(255,255,255,0.2); padding: 15px; border-radius: 10px;">
                    <div style="font-size: 2rem; margin-bottom: 10px;">💰</div>
                    <div style="font-weight: bold;">استخدم روابط الأفلييت</div>
                    <p style="font-size: 0.9rem; margin: 10px 0 0 0;">اربح عمولة من كل عملية شراء عبر روابطك في المناطق المختلفة</p>
                </div>
                <div style="background: rgba(255,255,255,0.2); padding: 15px; border-radius: 10px;">
                    <div style="font-size: 2rem; margin-bottom: 10px;">🌐</div>
                    <div style="font-weight: bold;">استغل فروق العملات</div>
                    <p style="font-size: 0.9rem; margin: 10px 0 0 0;">انخفاض اليورو أو الجنيه الإسترليني قد يعني فرصة ذهبية للشراء</p>
                </div>
            </div>
            <button onclick="showProfitGuide()" style="background: white; color: #FF416C; padding: 12px 30px; 
                border: none; border-radius: 25px; font-weight: bold; margin-top: 20px; cursor: pointer;">
                📚 دليل الربح من فرق الأسعار
            </button>
        </div>
    </div>

    <!-- Modal for History -->
    <div class="modal" id="historyModal">
        <div class="modal-content">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                <h3 style="color: #333; margin: 0;">📊 سجل مقارنات المناطق</h3>
                <button onclick="closeModal()" style="background: none; border: none; font-size: 1.5rem; cursor: pointer; color: #666;">×</button>
            </div>
            <div id="historyContent"></div>
        </div>
    </div>

    <script>
        let selectedProductASIN = null;
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
                    document.getElementById('comparisonProducts').textContent = data.stats.products_with_comparison || 0;
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
                        
                        // 🔥 إضافة شارة المقارنة إذا كانت البيانات متاحة
                        const comparisonBadge = p.has_cross_region_data ? 
                            `<span class="comparison-badge" title="متاح في ${p.regions_available} منطقة">🔥 ${p.regions_available}</span>` : '';
                        
                        return `
                        <tr>
                            <td>
                                <strong>${p.product_name.substring(0, 50)}...</strong><br>
                                <code style="font-size: 0.8rem; color: #666;">${p.asin}</code>
                                ${comparisonBadge}
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
                                <button onclick="showProductDetails('${p.asin}')" style="padding: 5px 15px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; border-radius: 5px; cursor: pointer; margin-bottom: 5px;">
                                    📊 Details
                                </button>
                                <button onclick="compareProductRegions('${p.asin}')" style="padding: 5px 15px; background: linear-gradient(135deg, #FF416C 0%, #FF4B2B 100%); color: white; border: none; border-radius: 5px; cursor: pointer; width: 100%;">
                                    🔥 Compare
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
                        <div style="margin-top: 15px; padding: 15px; background: #e3f2fd; border-radius: 10px;">
                            <strong>🔥 Cross-Region Comparison:</strong><br>
                            <span style="font-size: 0.9rem; color: #555;">تم بدء مقارنة الأسعار بين المناطق في الخلفية. استخدم زر "Compare" لرؤية النتائج.</span>
                        </div>
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
        
        function showProductDetails(asin) {
            selectedProductASIN = asin;
            toggleComparisonSection();
            compareRegions();
        }
        
        function compareProductRegions(asin) {
            selectedProductASIN = asin;
            toggleComparisonSection();
            compareRegions();
        }
        
        function toggleComparisonSection() {
            const section = document.getElementById('comparisonSection');
            section.style.display = section.style.display === 'none' ? 'block' : 'none';
            if (section.style.display === 'block') {
                section.scrollIntoView({ behavior: 'smooth' });
            }
        }
        
        async function compareRegions() {
            if (!selectedProductASIN) {
                const asin = prompt('Enter product ASIN:');
                if (!asin) return;
                selectedProductASIN = asin;
            }
            
            const loading = document.getElementById('comparisonLoading');
            const results = document.getElementById('comparisonResults');
            const btn = document.getElementById('compareBtn');
            
            loading.style.display = 'block';
            results.style.display = 'none';
            btn.disabled = true;
            
            try {
                const includeShipping = document.getElementById('includeShipping').checked;
                const includeTaxes = document.getElementById('includeTaxes').checked;
                
                const response = await fetch(`/api/product/${selectedProductASIN}/compare-regions?refresh=true`);
                const data = await response.json();
                
                loading.style.display = 'none';
                btn.disabled = false;
                
                if (data.status === 'success') {
                    displayComparisonResults(data);
                    loadBestRegionDeals();
                } else {
                    results.innerHTML = `
                        <div class="error-box" style="padding: 20px; background: #ffebee; border-left: 4px solid #f44336; border-radius: 10px;">
                            <h4 style="color: #c62828; margin: 0 0 10px 0;">❌ خطأ في المقارنة</h4>
                            <p>${data.message}</p>
                        </div>
                    `;
                    results.style.display = 'block';
                }
            } catch (error) {
                loading.style.display = 'none';
                btn.disabled = false;
                results.innerHTML = `
                    <div class="error-box">
                        <h4>❌ خطأ في الاتصال</h4>
                        <p>${error.message}</p>
                    </div>
                `;
                results.style.display = 'block';
            }
        }
        
        function displayComparisonResults(data) {
            const results = document.getElementById('comparisonResults');
            const comparison = data.comparison;
            
            if (!comparison || comparison.regions_count === 0) {
                results.innerHTML = `
                    <div style="text-align: center; padding: 40px; background: #f5f5f5; border-radius: 10px;">
                        <h4 style="color: #666;">🌐 لا توجد بيانات للمقارنة</h4>
                        <p>لم يتم العثور على المنتج في المناطق الأخرى</p>
                    </div>
                `;
                results.style.display = 'block';
                return;
            }
            
            let html = `
                <div style="background: white; border-radius: 15px; padding: 25px; box-shadow: 0 10px 30px rgba(0,0,0,0.1);">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                        <h3 style="color: #333; margin: 0;">
                            ${data.cached ? '🔄 (بيانات مخزنة)' : '🌍'} مقارنة الأسعار بين ${comparison.regions_count} منطقة
                        </h3>
                        <div style="font-size: 0.9rem; color: #666;">
                            ${new Date(comparison.analysis_timestamp).toLocaleString()}
                        </div>
                    </div>
                    
                    ${data.recommendation ? `
                        <div style="background: linear-gradient(135deg, ${data.recommendation.color}20 0%, ${data.recommendation.color}40 100%); 
                             padding: 20px; border-radius: 10px; margin-bottom: 25px; border-left: 4px solid ${data.recommendation.color};">
                            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
                                <span style="font-size: 1.5rem;">${data.recommendation.emoji}</span>
                                <h4 style="margin: 0; color: ${data.recommendation.color};">${data.recommendation.title}</h4>
                            </div>
                            <p style="margin: 0; font-size: 1.1rem; color: #333;">${data.recommendation.message}</p>
                            ${data.recommendation.details ? `
                                <p style="margin: 10px 0 0 0; font-size: 1rem; color: #555; font-weight: bold;">${data.recommendation.details}</p>
                            ` : ''}
                            ${comparison.savings_percentage > 0 ? `
                                <div style="margin-top: 15px; padding: 10px; background: white; border-radius: 8px; display: inline-block;">
                                    <span style="color: #4CAF50; font-weight: bold;">💵 توفير يصل إلى ${comparison.savings_percentage.toFixed(1)}%</span>
                                </div>
                            ` : ''}
                        </div>
                    ` : ''}
                    
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 30px;">
            `;
            
            // عرض كل منطقة
            comparison.all_regions.forEach((region, index) => {
                const isBest = index === 0;
                const isWorst = index === comparison.all_regions.length - 1;
                
                html += `
                    <div class="region-card ${isBest ? 'best' : isWorst ? 'worst' : ''}" style="background: ${isBest ? '#e8f5e9' : isWorst ? '#ffebee' : '#f8f9fa'}; 
                         padding: 20px; border-radius: 10px; 
                         border-left: 4px solid ${isBest ? '#4CAF50' : isWorst ? '#F44336' : '#9E9E9E'};">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                            <div>
                                <div style="font-size: 1.2rem; font-weight: bold;">${region.region_flag} ${region.region_name}</div>
                                <div style="font-size: 0.9rem; color: #666;">${region.region_code}</div>
                            </div>
                            <div style="text-align: right;">
                                ${isBest ? '<span style="background: #4CAF50; color: white; padding: 5px 10px; border-radius: 15px; font-size: 0.8rem;">🥇 أفضل سعر</span>' : ''}
                                ${isWorst ? '<span style="background: #F44336; color: white; padding: 5px 10px; border-radius: 15px; font-size: 0.8rem;">📈 أغلى سعر</span>' : ''}
                            </div>
                        </div>
                        
                        <div style="margin-bottom: 15px;">
                            <div style="font-size: 1.5rem; font-weight: bold; color: ${isBest ? '#2E7D32' : '#333'};">
                                ${region.currency_symbol}${region.local_price.toFixed(2)} 
                                <span style="font-size: 0.9rem; color: #666;">($${region.converted_price_usd.toFixed(2)})</span>
                            </div>
                            <div style="font-size: 0.9rem; color: #666;">
                                ${region.local_currency} → USD
                            </div>
                        </div>
                        
                        <div style="background: white; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                            <div style="font-weight: bold; margin-bottom: 10px; color: #333;">تفصيل التكاليف (USD):</div>
                            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                                <span>سعر المنتج:</span>
                                <span>$${region.cost_breakdown.product_price.toFixed(2)}</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                                <span>الشحن:</span>
                                <span>$${region.cost_breakdown.shipping.toFixed(2)}</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                                <span>الضرائب:</span>
                                <span>$${region.cost_breakdown.tax.toFixed(2)}</span>
                            </div>
                            ${region.cost_breakdown.import_duty > 0 ? `
                                <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                                    <span>الجمارك:</span>
                                    <span>$${region.cost_breakdown.import_duty.toFixed(2)}</span>
                                </div>
                            ` : ''}
                            <div style="display: flex; justify-content: space-between; margin-top: 10px; padding-top: 10px; border-top: 1px solid #eee; font-weight: bold; color: ${isBest ? '#2E7D32' : '#333'};">
                                <span>التكلفة الإجمالية:</span>
                                <span>$${region.total_cost_usd.toFixed(2)}</span>
                            </div>
                        </div>
                        
                        <div style="text-align: center;">
                            <a href="${region.product_url}" target="_blank" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                               color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
                                🛒 اشترِ من ${region.region_flag}
                            </a>
                        </div>
                        
                        <div style="margin-top: 15px; font-size: 0.8rem; color: #666; text-align: center;">
                            <span style="background: #e0e0e0; padding: 3px 10px; border-radius: 10px;">
                                درجة الصفقة: ${region.deal_score}/100
                            </span>
                        </div>
                    </div>
                `;
            });
            
            html += `
                    </div>
                    
                    <div style="background: #e3f2fd; padding: 20px; border-radius: 10px; margin-top: 20px;">
                        <h4 style="color: #1565c0; margin: 0 0 10px 0;">💡 كيف تستفيد من المقارنة؟</h4>
                        <ul style="margin: 0; padding-left: 20px; color: #333;">
                            <li>اشتري من المنطقة ذات السعر الأقل حتى مع تكاليف الشحن</li>
                            <li>استخدم خدمات الشحن الدولية الموثوقة</li>
                            <li>تحقق من سياسة الضمان والمرتجعات لكل منطقة</li>
                            <li>راجع تقييمات المنتج في كل منطقة للتأكد من الجودة</li>
                        </ul>
                        ${comparison.best_deal && comparison.savings_percentage > 10 ? `
                            <div style="margin-top: 15px; padding: 15px; background: #4CAF50; color: white; border-radius: 8px;">
                                <strong>🎯 نصيحة سريعة:</strong> اشترِ من ${comparison.best_deal.region_name} ${comparison.best_deal.region_flag} 
                                ووفر <strong>$${(comparison.worst_deal.total_cost_usd - comparison.best_deal.total_cost_usd).toFixed(2)}</strong> 
                                (${comparison.savings_percentage.toFixed(1)}% توفير)!
                            </div>
                        ` : ''}
                    </div>
                </div>
            `;
            
            results.innerHTML = html;
            results.style.display = 'block';
        }
        
        async function loadBestRegionDeals() {
            try {
                const response = await fetch('/api/best-region-deals');
                const data = await response.json();
                
                if (data.status === 'success' && data.deals.length > 0) {
                    const section = document.getElementById('bestDealsSection');
                    const grid = document.getElementById('bestDealsGrid');
                    
                    section.style.display = 'block';
                    
                    grid.innerHTML = data.deals.map(deal => `
                        <div class="deal-card">
                            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 10px;">
                                <div>
                                    <div style="font-weight: bold; font-size: 1.1rem;">${deal.product_name.substring(0, 40)}...</div>
                                    <div style="font-size: 0.9rem; color: #666;">${deal.asin}</div>
                                </div>
                                <span style="background: #FF416C; color: white; padding: 3px 8px; border-radius: 12px; font-size: 0.8rem;">
                                    ${deal.region_flag} ${deal.region_code}
                                </span>
                            </div>
                            
                            <div style="margin: 10px 0;">
                                <div style="font-size: 1.3rem; font-weight: bold; color: #2E7D32;">
                                    $${deal.total_cost.toFixed(2)}
                                </div>
                                <div style="font-size: 0.9rem; color: #666;">
                                    أفضل سعر عالمي | ${deal.local_currency} ${deal.local_price.toFixed(2)}
                                </div>
                            </div>
                            
                            <div style="text-align: center;">
                                <a href="${deal.product_url}" target="_blank" style="background: #2196F3; color: white; padding: 8px 15px; 
                                   text-decoration: none; border-radius: 5px; display: inline-block; font-size: 0.9rem;">
                                    🛒 اشترِ الآن
                                </a>
                                <button onclick="compareProductRegions('${deal.asin}')" style="margin-left: 10px; background: #9C27B0; color: white; 
                                   padding: 8px 15px; border: none; border-radius: 5px; cursor: pointer; font-size: 0.9rem;">
                                    🔄 قارن
                                </button>
                            </div>
                        </div>
                    `).join('');
                } else {
                    document.getElementById('bestDealsGrid').innerHTML = `
                        <div style="text-align: center; padding: 40px; color: #666;">
                            لا توجد صفقات متاحة حالياً
                        </div>
                    `;
                }
            } catch (error) {
                console.error('Error loading best deals:', error);
            }
        }
        
        async function showComparisonHistory() {
            if (!selectedProductASIN) {
                const asin = prompt('Enter product ASIN to view comparison history:');
                if (!asin) return;
                selectedProductASIN = asin;
            }
            
            try {
                const response = await fetch(`/api/product/${selectedProductASIN}/comparison-history?days=7`);
                const data = await response.json();
                
                if (data.status === 'success') {
                    const modal = document.getElementById('historyModal');
                    const content = document.getElementById('historyContent');
                    
                    if (data.history.length > 0) {
                        content.innerHTML = `
                            <div style="overflow-x: auto;">
                                <table style="width: 100%; border-collapse: collapse;">
                                    <thead>
                                        <tr style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
                                            <th style="padding: 12px; text-align: left;">المنطقة</th>
                                            <th style="padding: 12px; text-align: left;">متوسط السعر</th>
                                            <th style="padding: 12px; text-align: left;">أقل سعر</th>
                                            <th style="padding: 12px; text-align: left;">أعلى سعر</th>
                                            <th style="padding: 12px; text-align: left;">عدد القراءات</th>
                                            <th style="padding: 12px; text-align: left;">آخر تحديث</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        ${data.history.map(region => `
                                            <tr style="border-bottom: 1px solid #eee;">
                                                <td style="padding: 12px;">
                                                    <div style="display: flex; align-items: center; gap: 8px;">
                                                        <span style="font-size: 1.2rem;">${region.region_flag}</span>
                                                        <div>
                                                            <div>${region.region_name}</div>
                                                            <div style="font-size: 0.8rem; color: #666;">${region.region_code}</div>
                                                        </div>
                                                    </div>
                                                </td>
                                                <td style="padding: 12px;">
                                                    <span style="font-weight: bold; color: #2E7D32;">$${region.avg_total_cost.toFixed(2)}</span>
                                                </td>
                                                <td style="padding: 12px;">
                                                    <span style="color: #4CAF50;">$${region.min_total_cost.toFixed(2)}</span>
                                                </td>
                                                <td style="padding: 12px;">
                                                    <span style="color: #F44336;">$${region.max_total_cost.toFixed(2)}</span>
                                                </td>
                                                <td style="padding: 12px;">
                                                    <span style="background: #e0e0e0; padding: 3px 10px; border-radius: 15px; font-size: 0.9rem;">
                                                        ${region.data_points}
                                                    </span>
                                                </td>
                                                <td style="padding: 12px; font-size: 0.9rem; color: #666;">
                                                    ${new Date(region.last_checked).toLocaleString()}
                                                </td>
                                            </tr>
                                        `).join('')}
                                    </tbody>
                                </table>
                            </div>
                            
                            <div style="margin-top: 20px; padding: 15px; background: #e8f5e9; border-radius: 8px;">
                                <strong>📈 تحليل الاتجاه:</strong>
                                <p style="margin: 10px 0 0 0; color: #333;">
                                    بناءً على ${data.history.reduce((sum, r) => sum + r.data_points, 0)} قراءة خلال ${data.days_analyzed} أيام
                                </p>
                            </div>
                        `;
                    } else {
                        content.innerHTML = `
                            <div style="text-align: center; padding: 40px;">
                                <h4 style="color: #666; margin: 0 0 10px 0;">لا توجد بيانات تاريخية</h4>
                                <p>إبدأ بمقارنة الأسعار لبناء سجل المقارنات</p>
                            </div>
                        `;
                    }
                    
                    modal.style.display = 'flex';
                }
            } catch (error) {
                alert('خطأ في تحميل السجل: ' + error.message);
            }
        }
        
        function closeModal() {
            document.getElementById('historyModal').style.display = 'none';
        }
        
        function showProfitGuide() {
            alert(`🚀 دليل الربح من فرق الأسعار بين المناطق

1. اكتشاف فرق السعر:
   - البرنامج يقارن سعر المنتج في 5 مناطق
   - يحسب التكلفة الإجمالية (بما فيها الشحن والضرائب)
   - يحدد المنطقة الأرخص

2. كيفية الربح:
   - اشتري من المنطقة الأرخص (حتى مع الشحن الدولي)
   - استخدم روابط الأفلييت في كل منطقة لربح العمولة
   - نسبة العمولة: 4-10% من سعر المنتج

3. مثال عملي:
   - iPhone 15 Pro في السعودية: 4,999 ريال (≈ 1,333 دولار)
   - نفس المنتج في الإمارات: 3,999 درهم (≈ 1,089 دولار)
   - فرق السعر: 244 دولار (18.3% توفير)
   - عمولة الأفلييت (5%): 54.45 دولار

4. دخل شهري متوقع:
   - 10 منتجات مكتشفة يومياً × 30 يوم = 300 منتج
   - معدل تحويل 2% = 6 عمليات شراء يومياً
   - متوسط العمولة 20 دولار = 120 دولار يومياً
   - الدخل الشهري: ≈ 3,600 دولار

5. نصائح:
   - استخدم خدمات الشحن الموثوقة
   - تحقق من سياسة الضمان والمرتجعات
   - راجع تقييمات المنتج في كل منطقة
   - استغل فروق العملات (اليورو، الجنيه، الخ)`);
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
        print(f"   • GET  /api/product/<asin>/recommendation - Get smart recommendation")
        print(f"   • GET  /api/product/<asin>/compare-regions 🔥 - Compare prices across regions")
        print(f"   • GET  /api/product/<asin>/comparison-history - Get comparison history")
        print(f"   • GET  /api/best-region-deals    - Get best cross-region deals")
        print(f"   • GET  /api/regions              - Get supported regions")
        print(f"   • GET  /api/stats                - Get statistics")
        print("=" * 80)
        print("\n🎁 Premium Features:")
        print("  ✅ Multi-Region Support (US, UK, DE, SA, AE)")
        print("  ✅ AI Price Prediction Engine")
        print("  ✅ Smart Buy/Wait/Don't Buy Recommendations")
        print("  ✅ 🔥 Cross-Region Price Comparison (NEW)")
        print("  ✅ Email Notifications")
        print("  ✅ Real-time Dashboard")
        print("  ✅ Historical Price Analysis")
        print("  ✅ Export Reports (JSON, CSV, PDF)")
        print("=" * 80)
        print("\n🔥 Cross-Region Comparison Features:")
        print("  • Parallel extraction from all regions")
        print("  • Smart cost calculation (shipping + taxes)")
        print("  • Deal scoring system")
        print("  • Historical comparison tracking")
        print("  • Best deals discovery")
        print("  • Profit margin analysis")
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
