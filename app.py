"""
ultimate_amazon_price_tracker_enhanced.py - Ù†Ø¸Ø§Ù… ØªØªØ¨Ø¹ Ø£Ø³Ø¹Ø§Ø± Amazon Ø§Ù„Ø§Ø­ØªØ±Ø§ÙÙŠ
Ø§Ù„Ø¥ØµØ¯Ø§Ø±: 24.0 SMART BUY EDITION

Ù…ÙŠØ²Ø§Øª Ø¬Ø¯ÙŠØ¯Ø©:
âœ… Ù†Ø¸Ø§Ù… ØªÙˆØµÙŠØ§Øª Ø§Ù„Ø´Ø±Ø§Ø¡ Ø§Ù„Ø°ÙƒÙŠ (Ø§Ø´ØªØ±Ù Ø§Ù„Ø¢Ù† / Ø§Ù†ØªØ¸Ø± / Ù„Ø§ ØªØ´ØªØ±Ù)
âœ… ØªØ­Ù„ÙŠÙ„ Ù…ØªÙ‚Ø¯Ù… Ù„Ù„Ø£Ø³Ø¹Ø§Ø± (30 ÙŠÙˆÙ…Ø§Ù‹)
âœ… ÙƒØ´Ù Ø§Ù„Ø®ØµÙˆÙ…Ø§Øª Ø§Ù„ÙˆÙ‡Ù…ÙŠØ©
âœ… Ù…Ø¤Ø´Ø±Ø§Øª Ø¨ØµØ±ÙŠØ© ÙˆØ§Ø¶Ø­Ø©
âœ… ØªØ­Ù„ÙŠÙ„ Ø§Ù„Ø§ØªØ¬Ø§Ù‡ Ø§Ù„Ø³Ø¹Ø±ÙŠ
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

VERSION = "24.0 SMART BUY EDITION"
BUILD_DATE = datetime.now().strftime("%Y-%m-%d")

# Multi-Region Configuration
REGION_CONFIGS = {
    'US': {
        'domain': 'amazon.com',
        'currency': 'USD',
        'currency_symbol': '$',
        'name': 'United States',
        'flag': 'ðŸ‡ºðŸ‡¸'
    },
    'UK': {
        'domain': 'amazon.co.uk',
        'currency': 'GBP',
        'currency_symbol': 'Â£',
        'name': 'United Kingdom',
        'flag': 'ðŸ‡¬ðŸ‡§'
    },
    'DE': {
        'domain': 'amazon.de',
        'currency': 'EUR',
        'currency_symbol': 'â‚¬',
        'name': 'Germany',
        'flag': 'ðŸ‡©ðŸ‡ª'
    },
    'SA': {
        'domain': 'amazon.sa',
        'currency': 'SAR',
        'currency_symbol': 'Ø±.Ø³',
        'name': 'Saudi Arabia',
        'flag': 'ðŸ‡¸ðŸ‡¦'
    },
    'AE': {
        'domain': 'amazon.ae',
        'currency': 'AED',
        'currency_symbol': 'Ø¯.Ø¥',
        'name': 'UAE',
        'flag': 'ðŸ‡¦ðŸ‡ª'
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

# ðŸ†• SMART BUY RECOMMENDATION CONFIG
SMART_BUY_CONFIG = {
    'enabled': True,
    'analysis_window_days': 30,
    'buy_now_threshold': 25.0,  # Ø®ØµÙ… â‰¥ 25%
    'wait_threshold': 10.0,      # Ø®ØµÙ… Ø¨ÙŠÙ† 10-24%
    'min_data_points': 3,        # Ø§Ù„Ø­Ø¯ Ø§Ù„Ø£Ø¯Ù†Ù‰ Ù…Ù† Ø§Ù„Ù†Ù‚Ø§Ø· Ù„Ù„ØªØ­Ù„ÙŠÙ„
    'price_spike_threshold': 15.0  # ÙƒØ´Ù Ø±ÙØ¹ Ø§Ù„Ø³Ø¹Ø± Ø§Ù„Ù…ÙØ§Ø¬Ø¦
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
    'interval': 3600,
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
        logging.FileHandler('amazon_tracker_enhanced.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

print("=" * 80)
print("ðŸŽ¯ ULTIMATE AMAZON PRICE TRACKER - SMART BUY EDITION")
print(f"ðŸ“¦ Version: {VERSION} | Build: {BUILD_DATE}")
print("=" * 80)
print("\nðŸŒŸ PREMIUM FEATURES INITIALIZED:")
print("   âœ… Multi-Region Support (US, UK, DE, SA, AE)")
print("   âœ… AI-Powered Price Prediction")
print("   âœ… ðŸ†• Smart Buy Recommendations (Buy/Wait/Don't Buy)")
print("   âœ… Advanced Analytics Dashboard")
print("   âœ… Real-time Notifications (Email, Telegram, Push)")
print("   âœ… Smart Extraction System (3-Layer Fallback)")
print("   âœ… Historical Price Analysis")
print("   âœ… Fake Discount Detection")
print("   âœ… Trend Detection & Forecasting")
print("=" * 80)

# ==================== ENHANCED DATABASE ====================

class UltimateDatabaseManager:
    """Enterprise-Grade Database Manager with Smart Buy Analytics"""
    
    def __init__(self, db_path: str = "ultimate_tracker_enhanced.db"):
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
        
        # ============ ðŸ†• Smart Buy Recommendations Table ============
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS smart_buy_recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                asin TEXT NOT NULL,
                recommendation TEXT NOT NULL,
                signal_color TEXT NOT NULL,
                current_price REAL NOT NULL,
                avg_price_30d REAL,
                min_price_30d REAL,
                max_price_30d REAL,
                real_discount_percentage REAL,
                confidence_score REAL,
                analysis_details TEXT,
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
            'CREATE INDEX IF NOT EXISTS idx_smart_buy_asin ON smart_buy_recommendations(asin, created_at DESC)'
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
        
        conn.commit()
        logger.info("âœ… Database initialized successfully with Smart Buy features")
    
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
            logger.error(f"âŒ Error saving product: {e}")
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
            logger.error(f"âŒ Error getting products: {e}")
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
            logger.error(f"âŒ Error getting price history: {e}")
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
            logger.error(f"âŒ Error saving prediction: {e}")
            return False
    
    def save_smart_buy_recommendation(self, asin: str, recommendation_data: Dict) -> bool:
        """ðŸ†• Save smart buy recommendation"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO smart_buy_recommendations 
                 (asin, recommendation, signal_color, current_price, avg_price_30d,
                  min_price_30d, max_price_30d, real_discount_percentage, 
                  confidence_score, analysis_details)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                asin,
                recommendation_data['recommendation'],
                recommendation_data['signal_color'],
                recommendation_data['current_price'],
                recommendation_data.get('avg_price_30d'),
                recommendation_data.get('min_price_30d'),
                recommendation_data.get('max_price_30d'),
                recommendation_data.get('real_discount_percentage', 0.0),
                recommendation_data.get('confidence_score', 0.0),
                json.dumps(recommendation_data.get('analysis_details', {}))
            ))
            
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"âŒ Error saving smart buy recommendation: {e}")
            return False
    
    def get_latest_smart_buy_recommendation(self, asin: str) -> Optional[Dict]:
        """ðŸ†• Get latest smart buy recommendation"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM smart_buy_recommendations 
                WHERE asin = ? 
                ORDER BY created_at DESC 
                LIMIT 1
            ''', (asin,))
            
            row = cursor.fetchone()
            if row:
                columns = [desc[0] for desc in cursor.description]
                recommendation = dict(zip(columns, row))
                if recommendation.get('analysis_details'):
                    try:
                        recommendation['analysis_details'] = json.loads(recommendation['analysis_details'])
                    except:
                        recommendation['analysis_details'] = {}
                return recommendation
            return None
        except Exception as e:
            logger.error(f"âŒ Error getting smart buy recommendation: {e}")
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
            logger.error(f"âŒ Error logging event: {e}")

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
        
        logger.info("âœ… Smart Extraction Engine initialized")
    
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
        logger.info(f"ðŸ” Layer 1: Direct extraction for {asin} ({region_config['flag']} {region})")
        result = self._direct_extract(url, asin, region, region_config)
        if result:
            return result, "direct"
        
        # Layer 2: ScraperAPI
        if SCRAPERAPI_CONFIG['enabled']:
            logger.info(f"ðŸ” Layer 2: ScraperAPI extraction for {asin}")
            result = self._scraperapi_extract(url, asin, region, region_config)
            if result:
                return result, "scraperapi"
        
        # Layer 3: Fallback
        logger.info(f"ðŸ” Layer 3: Fallback extraction for {asin}")
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

# ==================== ðŸ†• SMART BUY ANALYZER ====================

class SmartBuyAnalyzer:
    """ðŸ†• Ù†Ø¸Ø§Ù… Ø§Ù„ØªÙˆØµÙŠØ§Øª Ø§Ù„Ø°ÙƒÙŠØ© Ù„Ù„Ø´Ø±Ø§Ø¡"""
    
    def __init__(self, db_manager: UltimateDatabaseManager):
        self.db = db_manager
        self.config = SMART_BUY_CONFIG
        logger.info("âœ… Smart Buy Analyzer initialized")
    
    def analyze_product(self, asin: str, current_price: float) -> Optional[Dict]:
        """
        ØªØ­Ù„ÙŠÙ„ Ø´Ø§Ù…Ù„ Ù„Ù„Ù…Ù†ØªØ¬ ÙˆØ¥Ø¹Ø·Ø§Ø¡ ØªÙˆØµÙŠØ© (Ø§Ø´ØªØ±Ù Ø§Ù„Ø¢Ù† / Ø§Ù†ØªØ¸Ø± / Ù„Ø§ ØªØ´ØªØ±Ù)
        """
        if not self.config['enabled']:
            return None
        
        try:
            # Ø§Ù„Ø­ØµÙˆÙ„ Ø¹Ù„Ù‰ Ø§Ù„ØªØ§Ø±ÙŠØ® Ø§Ù„Ø³Ø¹Ø±ÙŠ
            history = self.db.get_price_history(asin, days=self.config['analysis_window_days'])
            
            if len(history) < self.config['min_data_points']:
                # Ø¨ÙŠØ§Ù†Ø§Øª ØºÙŠØ± ÙƒØ§ÙÙŠØ© - ØªÙˆØµÙŠØ© Ø­Ø°Ø±Ø©
                return self._create_insufficient_data_recommendation(asin, current_price)
            
            # Ø§Ø³ØªØ®Ø±Ø§Ø¬ Ø§Ù„Ø£Ø³Ø¹Ø§Ø±
            prices = [h['price'] for h in history]
            
            # Ø­Ø³Ø§Ø¨ Ø§Ù„Ù…Ø¤Ø´Ø±Ø§Øª Ø§Ù„Ø¥Ø­ØµØ§Ø¦ÙŠØ©
            avg_price = statistics.mean(prices)
            min_price = min(prices)
            max_price = max(prices)
            median_price = statistics.median(prices)
            
            # Ø­Ø³Ø§Ø¨ Ø§Ù„Ø®ØµÙ… Ø§Ù„Ø­Ù‚ÙŠÙ‚ÙŠ Ù…Ù‚Ø§Ø±Ù†Ø© Ø¨Ø§Ù„Ù…ØªÙˆØ³Ø·
            real_discount_vs_avg = ((avg_price - current_price) / avg_price) * 100 if avg_price > 0 else 0
            
            # Ø­Ø³Ø§Ø¨ Ø§Ù„Ø®ØµÙ… Ù…Ù‚Ø§Ø±Ù†Ø© Ø¨Ø£Ù‚Ù„ Ø³Ø¹Ø±
            discount_vs_min = ((current_price - min_price) / min_price) * 100 if min_price > 0 else 0
            
            # ÙƒØ´Ù Ø±ÙØ¹ Ø§Ù„Ø³Ø¹Ø± Ø§Ù„Ù…ÙØ§Ø¬Ø¦
            recent_prices = prices[-5:] if len(prices) >= 5 else prices
            recent_avg = statistics.mean(recent_prices)
            price_spike = ((current_price - recent_avg) / recent_avg) * 100 if recent_avg > 0 else 0
            
            # ØªØ­Ù„ÙŠÙ„ Ø§Ù„Ø§ØªØ¬Ø§Ù‡
            trend = self._analyze_trend(prices)
            
            # Ø­Ø³Ø§Ø¨ Ø¯Ø±Ø¬Ø© Ø§Ù„Ø«Ù‚Ø©
            confidence = self._calculate_confidence(len(history), prices)
            
            # ðŸŽ¯ Ù‚Ø±Ø§Ø± Ø§Ù„ØªÙˆØµÙŠØ©
            recommendation = self._make_recommendation(
                current_price=current_price,
                avg_price=avg_price,
                min_price=min_price,
                max_price=max_price,
                real_discount_vs_avg=real_discount_vs_avg,
                discount_vs_min=discount_vs_min,
                price_spike=price_spike,
                trend=trend
            )
            
            # Ø¥Ù†Ø´Ø§Ø¡ Ø§Ù„ØªÙˆØµÙŠØ© Ø§Ù„Ù†Ù‡Ø§Ø¦ÙŠØ©
            result = {
                'asin': asin,
                'recommendation': recommendation['action'],
                'signal_color': recommendation['color'],
                'current_price': current_price,
                'avg_price_30d': round(avg_price, 2),
                'min_price_30d': round(min_price, 2),
                'max_price_30d': round(max_price, 2),
                'median_price_30d': round(median_price, 2),
                'real_discount_percentage': round(real_discount_vs_avg, 2),
                'discount_vs_min': round(discount_vs_min, 2),
                'price_spike_detected': abs(price_spike) > self.config['price_spike_threshold'],
                'price_spike_percentage': round(price_spike, 2),
                'trend': trend,
                'confidence_score': round(confidence, 2),
                'analysis_details': {
                    'data_points': len(history),
                    'analysis_window_days': self.config['analysis_window_days'],
                    'reasoning': recommendation['reasoning'],
                    'tips': recommendation['tips']
                }
            }
            
            # Ø­ÙØ¸ Ø§Ù„ØªÙˆØµÙŠØ© ÙÙŠ Ù‚Ø§Ø¹Ø¯Ø© Ø§Ù„Ø¨ÙŠØ§Ù†Ø§Øª
            self.db.save_smart_buy_recommendation(asin, result)
            
            logger.info(f"âœ… Smart Buy Analysis for {asin}: {recommendation['action']} ({recommendation['color']})")
            
            return result
            
        except Exception as e:
            logger.error(f"âŒ Smart Buy Analysis error for {asin}: {e}")
            return None
    
    def _make_recommendation(self, current_price: float, avg_price: float, 
                            min_price: float, max_price: float,
                            real_discount_vs_avg: float, discount_vs_min: float,
                            price_spike: float, trend: str) -> Dict:
        """
        Ø§ØªØ®Ø§Ø° Ù‚Ø±Ø§Ø± Ø§Ù„ØªÙˆØµÙŠØ© Ø¨Ù†Ø§Ø¡Ù‹ Ø¹Ù„Ù‰ Ø§Ù„ØªØ­Ù„ÙŠÙ„
        """
        
        # ðŸŸ¢ Ø§Ø´ØªØ±Ù Ø§Ù„Ø¢Ù† (Ø³Ø¹Ø± Ø¬ÙŠØ¯)
        if (current_price <= min_price or 
            real_discount_vs_avg >= self.config['buy_now_threshold'] or
            (real_discount_vs_avg >= 20 and trend == 'stable')):
            
            return {
                'action': 'buy_now',
                'color': 'green',
                'reasoning': f'Ø®ØµÙ… Ø­Ù‚ÙŠÙ‚ÙŠ {abs(real_discount_vs_avg):.1f}% Ù…Ù‚Ø§Ø±Ù†Ø© Ø¨Ù…ØªÙˆØ³Ø· 30 ÙŠÙˆÙ…Ø§Ù‹',
                'tips': [
                    'âœ… Ø§Ù„Ø³Ø¹Ø± Ø£Ù‚Ù„ Ù…Ù† Ø§Ù„Ù…ØªÙˆØ³Ø· Ø¨Ù†Ø³Ø¨Ø© ÙƒØ¨ÙŠØ±Ø©',
                    'âœ… ÙØ±ØµØ© Ø¬ÙŠØ¯Ø© Ù„Ù„Ø´Ø±Ø§Ø¡',
                    'âš¡ Ù‚Ø¯ Ù„Ø§ ÙŠØ³ØªÙ…Ø± Ù‡Ø°Ø§ Ø§Ù„Ø³Ø¹Ø± Ø·ÙˆÙŠÙ„Ø§Ù‹'
                ]
            }
        
        # ðŸ”´ Ù„Ø§ ØªØ´ØªØ±Ù (Ø³Ø¹Ø± Ø³ÙŠØ¦)
        elif (real_discount_vs_avg < self.config['wait_threshold'] or
              current_price > avg_price * 1.1 or
              abs(price_spike) > self.config['price_spike_threshold']):
            
            reasons = []
            if real_discount_vs_avg < self.config['wait_threshold']:
                reasons.append(f'Ø§Ù„Ø®ØµÙ… Ø¶Ø¹ÙŠÙ ({abs(real_discount_vs_avg):.1f}%)')
            if current_price > avg_price * 1.1:
                reasons.append('Ø§Ù„Ø³Ø¹Ø± Ø£Ø¹Ù„Ù‰ Ù…Ù† Ø§Ù„Ù…ØªÙˆØ³Ø·')
            if abs(price_spike) > self.config['price_spike_threshold']:
                reasons.append(f'Ø§Ø±ØªÙØ§Ø¹ Ù…ÙØ§Ø¬Ø¦ ÙÙŠ Ø§Ù„Ø³Ø¹Ø± ({abs(price_spike):.1f}%)')
            
            return {
                'action': 'dont_buy',
                'color': 'red',
                'reasoning': ' â€¢ '.join(reasons),
                'tips': [
                    'â›” Ø§Ù„Ø³Ø¹Ø± Ø§Ù„Ø­Ø§Ù„ÙŠ Ù…Ø±ØªÙØ¹',
                    'â° Ø§Ù†ØªØ¸Ø± ØªØ®ÙÙŠØ¶Ø§Ù‹ Ø£ÙØ¶Ù„',
                    'ðŸ“Š Ù‚Ø¯ ÙŠÙ†Ø®ÙØ¶ Ø§Ù„Ø³Ø¹Ø± Ù‚Ø±ÙŠØ¨Ø§Ù‹'
                ]
            }
        
        # ðŸŸ¡ Ø§Ù†ØªØ¸Ø± (Ø³Ø¹Ø± Ù…Ù‚Ø¨ÙˆÙ„)
        else:
            return {
                'action': 'wait',
                'color': 'yellow',
                'reasoning': f'Ø®ØµÙ… Ù…ØªÙˆØ³Ø· ({abs(real_discount_vs_avg):.1f}%)',
                'tips': [
                    'â³ Ø§Ù„Ø³Ø¹Ø± Ù…Ù‚Ø¨ÙˆÙ„ Ù„ÙƒÙ† Ù„ÙŠØ³ Ø§Ù„Ø£ÙØ¶Ù„',
                    'ðŸ“ˆ Ø±Ø§Ù‚Ø¨ Ø§Ù„Ø³Ø¹Ø± Ù„Ø£ÙŠØ§Ù… Ù‚Ø§Ø¯Ù…Ø©',
                    'ðŸ’¡ Ù‚Ø¯ ØªØ­ØµÙ„ Ø¹Ù„Ù‰ ÙØ±ØµØ© Ø£ÙØ¶Ù„'
                ]
            }
    
    def _analyze_trend(self, prices: List[float]) -> str:
        """ØªØ­Ù„ÙŠÙ„ Ø§ØªØ¬Ø§Ù‡ Ø§Ù„Ø³Ø¹Ø±"""
        if len(prices) < 3:
            return 'stable'
        
        # Ø­Ø³Ø§Ø¨ Ø§Ù„Ø§ØªØ¬Ø§Ù‡ Ø¨Ø§Ø³ØªØ®Ø¯Ø§Ù… Ø§Ù„Ù…ØªÙˆØ³Ø·Ø§Øª Ø§Ù„Ù…ØªØ­Ø±ÙƒØ©
        recent = statistics.mean(prices[-5:]) if len(prices) >= 5 else statistics.mean(prices[-3:])
        older = statistics.mean(prices[:5]) if len(prices) >= 5 else statistics.mean(prices[:3])
        
        change = ((recent - older) / older) * 100 if older > 0 else 0
        
        if change < -5:
            return 'decreasing'
        elif change > 5:
            return 'increasing'
        else:
            return 'stable'
    
    def _calculate_confidence(self, data_points: int, prices: List[float]) -> float:
        """Ø­Ø³Ø§Ø¨ Ø¯Ø±Ø¬Ø© Ø§Ù„Ø«Ù‚Ø© ÙÙŠ Ø§Ù„ØªÙˆØµÙŠØ©"""
        # ÙƒÙ„Ù…Ø§ Ø²Ø§Ø¯Øª Ù†Ù‚Ø§Ø· Ø§Ù„Ø¨ÙŠØ§Ù†Ø§ØªØŒ Ø²Ø§Ø¯Øª Ø§Ù„Ø«Ù‚Ø©
        data_confidence = min(100, (data_points / 30) * 100)
        
        # Ø§Ø³ØªÙ‚Ø±Ø§Ø± Ø§Ù„Ø³Ø¹Ø± ÙŠØ²ÙŠØ¯ Ø§Ù„Ø«Ù‚Ø©
        if len(prices) >= 5:
            std_dev = statistics.stdev(prices)
            avg_price = statistics.mean(prices)
            stability = 100 - min(100, (std_dev / avg_price) * 100) if avg_price > 0 else 50
        else:
            stability = 50
        
        # Ø§Ù„Ù…ØªÙˆØ³Ø· Ø§Ù„Ù…Ø±Ø¬Ø­
        confidence = (data_confidence * 0.6) + (stability * 0.4)
        
        return confidence
    
    def _create_insufficient_data_recommendation(self, asin: str, current_price: float) -> Dict:
        """ØªÙˆØµÙŠØ© ÙÙŠ Ø­Ø§Ù„Ø© Ø§Ù„Ø¨ÙŠØ§Ù†Ø§Øª ØºÙŠØ± Ø§Ù„ÙƒØ§ÙÙŠØ©"""
        return {
            'asin': asin,
            'recommendation': 'wait',
            'signal_color': 'yellow',
            'current_price': current_price,
            'avg_price_30d': None,
            'min_price_30d': None,
            'max_price_30d': None,
            'median_price_30d': None,
            'real_discount_percentage': 0.0,
            'discount_vs_min': 0.0,
            'price_spike_detected': False,
            'price_spike_percentage': 0.0,
            'trend': 'unknown',
            'confidence_score': 0.0,
            'analysis_details': {
                'data_points': 0,
                'analysis_window_days': self.config['analysis_window_days'],
                'reasoning': 'Ø¨ÙŠØ§Ù†Ø§Øª ØºÙŠØ± ÙƒØ§ÙÙŠØ© Ù„Ù„ØªØ­Ù„ÙŠÙ„',
                'tips': [
                    'âš ï¸ Ù„Ø§ ØªÙˆØ¬Ø¯ Ø¨ÙŠØ§Ù†Ø§Øª ØªØ§Ø±ÙŠØ®ÙŠØ© ÙƒØ§ÙÙŠØ©',
                    'â° Ø§Ù†ØªØ¸Ø± Ø¹Ø¯Ø© Ø£ÙŠØ§Ù… Ù„ØªØ¬Ù…ÙŠØ¹ Ø§Ù„Ø¨ÙŠØ§Ù†Ø§Øª',
                    'ðŸ” Ø±Ø§Ù‚Ø¨ Ø§Ù„Ø³Ø¹Ø± Ø¨Ø´ÙƒÙ„ Ø¯ÙˆØ±ÙŠ'
                ]
            }
        }

# ==================== AI PRICE PREDICTOR ====================

class AIPricePredictor:
    """AI-Powered Price Prediction Engine"""
    
    def __init__(self, db_manager: UltimateDatabaseManager):
        self.db = db_manager
        logger.info("âœ… AI Price Predictor initialized")
    
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
            logger.error(f"âŒ Prediction error for {asin}: {e}")
            return None

# ==================== NOTIFICATION MANAGER ====================

class NotificationManager:
    """Multi-Channel Notification System"""
    
    def __init__(self):
        self.email_config = NOTIFICATION_CONFIG['email']
        logger.info("âœ… Notification Manager initialized")
    
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
            
            subject = f"ðŸ”” Price Drop Alert: {product['product_name'][:50]}..."
            
            html_body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; color: white;">
                    <h1 style="margin: 0;">ðŸ”” Price Drop Alert!</h1>
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
                            ðŸ›’ View on Amazon
                        </a>
                    </div>
                    
                    <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0;">
                        <p style="margin: 0; color: #856404;"><strong>âš¡ Act Fast!</strong> Prices can change at any time.</p>
                    </div>
                </div>
                
                <div style="background: #333; color: white; padding: 20px; text-align: center; font-size: 12px;">
                    <p>Ultimate Amazon Price Tracker v{VERSION}</p>
                    <p>Powered by AI â€¢ Real-time Monitoring â€¢ Multi-Region Support</p>
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
            
            logger.info(f"âœ… Email alert sent for {product['asin']}")
            return True
            
        except Exception as e:
            logger.error(f"âŒ Email alert failed: {e}")
            return False

# ==================== FLASK APP ====================

app = Flask(__name__)

class UltimateTrackerSystem:
    """Ultimate Amazon Price Tracker System with Smart Buy Recommendations"""
    
    def __init__(self):
        self.db = UltimateDatabaseManager()
        self.extractor = SmartExtractionEngine()
        self.predictor = AIPricePredictor(self.db)
        self.smart_buy = SmartBuyAnalyzer(self.db)  # ðŸ†•
        self.notifier = NotificationManager()
        self.setup_routes()
        logger.info("âœ… Ultimate Tracker System initialized with Smart Buy features")
    
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
                
                # ðŸ†• Generate Smart Buy Recommendation
                smart_buy_rec = self.smart_buy.analyze_product(
                    product_data['asin'], 
                    product_data['current_price']
                )
                
                return jsonify({
                    'status': 'success',
                    'product': product_data,
                    'prediction': prediction,
                    'smart_buy': smart_buy_rec,  # ðŸ†•
                    'extraction_method': method
                })
                
            except Exception as e:
                logger.error(f"Error adding product: {e}")
                return jsonify({'status': 'error', 'message': str(e)}), 500
        
        @app.route('/api/products')
        def get_products():
            region = request.args.get('region')
            products = self.db.get_products(region=region)
            
            # ðŸ†• Ø¥Ø¶Ø§ÙØ© Ø§Ù„ØªÙˆØµÙŠØ§Øª Ù„ÙƒÙ„ Ù…Ù†ØªØ¬
            for product in products:
                rec = self.db.get_latest_smart_buy_recommendation(product['asin'])
                product['smart_buy'] = rec
            
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
        
        @app.route('/api/product/<asin>/smart-buy')
        def get_smart_buy(asin):
            """ðŸ†• Get smart buy recommendation for a product"""
            try:
                # Get current product
                products = self.db.get_products()
                product = next((p for p in products if p['asin'] == asin), None)
                
                if not product:
                    return jsonify({'status': 'error', 'message': 'Product not found'}), 404
                
                # Generate fresh recommendation
                recommendation = self.smart_buy.analyze_product(asin, product['current_price'])
                
                if recommendation:
                    return jsonify({'status': 'success', 'recommendation': recommendation})
                else:
                    return jsonify({'status': 'error', 'message': 'Analysis failed'}), 400
                    
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
                
                # ðŸ†• Smart Buy Stats
                cursor.execute('SELECT COUNT(*) FROM smart_buy_recommendations WHERE signal_color = "green"')
                buy_now_count = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(*) FROM smart_buy_recommendations WHERE signal_color = "red"')
                dont_buy_count = cursor.fetchone()[0]
                
                return jsonify({
                    'status': 'success',
                    'stats': {
                        'total_products': total_products,
                        'regions_count': regions_count,
                        'avg_discount': round(avg_discount, 2),
                        'alerts_today': alerts_today,
                        'buy_now_recommendations': buy_now_count,
                        'dont_buy_recommendations': dont_buy_count
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
                    'smart_buy_recommendations': SMART_BUY_CONFIG['enabled'],  # ðŸ†•
                    'notifications': NOTIFICATION_CONFIG['email']['enabled'],
                    'analytics': ANALYTICS_CONFIG['enabled']
                }
            })

# ==================== ENHANCED DASHBOARD TEMPLATE ====================

DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ðŸŽ¯ Ultimate Amazon Price Tracker - Smart Buy Edition</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1600px; margin: 0 auto; }
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
        
        /* ðŸ†• Smart Buy Signal Badges */
        .signal-badge {
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: bold;
            display: inline-block;
            font-size: 0.9rem;
        }
        .signal-green {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            color: white;
        }
        .signal-yellow {
            background: linear-gradient(135deg, #f7b733 0%, #fc4a1a 100%);
            color: white;
        }
        .signal-red {
            background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
            color: white;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
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
            text-align: right;
        }
        .products-table td {
            padding: 15px;
            border-bottom: 1px solid #e0e0e0;
            text-align: right;
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
        
        /* ðŸ†• Smart Buy Recommendation Card */
        .smart-buy-card {
            background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
            padding: 20px;
            border-radius: 15px;
            margin-top: 15px;
            border: 3px solid transparent;
        }
        .smart-buy-card.green-border { border-color: #38ef7d; }
        .smart-buy-card.yellow-border { border-color: #f7b733; }
        .smart-buy-card.red-border { border-color: #eb3349; }
        
        .recommendation-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 15px;
        }
        
        .recommendation-icon {
            font-size: 3rem;
        }
        
        .recommendation-details {
            background: white;
            padding: 15px;
            border-radius: 10px;
            margin-top: 10px;
        }
        
        .tips-list {
            list-style: none;
            padding: 0;
        }
        .tips-list li {
            padding: 8px;
            margin: 5px 0;
            background: #f8f9fa;
            border-radius: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>ðŸŽ¯ Ultimate Amazon Price Tracker</h1>
            <p style="color: #666; margin: 10px 0;">AI-Powered â€¢ Multi-Region â€¢ Smart Buy Recommendations</p>
            <span class="version-badge">v''' + VERSION + '''</span>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Ø¥Ø¬Ù…Ø§Ù„ÙŠ Ø§Ù„Ù…Ù†ØªØ¬Ø§Øª</div>
                <div class="stat-value" id="totalProducts">0</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Ø§Ù„Ù…Ù†Ø§Ø·Ù‚ Ø§Ù„Ù…ØªØªØ¨Ø¹Ø©</div>
                <div class="stat-value" id="regionsCount">0</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Ù…ØªÙˆØ³Ø· Ø§Ù„Ø®ØµÙ…</div>
                <div class="stat-value" id="avgDiscount">0%</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">ðŸŸ¢ Ø§Ø´ØªØ±Ù Ø§Ù„Ø¢Ù†</div>
                <div class="stat-value" id="buyNowCount">0</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">ðŸ”´ Ù„Ø§ ØªØ´ØªØ±Ù</div>
                <div class="stat-value" id="dontBuyCount">0</div>
            </div>
        </div>

        <div class="main-content">
            <div class="sidebar">
                <h2 style="margin-bottom: 20px; color: #333;">Ø¥Ø¶Ø§ÙØ© Ù…Ù†ØªØ¬</h2>
                
                <div class="add-product-section">
                    <input type="url" id="productUrl" class="input-field" 
                           placeholder="Ø§Ù„ØµÙ‚ Ø±Ø§Ø¨Ø· Ø§Ù„Ù…Ù†ØªØ¬ Ù…Ù† Amazon...">
                    <button class="btn-primary" onclick="addProduct()">
                        ðŸ” ØªØªØ¨Ø¹ Ø§Ù„Ù…Ù†ØªØ¬
                    </button>
                </div>
                
                <div id="loading" class="loading">
                    <div class="spinner"></div>
                    <p>Ø¬Ø§Ø±ÙŠ ØªØ­Ù„ÙŠÙ„ Ø§Ù„Ù…Ù†ØªØ¬...</p>
                </div>
                
                <div id="result" class="result-box"></div>
                
                <div style="margin-top: 30px;">
                    <h3 style="margin-bottom: 15px; color: #333;">ðŸŒ ØªØµÙÙŠØ© Ø­Ø³Ø¨ Ø§Ù„Ù…Ù†Ø·Ù‚Ø©</h3>
                    <div class="region-selector" id="regionSelector"></div>
                </div>
            </div>
            
            <div class="products-panel">
                <h2 style="margin-bottom: 20px; color: #333;">ðŸ“¦ Ø§Ù„Ù…Ù†ØªØ¬Ø§Øª Ø§Ù„Ù…ØªØªØ¨Ø¹Ø©</h2>
                <div style="max-height: 700px; overflow-y: auto;">
                    <table class="products-table">
                        <thead>
                            <tr>
                                <th>Ø§Ù„Ù…Ù†ØªØ¬</th>
                                <th>Ø§Ù„Ù…Ù†Ø·Ù‚Ø©</th>
                                <th>Ø§Ù„Ø³Ø¹Ø±</th>
                                <th>Ø§Ù„Ø®ØµÙ…</th>
                                <th>ðŸŽ¯ Ø§Ù„ØªÙˆØµÙŠØ©</th>
                                <th>Ø§Ù„ØªÙ†Ø¨Ø¤</th>
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
                    document.getElementById('buyNowCount').textContent = data.stats.buy_now_recommendations || 0;
                    document.getElementById('dontBuyCount').textContent = data.stats.dont_buy_recommendations || 0;
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
                            <div style="font-size: 1.5rem;">ðŸŒ</div>
                            <div style="font-size: 0.8rem; margin-top: 5px;">Ø§Ù„ÙƒÙ„</div>
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
                        tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; padding: 40px;">Ù„Ù… ÙŠØªÙ… ØªØªØ¨Ø¹ Ø£ÙŠ Ù…Ù†ØªØ¬Ø§Øª Ø¨Ø¹Ø¯. Ø£Ø¶Ù ÙˆØ§Ø­Ø¯Ø§Ù‹ Ø£Ø¹Ù„Ø§Ù‡!</td></tr>';
                        return;
                    }
                    
                    tbody.innerHTML = data.products.map(p => {
                        let signalHTML = '';
                        if (p.smart_buy) {
                            const signal = p.smart_buy;
                            let signalClass = 'signal-' + signal.signal_color;
                            let signalText = '';
                            let signalIcon = '';
                            
                            if (signal.recommendation === 'buy_now') {
                                signalText = 'Ø§Ø´ØªØ±Ù Ø§Ù„Ø¢Ù†';
                                signalIcon = 'ðŸŸ¢';
                            } else if (signal.recommendation === 'wait') {
                                signalText = 'Ø§Ù†ØªØ¸Ø±';
                                signalIcon = 'ðŸŸ¡';
                            } else {
                                signalText = 'Ù„Ø§ ØªØ´ØªØ±Ù';
                                signalIcon = 'ðŸ”´';
                            }
                            
                            signalHTML = `
                                <span class="signal-badge ${signalClass}">${signalIcon} ${signalText}</span>
                                <div style="font-size: 0.75rem; margin-top: 5px; color: #666;">
                                    ${signal.real_discount_percentage > 0 ? 
                                        `Ø®ØµÙ… Ø­Ù‚ÙŠÙ‚ÙŠ: ${signal.real_discount_percentage.toFixed(1)}%` : 
                                        'Ù„Ø§ ÙŠÙˆØ¬Ø¯ Ø®ØµÙ… Ø­Ù‚ÙŠÙ‚ÙŠ'}
                                </div>
                            `;
                        } else {
                            signalHTML = '<span style="color: #999;">Ù‚ÙŠØ¯ Ø§Ù„ØªØ­Ù„ÙŠÙ„...</span>';
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
                                    ${signalHTML}
                                </td>
                                <td>
                                    <button onclick="showDetails('${p.asin}')" style="padding: 5px 15px; background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; border: none; border-radius: 5px; cursor: pointer;">
                                        ðŸ“Š Ø§Ù„ØªÙØ§ØµÙŠÙ„
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
                alert('Ø§Ù„Ø±Ø¬Ø§Ø¡ Ø¥Ø¯Ø®Ø§Ù„ Ø±Ø§Ø¨Ø· Ø§Ù„Ù…Ù†ØªØ¬');
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
                    const smartBuy = data.smart_buy;
                    
                    let smartBuyHTML = '';
                    if (smartBuy) {
                        let borderClass = smartBuy.signal_color + '-border';
                        let icon = '';
                        let actionText = '';
                        
                        if (smartBuy.recommendation === 'buy_now') {
                            icon = 'ðŸŸ¢';
                            actionText = 'Ø§Ø´ØªØ±Ù Ø§Ù„Ø¢Ù† - Ø³Ø¹Ø± Ù…Ù…ØªØ§Ø²!';
                        } else if (smartBuy.recommendation === 'wait') {
                            icon = 'ðŸŸ¡';
                            actionText = 'Ø§Ù†ØªØ¸Ø± - Ø³Ø¹Ø± Ù…Ù‚Ø¨ÙˆÙ„';
                        } else {
                            icon = 'ðŸ”´';
                            actionText = 'Ù„Ø§ ØªØ´ØªØ±Ù - Ø³Ø¹Ø± Ù…Ø±ØªÙØ¹';
                        }
                        
                        smartBuyHTML = `
                            <div class="smart-buy-card ${borderClass}">
                                <div class="recommendation-header">
                                    <div>
                                        <h3 style="margin: 0; color: #333;">${icon} ${actionText}</h3>
                                        <p style="margin: 5px 0; color: #666; font-size: 0.9rem;">${smartBuy.analysis_details.reasoning}</p>
                                    </div>
                                    <div class="recommendation-icon">${icon}</div>
                                </div>
                                <div class="recommendation-details">
                                    <p><strong>Ø§Ù„Ø³Ø¹Ø± Ø§Ù„Ø­Ø§Ù„ÙŠ:</strong> ${p.currency} ${p.current_price.toFixed(2)}</p>
                                    ${smartBuy.avg_price_30d ? `<p><strong>Ù…ØªÙˆØ³Ø· 30 ÙŠÙˆÙ…:</strong> ${p.currency} ${smartBuy.avg_price_30d.toFixed(2)}</p>` : ''}
                                    ${smartBuy.min_price_30d ? `<p><strong>Ø£Ù‚Ù„ Ø³Ø¹Ø±:</strong> ${p.currency} ${smartBuy.min_price_30d.toFixed(2)}</p>` : ''}
                                    <p><strong>Ø§Ù„Ø®ØµÙ… Ø§Ù„Ø­Ù‚ÙŠÙ‚ÙŠ:</strong> ${smartBuy.real_discount_percentage.toFixed(1)}%</p>
                                    <p><strong>Ø¯Ø±Ø¬Ø© Ø§Ù„Ø«Ù‚Ø©:</strong> ${smartBuy.confidence_score.toFixed(1)}%</p>
                                    <ul class="tips-list">
                                        ${smartBuy.analysis_details.tips.map(tip => `<li>${tip}</li>`).join('')}
                                    </ul>
                                </div>
                            </div>
                        `;
                    }
                    
                    result.className = 'result-box';
                    result.innerHTML = `
                        <h3 style="color: #2e7d32;">âœ… ØªÙ…Øª Ø¥Ø¶Ø§ÙØ© Ø§Ù„Ù…Ù†ØªØ¬ Ø¨Ù†Ø¬Ø§Ø­!</h3>
                        <div style="margin: 15px 0;">
                            <strong>${p.product_name}</strong><br>
                            <div style="margin: 10px 0;">
                                <span style="font-size: 0.9rem; color: #666;">Ø§Ù„Ù…Ù†Ø·Ù‚Ø©: ${p.metadata.region_flag} ${p.region}</span><br>
                                <span style="font-size: 1.2rem; color: #d32f2f; font-weight: bold;">${p.currency} ${p.current_price.toFixed(2)}</span>
                            </div>
                        </div>
                        ${smartBuyHTML}
                        ${data.prediction ? `
                            <div style="background: #e3f2fd; padding: 15px; border-radius: 10px; margin-top: 15px;">
                                <strong>ðŸ”® Ø§Ù„ØªÙ†Ø¨Ø¤ Ø¨Ø§Ù„Ø³Ø¹Ø± (30 ÙŠÙˆÙ…):</strong><br>
                                Ø§Ù„Ø³Ø¹Ø± Ø§Ù„Ù…ØªÙˆÙ‚Ø¹: <strong>${p.currency} ${data.prediction.predicted_price.toFixed(2)}</strong><br>
                                Ø§Ù„Ø§ØªØ¬Ø§Ù‡: <strong>${data.prediction.trend}</strong><br>
                                Ø§Ù„Ø«Ù‚Ø©: <strong>${data.prediction.confidence_score.toFixed(1)}%</strong>
                            </div>
                        ` : ''}
                    `;
                    
                    document.getElementById('productUrl').value = '';
                    setTimeout(() => { loadStats(); loadProducts(); }, 1000);
                } else {
                    result.className = 'result-box error-box';
                    result.innerHTML = `<h3 style="color: #c62828;">âŒ Ø®Ø·Ø£</h3><p>${data.message}</p>`;
                }
            } catch (error) {
                loading.style.display = 'none';
                result.style.display = 'block';
                result.className = 'result-box error-box';
                result.innerHTML = `<h3 style="color: #c62828;">âŒ Ø®Ø·Ø£</h3><p>${error.message}</p>`;
            }
        }

        async function showDetails(asin) {
            try {
                const response = await fetch(`/api/product/${asin}/smart-buy`);
                const data = await response.json();
                
                if (data.status === 'success') {
                    const rec = data.recommendation;
                    let icon = rec.recommendation === 'buy_now' ? 'ðŸŸ¢' : 
                               rec.recommendation === 'wait' ? 'ðŸŸ¡' : 'ðŸ”´';
                    let action = rec.recommendation === 'buy_now' ? 'Ø§Ø´ØªØ±Ù Ø§Ù„Ø¢Ù†' : 
                                rec.recommendation === 'wait' ? 'Ø§Ù†ØªØ¸Ø±' : 'Ù„Ø§ ØªØ´ØªØ±Ù';
                    
                    alert(`${icon} Ø§Ù„ØªÙˆØµÙŠØ©: ${action}\n\n` +
                          `Ø§Ù„Ø³Ø¹Ø± Ø§Ù„Ø­Ø§Ù„ÙŠ: ${rec.current_price}\n` +
                          `Ù…ØªÙˆØ³Ø· 30 ÙŠÙˆÙ…: ${rec.avg_price_30d || 'N/A'}\n` +
                          `Ø§Ù„Ø®ØµÙ… Ø§Ù„Ø­Ù‚ÙŠÙ‚ÙŠ: ${rec.real_discount_percentage.toFixed(1)}%\n` +
                          `Ø§Ù„Ø«Ù‚Ø©: ${rec.confidence_score.toFixed(1)}%\n\n` +
                          `${rec.analysis_details.reasoning}\n\n` +
                          `${rec.analysis_details.tips.join('\n')}`);
                } else {
                    alert('Ù„Ø§ ØªÙˆØ¬Ø¯ Ø¨ÙŠØ§Ù†Ø§Øª ÙƒØ§ÙÙŠØ© Ù„Ù„ØªØ­Ù„ÙŠÙ„');
                }
            } catch (error) {
                alert('Ø®Ø·Ø£ ÙÙŠ Ø¬Ù„Ø¨ Ø§Ù„ØªÙØ§ØµÙŠÙ„');
            }
        }
    </script>
</body>
</html>
'''

# ==================== MAIN ====================

def main():
    print("\n" + "=" * 80)
    print("ðŸš€ STARTING ULTIMATE AMAZON PRICE TRACKER - SMART BUY EDITION")
    print("=" * 80)
    
    try:
        system = UltimateTrackerSystem()
        
        print("\nâœ… System Ready!")
        print(f"ðŸŒ Dashboard: http://localhost:9090")
        print(f"ðŸ“¡ API Endpoints:")
        print(f"   â€¢ POST /api/add-product         - Add new product")
        print(f"   â€¢ GET  /api/products            - Get all products")
        print(f"   â€¢ GET  /api/product/<asin>/smart-buy - Get smart buy recommendation")
        print(f"   â€¢ GET  /api/regions             - Get supported regions")
        print(f"   â€¢ GET  /api/stats               - Get statistics")
        print("=" * 80)
        print("\nðŸŒŸ Premium Features Active:")
        print("   âœ… Multi-Region Support (US, UK, DE, SA, AE)")
        print("   âœ… AI Price Prediction Engine")
        print("   âœ… ðŸ†• Smart Buy Recommendations (Buy/Wait/Don't Buy)")
        print("   âœ… Fake Discount Detection")
        print("   âœ… Email Notifications")
        print("   âœ… Real-time Dashboard")
        print("   âœ… Historical Price Analysis")
        print("=" * 80)
        
        app.run(
            host='0.0.0.0',
            port=9090,
            debug=False,
            threaded=True,
            use_reloader=False
        )
    except KeyboardInterrupt:
        print("\n\nâ¹ï¸ System stopped by user")
    except Exception as e:
        print(f"\nâŒ Unexpected error: {e}")
        traceback.print_exc()
    finally:
        print("\nâœ… System shutdown complete")

if __name__ == '__main__':
    main()
