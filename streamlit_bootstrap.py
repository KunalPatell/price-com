"""
Streamlit frontend for E-Commerce Product Comparator using Bootstrap
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from main import EcomProductComparator
import json

# Load configuration
def load_config():
    try:
        with open("config.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        # Use default configuration if config.json is not found
        return {
            "serpapi_key": "72593b5b010d8009bc594b31b094cf0fcde94a4714372e64f78eb6a7f3e5172a",
            "default_num_products": 5,
            "sites": ["amazon.in", "flipkart.com"],
            "weights": {
                "price": 0.4,
                "rating": 0.4,
                "reviews": 0.2
            }
        }

# Set page configuration with Bootstrap theme
st.set_page_config(
    page_title="E-Commerce Product Comparator",
    page_icon="🛒",
    layout="wide"
)

# Add Bootstrap CSS
st.markdown("""
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem 0;
        margin-bottom: 2rem;
        border-radius: 10px;
    }
    .product-card {
        transition: transform 0.2s;
        margin-bottom: 1rem;
        height: 100%;
    }
    .product-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .best-product {
        border: 3px solid #28a745;
        background-color: #f8fff8;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        margin-bottom: 1rem;
    }
    .recommendation-box {
        background-color: #d4edda;
        border-left: 5px solid #28a745;
        padding: 1.5rem;
        margin: 1rem 0;
        border-radius: 0 10px 10px 0;
    }
    .btn-buy {
        background-color: #28a745;
        border-color: #28a745;
    }
    .btn-buy:hover {
        background-color: #218838;
        border-color: #1e7e34;
    }
    .feature-icon {
        font-size: 2rem;
        margin-bottom: 1rem;
    }
    .comparison-table {
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        border-radius: 10px;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)

def create_visualizations(df, query):
    """Create visualizations for the comparison using Plotly"""
    if df.empty:
        st.warning("No data to visualize!")
        return
    
    # Filter out products with zero prices for visualization
    df_viz = df[df['price'] > 0].copy()
    if df_viz.empty:
        st.warning("No valid price data available for visualization!")
        return
    
    # Create tabs for different visualizations
    tab1, tab2, tab3, tab4 = st.tabs(["Price Comparison", "Rating Comparison", "Review Comparison", "Final Score Comparison"])
    
    with tab1:
        st.subheader("Average Price by Site")
        price_data = df_viz.groupby('site')['price'].mean().reset_index()
        if not price_data.empty:
            fig1 = px.bar(price_data, 
                          x='site', y='price', 
                          color='site',
                          labels={'price': 'Price (₹)', 'site': 'E-commerce Site'},
                          color_discrete_sequence=['#FF6B6B', '#4ECDC4'])
            fig1.update_layout(title=f"Average Price Comparison for '{query}'")
            st.plotly_chart(fig1, width='stretch')
        else:
            st.warning("No price data available for visualization")
    
    with tab2:
        st.subheader("Average Rating by Site")
        rating_data = df.groupby('site')['rating'].mean().reset_index()
        if not rating_data.empty:
            fig2 = px.bar(rating_data, 
                          x='site', y='rating', 
                          color='site',
                          labels={'rating': 'Rating (out of 5)', 'site': 'E-commerce Site'},
                          color_discrete_sequence=['#45B7D1', '#96CEB4'])
            fig2.update_layout(title=f"Average Rating Comparison for '{query}'")
            st.plotly_chart(fig2, width='stretch')
        else:
            st.warning("No rating data available for visualization")
    
    with tab3:
        st.subheader("Average Review Count by Site")
        review_data = df.groupby('site')['reviews'].mean().reset_index()
        if not review_data.empty:
            fig3 = px.bar(review_data, 
                          x='site', y='reviews', 
                          color='site',
                          labels={'reviews': 'Number of Reviews', 'site': 'E-commerce Site'},
                          color_discrete_sequence=['#FFEAA7', '#DDA0DD'])
            fig3.update_layout(title=f"Average Review Count Comparison for '{query}'")
            st.plotly_chart(fig3, width='stretch')
        else:
            st.warning("No review data available for visualization")
    
    with tab4:
        st.subheader("Average Final Score by Site")
        # Filter for visualization to avoid zero scores
        df_score_viz = df[df['final_score'] > 0].copy()
        score_data = df_score_viz.groupby('site')['final_score'].mean().reset_index()
        if not score_data.empty:
            fig4 = px.bar(score_data, 
                          x='site', y='final_score', 
                          color='site',
                          labels={'final_score': 'Score (0-1)', 'site': 'E-commerce Site'},
                          color_discrete_sequence=['#A29BFE', '#FD79A8'])
            fig4.update_layout(title=f"Average Final Score Comparison for '{query}'")
            st.plotly_chart(fig4, width='stretch')
        else:
            st.warning("No score data available for visualization")

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
    
    # Style the dataframe
    def highlight_best(s):
        if s.name == "Final Score":
            is_max = s == s.max()
            return ['background-color: #d4edda' if v else '' for v in is_max]
        return [''] * len(s)
    
    styled_df = display_df.style.apply(highlight_best, axis=0)
    st.dataframe(styled_df, width='stretch', height=400)

