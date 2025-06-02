# utils/helpers.py
import streamlit as st
import requests
import json
import re # For URL validation
# from streamlit_lottie import st_lottie # Not directly used here, but in pages

# --- Lottie Animation URLs (Keep your existing ones or update) ---
LOTTIE_EMPTY_STATE_URL = "https://lottie.host/228f0785-5b8c-4f73-8240-a0f8336acb97/2Q9C062F57.json"
LOTTIE_ADD_TOOL_URL = "https://lottie.host/0f6a56e0-5a4c-4c8a-a7a6-32e80b4c80b5/DTVNaXyUpz.json"
LOTTIE_LOADING_URL = "https://lottie.host/2999a872-1c78-4660-9a63-e724a8a07526/l7yUn09Ocg.json"
# Add any other Lottie URLs you use, like from your v1.0
LOTTIE_SUCCESS_URL = "https://assets1.lottiefiles.com/packages/lf20_5tkzkblw.json"
LOTTIE_NO_RESULTS_URL = "https://assets4.lottiefiles.com/packages/lf20_i8mmfrht.json"


@st.cache_data # Cache the Lottie data
def load_lottie_url(url: str):
    """Fetches Lottie animation JSON from a URL."""
    if not url: return None
    try:
        r = requests.get(url, timeout=10) # Added timeout
        r.raise_for_status()
        return r.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Lottie Error: Could not fetch animation from {url}. Details: {e}")
        return None
    except json.JSONDecodeError:
        st.error(f"Lottie Error: Invalid JSON from {url}. Content: {r.text[:200]}...")
        return None

# display_lottie_animation can be in pages where st_lottie is called, or here if preferred.
# For now, keeping it simple and assuming pages will call st_lottie directly.

# --- Form Constants and Validation ---
PREDEFINED_CATEGORIES = [
    "Content Creation", "Image Generation", "Data Analysis", "Social Media Management",
    "Email Marketing", "SEO Tools", "Video Editing", "Voice/Audio", "Translation",
    "Chatbots", "Design Tools", "Analytics", "PPT Creation"
] # These are defaults; new ones can be added via "Other"

PRICING_TYPES = ["Select Pricing", "Free", "Freemium", "Paid", "Contact for Pricing", "Usage-based"]

# List of names for the "Uploaded By" dropdown
UPLOADERS_LIST = [
    "Select Your Name", # Placeholder
    "Vamsi Krishna Yevvari",
    "Rayna",
    "Vijayashree",
    "Saakshi",
    "Sneha",
    "Sachin",
    "Manjunath",
    "Shamanth",
    "Other" # Option to type if name not in list
]

def is_valid_url(url_string: str) -> bool:
    """Checks if a string is a valid HTTP/HTTPS URL."""
    if not url_string:
        return False # Empty string is not a valid URL for this context
    # Regex for validating URLs (simplified, focuses on http/https)
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https:// or ftp:// or ftps://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'  # ...or ipv4
        r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'  # ...or ipv6
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(regex, url_string) is not None

def validate_tool_inputs(name, link, category, new_category_name, pricing_type, subscription_cost, uploaded_by, other_uploader_name, purpose):
    """Validates form inputs for adding a new tool. Returns a list of error messages."""
    errors = []
    
    name_clean = name.strip()
    link_clean = link.strip()
    purpose_clean = purpose.strip()
    new_category_name_clean = new_category_name.strip()
    other_uploader_name_clean = other_uploader_name.strip() if uploaded_by == "Other" else ""

    if len(name_clean) < 2:
        errors.append("Tool Name must be at least 2 characters long.")
    
    if not link_clean:
        errors.append("Tool Link is required.")
    elif not is_valid_url(link_clean):
        errors.append("Please enter a valid Tool Link (e.g., http://example.com).")

    if category == "Select Category":
        errors.append("Please select a tool Category.")
    elif category == "Other" and len(new_category_name_clean) < 2:
        errors.append("If 'Other' category is selected, New Category Name must be at least 2 characters.")
    
    if pricing_type == "Select Pricing":
        errors.append("Please select a Pricing Type.")
    elif pricing_type in ["Paid", "Freemium", "Usage-based"] and not subscription_cost.strip():
        # "Contact for Pricing" might not have a cost input
        errors.append(f"Subscription Cost is required if Pricing Type is '{pricing_type}'.")
    
    if uploaded_by == "Select Your Name":
        errors.append("Please select your name from the 'Uploaded By' list.")
    elif uploaded_by == "Other" and len(other_uploader_name_clean) < 2:
        errors.append("If 'Other' uploader is selected, please enter your name (at least 2 characters).")

    if len(purpose_clean) < 10: # Increased minimum length
        errors.append("Purpose & Usage description must be at least 10 characters long.")
        
    # You might want to add duplicate checks here or handle them in the page logic before calling data_manager.add_entry
    # For example, by loading data and checking:
    # from utils import data_manager
    # df_current = data_manager.load_data()
    # if name_clean and not df_current[df_current['Name'].str.lower() == name_clean.lower()].empty:
    #     errors.append(f"A tool with the name '{name_clean}' already exists.")
    # if link_clean and not df_current[df_current['Link'].str.lower() == link_clean.lower()].empty:
    #     errors.append(f"A tool with the link '{link_clean}' already exists.")
        
    return errors