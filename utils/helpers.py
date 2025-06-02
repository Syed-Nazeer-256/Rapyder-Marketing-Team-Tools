# utils/helpers.py
import streamlit as st
import requests
import json
import re # For URL validation
from streamlit_lottie import st_lottie

# Lottie Animation URLs (remain the same)
LOTTIE_EMPTY_STATE_URL = "https://lottie.host/228f0785-5b8c-4f73-8240-a0f8336acb97/2Q9C062F57.json"
LOTTIE_ADD_TOOL_URL = "https://lottie.host/0f6a56e0-5a4c-4c8a-a7a6-32e80b4c80b5/DTVNaXyUpz.json"
LOTTIE_LOADING_URL = "https://lottie.host/2999a872-1c78-4660-9a63-e724a8a07526/l7yUn09Ocg.json"

@st.cache_data
def load_lottie_url(url: str):
    try:
        r = requests.get(url)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching Lottie animation from {url}: {e}")
        return None
    except json.JSONDecodeError:
        st.error(f"Error decoding Lottie JSON from {url}. Content: {r.text[:200]}...")
        return None

def display_lottie_animation(lottie_json, height=200, key=None):
    if lottie_json:
        st_lottie(lottie_json, height=height, key=key, speed=1, loop=True, quality="high")

# --- Form Validation Constants ---
PREDEFINED_CATEGORIES = [
    "Content Creation", "Image Generation", "Data Analysis", "Social Media Management",
    "Email Marketing", "SEO Tools", "Video Editing", "Voice/Audio", "Translation",
    "Chatbots", "Design Tools", "Analytics", "PPT Creation"
]
PRICING_TYPES = ["Select Pricing", "Free", "Freemium", "Paid"]

def is_valid_url(url):
    """Basic URL validation."""
    if not url: # Allow empty URL initially if not mandatory
        return True
    # Regex for basic URL validation (simplified)
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(regex, url) is not None

def validate_inputs(name, link, category, new_category_name, pricing_type, subscription_cost, uploaded_by, purpose):
    """Validates form inputs and returns a list of error messages."""
    errors = []
    if len(name) < 2:
        errors.append("Tool Name must be at least 2 characters long.")
    
    if link and not is_valid_url(link): # Validate link only if provided
        errors.append("Please enter a valid URL for the Tool Link (e.g., http://example.com).")
    elif not link: # Make link mandatory
        errors.append("Tool Link is required.")


    if category == "Select Category":
        errors.append("Please select a category.")
    if category == "Other" and len(new_category_name.strip()) < 2:
        errors.append("New Category Name must be at least 2 characters long if 'Other' is selected.")
    
    if pricing_type == "Select Pricing":
        errors.append("Please select a Pricing Type.")
    if pricing_type in ["Paid", "Freemium"] and not subscription_cost:
        errors.append("Subscription Cost is required if Pricing Type is 'Paid' or 'Freemium'.")
    
    if len(uploaded_by) < 2:
        errors.append("Your Name must be at least 2 characters long.")
    if len(purpose) < 5:
        errors.append("Purpose & Usage description must be at least 5 characters long.")
    return errors