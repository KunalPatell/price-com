import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Tuple, Optional
from scraper import get_phone_data, get_popular_phones
from datetime import datetime
import time

# Page configuration
st.set_page_config(
    page_title="Smartphone Comparison Tool",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded"
)

def create_dataframe_from_scraped_data(phone1_data: Dict, phone2_data: Dict) -> pd.DataFrame:
    """
    Create a DataFrame from scraped phone data for comparison.
    
    Args:
        phone1_data: Dictionary containing data for first phone from both platforms
        phone2_data: Dictionary containing data for second phone from both platforms
        
    Returns:
        DataFrame containing phone comparison data
    """
    rows = []
    
    # Process phone 1 data
    for platform in ['flipkart', 'amazon']:
        if phone1_data.get(platform):
            data = phone1_data[platform]
            row = {
                'Name': data['name'],
                'Platform': data['platform'],
                'Price': data['price'],
                'Rating': data['rating'],
                'Reviews': data['reviews'],
                'Battery': data['specs']['battery'],
                'Camera': data['specs']['camera'],
                'Storage': data['specs']['storage'],
                'Processor': data['specs']['processor'],
                'Image_URL': data['image_url'],
                'Phone_ID': 'phone1'
            }
            rows.append(row)
    
    # Process phone 2 data
    for platform in ['flipkart', 'amazon']:
        if phone2_data.get(platform):
            data = phone2_data[platform]
            row = {
                'Name': data['name'],
                'Platform': data['platform'],
                'Price': data['price'],
                'Rating': data['rating'],
                'Reviews': data['reviews'],
                'Battery': data['specs']['battery'],
                'Camera': data['specs']['camera'],
                'Storage': data['specs']['storage'],
                'Processor': data['specs']['processor'],
                'Image_URL': data['image_url'],
                'Phone_ID': 'phone2'
            }
            rows.append(row)
    
    return pd.DataFrame(rows)

def normalize_feature(values: pd.Series, lower_is_better: bool = False) -> pd.Series:
    """
    Normalize feature values to 0-1 scale.
    
    Args:
        values: Series of numeric values to normalize
        lower_is_better: If True, lower values get higher scores (e.g., price)
        
    Returns:
        Normalized series with values between 0 and 1
    """
    if values.empty or values.isna().all():
        return values
        
    min_val = values.min()
    max_val = values.max()
    
    # Handle case where all values are the same
    if min_val == max_val:
        return pd.Series([0.5] * len(values), index=values.index)
    
    if lower_is_better:
        # For price: lower values should get higher scores
        normalized = (max_val - values) / (max_val - min_val)
    else:
        # For other features: higher values should get higher scores
        normalized = (values - min_val) / (max_val - min_val)
    
    return normalized

def calculate_weighted_score(phone_data: pd.Series, weights: Dict[str, float], 
                           normalized_data: pd.DataFrame) -> float:
    """
    Calculate weighted score for a phone based on normalized features and user weights.
    
    Args:
        phone_data: Series containing phone specifications
        weights: Dictionary of feature weights (1-5)
        normalized_data: DataFrame with normalized feature values
        
    Returns:
        Weighted score between 0 and 1
    """
    score = 0
    total_weight = 0
    
    feature_mapping = {
        'Price': 'Price',
        'Battery': 'Battery', 
        'Camera': 'Camera',
        'Storage': 'Storage',
        'Processor': 'Processor',
        'Rating': 'Rating'
    }
    
    phone_index = phone_data.name
    
    for feature, weight in weights.items():
        if feature in feature_mapping and weight > 0:
            normalized_value = normalized_data.loc[phone_index, feature_mapping[feature]]
            score += normalized_value * weight
            total_weight += weight
    
    # Avoid division by zero
    if total_weight == 0:
        return 0
        
    return score / total_weight

