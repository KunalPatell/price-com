import requests
from bs4 import BeautifulSoup, Tag
import time
import re
from typing import Dict, Optional, List, Union
import streamlit as st
from urllib.parse import quote_plus
import json
from datetime import datetime
import logging
import random

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PhoneScraper:
    """Class to scrape phone data from Flipkart and Amazon"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def search_flipkart(self, phone_name: str) -> Optional[Dict]:
        """Search and scrape phone data from Flipkart"""
        try:
            # Clean phone name for search
            search_query = quote_plus(phone_name)
            search_url = f"https://www.flipkart.com/search?q={search_query}&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=on&as=off"
            
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # For demo purposes, return realistic mock data based on phone name
            return self._get_mock_flipkart_data(phone_name)
                    
            return None
            
        except Exception as e:
            logger.error(f"Error scraping Flipkart: {e}")
            return None
    
    def search_amazon(self, phone_name: str) -> Optional[Dict]:
        """Search and scrape phone data from Amazon"""
        try:
            # Clean phone name for search
            search_query = quote_plus(phone_name)
            search_url = f"https://www.amazon.in/s?k={search_query}&ref=nb_sb_noss"
            
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # For demo purposes, return realistic mock data based on phone name
            return self._get_mock_amazon_data(phone_name)
                    
            return None
            
        except Exception as e:
            logger.error(f"Error scraping Amazon: {e}")
            return None
    
    def _is_matching_phone(self, search_term: str, product_name: str) -> bool:
        """Check if the product name matches the search term"""
        search_words = search_term.lower().split()
        product_words = product_name.lower()
        
        # At least 2 words should match for phones
        matches = sum(1 for word in search_words if word in product_words)
        return matches >= min(2, len(search_words))
    
    def _extract_price(self, price_text: str) -> float:
        """Extract numeric price from text"""
        # Remove currency symbols and commas
        price_numbers = re.findall(r'[\d,]+', price_text.replace(',', ''))
        if price_numbers:
            try:
                return float(price_numbers[0])
            except:
                pass
        return 0.0
    
    def _extract_rating(self, rating_text: str) -> float:
        """Extract numeric rating from text"""
        rating_match = re.search(r'(\d+\.?\d*)', rating_text)
        if rating_match:
            try:
                rating = float(rating_match.group(1))
                return min(rating, 5.0)  # Cap at 5.0
            except:
                pass
        return 0.0
    
    def _extract_review_count(self, review_text: str) -> int:
        """Extract review count from text"""
        # Look for numbers followed by common review indicators
        review_match = re.search(r'(\d+(?:,\d+)*)', review_text.replace(',', ''))
        if review_match:
            try:
                return int(review_match.group(1))
            except:
                pass
        return 0
    
    def _estimate_specs_from_name(self, product_name: str) -> Dict[str, float]:
        """Estimate specs based on product name patterns"""
        name_lower = product_name.lower()
        
        # Default specs
        specs = {
            'battery': 4000.0,
            'camera': 48.0,
            'storage': 128.0,
            'processor': 2.8
        }
        
        # Battery estimation based on phone series
        if any(series in name_lower for series in ['pro max', 'ultra', 'note']):
            specs['battery'] = 5000.0
        elif any(series in name_lower for series in ['pro', 'plus']):
            specs['battery'] = 4500.0
        
        # Camera estimation
        if 'pro' in name_lower or 'ultra' in name_lower:
            specs['camera'] = 108.0
        elif any(series in name_lower for series in ['15', '14', '13']):
            specs['camera'] = 48.0
        
        # Storage estimation
        if any(storage in name_lower for storage in ['512gb', '512 gb']):
            specs['storage'] = 512.0
        elif any(storage in name_lower for storage in ['256gb', '256 gb']):
            specs['storage'] = 256.0
        elif any(storage in name_lower for storage in ['64gb', '64 gb']):
            specs['storage'] = 64.0
        
        # Processor estimation (simplified)
        if any(series in name_lower for series in ['15 pro', '14 pro', 's24 ultra']):
            specs['processor'] = 3.8
        elif any(series in name_lower for series in ['15', '14', 's24']):
            specs['processor'] = 3.2
        
        return specs
    
    def _get_mock_flipkart_data(self, phone_name: str) -> Optional[Dict]:
        """Generate realistic mock data for Flipkart"""
        try:
            specs = self._estimate_specs_from_name(phone_name)
            
            # Generate realistic price variations
            base_price = self._estimate_base_price(phone_name)
            flipkart_price = base_price + random.randint(-5000, 3000)
            
            # Generate realistic ratings and reviews
            rating = round(random.uniform(3.8, 4.7), 1)
            reviews = random.randint(5000, 50000)
            
            return {
                'name': phone_name,
                'price': max(flipkart_price, 10000),  # Minimum price
                'rating': rating,
                'reviews': reviews,
                'image_url': self._get_mock_image_url(phone_name),
                'platform': 'Flipkart',
                'specs': specs,
                'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        except Exception as e:
            logger.error(f"Error generating Flipkart mock data: {e}")
            return None
    
    def _get_mock_amazon_data(self, phone_name: str) -> Optional[Dict]:
        """Generate realistic mock data for Amazon"""
        try:
            specs = self._estimate_specs_from_name(phone_name)
            
            # Generate realistic price variations
            base_price = self._estimate_base_price(phone_name)
            amazon_price = base_price + random.randint(-3000, 5000)
            
            # Generate realistic ratings and reviews
            rating = round(random.uniform(3.9, 4.6), 1)
            reviews = random.randint(3000, 40000)
            
            return {
                'name': phone_name,
                'price': max(amazon_price, 10000),  # Minimum price
                'rating': rating,
                'reviews': reviews,
                'image_url': self._get_mock_image_url(phone_name),
                'platform': 'Amazon',
                'specs': specs,
                'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        except Exception as e:
            logger.error(f"Error generating Amazon mock data: {e}")
            return None
    
    def _estimate_base_price(self, phone_name: str) -> int:
        """Estimate base price based on phone name"""
        name_lower = phone_name.lower()
        
        # Premium phones
        if any(term in name_lower for term in ['15 pro', '14 pro', 's24 ultra', 'ultra']):
            return 100000
        elif any(term in name_lower for term in ['15', '14', 's24', 'pro']):
            return 70000
        elif any(term in name_lower for term in ['pixel 8', 'oneplus', 'xiaomi']):
            return 50000
        else:
            return 30000
    
    def _get_mock_image_url(self, phone_name: str) -> str:
        """Generate mock image URL for demo purposes"""
        # Return placeholder image URL
        return "https://via.placeholder.com/300x400/007ACC/FFFFFF?text=Phone+Image"

@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_phone_data(phone_name: str) -> Dict:
    """Get phone data from both platforms with caching"""
    scraper = PhoneScraper()
    
    # Add delay between requests to be polite
    flipkart_data = scraper.search_flipkart(phone_name)
    time.sleep(2)  # 2 second delay
    amazon_data = scraper.search_amazon(phone_name)
    
    return {
        'flipkart': flipkart_data,
        'amazon': amazon_data,
        'last_scraped': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

def get_popular_phones() -> List[str]:
    """Return list of popular phone names for selection"""
    return [
        "iPhone 15 Pro",
        "iPhone 15",
        "Samsung Galaxy S24 Ultra",
        "Samsung Galaxy S24",
        "Google Pixel 8 Pro",
        "Google Pixel 8",
        "OnePlus 12",
        "OnePlus 11",
        "Xiaomi 14 Ultra",
        "Xiaomi 13T Pro",
        "Nothing Phone 2",
        "Realme GT 5 Pro"
    ]