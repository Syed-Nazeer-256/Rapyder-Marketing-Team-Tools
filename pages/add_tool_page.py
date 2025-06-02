# pages/add_tool_page.py
import streamlit as st
import time
from utils import data_manager, helpers, style_utils # Ensure all are imported
from streamlit_lottie import st_lottie # For displaying Lottie animations

def show_add_tool_page():
    """Displays the Add New Tool page."""
    
    # Use styled page header from style_utils
    style_utils.page_header(
        title="Launch New AI Tool",
        subtitle="Contribute to our growing arsenal of marketing AI resources.",
        icon="➕",
        animation_class="anim-slideInDown" # Use animation class from style_utils
    )

    col_form, col_info = st.columns([2, 1.2]) # Adjust column ratio for aesthetics

    with col_form:
        # Use a custom class for the form container for potential specific styling
        st.markdown("<div class='form-wrapper-card anim-slideInUp'>", unsafe_allow_html=True) 
        # Define .form-wrapper-card in style.css for card-like appearance if desired:
        # .form-wrapper-card { background-color: #fff; padding: 2rem; border-radius: 12px; box-shadow: 0 6px 20px rgba(0,0,0,0.08); }
        
        style_utils.section_title("Submit Tool Details", icon="📝", alignment="left", margin_bottom="1rem")

        with st.form(key="add_tool_form", clear_on_submit=False): # Keep form data on validation error
            tool_name = st.text_input("Tool Name*", placeholder="e.g., Stellar Scribe AI", help="The official name of the AI tool.")
            tool_link = st.text_input("Tool Link*", placeholder="https://www.example.ai", help="Direct URL to the tool's main page.")
            
            # --- Category Selection with "Other" ---
            all_db_categories = data_manager.get_all_categories() # Fetches from DB + predefined
            # Ensure "Select Category" and "Other" are distinctly handled
            category_options = ["Select Category"] + sorted(list(set(all_db_categories))) + ["Other (Specify Below)"]
            # Remove duplicates just in case
            category_options = list(dict.fromkeys(category_options)) 
            
            selected_category = st.selectbox(
                "Category*", 
                options=category_options, 
                help="Choose the most relevant category or specify a new one."
            )
            
            new_category_name_input = ""
            if selected_category == "Other (Specify Below)":
                new_category_name_input = st.text_input(
                    "New Category Name*", 
                    placeholder="Enter new category",
                    help="Provide a concise name for the new category."
                )

            # --- Pricing Type and Cost ---
            pricing_type = st.selectbox(
                "Pricing Model*", 
                options=helpers.PRICING_TYPES, # From helpers.py
                help="Select the tool's pricing structure."
            )
            
            subscription_cost_input = ""
            if pricing_type in ["Paid", "Freemium", "Usage-based"]: # Only show cost if relevant
                subscription_cost_input = st.text_input(
                    "Subscription Cost / Details*", 
                    placeholder="e.g., $20/month, $0.01/token, See website", 
                    help="Specify cost or how to find it."
                )

            # --- Uploaded By Dropdown ---
            uploaded_by_selection = st.selectbox(
                "Uploaded By*", 
                options=helpers.UPLOADERS_LIST, # From helpers.py
                help="Please select your name."
            )
            other_uploader_name_input = ""
            if uploaded_by_selection == "Other":
                other_uploader_name_input = st.text_input(
                    "Your Name (if 'Other')*", 
                    placeholder="Please enter your full name",
                    help="Enter your name if not in the list."
                )
            
            purpose_description = st.text_area(
                "Purpose & Key Benefits*", 
                placeholder="Describe the tool's main function, how it helps marketing, and its unique advantages...", 
                height=180, 
                help="Be detailed and specific about its value."
            )
            
            st.caption("* Fields are mandatory.")
            submit_button = st.form_submit_button(label="🚀 Launch into Database!", use_container_width=True)

        if submit_button:
            # Determine final category
            final_category_name = new_category_name_input.strip().capitalize() if selected_category == "Other (Specify Below)" else selected_category
            
            # Determine final uploader name
            final_uploader_name = other_uploader_name_input.strip() if uploaded_by_selection == "Other" else uploaded_by_selection

            # Validate inputs
            errors = helpers.validate_tool_inputs(
                tool_name, tool_link, 
                selected_category, # Pass the selection, validation handles "Other" logic
                new_category_name_input, 
                pricing_type, subscription_cost_input,
                uploaded_by_selection, # Pass the selection
                other_uploader_name_input,
                purpose_description
            )
            
            if errors:
                for error_msg in errors:
                    st.error(f"⚠️ {error_msg}")
            else:
                # Check for duplicates before adding (more user-friendly)
                current_df = data_manager.load_data()
                if not current_df[current_df['Name'].str.lower() == tool_name.strip().lower()].empty:
                    st.error(f"⚠️ A tool with the name '{tool_name.strip()}' already exists.")
                elif not current_df[current_df['Link'].str.lower() == tool_link.strip().lower()].empty:
                     st.error(f"⚠️ A tool with the link '{tool_link.strip()}' already exists.")
                else:
                    with st.spinner("Transmitting data to the AI Galaxy... Please wait. 🌌"):
                        time.sleep(1.5) # Simulate network latency/processing
                        
                        # Prepare data for saving
                        actual_subscription_cost = subscription_cost_input.strip() if pricing_type in ["Paid", "Freemium", "Usage-based"] else ""

                        if data_manager.add_entry(
                            name=tool_name.strip(), 
                            link=tool_link.strip(), 
                            category=final_category_name, 
                            pricing_type=pricing_type, 
                            subscription_cost=actual_subscription_cost, 
                            uploaded_by=final_uploader_name, 
                            purpose=purpose_description.strip()
                        ):
                            st.success(f"🌠 Success! '{tool_name.strip()}' has been successfully added to our AI toolkit.")
                            if helpers.LOTTIE_SUCCESS_URL:
                                lottie_json = helpers.load_lottie_url(helpers.LOTTIE_SUCCESS_URL)
                                if lottie_json:
                                    st_lottie(lottie_json, height=120, loop=False, key="add_tool_success_lottie", speed=1)
                            st.balloons()
                            # Consider clearing specific form fields if clear_on_submit=False,
                            # or rely on Streamlit's rerun behavior.
                            # For a cleaner UX, explicitly clear relevant session state or use st.experimental_rerun()
                            # after a short delay if you want the form to truly reset.
                            # For now, form will persist data due to clear_on_submit=False, good for fixing errors.
                        else:
                            st.error("🔥 Houston, we have a problem! Failed to save the tool. Please check logs or try again.")
        
        st.markdown("</div>", unsafe_allow_html=True) # Close .form-wrapper-card

    with col_info:
        # Use a custom class for the info column for styling
        st.markdown("<div class='info-column-card anim-slideInUp' style='animation-delay: 0.2s;'>", unsafe_allow_html=True)
        # Define .info-column-card in style.css:
        # .info-column-card { background-color: #f8f9fa; padding: 1.5rem; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); height: 100%; }

        style_utils.section_title("Submission Guidelines", icon="📜", alignment="left", margin_bottom="1rem")
        
        st.markdown("""
        <ul style="font-size: 0.9rem; line-height: 1.6; color: #555;">
            <li><strong>Accuracy is Key:</strong> Ensure all tool details are correct and up-to-date.</li>
            <li><strong>Clear Purpose:</strong> Describe the tool's primary function and unique benefits for marketing tasks concisely.</li>
            <li><strong>Relevant Category:</strong> Choose the most fitting category. If it's new, provide a clear name.</li>
            <li><strong>Valid Link:</strong> Double-check the website URL (must start with <code>http://</code> or <code>https://</code>).</li>
            <li><strong>Your Contribution Matters:</strong> Thanks for helping expand our AI resource hub!</li>
        </ul>
        """, unsafe_allow_html=True)
        
        style_utils.styled_divider(margin="1.5rem 0") # Use styled divider

        if helpers.LOTTIE_ADD_TOOL_URL:
            lottie_json = helpers.load_lottie_url(helpers.LOTTIE_ADD_TOOL_URL)
            if lottie_json:
                st_lottie(lottie_json, height=280, key="add_tool_visual_lottie", speed=1)
            else:
                st.info("✨ Adding new tools helps the whole team discover valuable AI resources!")
        st.markdown("</div>", unsafe_allow_html=True) # Close .info-column-card