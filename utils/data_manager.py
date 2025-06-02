# utils/data_manager.py

import streamlit as st
import pandas as pd
import datetime
import os
# Import helpers at the end to avoid circular dependency if helpers imports data_manager
# from utils import helpers # This will be moved to the end or managed carefully

CSV_FILE_PATH = "ai_tools_database.csv"
EXPECTED_COLUMNS = [
    "Serial_Number", "Name", "Link", "Category", "Pricing_Type", 
    "Subscription_Cost", "Uploaded_By", "Date_Time", "Purpose"
]

def initialize_csv():
    """Creates the CSV file with headers if it doesn't exist."""
    if not os.path.exists(CSV_FILE_PATH):
        try:
            df = pd.DataFrame(columns=EXPECTED_COLUMNS)
            df.to_csv(CSV_FILE_PATH, index=False)
        except Exception as e:
            st.error(f"Failed to initialize CSV file: {e}")

@st.cache_data(ttl=600) # Cache data for 10 minutes
def load_data():
    """Loads data from the CSV file with error handling and schema validation."""
    initialize_csv() # Ensure file exists
    try:
        df = pd.read_csv(CSV_FILE_PATH)
        
        # Schema migration: Add missing columns if an older CSV is used
        updated_csv = False
        for col in EXPECTED_COLUMNS:
            if col not in df.columns:
                df[col] = pd.NA  # Add missing column with NA values
                updated_csv = True
        
        # Ensure correct column order
        if list(df.columns) != EXPECTED_COLUMNS:
            df = df[EXPECTED_COLUMNS]
            updated_csv = True

        if updated_csv:
            st.info("Database schema updated. New columns have been added.")
            save_data(df) # Save the updated structure immediately

        if 'Date_Time' in df.columns:
            df['Date_Time'] = pd.to_datetime(df['Date_Time'], errors='coerce')
        else:
            df['Date_Time'] = pd.NaT
            
        # Ensure Serial_Number is int, handling potential read as float from CSV with NAs
        if 'Serial_Number' in df.columns and not df.empty:
            df['Serial_Number'] = pd.to_numeric(df['Serial_Number'], errors='coerce').fillna(0).astype(int)


        return df.sort_values(by="Date_Time", ascending=False).reset_index(drop=True)

    except pd.errors.EmptyDataError:
        # st.info("Database is empty. Add some tools!") # This message might be better on the dashboard
        return pd.DataFrame(columns=EXPECTED_COLUMNS)
    except Exception as e:
        st.error(f"Error loading data from CSV: {e}")
        return pd.DataFrame(columns=EXPECTED_COLUMNS)

def save_data(df):
    """Saves the DataFrame to the CSV file."""
    try:
        df_save = df.copy()
        if 'Date_Time' in df_save.columns and pd.api.types.is_datetime64_any_dtype(df_save['Date_Time']):
             df_save['Date_Time'] = df_save['Date_Time'].dt.strftime('%Y-%m-%d %H:%M:%S')
        
        # Convert new columns to string to avoid issues if they are all NA, especially cost
        if 'Subscription_Cost' in df_save.columns:
            df_save['Subscription_Cost'] = df_save['Subscription_Cost'].astype(str).replace('nan', '')


        df_save.to_csv(CSV_FILE_PATH, index=False)
        st.cache_data.clear() 
    except Exception as e:
        st.error(f"Error saving data to CSV: {e}")

def get_next_serial_number(df):
    """Calculates the next serial number."""
    if df.empty or 'Serial_Number' not in df.columns or df['Serial_Number'].isnull().all() or df['Serial_Number'].max() == 0: # Check for max 0 too
        return 1
    return int(df['Serial_Number'].max()) + 1

def add_entry(name, link, category, pricing_type, subscription_cost, uploaded_by, purpose):
    """Adds a new tool entry to the database."""
    df = load_data()
    
    if 'Serial_Number' not in df.columns or not pd.api.types.is_numeric_dtype(df['Serial_Number']) or (not df.empty and df['Serial_Number'].max() == 0 and len(df)>1) :
        df['Serial_Number'] = range(1, len(df) + 1)
        if not df.empty:
             st.warning("Serial_Number column integrity issue resolved.")

    next_sn = get_next_serial_number(df)
    
    new_entry_data = {
        "Serial_Number": next_sn,
        "Name": name,
        "Link": link,
        "Category": category,
        "Pricing_Type": pricing_type,
        "Subscription_Cost": subscription_cost if pricing_type in ["Paid", "Freemium"] else "",
        "Uploaded_By": uploaded_by,
        "Date_Time": datetime.datetime.now(),
        "Purpose": purpose
    }
    # Ensure all expected columns are present in the new entry
    for col in EXPECTED_COLUMNS:
        if col not in new_entry_data:
            new_entry_data[col] = pd.NA # Or appropriate default

    new_entry = pd.DataFrame([new_entry_data])
    
    df = pd.concat([df, new_entry], ignore_index=True)
    save_data(df)
    return True

def get_all_categories():
    """Gets all unique categories from the data, plus predefined ones."""
    df = load_data()
    data_categories = []
    if not df.empty and 'Category' in df.columns:
        data_categories = df['Category'].dropna().unique().tolist()
    
    # Late import to resolve circular dependency
    from utils import helpers 
    combined_categories = sorted(list(set(helpers.PREDEFINED_CATEGORIES + data_categories)))
    return combined_categories

# Import helpers here if not done above, or structure imports to avoid circularity
# from utils import helpers # Already done above