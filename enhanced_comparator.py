"""
Enhanced E-Commerce Product Comparator with Advanced Features
"""
import requests
import pandas as pd
import numpy as np
from typing import List, Dict, Any
import json
import re
from main import EcomProductComparator

class EnhancedEcomComparator(EcomProductComparator):
    def __init__(self, serpapi_key: str):
        super().__init__(serpapi_key)
        # Include more e-commerce sites
        self.sites = {
            "amazon.in": "Amazon India",
            "flipkart.com": "Flipkart",
            "reliancedigital.in": "Reliance Digital",
            "snapdeal.com": "Snapdeal"
        }
    
    def compare_products(self, query: str, num_products: int = 5) -> pd.DataFrame:
        """Compare products across all e-commerce sites with enhanced features"""
        print(f"Searching for '{query}' on all e-commerce sites...")
        
        # Fetch products from all sites
        all_products = []
        for site_key in self.sites.keys():
            products = self.fetch_products(query, site_key, num_products)
            for product in products:
                all_products.append(self.extract_product_info(product, site_key))
        
        # Create DataFrame
        df = pd.DataFrame(all_products)
        
        if df.empty:
            print("No products found!")
            return df
        
        # Normalize and score products
        df = self._normalize_and_score(df)
        
        return df
    
    def extract_product_info(self, product: Dict[Any, Any], site: str) -> Dict[str, Any]:
        """Extract relevant information from a product with enhanced data extraction"""
        # Extract price and convert to numeric
        price_str = product.get("price", "0")
        
        # If price is not directly available, try to find it in other fields
        if not price_str or price_str == "0":
            # Check if there's price information in the snippet or other fields
            snippet = product.get("snippet", "")
            price_str = self._extract_price_from_text(snippet)
            
            # If still no price found, check the title
            if price_str == "0":
                title = product.get("title", "")
                price_str = self._extract_price_from_text(title)
        
        price = self._extract_price(price_str)
        
        # Extract rating and reviews from rich_snippet if available
        rating = product.get("rating", 0)
        reviews = product.get("reviews", 0)
        
        # Check rich_snippet for rating/reviews if not directly available
        rich_snippet = product.get("rich_snippet", {})
        if rich_snippet:
            top = rich_snippet.get("top", {})
            detected_extensions = top.get("detected_extensions", {})
            if not rating and "rating" in detected_extensions:
                rating = detected_extensions.get("rating", 0)
            if not reviews and "reviews" in detected_extensions:
                reviews = detected_extensions.get("reviews", 0)
        
        # If we still don't have rating/reviews, try to extract from snippet
        if not rating or not reviews:
            snippet = product.get("snippet", "")
            if not rating:
                rating = self._extract_rating_from_text(snippet)
            if not reviews:
                reviews = self._extract_reviews_from_text(snippet)
        
        # Extract image URL if available
        image_url = product.get("thumbnail", "") or product.get("image", "")
        
        return {
            "name": product.get("title", ""),
            "price": price,
            "rating": rating,
            "reviews": reviews,
            "link": product.get("link", ""),
            "site": self.sites.get(site, site),
            "raw_price": price_str,
            "image_url": image_url
        }
    
    def _extract_price_from_text(self, text: str) -> str:
        """Extract price from text using regex patterns with enhanced logic"""
        if not text:
            return "0"
        
        # Look for price patterns in the text
        patterns = [
            r'[₹$€£]\s*\d+(?:,\d+)+(?:\.\d+)?',  # ₹ 60,000.00 or $ 1,299.99 (requires comma)
            r'[₹$€£]\d+(?:,\d+)+(?:\.\d+)?',     # ₹60,000.00 or $1,299.99 (requires comma)
            r'INR\s*\d+(?:,\d+)+(?:\.\d+)?',     # INR 60,000.00 (requires comma)
            r'Rs\.\s*\d+(?:,\d+)+(?:\.\d+)?',    # Rs. 60,000.00 (requires comma)
        ]
        
        # Try patterns that require commas (more likely to be actual prices)
        for pattern in patterns:
            matches = re.findall(pattern, text)
            if matches:
                # Return the first match that looks like a reasonable product price
                for match in matches:
                    price_value = self._extract_price(match)
                    if price_value >= 1000:  # Lower threshold for more products
                        return match
        
        # If no comma-based prices found, try simpler patterns but be more selective
        simple_patterns = [
            r'[₹$€£]\s*\d{4,}(?:\.\d+)?',       # ₹ followed by 4+ digits
            r'[₹$€£]\d{4,}(?:\.\d+)?',          # ₹ followed by 4+ digits
        ]
        
        for pattern in simple_patterns:
            matches = re.findall(pattern, text)
            if matches:
                # Return the first match that looks like a reasonable product price
                for match in matches:
                    price_value = self._extract_price(match)
                    if price_value >= 1000:  # Lower threshold for more products
                        return match
        
        return "0"
    
    def get_recommendation(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get the best product recommendation with image URL"""
        if df.empty:
            return {}
            
        # Get product with highest score
        best_product = df.loc[df["final_score"].idxmax()]
        
        return {
            "name": best_product["name"],
            "site": best_product["site"],
            "price": best_product["price"],
            "raw_price": best_product["raw_price"],
            "rating": best_product["rating"],
            "reviews": best_product["reviews"],
            "link": best_product["link"],
            "score": best_product["final_score"],
            "image_url": best_product.get("image_url", "")
        }

def main():
    # Your SerpAPI key
    SERPAPI_KEY = "72593b5b010d8009bc594b31b094cf0fcde94a4714372e64f78eb6a7f3e5172a"
    
    # Create comparator instance
    comparator = EnhancedEcomComparator(SERPAPI_KEY)
    
    # Get user input
    product_query = input("Enter product name (e.g., 'iPhone 16'): ") or "iPhone 16"
    num_products = input("Number of products to compare (default 5): ") or "5"
    
    try:
        num_products = int(num_products)
    except ValueError:
        num_products = 5
    
    print(f"\nComparing top {num_products} '{product_query}' products...")
    print("Please wait, fetching data...\n")
    
    # Run comparison
    df = comparator.compare_products(product_query, num_products)
    
    if df.empty:
        print("No products found!")
        return
    
    # Display results
    comparator.display_comparison(df)
    
    # Get and display recommendation
    recommendation = comparator.get_recommendation(df)
    
    if recommendation:
        print("\n" + "=" * 80)
        print("BEST PRODUCT RECOMMENDATION:")
        print("=" * 80)
        print(f"Product: {recommendation['name']}")
        print(f"Site: {recommendation['site']}")
        print(f"Price: {recommendation['raw_price']}")
        print(f"Rating: {recommendation['rating']} ⭐ ({recommendation['reviews']} reviews)")
        print(f"Score: {recommendation['score']:.2f}")
        print(f"Buy Now: {recommendation['link']}")

if __name__ == "__main__":
    main()