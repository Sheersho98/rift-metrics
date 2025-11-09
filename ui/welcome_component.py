import streamlit as st
import base64
import os
from ui.styles import apply_welcome_background_styles

def render_welcome_page():
    apply_welcome_background_styles()
    logo_path = "assets/RiftMetricsTransparent.png"
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            img_data = base64.b64encode(f.read()).decode()
        
        st.markdown(f"""
            <h1 style='color: white; display: flex; align-items: center;'>
                Welcome to 
                <img src='data:image/png;base64,{img_data}' style='height: 60px; margin-left: 15px;' alt='Rift Metrics' />
            </h1>
        """, unsafe_allow_html=True)
    else:
        st.title("Welcome to Rift Metrics!    :material/analytics: ")
    st.markdown("### Your League of Legends metrics now with AI Powered Analysis!")
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### :material/stadia_controller:    Track Your Performance")
        st.write("Analyze your recent ranked games with detailed statistics and insights")
    
    with col2:
        st.markdown("#### :material/chart_data:    Discover Patterns")
        st.write("See what you do differently in wins vs losses and identify improvement areas")
    
    with col3:
        st.markdown("#### :material/network_intelligence:    AI Coaching")
        st.write("Get personalized advice from an AI coach that understands your playstyle")
    
    st.markdown("---")
    
    st.markdown("### :material/rocket_launch:    Getting Started")
    st.markdown("""
    1. **Enter your Riot ID** in the sidebar (without the # symbol)
    2. **Select your region** from the dropdown
    3. **Click 'Fetch & Analyze Data'** to begin
    
    Example: If your Riot ID is `Faker#KR1`, and your server region is KR, enter:
    - Game Name: `Faker`
    - Tag Line: `KR1`
    - Region: `KR`
    """)
    
    st.info(" :material/lightbulb:    **Tip:** The more matches you analyze, the more accurate your insights will be!")
    
    st.warning("""
    :material/warning:    **Important Note:**
    - This app only fetches **Ranked matches** (Solo/Duo and Flex 5v5)
    - Maximum of **100 most recent games** due to Riot Development API limitations
    - Normal/ARAM games are not included in the analysis
    """)
    