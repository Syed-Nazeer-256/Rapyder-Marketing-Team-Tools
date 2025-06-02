# main.py
import streamlit as st
from streamlit_option_menu import option_menu
import datetime
import pandas as pd
import io # For CSV download buffer

# Import utility and page modules
from utils import style_utils, data_manager, helpers
from pages import dashboard_page, add_tool_page

# --- Application Configuration ---
APP_NAME = "AI Marketing Arsenal"
APP_ICON = "🎯" # Changed to match dashboard page icon
APP_VERSION = "2.0.0" # Updated version

# --- Page Configuration (MUST be the first Streamlit command) ---
st.set_page_config(
    page_title=APP_NAME,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="collapsed" # Using top navbar, so sidebar can be collapsed
)

# --- Load Custom CSS ---
# This should be called early, after set_page_config
style_utils.load_app_style()


# --- Helper Function for CSV Download ---
def get_csv_download_content():
    """Prepares the DataFrame for CSV download."""
    df = data_manager.load_data()
    if df.empty:
        return None, None # No data, no filename

    df_download = df.copy()
    
    # Ensure Date_Time is string for CSV, and handle other potential type issues
    if 'Date_Time' in df_download.columns and pd.api.types.is_datetime64_any_dtype(df_download['Date_Time']):
        df_download['Date_Time'] = df_download['Date_Time'].dt.strftime('%Y-%m-%d %H:%M:%S')
    
    # Ensure Subscription_Cost is a clean string
    if 'Subscription_Cost' in df_download.columns:
        df_download['Subscription_Cost'] = df_download['Subscription_Cost'].astype(str).replace('nan', '').replace('<NA>', '')

    # Select and reorder columns for the download to match EXPECTED_COLUMNS for consistency
    # Or define a specific set of columns you want in the downloaded file
    cols_to_download = data_manager.EXPECTED_COLUMNS 
    df_download = df_download.reindex(columns=cols_to_download, fill_value='')


    csv_buffer = io.StringIO()
    df_download.to_csv(csv_buffer, index=False, encoding='utf-8')
    csv_content = csv_buffer.getvalue()
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"ai_marketing_arsenal_data_{timestamp}.csv"
    
    return csv_content, filename

# --- Main Application Logic ---
def run_app():
    """Main function to define and run the Streamlit application."""

    # --- Horizontal Navbar using streamlit-option-menu ---
    # Styling for the navbar is more effectively done via its `styles` parameter
    # or by targeting its specific generated classes in style.css if `styles` isn't enough.
    
    # Example refined styles for option_menu
    # These colors should align with your --color-primary etc. in style.css for consistency
    # For full gradient background on navbar, it's tricky without custom components.
    # A solid color or subtle gradient via styles is more robust.
    nav_styles = {
        "container": {"padding": "0.4rem 0rem!important", "background_color": "#f8f9fa"}, # Light neutral background
        "icon": {"color": style_utils.COLOR_PRIMARY, "font-size": "1.15rem"},
        "nav-link": {
            "font-size": "1.05rem",
            "font-weight": "500",
            "color": style_utils.COLOR_TEXT_MUTED,
            "text-align": "center",
            "margin": "0px 0.5rem", # Spacing between nav items
            "--hover-color": "#e9ecef", # Light hover background
            "border-radius": style_utils.VAR_BORDER_RADIUS_SOFT # Soft radius on hover
        },
        "nav-link-selected": {
            "background_color": style_utils.COLOR_PRIMARY,
            "color": style_utils.COLOR_TEXT_LIGHT,
            "font-weight": "600",
            "border-radius": style_utils.VAR_BORDER_RADIUS_SOFT
        },
    }
    # Check if VAR_BORDER_RADIUS_SOFT is defined in style_utils, if not use a fallback
    if not hasattr(style_utils, 'VAR_BORDER_RADIUS_SOFT'):
        nav_styles["nav-link"]["border-radius"] = "6px"
        nav_styles["nav-link-selected"]["border-radius"] = "6px"


    # Use a container to constrain the width of the option_menu slightly for better aesthetics on wide screens
    nav_container = st.container()
    with nav_container:
        selected_page = option_menu(
            menu_title=None,  # No title for the menu bar itself
            options=["🛡️ Dashboard", "➕ Add Tool", "📥 Download Data"],
            icons=["shield-shaded", "plus-circle-dotted", "cloud-arrow-down"],  # Updated icons from Bootstrap Icons
            menu_icon="cast", # Optional: Main icon for the menu bar
            default_index=0,
            orientation="horizontal",
            styles=nav_styles
        )
    
    style_utils.styled_divider(height="1px", color="#e0e4e8", margin="0 0 1.5rem 0") # Divider below navbar

    # --- Page Routing ---
    if selected_page == "🛡️ Dashboard":
        dashboard_page.show_dashboard_page()
    elif selected_page == "➕ Add Tool":
        add_tool_page.show_add_tool_page()
    elif selected_page == "📥 Download Data":
        style_utils.page_header(
            title="Download Toolkit Data",
            subtitle="Get the latest snapshot of our AI Marketing Arsenal in CSV format.",
            icon="💾",
            animation_class="anim-slideInDown"
        )
        
        st.markdown("<div class='anim-fadeIn' style='text-align:center; margin-top: 2rem; padding: 0 2rem;'>", unsafe_allow_html=True)
        st.write("Click the button below to download the complete AI tools database.")
        
        csv_data, file_name = get_csv_download_content()
        
        if csv_data and file_name:
            st.download_button(
                label="⬇️ Download AI Tools CSV",
                data=csv_data,
                file_name=file_name,
                mime="text/csv",
                key="download_main_csv_button",
                help="Downloads the entire dataset as a CSV file.",
                use_container_width=False, # Let button size naturally or style via CSS
                type="primary" # Use Streamlit's primary button styling
            )
        elif csv_data is None and file_name is None: # Explicitly check for no data case
             style_utils.empty_state_message(
                message="The AI Arsenal is currently empty. There's no data to download yet.",
                lottie_url=helpers.LOTTIE_EMPTY_STATE_URL, # Or a specific "no data" Lottie
                height=180
            )
        else: # Error case from get_csv_download_content (should be rare)
            st.error("Could not prepare data for download. Please try again later.")
            
        st.markdown("</div>", unsafe_allow_html=True)

    # --- Footer ---
    style_utils.styled_divider(margin="3rem 0 1.5rem 0")
    st.markdown(
        f"""
        <div class="app-footer anim-fadeIn" style="animation-delay: 0.5s;">
            <p>{APP_NAME} - Version {APP_VERSION}</p>
            <p>© {datetime.datetime.now().year} Your Marketing Team. All rights reserved.</p>
            <p>Powered by Streamlit & Human Ingenuity 🧠</p>
        </div>
        """, unsafe_allow_html=True
    )

if __name__ == "__main__":
    run_app()