def display_platform_comparison(phone_data: Dict, phone_name: str) -> None:
    """
    Display comparison of the same phone across different platforms.
    
    Args:
        phone_data: Dictionary containing data from both platforms
        phone_name: Name of the phone being compared
    """
    st.subheader(f"🛒 Platform Comparison: {phone_name}")
    
    platforms = ['flipkart', 'amazon']
    cols = st.columns(len(platforms))
    
    best_price = float('inf')
    best_platform = None
    
    for i, platform in enumerate(platforms):
        if phone_data.get(platform):
            data = phone_data[platform]
            
            with cols[i]:
                st.markdown(f"### {data['platform']}")
                
                # Display image
                if data['image_url']:
                    try:
                        st.image(data['image_url'], width=150)
                    except:
                        st.info("Image not available")
                
                # Display price and rating
                price = data['price']
                if price > 0 and price < best_price:
                    best_price = price
                    best_platform = data['platform']
                
                st.write(f"💰 **Price:** ₹{price:,.0f}")
                st.write(f"⭐ **Rating:** {data['rating']:.1f}/5")
                st.write(f"📝 **Reviews:** {data['reviews']:,}")
                
                # Highlight best price
                if price == best_price and price > 0:
                    st.success("💡 Best Price!")
        else:
            with cols[i]:
                platform_name = platform.title()
                st.markdown(f"### {platform_name}")
                st.info(f"Not available on {platform_name}")
    
    return best_platform, best_price

def display_detailed_comparison(phone1_data: Dict, phone2_data: Dict, 
                              phone1_name: str, phone2_name: str,
                              phone1_score: float, phone2_score: float) -> None:
    """
    Display detailed comparison of two phones with platform data.
    
    Args:
        phone1_data: Dictionary containing first phone's platform data
        phone2_data: Dictionary containing second phone's platform data
        phone1_name: Name of first phone
        phone2_name: Name of second phone
        phone1_score: Weighted score for first phone
        phone2_score: Weighted score for second phone
    """
    st.subheader("📊 Detailed Phone Comparison")
    
    # Get best data for each phone (prefer platform with better price/rating)
    def get_best_phone_data(phone_data):
        flipkart = phone_data.get('flipkart')
        amazon = phone_data.get('amazon')
        
        if not flipkart and not amazon:
            return None
        elif not flipkart:
            return amazon
        elif not amazon:
            return flipkart
        else:
            # Choose based on price and rating
            if flipkart['price'] > 0 and amazon['price'] > 0:
                flipkart_value = (flipkart['rating'] * 2) - (flipkart['price'] / 10000)
                amazon_value = (amazon['rating'] * 2) - (amazon['price'] / 10000)
                return flipkart if flipkart_value > amazon_value else amazon
            elif flipkart['price'] > 0:
                return flipkart
            else:
                return amazon
    
    phone1_best = get_best_phone_data(phone1_data)
    phone2_best = get_best_phone_data(phone2_data)
    
    if not phone1_best or not phone2_best:
        st.error("Unable to load data for comparison")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"### {phone1_best['name']}")
        st.markdown(f"**Platform:** {phone1_best['platform']}")
        
        if phone1_best['image_url']:
            try:
                st.image(phone1_best['image_url'], width=200)
            except:
                st.info("Image not available")
        
        st.markdown("**Specifications:**")
        st.write(f"💰 **Price:** ₹{phone1_best['price']:,.0f}")
        st.write(f"⭐ **Rating:** {phone1_best['rating']:.1f}/5")
        st.write(f"📝 **Reviews:** {phone1_best['reviews']:,}")
        st.write(f"🔋 **Battery:** {phone1_best['specs']['battery']:,.0f} mAh")
        st.write(f"📷 **Camera:** {phone1_best['specs']['camera']:,.0f} MP")
        st.write(f"💾 **Storage:** {phone1_best['specs']['storage']:,.0f} GB")
        st.write(f"⚡ **Processor:** {phone1_best['specs']['processor']:,.1f} GHz")
        st.metric("**Weighted Score**", f"{phone1_score:.3f}")
    
    with col2:
        st.markdown(f"### {phone2_best['name']}")
        st.markdown(f"**Platform:** {phone2_best['platform']}")
        
        if phone2_best['image_url']:
            try:
                st.image(phone2_best['image_url'], width=200)
            except:
                st.info("Image not available")
        
        st.markdown("**Specifications:**")
        st.write(f"💰 **Price:** ₹{phone2_best['price']:,.0f}")
        st.write(f"⭐ **Rating:** {phone2_best['rating']:.1f}/5")
        st.write(f"📝 **Reviews:** {phone2_best['reviews']:,}")
        st.write(f"🔋 **Battery:** {phone2_best['specs']['battery']:,.0f} mAh")
        st.write(f"📷 **Camera:** {phone2_best['specs']['camera']:,.0f} MP")
        st.write(f"💾 **Storage:** {phone2_best['specs']['storage']:,.0f} GB")
        st.write(f"⚡ **Processor:** {phone2_best['specs']['processor']:,.1f} GHz")
        st.metric("**Weighted Score**", f"{phone2_score:.3f}")