def display_recommendation(recommendation):
    """Display the best product recommendation"""
    if not recommendation:
        st.warning("No recommendation available!")
        return
    
    st.subheader("🏆 Best Product Recommendation")
    
    with st.container():
        st.markdown(f"""
        <div class="recommendation-box">
            <h3>{recommendation['name']}</h3>
            <div class="row">
                <div class="col-md-6">
                    <p><strong>Site:</strong> {recommendation['site']}</p>
                    <p><strong>Price:</strong> {recommendation['raw_price']}</p>
                </div>
                <div class="col-md-6">
                    <p><strong>Rating:</strong> {recommendation['rating']} ⭐ ({recommendation['reviews']} reviews)</p>
                    <p><strong>Final Score:</strong> {recommendation['score']:.3f}</p>
                </div>
            </div>
            <a href="{recommendation['link']}" target="_blank" class="btn btn-success btn-lg">
                🛒 Buy Now on {recommendation['site']}
            </a>
        </div>
        """, unsafe_allow_html=True)

def display_product_cards(df):
    """Display products as cards"""
    if df.empty:
        return
    
    st.subheader("Product Details")
    
    # Sort by final score
    df_sorted = df.sort_values("final_score", ascending=False)
    
    # Create rows of cards
    for i in range(0, len(df_sorted), 3):
        cols = st.columns(3)
        for j in range(3):
            if i + j < len(df_sorted):
                row = df_sorted.iloc[i + j]
                is_best = (i + j) == 0  # First product is the best
                
                with cols[j]:
                    card_class = "card product-card h-100" + (" best-product" if is_best else "")
                    st.markdown(f"""
                    <div class="{card_class}">
                        <div class="card-body d-flex flex-column">
                            <h5 class="card-title">{row['name']}</h5>
                            <p class="card-text">
                                <span class="badge bg-primary">{row['site']}</span>
                            </p>
                            <p class="card-text"><strong>Price:</strong> {row['raw_price']}</p>
                            <p class="card-text"><strong>Rating:</strong> {row['rating']} ⭐</p>
                            <p class="card-text"><strong>Reviews:</strong> {row['reviews']:,}</p>
                            <p class="card-text"><strong>Score:</strong> {row['final_score']:.3f}</p>
                            <div class="mt-auto">
                                <a href="{row['link']}" target="_blank" class="btn btn-primary w-100">
                                    🔗 View on {row['site']}
                                </a>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

def main():
    # Load configuration
    config = load_config()
    
    # Main header with Bootstrap styling
    st.markdown("""
    <div class="main-header text-center">
        <div class="container">
            <h1 class="display-4">🛒 E-Commerce Product Comparator</h1>
            <p class="lead">Compare products across Amazon and Flipkart to find the best value</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Create sidebar for inputs
    with st.sidebar:
        st.header("🔍 Search Parameters")
        
        # Product search
        product_query = st.text_input("Product Name", "iPhone 16", 
                                    help="Enter the product you want to compare")
        
        # Number of products per site
        num_products = st.slider("Number of products per site", 1, 10, 
                                config.get("default_num_products", 5),
                                help="Number of products to compare from each site")
        
        # Multi-product comparison option
        st.subheader("Multi-Product Comparison")
        multi_product_mode = st.checkbox("Compare multiple products", 
                                       help="Enable to compare different products across sites")
        
        if multi_product_mode:
            st.info("Enter product names separated by commas (e.g., 'iPhone 16, Samsung Galaxy S24')")
            product_list = st.text_area("Product Names (comma separated)", 
                                      "iPhone 16, Samsung Galaxy S24",
                                      help="Enter multiple products to compare")
        
        # Visualization option
        show_visualizations = st.checkbox("Show Visualizations", True,
                                        help="Display charts and graphs for comparison")
        
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
        st.markdown("""
        <div class="alert alert-info" role="alert">
            This tool compares products across major e-commerce sites to help you find the best value.
            
            <strong>The final score is calculated using a weighted formula:</strong>
            <ul>
                <li>Lower price = higher score</li>
                <li>Higher rating = higher score</li>
                <li>More reviews = higher score</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Main content area
    if run_comparison:
        if not product_query.strip():
            st.error("Please enter a product name to compare!")
            return
        
        with st.spinner(f"Searching for products on Amazon and Flipkart..."):
            try:
                # Initialize comparator from main.py
                serpapi_key = config["serpapi_key"]
                comparator = EcomProductComparator(serpapi_key)
                
                if multi_product_mode:
                    # Multi-product comparison mode
                    products = [p.strip() for p in product_list.split(",") if p.strip()]
                    if not products:
                        st.error("Please enter at least one product name for comparison!")
                        return
                    
                    all_results = []
                    for product in products:
                        with st.spinner(f"Searching for '{product}'..."):
                            df = comparator.compare_products(product, num_products)
                            if not df.empty:
                                all_results.append(df)
                            else:
                                st.warning(f"No products found for '{product}'")
                    
                    if all_results:
                        # Combine all results
                        df = pd.concat(all_results, ignore_index=True)
                        # Re-sort by final score
                        df = df.sort_values("final_score", ascending=False)
                    else:
                        st.error("No products found for any of the entered products!")
                        return
                else:
                    # Single product comparison mode
                    df = comparator.compare_products(product_query, num_products)
                
                if df.empty:
                    st.warning("No products found for your search. Try a different product name.")
                    return
                
                # Filter out products with zero prices for scoring if we have products with valid prices
                df_filtered = df[df['price'] > 0].copy()
                if not df_filtered.empty and len(df_filtered) < len(df):
                    st.info(f"Filtered out {len(df) - len(df_filtered)} products with invalid prices")
                    df = df_filtered
                
                # Display results
                st.success(f"Found {len(df)} products for comparison!")
                
                # Display key metrics using Bootstrap cards
                st.subheader("Key Metrics")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="feature-icon">📦</div>
                        <h3>{len(df)}</h3>
                        <p>Total Products</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    # Calculate average price excluding zero prices
                    valid_prices = df[df['price'] > 0]['price']
                    avg_price = valid_prices.mean() if not valid_prices.empty else 0
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="feature-icon">💰</div>
                        <h3>₹{avg_price:,.0f}</h3>
                        <p>Average Price</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    avg_rating = df['rating'].mean()
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="feature-icon">⭐</div>
                        <h3>{avg_rating:.2f}</h3>
                        <p>Average Rating</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col4:
                    total_reviews = df['reviews'].sum()
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="feature-icon">👥</div>
                        <h3>{total_reviews:,}</h3>
                        <p>Total Reviews</p>
                    </div>
                    """, unsafe_allow_html=True)
                
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
            'name': ['Apple iPhone 16 (128GB) - Black', 'Apple iPhone 16 (128GB) - Black'],
            'site': ['Amazon', 'Flipkart'],
            'price': [60000, 60500],
            'raw_price': ['₹60,000', '₹60,500'],
            'rating': [4.5, 4.3],
            'reviews': [1200, 800],
            'final_score': [0.845, 0.812]
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
            "score": 0.845
        }
        display_recommendation(sample_recommendation)

if __name__ == "__main__":
    main()