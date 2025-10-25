import requests
import pandas as pd
import numpy as np
import time
from typing import List, Dict, Any
import json
import re

class EcomProductComparator:
    def __init__(self, serpapi_key: str):
        self.serpapi_key = serpapi_key
        self.base_url = "https://serpapi.com/search.json"
        # Include more e-commerce sites
        self.sites = {
            "amazon.in": "Amazon India",
            "flipkart.com": "Flipkart",
            "reliancedigital.in": "Reliance Digital",
            "snapdeal.com": "Snapdeal"
        }
        
    def fetch_products(self, query: str, site: str, num_results: int = 5) -> List[Dict[Any, Any]]:
        """Fetch products from a specific site using SerpAPI"""
        # Improve search query to get better results with pricing information
        search_query = f"{query} price site:{site}"
        params = {
            "engine": "google",
            "q": search_query,
            "api_key": self.serpapi_key
        }
        
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Extract organic results (products)
            products = data.get("organic_results", [])[:num_results]
            return products
        except Exception as e:
            print(f"Error fetching products from {site}: {e}")
            return []
    
    def extract_product_info(self, product: Dict[Any, Any], site: str) -> Dict[str, Any]:
        """Extract relevant information from a product"""
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
        """Extract price from text using regex patterns"""
        if not text:
            return "0"
        
        import re
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
            r'[₹$€£]\s*\d{5,}(?:\.\d+)?',       # ₹ followed by 5+ digits
            r'[₹$€£]\d{5,}(?:\.\d+)?',          # ₹ followed by 5+ digits
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
    
    def _extract_rating_from_text(self, text: str) -> float:
        """Extract rating from text using regex patterns"""
        if not text:
            return 0.0
        
        import re
        # Look for rating patterns like "4.5" or "4.5 stars" or "4.5★"
        patterns = [
            r'(\d+\.\d+)\s*(?:stars?|★|rating|out of 5)',
            r'(\d+\.\d+)\s*out of 5',
            r'Rating:\s*(\d+\.\d+)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                try:
                    return float(matches[0])
                except:
                    pass
        
        # Try simple pattern for just decimal numbers
        simple_matches = re.findall(r'\b(\d+\.\d+)\b', text)
        for match in simple_matches:
            try:
                rating = float(match)
                if 1 <= rating <= 5:  # Valid rating range
                    return rating
            except:
                pass
        
        return 0.0
    
    def _extract_reviews_from_text(self, text: str) -> int:
        """Extract number of reviews from text using regex patterns"""
        if not text:
            return 0
        
        import re
        # Look for review count patterns
        patterns = [
            r'(\d+(?:,\d+)*)\s*(?:reviews?|ratings?)',
            r'\((\d+(?:,\d+)*)\s*(?:reviews?|ratings?)\)',
            r'(\d+(?:,\d+)*)\s*reviews?',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                try:
                    # Remove commas and convert to integer
                    reviews_str = re.sub(r'[^\d]', '', matches[0])
                    return int(reviews_str)
                except:
                    pass
        
        return 0
    
    def _extract_price(self, price_str: str) -> float:
        """Extract numeric price from string"""
        if not price_str:
            return 0.0
            
        # Remove currency symbols and other non-numeric characters except decimal point
        # Handle various currency formats (₹, $, €, etc.) and comma separators
        price_str = re.sub(r'[^\d.,]', '', price_str)
        
        # Handle cases like "60,000" or "60.000" (comma as thousand separator)
        # We'll assume the last dot or comma is the decimal separator
        if ',' in price_str and '.' in price_str:
            # Both present, last one is decimal separator
            if price_str.rfind('.') > price_str.rfind(','):
                # Dot is decimal separator, remove commas
                price_str = price_str.replace(',', '')
            else:
                # Comma is decimal separator, replace with dot
                price_str = price_str.replace(',', 'TEMP').replace('.', '').replace('TEMP', '.')
        elif ',' in price_str:
            # Only comma present, check if it's likely a decimal separator
            parts = price_str.split(',')
            if len(parts[-1]) == 2 or len(parts[-1]) == 3:
                # Likely thousand separator
                price_str = price_str.replace(',', '')
            else:
                # Likely decimal separator
                price_str = price_str.replace(',', '.')
        # If only dots, remove if more than one (thousand separators)
        elif price_str.count('.') > 1:
            price_str = price_str.replace('.', '')
        
        try:
            return float(price_str) if price_str else 0.0
        except:
            return 0.0
    
    def compare_products(self, query: str, num_products: int = 5) -> pd.DataFrame:
        """Compare products across all configured sites"""
        print(f"Searching for '{query}' on all configured sites...")
        
        # Load configuration to get sites
        try:
            with open("config.json", "r") as f:
                config = json.load(f)
                sites = config.get("sites", ["amazon.in", "flipkart.com", "reliancedigital.in", "snapdeal.com"])
        except FileNotFoundError:
            sites = ["amazon.in", "flipkart.com", "reliancedigital.in", "snapdeal.com"]
        
        # Fetch products from all sites
        all_products = []
        for site in sites:
            products = self.fetch_products(query, site, num_products)
            all_products.extend(products)
        
        # Process products
        processed_products = []
        for product in all_products:
            # Determine site from link
            link = product.get("link", "")
            site_name = "Unknown"
            for s in sites:
                if s in link:
                    site_name = s.split(".")[0].title()
                    break
            processed_products.append(self.extract_product_info(product, site_name))
        
        # Create DataFrame
        df = pd.DataFrame(processed_products)
        
        if df.empty:
            print("No products found!")
            return df
        
        # Normalize and score products
        df = self._normalize_and_score(df)
        
        return df
    
    def _normalize_and_score(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize features and calculate scores"""
        # Handle missing values
        df["rating"] = pd.to_numeric(df["rating"], errors='coerce').fillna(0)
        df["reviews"] = pd.to_numeric(df["reviews"], errors='coerce').fillna(0)
        df["price"] = pd.to_numeric(df["price"], errors='coerce').fillna(0)
        
        # Filter out products with zero prices for scoring
        df_filtered = df[df['price'] > 0].copy()
        
        if len(df_filtered) > 1:
            # Normalize price (lower is better)
            max_price = df_filtered["price"].max()
            df_filtered["price_score"] = (max_price - df_filtered["price"]) / max_price if max_price > 0 else 0
            
            # Normalize rating (higher is better)
            df_filtered["rating_score"] = df_filtered["rating"] / 5.0
            
            # Normalize reviews (higher is better)
            max_reviews = df_filtered["reviews"].max()
            df_filtered["review_score"] = df_filtered["reviews"] / max_reviews if max_reviews > 0 else 0
            
            # Calculate final weighted score
            # Weights: Price (40%), Features/Rating (40%), Reviews (20%)
            df_filtered["final_score"] = (
                0.4 * df_filtered["price_score"] + 
                0.4 * df_filtered["rating_score"] + 
                0.2 * df_filtered["review_score"]
            )
            
            # Update the original dataframe with scores
            df.loc[df_filtered.index, df_filtered.columns] = df_filtered
        elif len(df_filtered) == 1:
            # If only one product with valid price, give it a perfect score
            df.loc[df_filtered.index, "final_score"] = 1.0
            df.loc[df_filtered.index, "price_score"] = 1.0
            df.loc[df_filtered.index, "rating_score"] = df_filtered["rating"].iloc[0] / 5.0
            df.loc[df_filtered.index, "review_score"] = 1.0 if df_filtered["reviews"].iloc[0] > 0 else 0.0
        else:
            # If no products with valid prices, give all products equal scores
            df["final_score"] = 0.5
            df["price_score"] = 0.5
            df["rating_score"] = 0.5
            df["review_score"] = 0.5
        
        # Handle NaN values in scores
        df["final_score"] = df["final_score"].fillna(0.5)
        df["price_score"] = df["price_score"].fillna(0.5)
        df["rating_score"] = df["rating_score"].fillna(0.5)
        df["review_score"] = df["review_score"].fillna(0.5)
        
        return df
    
    def get_recommendation(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get the best product recommendation"""
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
            "image_url": best_product["image_url"]
        }
    
    def display_comparison(self, df: pd.DataFrame):
        """Display product comparison table"""
        if df.empty:
            print("No products to display!")
            return
            
        # Sort by final score
        df_sorted = df.sort_values("final_score", ascending=False)
        
        # Display key columns
        display_df = df_sorted[[
            "name", "site", "raw_price", "rating", "reviews", "final_score"
        ]].copy()
        
        display_df.columns = ["Product", "Site", "Price", "Rating", "Reviews", "Score"]
        print("\nProduct Comparison:")
        print("=" * 80)
        print(display_df.to_string(index=False))
    
    def run_comparison(self, query: str, num_products: int = 5):
        """Run the complete comparison process"""
        # Compare products
        df = self.compare_products(query, num_products)
        
        if df.empty:
            return
        
        # Display comparison
        self.display_comparison(df)
        
        # Get and display recommendation
        recommendation = self.get_recommendation(df)
        
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

def main():
    # Your SerpAPI key
    SERPAPI_KEY = "72593b5b010d8009bc594b31b094cf0fcde94a4714372e64f78eb6a7f3e5172a"
    
    # Create comparator instance
    comparator = EcomProductComparator(SERPAPI_KEY)
    
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
    comparator.run_comparison(product_query, num_products)

if __name__ == "__main__":
    main()