def display_recommendation(phone1_data: Dict, phone2_data: Dict,
                         phone1_name: str, phone2_name: str,
                         phone1_score: float, phone2_score: float) -> None:
    """
    Display recommendation based on weighted scores and platform analysis.
    
    Args:
        phone1_data: Dictionary containing first phone's platform data
        phone2_data: Dictionary containing second phone's platform data
        phone1_name: Name of first phone
        phone2_name: Name of second phone
        phone1_score: Weighted score for first phone
        phone2_score: Weighted score for second phone
    """
    st.subheader("🏆 Final Recommendation")
    
    # Determine winning phone
    if phone1_score > phone2_score:
        winner_name = phone1_name
        winner_data = phone1_data
        winner_score = phone1_score
        score_diff = phone1_score - phone2_score
    elif phone2_score > phone1_score:
        winner_name = phone2_name
        winner_data = phone2_data
        winner_score = phone2_score
        score_diff = phone2_score - phone1_score
    else:
        st.info("🤝 It's a tie! Both phones have the same weighted score based on your preferences.")
        return
    
    # Find best platform for the winning phone
    best_platform = None
    best_deal = None
    
    for platform in ['flipkart', 'amazon']:
        if winner_data.get(platform):
            data = winner_data[platform]
            if data['price'] > 0:
                # Calculate deal score (considering price and rating)
                deal_score = (data['rating'] * 20) - (data['price'] / 1000)
                if best_deal is None or deal_score > best_deal:
                    best_deal = deal_score
                    best_platform = data
    
    # Display recommendation
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.success(f"**🏆 Recommended Phone: {winner_name}**")
        st.write(f"**Weighted Score:** {winner_score:.3f}")
        st.write(f"**Score Advantage:** {score_diff:.3f} points")
        
        if score_diff > 0.2:
            st.write("✅ **Strong recommendation** - This phone significantly outperforms the other based on your priorities.")
        elif score_diff > 0.1:
            st.write("✅ **Good choice** - This phone performs better according to your preferences.")
        else:
            st.write("✅ **Slight edge** - The phones are very close, but this one has a small advantage.")
    
    with col2:
        if best_platform:
            st.info(f"**🛒 Best Platform: {best_platform['platform']}**")
            st.write(f"**Price:** ₹{best_platform['price']:,.0f}")
            st.write(f"**Rating:** {best_platform['rating']:.1f}/5")
            st.write(f"**Reviews:** {best_platform['reviews']:,}")
        else:
            st.warning("Price information not available")

