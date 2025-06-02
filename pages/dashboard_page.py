# pages/dashboard_page.py
import streamlit as st
import pandas as pd
import plotly.express as px 
from utils import data_manager, helpers, style_utils
import html # For HTML escaping
from streamlit_lottie import st_lottie # For displaying Lottie animations

def get_tool_icon(category):
    """ Returns an emoji icon based on the tool category. """
    icon_map = {
        "Content Creation": "✍️", "Image Generation": "🎨", "Data Analysis": "📊",
        "Social Media Management": "📱", "Email Marketing": "📧", "SEO Tools": "🔍",
        "Video Editing": "🎬", "Voice/Audio": "🎤", "Translation": "🌐",
        "Chatbots": "🤖", "Design Tools": "🖼️", "Analytics": "📈",
        "PPT Creation": "💻", "Other": "🌟"
    }
    return icon_map.get(str(category).strip(), "🛠️")

# pages/dashboard_page.py
# ... (imports: streamlit, pandas, plotly.express, data_manager, helpers, style_utils, st_lottie) ...
import html # For HTML escaping

# ... (get_tool_icon function) ...

def display_compact_ai_tool_card(tool_data, card_index):
    name = tool_data.get('Name', 'N/A')
    link_raw = tool_data.get('Link')
    link_str = str(link_raw) if pd.notna(link_raw) else '#'
    
    category = tool_data.get('Category', 'Other')
    icon = get_tool_icon(category) # This is an emoji, should be fine directly
    
    pricing_type = tool_data.get('Pricing_Type', 'N/A')
    subscription_cost = tool_data.get('Subscription_Cost', '')
    
    purpose_full = tool_data.get('Purpose', 'No detailed purpose provided.')
    if pd.isna(purpose_full) or not str(purpose_full).strip():
        purpose_full = 'No detailed purpose provided.'
    
    key_benefit_snippet = ' '.join(purpose_full.split()[:15])
    if len(purpose_full.split()) > 15:
        key_benefit_snippet += "..."

    uploaded_by = tool_data.get('Uploaded_By', 'N/A')

    # --- Prepare HTML-safe versions of dynamic content ---
    # Name and Link (tool_name_html ALREADY constructs HTML, so its components need escaping)
    safe_name = html.escape(name)
    tool_name_html_rendered = safe_name # Default to safe name
    if link_str != '#':
        safe_link = html.escape(link_str)
        tool_name_html_rendered = f"<a href='{safe_link}' target='_blank' class='tool-card-link'>{safe_name} <span class='link-icon'>🔗</span></a>"
    
    safe_category = html.escape(str(category))
    safe_key_benefit_snippet = html.escape(key_benefit_snippet)
    
    pricing_stat_value_rendered = html.escape(str(pricing_type))
    if pricing_type in ["Paid", "Freemium", "Usage-based"] and pd.notna(subscription_cost) and str(subscription_cost).strip() and str(subscription_cost).lower() != 'nan':
        pricing_stat_value_rendered += f" ({html.escape(str(subscription_cost))})"
        
    safe_uploaded_by = html.escape(str(uploaded_by))
    safe_purpose_full_snippet = html.escape(purpose_full[:150]) + ('...' if len(purpose_full) > 150 else '')


    # --- Card HTML Construction ---
    card_variants = ["variant-1", "variant-2", "variant-3", "variant-4", "variant-5"]
    variant_class = card_variants[card_index % len(card_variants)]
    
    animation_delay = card_index * 0.08
    card_animation_class = style_utils.get_css_animation_class("slideInUp")

    # The f-string should now use these pre-escaped variables directly
    # OR, if a variable *is* supposed to be raw HTML (like tool_name_html_rendered),
    # then it should NOT be escaped again when inserted into this f-string.
    # The key is to escape user data once, just before it's embedded in an HTML structure.

    card_html = f"""
    <div class="tool-card-wrapper {variant_class} {card_animation_class}" style="animation-delay: {animation_delay}s;">
        <div class="card-header-front">
            <div class="tool-name-front">{tool_name_html_rendered}</div> {/* tool_name_html_rendered is already HTML */}
            <div class="tool-category-badge">{safe_category}</div>
        </div>
        
        <div class="tool-icon-front">{icon}</div> {/* Emojis are typically fine directly */}
        
        <div> 
            <div class="tool-key-benefit-title">Key Benefit / Use</div>
            <div class="tool-key-benefit-text">
                {safe_key_benefit_snippet}
            </div>
        </div>
        
        <div class="tool-stats-front">
            <div class="tool-stat">
                <div class="tool-stat-label">Pricing</div>
                <div class="tool-stat-value">{pricing_stat_value_rendered}</div>
            </div>
            <div class="tool-stat">
                <div class="tool-stat-label">Added By</div>
                <div class="tool-stat-value">{safe_uploaded_by}</div>
            </div>
        </div>

        <div class="tool-purpose-details-area">
            <p class="tool-purpose-text-label">Purpose:</p>
            <p class="tool-purpose-full-text">{safe_purpose_full_snippet}</p>
        </div>

        <div class="tool-card-button-placeholder"></div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

    # Render the interactive button using Streamlit's widget, styled by CSS
    if link_str != '#': # Use original unescaped link_str for the button's href
        st.link_button("Visit Tool ➔", link_str, use_container_width=True)
    else:
        st.markdown("<p class='no-website-message-card'>No website link provided</p>", unsafe_allow_html=True)

def show_dashboard_page():
    """Displays the Dashboard page."""
    df = data_manager.load_data()

    # Use styled page header from style_utils
    style_utils.page_header(
        title="AI Marketing Arsenal", # Updated title
        subtitle="Discover, analyze, and leverage top AI tools for your campaigns.",
        icon="🛡️", 
        animation_class="anim-slideInDown" # Use defined animation class
    )

    # Use styled section title for metrics
    style_utils.section_title("Dashboard Overview", icon="📊", alignment="left", margin_bottom="0.5rem")
    
    metric_cols = st.columns(3)
    total_tools = len(df)
    num_categories = df['Category'].nunique() if not df.empty and 'Category' in df.columns else 0
    
    last_added_name = "N/A"
    last_added_full_name = "No tools yet"
    if not df.empty:
        last_added_obj = df.iloc[0] # Assuming df is sorted by Date_Time descending
        if last_added_obj is not None and pd.notna(last_added_obj['Name']):
            last_added_full_name = last_added_obj['Name']
            last_added_name = last_added_full_name[:15] + '...' if len(last_added_full_name) > 15 else last_added_full_name
    
    with metric_cols[0]:
        style_utils.metric_display("Total Tools", str(total_tools), icon="🛠️", animation="tada")
    with metric_cols[1]:
        style_utils.metric_display("Categories", str(num_categories), icon="🏷️", animation="bounce")
    with metric_cols[2]:
        style_utils.metric_display(
            "Recently Added", 
            last_added_name,
            icon="⏱️", 
            help_text=f"Full name: {last_added_full_name}"
        )
    
    style_utils.styled_divider() # Use styled divider

    if df.empty:
        style_utils.empty_state_message(
            message="Our AI Arsenal is awaiting its first weapon! Add tools to begin.",
            lottie_url=helpers.LOTTIE_EMPTY_STATE_URL,
            action_button_label="➕ Add First AI Tool",
            action_button_key="dashboard_empty_add_tool"
            # To make this button navigate, you'd need to handle its click in main.py
            # and change st.session_state or use st.experimental_set_query_params
        )
    else:
        style_utils.section_title("Explore AI Tools", icon="🔭", alignment="left", margin_bottom="1rem")
        
        # Filters
        filter_container = st.container()
        with filter_container:
            # For custom styling, you might wrap this in: 
            # st.markdown("<div class='filter-bar-container anim-fadeIn'>", unsafe_allow_html=True)
            f_col1, f_col2, f_col3 = st.columns([2,1,1])
            with f_col1:
                search_term = st.text_input("Search by Name or Purpose:", placeholder="E.g., 'Copywriting'", key="dashboard_search_input")
            with f_col2:
                # Robust category options
                cat_list = []
                if 'Category' in df.columns:
                    cat_list = sorted(df['Category'].astype(str).str.strip().replace('', pd.NA).dropna().unique().tolist())
                cat_options = ["All Categories"] + cat_list
                selected_category = st.selectbox("Filter by Category:", options=list(dict.fromkeys(cat_options)), key="dashboard_cat_select")
            with f_col3:
                # Robust pricing options
                price_list = []
                if 'Pricing_Type' in df.columns:
                    price_list = sorted(df['Pricing_Type'].astype(str).str.strip().replace('', pd.NA).dropna().unique().tolist())
                price_options = ["All Pricing"] + price_list
                selected_pricing = st.selectbox("Filter by Pricing:", options=list(dict.fromkeys(price_options)), key="dashboard_price_select")
            # if using wrapper div: st.markdown("</div>", unsafe_allow_html=True)

        # Apply filters
        filtered_df = df.copy()
        if search_term:
            st_lower = search_term.lower()
            name_match = filtered_df['Name'].str.lower().str.contains(st_lower, na=False)
            purpose_match = pd.Series([False] * len(filtered_df)) # Default to false
            if 'Purpose' in filtered_df.columns and filtered_df['Purpose'].notna().any():
                 purpose_match = filtered_df['Purpose'].astype(str).str.lower().str.contains(st_lower, na=False)
            filtered_df = filtered_df[name_match | purpose_match]

        if selected_category != "All Categories":
            filtered_df = filtered_df[filtered_df['Category'] == selected_category]
        if selected_pricing != "All Pricing":
            filtered_df = filtered_df[filtered_df['Pricing_Type'] == selected_pricing]
        
        if filtered_df.empty:
            style_utils.empty_state_message(
                message="No AI tools match your current filters. Try widening your search!",
                lottie_url=helpers.LOTTIE_NO_RESULTS_URL,
                height=200
            )
        else:
            num_display_columns = 3 
            tool_items_list = filtered_df.to_dict(orient="records")

            for i in range(0, len(tool_items_list), num_display_columns):
                row_item_cols = st.columns(num_display_columns)
                batch = tool_items_list[i : i + num_display_columns]
                for col_idx, tool_data_item in enumerate(batch):
                    if col_idx < len(row_item_cols): # Ensure we don't exceed available columns
                        with row_item_cols[col_idx]:
                            display_compact_ai_tool_card(tool_data_item, i + col_idx) 
        
        style_utils.styled_divider()
        style_utils.section_title("Toolkit Analytics", icon="📈", alignment="left")
        
        if not df.empty and 'Category' in df.columns and not df['Category'].dropna().empty:
            category_counts = df['Category'].value_counts().reset_index()
            category_counts.columns = ['Category', 'Count']
            try:
                fig_bar = px.bar(category_counts, x='Category', y='Count',
                                 title='Tools per Category', color='Category',
                                 labels={'Count': '# of Tools', 'Category': 'Tool Category'},
                                 height=400, template="plotly_white")
                fig_bar.update_layout(title_x=0.5, 
                                      plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                                      font=dict(family="Poppins, sans-serif", color="#4A5568"),
                                      xaxis={'categoryorder':'total descending'})
                st.plotly_chart(fig_bar, use_container_width=True)
            except Exception as e:
                st.error(f"Chart Error: Could not generate category distribution. {e}")
        else:
            st.caption("Analytics will appear once there's enough data in various categories.")

        style_utils.styled_divider()
        style_utils.section_title("Recent Additions", icon="⏱️", alignment="left")
        
        recent_cols_to_show = ['Name', 'Category', 'Uploaded_By', 'Date_Time']
        existing_recent_cols = [col for col in recent_cols_to_show if col in df.columns]

        if not df.empty and existing_recent_cols:
            recent_display_df = df[existing_recent_cols].head(10).copy()
            if 'Date_Time' in recent_display_df.columns and pd.api.types.is_datetime64_any_dtype(recent_display_df['Date_Time']):
                 recent_display_df['Date_Time'] = recent_display_df['Date_Time'].dt.strftime('%Y-%m-%d %H:%M')
            else: # If Date_Time is already string or other type
                recent_display_df['Date_Time'] = "N/A" 
            
            rename_map_recent = {'Date_Time': 'Added', 'Uploaded_By': 'Contributor'}
            actual_rename_map_recent = {k: v for k, v in rename_map_recent.items() if k in recent_display_df.columns}
            recent_display_df.rename(columns=actual_rename_map_recent, inplace=True)
            
            # For better table display, consider st.data_editor or ensuring column widths
            st.dataframe(recent_display_df, use_container_width=True, hide_index=True)
        else:
            st.caption("No recent tool additions to show.")

# This last call to styled_divider was outside the show_dashboard_page function.
# It should be inside if it's part of the page content, or in main.py if it's after the page.
# For now, assuming it's part of the page:
# style_utils.styled_divider() # Moved this to be the last element inside show_dashboard_page if needed, or remove if footer in main.py handles final separation.