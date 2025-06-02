import streamlit as st
import pandas as pd
import plotly.express as px
from utils import data_manager, helpers, style_utils

def display_tool_card(tool, index):
    """ Displays a single tool card with animations. """
    # Add a delay for staggered animation effect
    # This simple delay might not work well with Streamlit's execution model for many cards.
    # A more robust way is to manage visibility/animation state, but for now, class-based.
    
    # Truncate purpose for display
    purpose_snippet = (tool['Purpose'][:100] + '...') if len(tool['Purpose']) > 100 else tool['Purpose']
    
    # Format Date/Time
    date_time_str = tool['Date_Time'].strftime('%b %d, %Y %I:%M %p') if pd.notna(tool['Date_Time']) else "N/A"

    st.markdown(
        f"""
        <div class="tool-card slideInUp" style="animation-delay: {index * 0.05}s;">
            <h3>{tool['Name']}</h3>
            <span class="category-badge">{tool['Category']}</span>
            <p class="purpose">{purpose_snippet}</p>
            <div class="details">
                Added by: {tool['Uploaded_By']} <br>
                On: {date_time_str}
            </div>
        </div>
        """, unsafe_allow_html=True
    )

def show_dashboard_page():
    """Displays the Dashboard page."""
    df = data_manager.load_data()

    # Hero Section
    st.markdown(
        f"""
        <div class="hero-section primary-gradient slideInDown">
            <h1 class="hero-title animated-title">🚀 AI Tools Navigator</h1>
            <p class="hero-subtitle animated-subtitle">Explore and manage AI tools for your marketing team.</p>
        </div>
        """, unsafe_allow_html=True
    )

    # Key Metrics
    st.subheader("📊 At a Glance", anchor=False)
    col1, col2, col3 = st.columns(3)
    total_tools = len(df)
    num_categories = df['Category'].nunique() if not df.empty else 0
    last_added_tool = df['Name'].iloc[0] if not df.empty else "N/A"
    
    with col1:
        st.markdown(f"""
        <div class="metric-card fadeIn">
            <h4>Total Tools</h4>
            {style_utils.animated_metric_value(total_tools)}
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card fadeIn" style="animation-delay: 0.2s;">
            <h4>Unique Categories</h4>
            {style_utils.animated_metric_value(num_categories)}
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card fadeIn" style="animation-delay: 0.4s;">
            <h4>Last Added</h4>
            <p style="font-size: 1.2rem; font-weight: 600; color: #764ba2; margin-top: 0.2rem; height: 48px; overflow:hidden; text-overflow: ellipsis;">{last_added_tool}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    if df.empty:
        st.markdown("<div class='fadeIn' style='text-align:center;'>", unsafe_allow_html=True)
        lottie_empty = helpers.load_lottie_url(helpers.LOTTIE_EMPTY_STATE_URL)
        if lottie_empty:
            helpers.display_lottie_animation(lottie_empty, height=300, key="empty_state")
        st.warning("Looks like there are no tools in the database yet. Be the first to add one!")
        st.info("Navigate to the '➕ Add Tools' page to contribute.")
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        # Tools Presentation - Beautiful Card Design
        st.subheader("🛠️ Discover AI Tools", anchor=False)
        
        # Search and Filter
        search_term = st.text_input("Search tools by name or purpose:", placeholder="Type to search...", key="search_tools")
        
        all_cats = ["All Categories"] + sorted(df['Category'].unique().tolist())
        selected_category = st.selectbox("Filter by category:", options=all_cats, key="filter_category")

        filtered_df = df.copy()
        if search_term:
            filtered_df = filtered_df[
                filtered_df['Name'].str.contains(search_term, case=False, na=False) |
                filtered_df['Purpose'].str.contains(search_term, case=False, na=False)
            ]
        if selected_category != "All Categories":
            filtered_df = filtered_df[filtered_df['Category'] == selected_category]
        
        if filtered_df.empty and (search_term or selected_category != "All Categories"):
             st.info(f"No tools found matching your criteria ('{search_term}' in category '{selected_category}'). Try a different search or filter.")
        elif not filtered_df.empty:
            st.markdown("<div class='tool-card-container'>", unsafe_allow_html=True)
            for index, row in filtered_df.iterrows():
                display_tool_card(row, index)
            st.markdown("</div>", unsafe_allow_html=True)
        elif df.empty: # Should be caught by earlier check, but as a fallback
            st.info("No tools available yet.")


        st.markdown("---")
        
        # Analytics Section
        st.subheader("📈 Tools Analytics", anchor=False)
        
        # Tools per Category Chart
        if not df.empty:
            category_counts = df['Category'].value_counts().reset_index()
            category_counts.columns = ['Category', 'Count']
            
            fig_bar = px.bar(category_counts, x='Category', y='Count',
                             title='Number of Tools per Category',
                             color='Category',
                             labels={'Count': 'Number of Tools'},
                             height=400)
            fig_bar.update_layout(xaxis_title="Category", yaxis_title="Number of Tools", title_x=0.5,
                                  plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                                  font=dict(family="Poppins, sans-serif", color="#333"))
            st.plotly_chart(fig_bar, use_container_width=True)

        st.markdown("---")

        # Recent Activity Table
        st.subheader("⏱️ Recent Activity (Last 10)", anchor=False)
        # Select and rename columns for display
        recent_df = df[['Name', 'Category', 'Uploaded_By', 'Date_Time']].head(10).copy()
        recent_df['Date_Time'] = recent_df['Date_Time'].dt.strftime('%Y-%m-%d %H:%M') if pd.notna(recent_df['Date_Time']).all() else 'N/A'
        recent_df.rename(columns={'Date_Time': 'Added On'}, inplace=True)
        
        # Use st.data_editor for a modern look, or st.dataframe
        st.dataframe(recent_df, use_container_width=True, hide_index=True)