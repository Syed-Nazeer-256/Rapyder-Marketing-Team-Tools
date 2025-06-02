import streamlit as st

PRIMARY_GRADIENT = "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
SECONDARY_GRADIENT = "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)"

def load_css(file_name="assets/css/style.css"):
    """Loads and injects a CSS file."""
    try:
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"CSS file not found: {file_name}")

def apply_gradient_background(css_class, gradient):
    """Applies a gradient background to elements with a specific class."""
    st.markdown(f"""
    <style>
    .{css_class} {{
        background: {gradient};
    }}
    </style>
    """, unsafe_allow_html=True)

# --- Animation Helper Functions ---
def get_animation_class(animation_name):
    """Returns the CSS class for a given animation."""
    animations = {
        "slideInDown": "slideInDown",
        "slideInUp": "slideInUp",
        "fadeIn": "fadeIn",
        "pulse": "pulse",
        "bounce": "bounce"
    }
    return animations.get(animation_name, "")

def animated_metric_value(value, animation_name="bounce"):
    """Returns HTML for an animated metric value."""
    animation_class = get_animation_class(animation_name)
    return f'<span class="metric-value {animation_class}">{value}</span>'