# utils/data_manager.py
import streamlit as st
import pandas as pd
import datetime
import os
# from utils import helpers # Loaded at the end if needed, or manage imports carefully

CSV_FILE_PATH = "ai_tools_database.csv" # You might want to rename this to align with your v1.0 (e.g., "data/ai_tools.csv")
# Ensure this path is consistent with where you want the file.
# If you used "data/ai_tools.xlsx" or "data/ai_tools.csv" in your v1.0, adjust CSV_FILE_PATH.

# This schema is from our "battle card" enhancement phase.
# If your v1.0 had a different schema, adjust this to match the columns you actually want to save and use.
EXPECTED_COLUMNS = [
    "Serial_Number", "Name", "Link", "Category", "Pricing_Type", 
    "Subscription_Cost", "Uploaded_By", "Date_Time", "Purpose"
]

def initialize_csv():
    """Creates the CSV file with headers if it doesn't exist."""
    # Check if the directory for CSV_FILE_PATH exists, create if not
    data_dir = os.path.dirname(CSV_FILE_PATH)
    if data_dir and not os.path.exists(data_dir): # Check if data_dir is not empty (i.e., not root)
        try:
            os.makedirs(data_dir, exist_ok=True)
        except OSError as e:
            st.error(f"Could not create data directory '{data_dir}': {e}")
            return # Stop if directory creation fails

    if not os.path.exists(CSV_FILE_PATH):
        try:
            df = pd.DataFrame(columns=EXPECTED_COLUMNS)
            df.to_csv(CSV_FILE_PATH, index=False)
        except Exception as e:
            st.error(f"Failed to initialize CSV file '{CSV_FILE_PATH}': {e}")

@st.cache_data(ttl=600) # Cache data for 10 minutes
def load_data():
    """Loads data from the CSV file with error handling and schema validation."""
    initialize_csv() 
    try:
        df = pd.read_csv(CSV_FILE_PATH)
        
        updated_csv = False
        current_columns = list(df.columns)

        for col in EXPECTED_COLUMNS:
            if col not in df.columns:
                df[col] = pd.NA
                updated_csv = True
        
        # If columns were added or order changed, re-order and save
        if updated_csv or [col for col in EXPECTED_COLUMNS if col in current_columns] != [col for col in current_columns if col in EXPECTED_COLUMNS]:
             # Ensure only expected columns are kept, in the right order
            df = df.reindex(columns=EXPECTED_COLUMNS, fill_value=pd.NA)
            if updated_csv: # Only show info if new columns were actually added
                st.info("Database schema updated. Columns have been adjusted/added.")
            # save_data(df) # Save immediately if schema changed (be careful with recursion if save_data calls load_data)
                           # It's generally safer to let the next save operation handle it or handle it post-load.


        if 'Date_Time' in df.columns:
            df['Date_Time'] = pd.to_datetime(df['Date_Time'], errors='coerce')
        else: # Should not happen if initialize_csv and validation work
            df['Date_Time'] = pd.NaT
            
        if 'Serial_Number' in df.columns and not df.empty:
            # Coerce to numeric, fill NA with 0 (for max() to work), then int.
            # If all are NA after coerce, fillna(0) makes max() return 0.
            df['Serial_Number'] = pd.to_numeric(df['Serial_Number'], errors='coerce').fillna(0).astype(int)

        return df.sort_values(by="Date_Time", ascending=False).reset_index(drop=True)

    except pd.errors.EmptyDataError:
        return pd.DataFrame(columns=EXPECTED_COLUMNS) # Return empty df with correct columns
    except FileNotFoundError:
        st.error(f"Data file '{CSV_FILE_PATH}' not found. A new one will be created on next save.")
        return pd.DataFrame(columns=EXPECTED_COLUMNS)
    except Exception as e:
        st.error(f"Error loading data from CSV '{CSV_FILE_PATH}': {e}")
        return pd.DataFrame(columns=EXPECTED_COLUMNS)

