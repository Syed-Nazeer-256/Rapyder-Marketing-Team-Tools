# pages/add_tool_page.py
import streamlit as st
import time
from utils import data_manager, helpers, style_utils

def show_add_tool_page():
    """Displays the Add New Tool page."""
    st.markdown(
        f"""
        <div class="page-header slideInDown" style="background: {style_utils.PRIMARY_GRADIENT};">
            <h2 class="animated-title">➕ Add New AI Tool</h2>
        </div>
        """, unsafe_allow_html=True
    )

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("<div class='form-container slideInUp'>", unsafe_allow_html=True)
        with st.form(key="add_tool_form", clear_on_submit=True):
            st.subheader("Tool Details")
            
            tool_name = st.text_input("Tool Name*", placeholder="e.g., ChatGPT, Midjourney", help="Enter the official name of the AI tool.")
            tool_link = st.text_input("Tool Link*", placeholder="https://www.example.com", help="Enter the direct URL to the AI tool.")
            
            current_categories = ["Select Category"] + data_manager.get_all_categories() + ["Other"]
            category = st.selectbox("Category*", options=list(dict.fromkeys(current_categories)), help="Select the primary category of the tool.")
            
            new_category_name = ""
            if category == "Other":
                new_category_name = st.text_input("New Category Name*", placeholder="Specify new category", help="If 'Other', please provide a new category name.")

            pricing_type = st.selectbox("Pricing Type*", options=helpers.PRICING_TYPES, help="Select the pricing model of the tool.")
            
            subscription_cost = ""
            if pricing_type in ["Paid", "Freemium"]:
                subscription_cost = st.text_input("Subscription Cost*", placeholder="e.g., $10/month, $99/year, Contact for pricing", help="Specify the cost if applicable.")

            uploaded_by = st.text_input("Your Name*", placeholder="e.g., Jane Doe", help="Who is adding this tool?")
            purpose = st.text_area("Purpose & Usage*", placeholder="Describe how this tool is used and its benefits for marketing...", height=150, help="Provide a detailed description.")
            
            st.caption("* Fields are mandatory")
            submit_button = st.form_submit_button(label="✨ Add Tool to Database")

        if submit_button:
            final_category = new_category_name.strip() if category == "Other" else category
            
            # Ensure subscription_cost is empty if not Paid/Freemium (already handled in data_manager, but good practice)
            current_subscription_cost = subscription_cost if pricing_type in ["Paid", "Freemium"] else ""

            errors = helpers.validate_inputs(
                tool_name, tool_link, category, new_category_name if category=="Other" else "N/A",
                pricing_type, current_subscription_cost, uploaded_by, purpose
            )
            
            if errors:
                for error in errors:
                    st.error(f"⚠️ Validation Error: {error}")
            else:
                with st.spinner("Submitting your tool... Hang tight! ⏳"):
                    time.sleep(1) 
                    if data_manager.add_entry(
                        tool_name, tool_link, final_category, pricing_type, 
                        current_subscription_cost, uploaded_by, purpose
                    ):
                        st.success(f"🎉 Hooray! '{tool_name}' has been successfully added to the database.")
                        st.balloons()
                    else:
                        st.error("🔥 Uh oh! Something went wrong while saving the tool. Please try again.")
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='info-column slideInUp'>", unsafe_allow_html=True)
        st.markdown("<h4>💡 Quick Tips</h4>", unsafe_allow_html=True)
        st.markdown("""
        <ul>
            <li>Provide a direct link to the tool.</li>
            <li>Be accurate with pricing information.</li>
            <li>Ensure all mandatory fields are filled.</li>
        </ul>
        """, unsafe_allow_html=True)
        
        lottie_add_tool = helpers.load_lottie_url(helpers.LOTTIE_ADD_TOOL_URL)
        if lottie_add_tool:
            helpers.display_lottie_animation(lottie_add_tool, height=300, key="add_tool_visual")
        else:
            st.info("Adding new tools enriches our shared AI resource pool!")
        st.markdown("</div>", unsafe_allow_html=True)