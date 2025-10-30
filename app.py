# app.py
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import random

# Configuration - No API Keys Needed!
API_BASE_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Geo-Keyword Finder - 100% Free",
    page_icon="📍",
    layout="wide"
)

# Simple CSS
st.markdown("""
<style>
    .main-title {
        font-size: 2.5rem;
        color: #FF4B4B;
        text-align: center;
        font-weight: bold;
    }
    .free-badge {
        background: #4CAF50;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-title">📍 Geo-Keyword Finder</div>', unsafe_allow_html=True)
st.markdown('<div style="text-align: center; margin-bottom: 2rem;"><span class="free-badge"></span></div>', unsafe_allow_html=True)

# Check if backend is running
try:
    response = requests.get(f"{API_BASE_URL}/", timeout=3)
    backend_running = response.status_code == 200
except:
    backend_running = False

if not backend_running:
    st.error("Backend server not running. Please start it first!")
    st.info("""
    **To start the backend (Terminal 1):**
    ```bash
    python main.py
    ```
    
    **Then start frontend (Terminal 2):**
    ```bash
    streamlit run app.py
    ```
    """)
    st.stop()

# Sidebar
with st.sidebar:
    st.header("🔍 Search Settings")
    
    # Get available options
    try:
        locations_data = requests.get(f"{API_BASE_URL}/locations").json()
        cities = locations_data["cities"]
        business_types = locations_data["business_types"]
    except:
        cities = ["Chennai", "Bangalore", "Mumbai", "Delhi", "Hyderabad", "Kolkata", "Pune"]
        business_types = ["Gym", "Restaurant", "Cafe", "Salon", "Retail Store"]
    
    location = st.selectbox("📍 City", cities)
    business_type = st.selectbox("🏢 Business Type", business_types)
    
    if st.button("🚀 Analyze Market", type="primary", use_container_width=True):
        with st.spinner("Analyzing..."):
            try:
                response = requests.post(
                    f"{API_BASE_URL}/analyze",
                    json={"location": location, "business_type": business_type}
                )
                if response.status_code == 200:
                    st.session_state.result = response.json()
                    st.success("Analysis complete! ✅")
                else:
                    st.error("Analysis failed. Please try again.")
            except Exception as e:
                st.error(f"Error: {e}")

# Main content
if 'result' in st.session_state:
    result = st.session_state.result
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🏢 Competitors", result['competitor_count'])
    with col2:
        st.metric("😊 Sentiment", f"{result['sentiment_score']:.2f}")
    with col3:
        st.metric("📈 Market Score", f"{result['market_score']}%")
    with col4:
        st.metric("🔥 Keywords", len(result['trending_keywords']))
    
    # Recommendation
    st.info(f"**🎯 Recommendation:** {result['recommendation']}")
    
    # Suggested Areas
    st.subheader("📍 Suggested Areas")
    for area in result['suggested_locations']:
        st.write(f"• {area}")
    
    # Visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        # Market Score Gauge
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=result['market_score'],
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Market Score"},
            gauge={'axis': {'range': [None, 100]},
                   'steps': [{'range': [0, 50], 'color': "lightgray"},
                           {'range': [50, 70], 'color': "yellow"},
                           {'range': [70, 100], 'color': "lightgreen"}]}
        ))
        st.plotly_chart(fig_gauge, use_container_width=True)
    
    with col2:
        # Keywords
        keywords_df = pd.DataFrame({
            'Keyword': result['trending_keywords'],
            'Popularity': [random.randint(70, 95) for _ in result['trending_keywords']]
        })
        fig = px.bar(keywords_df, x='Popularity', y='Keyword', orientation='h',
                    title="Trending Keywords")
        st.plotly_chart(fig, use_container_width=True)
    
    # History
    st.subheader("📊 Recent Searches")
    try:
        history = requests.get(f"{API_BASE_URL}/history").json()
        if history:
            history_df = pd.DataFrame(history)
            st.dataframe(history_df[['location', 'business_type', 'competitor_count', 'market_score']])
    except:
        st.info("No search history yet")

else:
    # Welcome screen
    st.success("✅ **System Ready!** No API keys needed - using smart algorithms")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🎯 How It Works")
        st.write("""
        1. **Select** a city and business type
        2. **Analyze** market potential instantly  
        3. **Get** data-driven recommendations
        4. **Make** informed business decisions
        
        **All data is generated using smart algorithms - no external APIs!**
        """)
    
    with col2:
        st.subheader("🏆 Example Results")
        example_data = {
            "Scenario": ["Gym in Chennai", "Cafe in Bangalore"],
            "Competitors": [45, 120],
            "Market Score": ["78%", "65%"]
        }
        st.dataframe(pd.DataFrame(example_data))

# Footer
st.markdown("---")
