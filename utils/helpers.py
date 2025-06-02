import streamlit as st
import requests
import json
from streamlit_lottie import st_lottie # Ensure this is installed

# Lottie Animation URLs (replace with your preferred ones)
LOTTIE_EMPTY_STATE_URL = "https://lottie.host/228f0785-5b8c-4f73-8240-a0f8336acb97/2Q9C062F57.json" # Searching/Empty
LOTTIE_ADD_TOOL_URL = "https://lottie.host/0f6a56e0-5a4c-4c8a-a7a6-32e80b4c80b5/DTVNaXyUpz.json" # Creative/Adding
LOTTIE_LOADING_URL = "https://lottie.host/2999a872-1c78-4660-9a63-e724a8a07526/l7yUn09Ocg.json" # Simple Loader

@st.cache_data # Cache the Lottie data
def load_lottie_url(url: str):
    """Fetches Lottie animation JSON from a URL."""
    try:
        r = requests.get(url)
        r.raise_for_status()  # Raise an exception for HTTP errors
        return r.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching Lottie animation from {url}: {e}")
        return None
    except json.JSONDecodeError:
        st.error(f"Error decoding Lottie JSON from {url}. Content: {r.text[:200]}...") # Show first 200 chars
        return None

def display_lottie_animation(lottie_json, height=200, key=None):
    """Displays a Lottie animation."""
    if lottie_json:
        st_lottie(lottie_json, height=height, key=key, speed=1, loop=True, quality="high")

# --- Form Validation ---
PREDEFINED_CATEGORIES = [
    "Content Creation", "Image Generation", "Data Analysis", "Social Media Management",
    "Email Marketing", "SEO Tools", "Video Editing", "Voice/Audio", "Translation",
    "Chatbots", "Design Tools", "Analytics", "PPT Creation"
]

def validate_inputs(name, category, new_category_name, uploaded_by, purpose):
    """Validates form inputs and returns a list of error messages."""
    errors = []
    if len(name) < 2:
        errors.append("Tool Name must be at least 2 characters long.")
    if category == "Select Category":
        errors.append("Please select a category.")
    if category == "Other" and len(new_category_name.strip()) < 2:
        errors.append("New Category Name must be at least 2 characters long if 'Other' is selected.")
    if len(uploaded_by) < 2:
        errors.append("Your Name must be at least 2 characters long.")
    if len(purpose) < 5:
        errors.append("Purpose & Usage description must be at least 5 characters long.")
    return errors