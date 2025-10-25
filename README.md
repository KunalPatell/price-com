# E-Commerce Product Comparator Pro

A professional Streamlit application for comparing products across major e-commerce platforms (Amazon, Flipkart, Reliance Digital, and Snapdeal) to find the best value based on price, ratings, and reviews.

## Features

- **Real-time Product Comparison**: Fetches live data from 4 major e-commerce platforms
- **Advanced Scoring Algorithm**: Weighed scoring based on price, ratings, and reviews
- **Interactive Visualizations**: Beautiful charts and graphs using Plotly
- **Professional UI/UX**: Modern Bootstrap-based interface with enhanced styling
- **Multi-Product Comparison**: Compare multiple products simultaneously
- **Product Images**: Visual representation of products
- **Category Filtering**: Search by product categories
- **Site Selection**: Choose which e-commerce sites to include
- **Detailed Insights**: Advanced product analysis and recommendations
- **Price Trend Analysis**: Line charts showing price trends
- **Correlation Analysis**: Heatmaps showing feature correlations

## Installation

1. Clone or download this repository
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Method 1: Using the Batch File (Windows)
- Double-click on `run_bootstrap.bat` to start the original application
- Double-click on `run_enhanced.bat` to start the enhanced application

### Method 2: Command Line
Navigate to the project directory and run:
```bash
# Original application
python -m streamlit run streamlit_bootstrap.py

# Enhanced application
python -m streamlit run enhanced_comparator.py
```

The application will open in your default web browser at `http://localhost:8501`.

## How It Works

The application uses SerpAPI to fetch product data from e-commerce sites. It then processes this data to extract:
- Product names
- Prices
- Ratings
- Review counts
- Product links
- Product images

The final score is calculated using a weighted formula:
```
Final Score = 0.4 × Price Score + 0.4 × Rating Score + 0.2 × Review Score
```

Where:
- **Price Score**: Higher for lower prices
- **Rating Score**: Higher for better ratings (out of 5)
- **Review Score**: Higher for more reviews

## Configuration

The application can be configured using `config.json`:
```json
{
    "serpapi_key": "YOUR_SERPAPI_KEY",
    "default_num_products": 5,
    "sites": ["amazon.in", "flipkart.com", "reliancedigital.in", "snapdeal.com"],
    "categories": [
        "Electronics",
        "Mobiles",
        "Laptops",
        "Home Appliances",
        "Fashion",
        "Books",
        "Sports",
        "Beauty"
    ],
    "weights": {
        "price": 0.4,
        "rating": 0.4,
        "reviews": 0.2
    }
}
```

## Enhanced Features

### Product Images
The enhanced version displays product images for better visual comparison.

### Category Filtering
Users can select product categories for more targeted searches.

### Multi-Site Selection
Choose which e-commerce sites to include in the comparison.

### Advanced Visualizations
- Price trend analysis with line charts
- Feature correlation heatmaps
- Enhanced bar charts with better color schemes
- Scatter plots for price vs rating analysis

### Improved UI/UX
- Modern color scheme with better visibility
- Enhanced card designs with hover effects
- Progress bars for score visualization
- Better responsive design

## Screenshots

### Main Interface
![Main Interface](screenshots/main_interface.png)

### Product Comparison
![Product Comparison](screenshots/product_comparison.png)

### Visualizations
![Visualizations](screenshots/visualizations.png)

## Contributing

1. Fork the repository
2. Create a new branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [SerpAPI](https://serpapi.com/) for providing the search API
- [Streamlit](https://streamlit.io/) for the amazing web framework
- [Plotly](https://plotly.com/) for interactive visualizations