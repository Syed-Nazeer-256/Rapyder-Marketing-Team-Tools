import streamlit as st
from streamlit_option_menu import option_menu # Ensure this is installed
import datetime
import pandas as pd

from utils import style_utils, data_manager
from pages import dashboard_page, add_tool_page

# --- Page Configuration ---
st.set_page_config(
    page_title="AI Tools Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed" # Collapse sidebar as we use top nav
)

# --- Load Custom CSS ---
style_utils.load_css()

def get_csv_download_link():
    """Generates a download button for the CSV file."""
    df = data_manager.load_data()
    if df.empty:
        st.info("No data available to download yet.")
        return

    # Ensure Date_Time is string for CSV
    df_download = df.copy()
    if 'Date_Time' in df_download.columns and pd.api.types.is_datetime64_any_dtype(df_download['Date_Time']):
        df_download['Date_Time'] = df_download['Date_Time'].dt.strftime('%Y-%m-%d %H:%M:%S')
    
    csv = df_download.to_csv(index=False).encode('utf-8')
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"ai_tools_database_{timestamp}.csv"
    
    st.download_button(
        label="📥 Download Tools CSV",
        data=csv,
        file_name=filename,
        mime="text/csv",
        key="download_csv_button",
        help="Download the complete AI tools database as a CSV file."
    )

def main():
    """Main function to run the Streamlit app."""

    # --- Horizontal Navbar ---
    # Apply gradient background to the option_menu container manually if needed via CSS injection
    # The streamlit-option-menu itself does not directly support complex background styles like gradients.
    # We can wrap it or try to target its generated HTML elements (which can be brittle).
    
    # For a gradient navbar background, one approach is to place it in a styled st.container
    # However, option_menu typically tries to fit its parent.
    # A simpler visual cue or solid color matching the theme might be more robust.
    
    # For now, we'll use its default styling capabilities and focus on functionality.
    # To style option_menu, you typically pass CSS overrides to its `styles` parameter.
    # Example styling for option_menu (can be refined):
    
    nav_style = {
        "container": {"padding": "0.3rem 0rem", "background_color": "#f0f2f5"}, # Light background for nav bar area
        "icon": {"color": "#764ba2", "font-size": "1.1rem"}, # Purple icon color
        "nav-link": {
            "font-size": "1rem",
            "text-align": "left",
            "margin": "0px",
            "--hover-color": "#e0e0e0", # Light grey hover
            "font-weight": "500"
        },
        "nav-link-selected": {"background-color": "#667eea", "color": "white", "font-weight": "600"}, # Primary color for selected
    }

    selected_page = option_menu(
        menu_title=None,  # No title for the menu itself
        options=["🏠 Dashboard", "➕ Add Tool", "🗄️ Download Data"],
        icons=["house-fill", "plus-circle-fill", "download"],  # Bootstrap icons
        menu_icon="cast",  # Optional: main menu icon
        default_index=0,
        orientation="horizontal",
        styles=nav_style
    )

    # --- Page Routing ---
    if selected_page == "🏠 Dashboard":
        dashboard_page.show_dashboard_page()
    elif selected_page == "➕ Add Tool":
        add_tool_page.show_add_tool_page()
    elif selected_page == "🗄️ Download Data":
        st.markdown(
            f"""
            <div class="page-header slideInDown" style="background: {style_utils.SECONDARY_GRADIENT}; margin-bottom:1rem;">
                <h2 class="animated-title">🗄️ Download AI Tools Data</h2>
            </div>
            """, unsafe_allow_html=True
        )
        st.markdown("<div class='fadeIn' style='text-align:center; margin-top: 2rem;'>", unsafe_allow_html=True)
        st.write("Click the button below to download the latest version of the AI tools database in CSV format.")
        get_csv_download_link()
        st.markdown("</div>", unsafe_allow_html=True)


    # --- Footer ---
    st.markdown("---") # Visual separator
    st.markdown(
        f"""
        <div class="footer primary-gradient fadeIn">
            <p>© {datetime.datetime.now().year} AI Tools Dashboard for Marketing Teams. Version 1.0.0</p>
            <p>Crafted with 💜 and Streamlit</p>
        </div>
        """, unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()