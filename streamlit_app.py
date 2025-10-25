"""
Streamlit frontend for E-Commerce Product Comparator
"""
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import time
import json
from enhanced_comparator import EnhancedEcomComparator
from main import EcomProductComparator

# Set page configuration
st.set_page_config(
    page_title="E-Commerce Product Comparator",
    page_icon="🛒",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #4CAF50;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #2196F3;
        margin-bottom: 1rem;
    }
    .product-card {
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .best-product {
        border: 2px solid #4CAF50;
        background-color: #f8fff8;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
    }
    .recommendation-box {
        background-color: #e8f5e9;
        border-left: 5px solid #4CAF50;
        padding: 1.5rem;
        margin: 1rem 0;
        border-radius: 0 10px 10px 0;
    }
    .product-image {
        width: 100%;
        height: 200px;
        object-fit: contain;
        background: #f0f2f6;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

def load_config():
    """Load configuration from config.json"""
    try:
        with open("config.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("Config file not found. Please make sure config.json exists.")
        return None

def create_visualizations(df, query):
    """Create visualizations for the comparison"""
    if df.empty:
        st.warning("No data to visualize!")
        return
    
    # Create tabs for different visualizations
    tab1, tab2, tab3, tab4 = st.tabs(["Price Comparison", "Rating Comparison", "Review Comparison", "Final Score Comparison"])
    
    with tab1:
        st.subheader("Average Price by Site")
        fig1, ax1 = plt.subplots(figsize=(8, 6))
        price_data = df.groupby('site')['price'].mean()
        bars1 = ax1.bar(price_data.index, price_data.values, color=['#FF6B6B', '#4ECDC4', '#8b5cf6', '#f59e0b'])
        ax1.set_ylabel('Price (₹)')
        ax1.tick_params(axis='x', rotation=45)
        
        # Add value labels on bars
        for bar in bars1:
            height = bar.get_height()
            ax1.annotate(f'₹{height:,.0f}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom')
        
        st.pyplot(fig1)
    
    with tab2:
        st.subheader("Average Rating by Site")
        fig2, ax2 = plt.subplots(figsize=(8, 6))
        rating_data = df.groupby('site')['rating'].mean()
        bars2 = ax2.bar(rating_data.index, rating_data.values, color=['#45B7D1', '#96CEB4', '#8b5cf6', '#f59e0b'])
        ax2.set_ylabel('Rating (out of 5)')
        ax2.tick_params(axis='x', rotation=45)
        
        # Add value labels on bars
        for bar in bars2:
            height = bar.get_height()
            ax2.annotate(f'{height:.2f}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom')
        
        st.pyplot(fig2)
    
    with tab3:
        st.subheader("Average Review Count by Site")
        fig3, ax3 = plt.subplots(figsize=(8, 6))
        review_data = df.groupby('site')['reviews'].mean()
        bars3 = ax3.bar(review_data.index, review_data.values, color=['#FFEAA7', '#DDA0DD', '#8b5cf6', '#f59e0b'])
        ax3.set_ylabel('Number of Reviews')
        ax3.tick_params(axis='x', rotation=45)
        
        # Add value labels on bars
        for bar in bars3:
            height = bar.get_height()
            ax3.annotate(f'{height:,.0f}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom')
        
        st.pyplot(fig3)
    
    with tab4:
        st.subheader("Average Final Score by Site")
        fig4, ax4 = plt.subplots(figsize=(8, 6))
        score_data = df.groupby('site')['final_score'].mean()
        bars4 = ax4.bar(score_data.index, score_data.values, color=['#A29BFE', '#FD79A8', '#8b5cf6', '#f59e0b'])
        ax4.set_ylabel('Score (0-1)')
        ax4.tick_params(axis='x', rotation=45)
        
        # Add value labels on bars
        for bar in bars4:
            height = bar.get_height()
            ax4.annotate(f'{height:.2f}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom')
        
        st.pyplot(fig4)

def display_product_comparison(df):
    """Display product comparison table"""
    if df.empty:
        st.warning("No products to display!")
        return
    
    # Sort by final score
    df_sorted = df.sort_values("final_score", ascending=False)
    
    # Display key columns
    display_df = df_sorted[[
        "name", "site", "raw_price", "rating", "reviews", "final_score"
    ]].copy()
    
    display_df.columns = ["Product", "Site", "Price", "Rating", "Reviews", "Final Score"]
    
    st.subheader("Product Comparison")
    st.dataframe(display_df, width='stretch')

def display_recommendation(recommendation):
    """Display the best product recommendation"""
    if not recommendation:
        st.warning("No recommendation available!")
        return
    
    st.subheader("🏆 Best Product Recommendation")
    
    with st.container():
        # Check if image URL is available
        image_html = ""
        if recommendation.get('image_url'):
            image_html = f"<img src='{recommendation['image_url']}' class='product-image' alt='Product Image'>"
        
        st.markdown(f"""
        <div class="recommendation-box">
            {image_html}
            <h3>{recommendation['name']}</h3>
            <p><strong>Site:</strong> {recommendation['site']}</p>
            <p><strong>Price:</strong> {recommendation['raw_price']}</p>
            <p><strong>Rating:</strong> {recommendation['rating']} ⭐ ({recommendation['reviews']} reviews)</p>
            <p><strong>Final Score:</strong> {recommendation['score']:.3f}</p>
            <a href="{recommendation['link']}" target="_blank" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin-top: 10px;">Buy Now on {recommendation['site']}</a>
        </div>
        """, unsafe_allow_html=True)

def display_product_cards(df):
    """Display products as cards"""
    if df.empty:
        return
    
    st.subheader("Product Details")
    
    # Sort by final score
    df_sorted = df.sort_values("final_score", ascending=False)
    
    # Create columns for product cards
    cols = st.columns(min(len(df_sorted), 4))
    
    for idx, (i, row) in enumerate(df_sorted.iterrows()):
        with cols[idx % 4]:
            is_best = idx == 0  # First product is the best
            card_class = "product-card best-product" if is_best else "product-card"
            
            # Check if image URL is available
            image_html = ""
            if row.get('image_url'):
                image_html = f"<img src='{row['image_url']}' class='product-image' alt='Product Image'>"
            
            st.markdown(f"""
            <div class="{card_class}">
                {image_html}
                <h4>{row['name']}</h4>
                <p><strong>Site:</strong> {row['site']}</p>
                <p><strong>Price:</strong> {row['raw_price']}</p>
                <p><strong>Rating:</strong> {row['rating']} ⭐</p>
                <p><strong>Reviews:</strong> {row['reviews']:,}</p>
                <p><strong>Score:</strong> {row['final_score']:.3f}</p>
                <a href="{row['link']}" target="_blank" style="background-color: #2196F3; color: white; padding: 8px 16px; text-decoration: none; border-radius: 5px; display: inline-block; margin-top: 10px;">View on {row['site']}</a>
            </div>
            """, unsafe_allow_html=True)

def main():
    st.markdown("<h1 class='main-header'>🛒 E-Commerce Product Comparator</h1>", unsafe_allow_html=True)
    
    st.markdown("""
    Compare products across Amazon, Flipkart, Reliance Digital, and Snapdeal to find the best value based on price, ratings, and reviews.
    """)
    
    # Load configuration
    config = load_config()
    if not config:
        return
    
    # Create sidebar for inputs
    with st.sidebar:
        st.header("🔍 Search Parameters")
        
        # Product search
        product_query = st.text_input("Product Name", "iPhone 16", 
                                    help="Enter the product you want to compare")
        
        # Number of products
        num_products = st.slider("Number of products per site", 1, 15, 
                                config.get("default_num_products", 5),
                                help="Number of products to compare from each site")
        
        # Visualization option
        show_visualizations = st.checkbox("Show Visualizations", True,
                                        help="Display charts and graphs for comparison")
        
        # Comparison mode
        comparison_mode = st.radio("Comparison Mode", 
                                  ["Enhanced (with images)", "Basic"],
                                  help="Choose between enhanced and basic comparison")
        
        # Run comparison button
        run_comparison = st.button("🔍 Compare Products", type="primary",
                                  width='stretch')
        
        st.divider()
        
        # Display weights information
        st.header("⚖️ Scoring Weights")
        st.info(f"""
        **Price Weight:** {config['weights']['price']:.0%}
        **Rating Weight:** {config['weights']['rating']:.0%}
        **Reviews Weight:** {config['weights']['reviews']:.0%}
        """)
        
        st.divider()
        
        # About section
        st.header("ℹ️ About")
        st.info("""
        This tool compares products across major e-commerce sites to help you find the best value.
        
        The final score is calculated using a weighted formula:
        - Lower price = higher score
        - Higher rating = higher score
        - More reviews = higher score
        """)
    
    # Main content area
    if run_comparison:
        if not product_query.strip():
            st.error("Please enter a product name to compare!")
            return
        
        with st.spinner(f"Searching for '{product_query}' on e-commerce sites..."):
            try:
                # Initialize comparator based on selected mode
                if comparison_mode == "Enhanced (with images)":
                    serpapi_key = config["serpapi_key"]
                    comparator = EnhancedEcomComparator(serpapi_key)
                    df = comparator.compare_products(product_query, num_products)
                else:
                    serpapi_key = config["serpapi_key"]
                    comparator = EcomProductComparator(serpapi_key)
                    df = comparator.compare_products(product_query, num_products)
                
                if df.empty:
                    st.warning("No products found for your search. Try a different product name.")
                    return
                
                # Display results
                st.success(f"Found {len(df)} products for comparison!")
                
                # Display key metrics
                col1, col2, col3, col4, col5 = st.columns(5)
                
                with col1:
                    st.metric("Total Products", len(df))
                
                with col2:
                    avg_price = df['price'].mean()
                    st.metric("Average Price", f"₹{avg_price:,.0f}")
                
                with col3:
                    avg_rating = df['rating'].mean()
                    st.metric("Average Rating", f"{avg_rating:.2f} ⭐")
                
                with col4:
                    total_reviews = df['reviews'].sum()
                    st.metric("Total Reviews", f"{total_reviews:,}")
                
                with col5:
                    sites_count = df['site'].nunique()
                    st.metric("Sites Compared", sites_count)
                
                # Display product comparison table
                display_product_comparison(df)
                
                # Display product cards
                display_product_cards(df)
                
                # Get and display recommendation
                recommendation = comparator.get_recommendation(df)
                display_recommendation(recommendation)
                
                # Create visualizations if requested
                if show_visualizations:
                    st.subheader("📊 Visualizations")
                    create_visualizations(df, product_query)
                
            except Exception as e:
                st.error(f"An error occurred during comparison: {str(e)}")
                st.info("Please check your internet connection and try again.")
    else:
        # Display welcome message and instructions
        st.info("👈 Enter your product search parameters in the sidebar and click 'Compare Products' to begin!")
        
        # Display sample results
        st.subheader("Example Output")
        sample_data = {
            'name': ['Apple iPhone 16 (128GB) - Black', 'Apple iPhone 16 (128GB) - Black', 'Samsung Galaxy S24 Ultra'],
            'site': ['Amazon', 'Flipkart', 'Reliance Digital'],
            'price': [60000, 60500, 75000],
            'raw_price': ['₹60,000', '₹60,500', '₹75,000'],
            'rating': [4.5, 4.3, 4.7],
            'reviews': [1200, 800, 950],
            'final_score': [0.845, 0.812, 0.789],
            'image_url': ['https://via.placeholder.com/200x200.png?text=iPhone+16', '', 'https://via.placeholder.com/200x200.png?text=Galaxy+S24']
        }
        sample_df = pd.DataFrame(sample_data)
        display_product_comparison(sample_df)
        
        sample_recommendation = {
            "name": "Apple iPhone 16 (128GB) - Black",
            "site": "Amazon",
            "price": 60000,
            "raw_price": "₹60,000",
            "rating": 4.5,
            "reviews": 1200,
            "link": "https://www.amazon.in",
            "score": 0.845,
            "image_url": "https://via.placeholder.com/200x200.png?text=iPhone+16"
        }
        display_recommendation(sample_recommendation)

if __name__ == "__main__":
    main()