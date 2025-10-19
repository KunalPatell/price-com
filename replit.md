# Overview

This project is a Live Smartphone Comparison Tool built with Streamlit that allows users to compare smartphones with real-time data from e-commerce platforms. The application fetches live product details from Flipkart and Amazon, providing side-by-side comparisons with weighted scoring based on user preferences. Users can compare prices, ratings, specifications, and get platform-specific recommendations for the best deals.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
- **Framework**: Streamlit-based web application providing reactive UI components
- **Visualization**: Plotly integration for interactive charts and graphs (both Express and Graph Objects)
- **Layout**: Wide layout with expandable sidebar for controls and filters
- **Caching**: Streamlit's `@st.cache_data` decorator for optimized data loading performance

## Data Processing Layer
- **Data Handling**: Pandas DataFrame for structured data manipulation and analysis
- **Validation**: Built-in data validation ensuring required columns exist and numeric data integrity
- **Cleaning**: Automatic removal of rows with missing critical data using `dropna()`
- **Type Conversion**: Robust numeric conversion with error handling using `pd.to_numeric()`

## Data Input Architecture
- **Source Format**: Live web scraping from Flipkart and Amazon e-commerce platforms
- **Mock Data System**: Realistic mock data generation for demonstration and fallback purposes
- **Schema Requirements**: Dynamic data extraction with fields (Name, Price, Rating, Reviews, Battery, Camera, Storage, Processor, Image_URL)
- **Error Handling**: Comprehensive error handling for network issues, parsing failures, and missing data
- **Data Types**: Mixed data types with string identifiers, numeric specifications, and platform metadata

## Performance Optimization
- **Caching Strategy**: Function-level caching for data loading operations to minimize I/O overhead
- **Memory Management**: NumPy integration for efficient numerical computations
- **Lazy Loading**: Data loaded only when required through cached functions

# External Dependencies

## Core Framework Dependencies
- **Streamlit**: Primary web application framework for creating the interactive interface
- **Pandas**: Data manipulation and analysis library for handling smartphone datasets
- **NumPy**: Numerical computing library supporting mathematical operations
- **Plotly Express & Graph Objects**: Interactive visualization libraries for creating charts and graphs

## Web Scraping Dependencies
- **Requests**: HTTP library for making web requests to e-commerce platforms
- **BeautifulSoup4**: HTML parsing library for extracting product data from web pages
- **Selenium**: Browser automation for handling dynamic content (when needed)
- **WebDriver Manager**: Automated browser driver management for Selenium
- **lxml**: Fast XML and HTML parsing library
- **urllib3**: Advanced HTTP client library

## Data Storage
- **Live Data Fetching**: Real-time data retrieval from e-commerce platforms
- **Caching System**: Streamlit cache with 1-hour TTL for performance optimization
- **Mock Data Generation**: Intelligent mock data system for demo and fallback scenarios
- **Platform Comparison**: Side-by-side data from multiple e-commerce sources

## Python Type System
- **Typing Module**: Type hints for better code documentation and IDE support (Dict, List, Tuple annotations)