def save_data(df_to_save):
    """Saves the DataFrame to the CSV file."""
    if df_to_save is None:
        st.error("No data provided to save.")
        return False
    
    try:
        # Ensure the directory exists before saving
        data_dir = os.path.dirname(CSV_FILE_PATH)
        if data_dir and not os.path.exists(data_dir):
            os.makedirs(data_dir, exist_ok=True)

        df_save = df_to_save.copy()
        # Ensure Date_Time is string for CSV storage
        if 'Date_Time' in df_save.columns and pd.api.types.is_datetime64_any_dtype(df_save['Date_Time']):
             df_save['Date_Time'] = df_save['Date_Time'].dt.strftime('%Y-%m-%d %H:%M:%S')
        
        # Handle Subscription_Cost: convert to string, replace 'nan' from float NAs
        if 'Subscription_Cost' in df_save.columns:
            df_save['Subscription_Cost'] = df_save['Subscription_Cost'].astype(str).replace('nan', '').replace('<NA>', '')

        # Ensure only expected columns are saved, in the correct order
        df_final_to_write = df_save.reindex(columns=EXPECTED_COLUMNS, fill_value='') # Fill missing with empty string for CSV

        df_final_to_write.to_csv(CSV_FILE_PATH, index=False)
        st.cache_data.clear() # Clear cache after saving new data
        return True
    except Exception as e:
        st.error(f"Error saving data to CSV '{CSV_FILE_PATH}': {e}")
        return False

def get_next_serial_number(df):
    """Calculates the next serial number."""
    if df.empty or 'Serial_Number' not in df.columns or df['Serial_Number'].isnull().all() or df['Serial_Number'].max() == 0:
        return 1
    # Ensure we are taking max of integers
    valid_sns = pd.to_numeric(df['Serial_Number'], errors='coerce').dropna()
    if valid_sns.empty:
        return 1
    return int(valid_sns.max()) + 1

def add_entry(name, link, category, pricing_type, subscription_cost, uploaded_by, purpose):
    """Adds a new tool entry to the database."""
    df = load_data() # Load current data
    
    # Integrity check for Serial_Number (should be handled by load_data, but good to be defensive)
    if 'Serial_Number' not in df.columns or not pd.api.types.is_numeric_dtype(df['Serial_Number']):
        df['Serial_Number'] = pd.Series(range(1, len(df) + 1), dtype=int) if not df.empty else pd.Series(dtype=int)
        if not df.empty:
             st.warning("Serial_Number column integrity issue detected and resolved before adding new entry.")

    next_sn = get_next_serial_number(df)
    
    new_entry_data = {
        "Serial_Number": next_sn,
        "Name": name,
        "Link": link,
        "Category": category,
        "Pricing_Type": pricing_type,
        "Subscription_Cost": subscription_cost if pricing_type in ["Paid", "Freemium"] else "",
        "Uploaded_By": uploaded_by,
        "Date_Time": datetime.datetime.now(), # Store as datetime object initially
        "Purpose": purpose
    }
    
    # Ensure all EXPECTED_COLUMNS are present in the new entry dictionary for pd.DataFrame constructor
    for col in EXPECTED_COLUMNS:
        if col not in new_entry_data:
            new_entry_data[col] = pd.NA 

    new_entry_df = pd.DataFrame([new_entry_data])
    
    # Important: Realign columns of new_entry_df to match df (or EXPECTED_COLUMNS) before concat
    new_entry_df = new_entry_df.reindex(columns=df.columns if not df.empty else EXPECTED_COLUMNS, fill_value=pd.NA)

    df_updated = pd.concat([df, new_entry_df], ignore_index=True)
    
    if save_data(df_updated):
        return True
    else: # If save fails, we shouldn't consider the entry added
        return False

def get_all_categories():
    """Gets all unique categories from the data, plus predefined ones from helpers."""
    df = load_data()
    data_categories = []
    if not df.empty and 'Category' in df.columns:
        # Ensure categories are strings, drop NAs, get unique, convert to list
        data_categories = df['Category'].astype(str).str.strip().replace('', pd.NA).dropna().unique().tolist()
    
    from utils import helpers # Late import to avoid circularity if helpers imports data_manager
    # Combine, ensure uniqueness, and sort
    combined_categories = sorted(list(set(helpers.PREDEFINED_CATEGORIES + [cat for cat in data_categories if cat])))
    return combined_categories