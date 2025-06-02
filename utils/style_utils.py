# utils/style_utils.py
import streamlit as st
import os
from utils import helpers # For Lottie URLs
import html # <--- Standard HTML escaping

# --- Configuration ---
CSS_FILE_PATH = os.path.join("assets", "css", "style.css")

# utils/style_utils.py
import streamlit as st
import os
from utils import helpers # For Lottie URLs
import html

# --- Configuration ---
CSS_FILE_PATH = os.path.join("assets", "css", "style.css")

# --- Color Palette & Gradients (Define your app's theme here) ---
COLOR_PRIMARY = "#667eea"
COLOR_SECONDARY = "#764ba2"
COLOR_ACCENT = "#f093fb"
COLOR_SUCCESS = "#2ecc71"
COLOR_ERROR = "#e74c3c"
COLOR_WARNING = "#f39c12"
COLOR_TEXT_LIGHT = "#FFFFFF"
COLOR_TEXT_DARK = "#2c3e50"
COLOR_TEXT_MUTED = "#718096" # <--- MAKE SURE THIS LINE EXISTS AND IS SPELLED CORRECTLY

# Also ensure any other color variables used in main.py's nav_styles are here
VAR_BORDER_RADIUS_SOFT = "6px" # Example, if you used this constant name


GRADIENT_PRIMARY = f"linear-gradient(135deg, {COLOR_PRIMARY} 0%, {COLOR_SECONDARY} 100%)"
# ... (rest of your gradient definitions)

# --- Core Style Loading ---
def load_app_style():
    try:
        with open(CSS_FILE_PATH) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"Critical Error: Main CSS file not found at '{CSS_FILE_PATH}'. UI might be affected.")
        st.info(f"Please ensure '{CSS_FILE_PATH}' exists in your project directory.")

# --- Styled UI Component Generators ---

def page_header(title: str, subtitle: str = "", icon: str = "🚀", animation_class: str = "slideInDown"):
    icon_html = f"<span class='app-page-icon'>{icon}</span>" if icon else ""
    # Use html.escape() instead of st.markdown._html.escape()
    subtitle_html = f"<p class='app-page-subtitle {animation_class}' style='animation-delay: 0.2s;'>{html.escape(subtitle)}</p>" if subtitle else ""
    
    st.markdown(
        f"""
        <div class="app-page-header {animation_class}">
            {icon_html}
            <h1 class="app-page-title">{html.escape(title)}</h1>
            {subtitle_html}
        </div>
        """, unsafe_allow_html=True
    )

def section_title(title: str, icon: str = "", alignment: str = "left", margin_bottom: str = "1.5rem", animation_class: str = "fadeIn"):
    icon_html = f"<span class='app-section-icon'>{icon}</span> " if icon else ""
    st.markdown(
        f"""
        <div class="app-section-title-wrapper {animation_class}" style="text-align: {alignment}; margin-bottom: {margin_bottom};">
            <h2 class="app-section-title">{icon_html}{html.escape(title)}</h2>
        </div>
        """, unsafe_allow_html=True
    )

def custom_button_link(label: str, url: str, icon: str = "🔗", button_class: str = "app-custom-button", new_tab: bool = True, use_container_width:bool = False):
    target = "_blank" if new_tab else "_self"
    icon_html = f"{icon} " if icon else ""
    width_style = "width: 100%; display: block;" if use_container_width else ""
    
    st.markdown(
        f"""
        <a href="{html.escape(url)}" target="{target}" class="{button_class}" style="{width_style} text-decoration: none;">
            {icon_html}{html.escape(label)}
        </a>
        """, unsafe_allow_html=True
    )

def empty_state_message(
    message: str, 
    lottie_url: str = helpers.LOTTIE_EMPTY_STATE_URL, 
    height: int = 250, 
    action_button_label: str = None, 
    on_action_click_rerun: bool = False,
    action_button_key: str = None
    ):
    st.markdown("<div class='app-empty-state-container fadeIn'>", unsafe_allow_html=True)
    
    lottie_json = helpers.load_lottie_url(lottie_url)
    if lottie_json:
        from streamlit_lottie import st_lottie 
        st_lottie(lottie_json, height=height, key=f"empty_state_lottie_{message[:10].replace(' ','_')}", speed=1, loop=True, quality="high") # Made key safer
        
    st.markdown(f"<p class='app-empty-state-message'>{html.escape(message)}</p>", unsafe_allow_html=True)
    
    if action_button_label:
        if st.button(action_button_label, key=action_button_key or f"empty_state_action_{message[:10].replace(' ','_')}", use_container_width=True): # Made key safer
            if on_action_click_rerun:
                st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)

def get_css_animation_class(animation_name: str) -> str:
    animations = {
        "slideInDown": "anim-slideInDown", "slideInUp": "anim-slideInUp",
        "fadeIn": "anim-fadeIn", "fadeOut": "anim-fadeOut",
        "pulse": "anim-pulse", "bounce": "anim-bounce", "tada": "anim-tada"
    }
    return animations.get(animation_name, "")

def animated_text(text: str, animation_name: str = "fadeIn", tag: str = "span", css_class: str = ""):
    anim_class = get_css_animation_class(animation_name)
    return f"<{tag} class='{anim_class} {css_class}'>{html.escape(text)}</{tag}>"

def metric_display(label: str, value: str, icon: str = "", unit: str = "", animation: str = "bounce", help_text:str = ""):
    icon_html = f"<div class='app-metric-icon'>{icon}</div>" if icon else ""
    unit_html = f"<span class='app-metric-unit'>{html.escape(unit)}</span>" if unit else ""
    # Value is already escaped by animated_text
    value_html = animated_text(str(value), animation_name=animation, tag="div", css_class="app-metric-value-text") # Ensure value is string
    
    tooltip_html = f" title='{html.escape(help_text)}'" if help_text else ""

    st.markdown(
        f"""
        <div class="app-metric-card fadeIn"{tooltip_html}>
            {icon_html}
            <div class="app-metric-label">{html.escape(label)}</div>
            <div class="app-metric-value">
                {value_html}{unit_html}
            </div>
        </div>
        """, unsafe_allow_html=True
    )

def styled_divider(height:str = "1px", color:str = "rgba(0,0,0,0.1)", margin:str = "2rem 0"):
    st.markdown(f"<hr style='height:{height}; background-color:{color}; margin:{margin}; border:none;'>", unsafe_allow_html=True)