def create_score_chart(phone1_name: str, phone2_name: str, 
                      phone1_score: float, phone2_score: float) -> None:
    """
    Create and display bar chart comparing weighted scores.
    
    Args:
        phone1_name: Name of first phone
        phone2_name: Name of second phone
        phone1_score: Weighted score for first phone
        phone2_score: Weighted score for second phone
    """
    st.subheader("📈 Score Comparison Chart")
    
    # Create bar chart data
    phones = [phone1_name, phone2_name]
    scores = [phone1_score, phone2_score]
    colors = ['#FF6B6B' if phone1_score > phone2_score else '#4ECDC4',
              '#4ECDC4' if phone2_score > phone1_score else '#FF6B6B']
    
    fig = go.Figure(data=[
        go.Bar(
            x=phones,
            y=scores,
            marker_color=colors,
            text=[f'{score:.3f}' for score in scores],
            textposition='auto',
        )
    ])
    
    fig.update_layout(
        title="Weighted Score Comparison",
        xaxis_title="Smartphones",
        yaxis_title="Weighted Score",
        yaxis=dict(range=[0, 1]),
        showlegend=False,
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

def main():
    """Main application function with live data scraping."""
    
    # App header
    st.title("📱 Live Smartphone Comparison Tool")
    st.markdown("Compare smartphones with real-time data from Flipkart and Amazon!")
    
    # Sidebar for phone selection and weights
    st.sidebar.header("🔧 Configuration")
    
    # Phone selection
    st.sidebar.subheader("Select Phones to Compare")
    popular_phones = get_popular_phones()
    
    # Allow custom phone input
    phone_input_method = st.sidebar.radio(
        "Phone Selection Method:",
        ["Popular Phones", "Custom Search"],
        key="input_method"
    )
    
    if phone_input_method == "Popular Phones":
        phone1_name = st.sidebar.selectbox(
            "First Phone:",
            popular_phones,
            index=0,
            key="phone1"
        )
        
        available_phones2 = [name for name in popular_phones if name != phone1_name]
        phone2_name = st.sidebar.selectbox(
            "Second Phone:",
            available_phones2,
            index=0,
            key="phone2"
        )
    else:
        phone1_name = st.sidebar.text_input(
            "First Phone (e.g., 'iPhone 15 Pro'):",
            value="iPhone 15 Pro",
            key="custom_phone1"
        )
        
        phone2_name = st.sidebar.text_input(
            "Second Phone (e.g., 'Samsung Galaxy S24'):",
            value="Samsung Galaxy S24",
            key="custom_phone2"
        )
    
    # Weight sliders
    st.sidebar.subheader("🎚️ Feature Priorities")
    st.sidebar.markdown("*Set importance level for each feature (1=Low, 5=High)*")
    
    weights = {
        'Price': st.sidebar.slider(
            "💰 Price Importance (lower price = better)",
            min_value=1, max_value=5, value=3, key="price_weight"
        ),
        'Battery': st.sidebar.slider(
            "🔋 Battery Importance",
            min_value=1, max_value=5, value=3, key="battery_weight"
        ),
        'Camera': st.sidebar.slider(
            "📷 Camera Importance",
            min_value=1, max_value=5, value=3, key="camera_weight"
        ),
        'Storage': st.sidebar.slider(
            "💾 Storage Importance",
            min_value=1, max_value=5, value=3, key="storage_weight"
        ),
        'Processor': st.sidebar.slider(
            "⚡ Processor Importance",
            min_value=1, max_value=5, value=3, key="processor_weight"
        ),
        'Rating': st.sidebar.slider(
            "⭐ Rating Importance",
            min_value=1, max_value=5, value=3, key="rating_weight"
        )
    }
    
    # Add compare button
    if st.sidebar.button("🔍 Compare Phones", type="primary"):
        if phone1_name and phone2_name and phone1_name != phone2_name:
            
            # Show loading message
            with st.spinner("Fetching live data from Flipkart and Amazon..."):
                # Get data for both phones
                phone1_data = get_phone_data(phone1_name)
                phone2_data = get_phone_data(phone2_name)
            
            # Check if we got valid data
            phone1_available = phone1_data['flipkart'] or phone1_data['amazon']
            phone2_available = phone2_data['flipkart'] or phone2_data['amazon']
            
            if not phone1_available and not phone2_available:
                st.error("Could not find data for either phone. Please try different phone names.")
                return
            elif not phone1_available:
                st.error(f"Could not find data for {phone1_name}. Please try a different phone name.")
                return
            elif not phone2_available:
                st.error(f"Could not find data for {phone2_name}. Please try a different phone name.")
                return
            
            # Display last updated info
            st.info(f"🕒 Data last updated: {phone1_data['last_scraped']}")
            
            # Create DataFrame for calculations
            df = create_dataframe_from_scraped_data(phone1_data, phone2_data)
            
            if not df.empty:
                # Normalize features for scoring
                normalized_df = df.copy()
                normalized_df['Price'] = normalize_feature(df['Price'], lower_is_better=True)
                normalized_df['Battery'] = normalize_feature(df['Battery'], lower_is_better=False)
                normalized_df['Camera'] = normalize_feature(df['Camera'], lower_is_better=False)
                normalized_df['Storage'] = normalize_feature(df['Storage'], lower_is_better=False)
                normalized_df['Processor'] = normalize_feature(df['Processor'], lower_is_better=False)
                normalized_df['Rating'] = normalize_feature(df['Rating'], lower_is_better=False)
                
                # Get best representatives for each phone for scoring
                phone1_rows = df[df['Phone_ID'] == 'phone1']
                phone2_rows = df[df['Phone_ID'] == 'phone2']
                
                if not phone1_rows.empty and not phone2_rows.empty:
                    # Use the row with best overall value for scoring
                    phone1_best_idx = phone1_rows.index[0]  # For simplicity, use first available
                    phone2_best_idx = phone2_rows.index[0]  # For simplicity, use first available
                    
                    phone1_score = calculate_weighted_score(df.loc[phone1_best_idx], weights, normalized_df)
                    phone2_score = calculate_weighted_score(df.loc[phone2_best_idx], weights, normalized_df)
                    
                    # Display platform comparisons
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        display_platform_comparison(phone1_data, phone1_name)
                    
                    with col2:
                        display_platform_comparison(phone2_data, phone2_name)
                    
                    st.markdown("---")
                    
                    # Display detailed comparison
                    display_detailed_comparison(phone1_data, phone2_data, phone1_name, phone2_name, phone1_score, phone2_score)
                    
                    st.markdown("---")
                    
                    # Display recommendation
                    display_recommendation(phone1_data, phone2_data, phone1_name, phone2_name, phone1_score, phone2_score)
                    
                    st.markdown("---")
                    
                    # Display score chart
                    create_score_chart(phone1_name, phone2_name, phone1_score, phone2_score)
                    
                    # Display weight summary
                    st.subheader("⚖️ Your Priority Weights")
                    weight_col1, weight_col2 = st.columns(2)
                    
                    with weight_col1:
                        st.write("💰 **Price:** ", weights['Price'], "/5")
                        st.write("🔋 **Battery:** ", weights['Battery'], "/5")
                        st.write("📷 **Camera:** ", weights['Camera'], "/5")
                    
                    with weight_col2:
                        st.write("💾 **Storage:** ", weights['Storage'], "/5")
                        st.write("⚡ **Processor:** ", weights['Processor'], "/5")
                        st.write("⭐ **Rating:** ", weights['Rating'], "/5")
            else:
                st.error("Unable to process the phone data for comparison.")
        else:
            st.warning("Please select two different phones to compare.")
    else:
        # Show instructions when no comparison is active
        st.markdown("""
        ### 🚀 How to Use This Tool
        
        1. **Select Phones**: Choose two smartphones from the popular list or enter custom names
        2. **Set Priorities**: Adjust the importance weights for different features
        3. **Compare**: Click the "Compare Phones" button to fetch live data
        4. **Review**: Get personalized recommendations based on your preferences
        
        ### 📊 What You'll Get
        
        - **Live Pricing**: Real-time prices from Flipkart and Amazon
        - **Platform Comparison**: See which platform offers the best deal
        - **Detailed Specs**: Battery, camera, storage, and processor comparisons
        - **Smart Recommendations**: Personalized suggestions based on your priorities
        - **Visual Charts**: Easy-to-understand comparison charts
        
        ### 🔍 Data Sources
        
        This tool fetches live data from:
        - **Flipkart**: India's leading e-commerce platform
        - **Amazon**: Global marketplace with extensive phone selection
        
        *Note: Data is cached for 1 hour to improve performance and reduce server load.*
        """)
    
    # Footer
    st.markdown("---")
    st.markdown("*💡 Tip: Try adjusting the priority weights to see how recommendations change based on what matters most to you!*")

if __name__ == "__main__":
    main()
