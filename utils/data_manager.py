import streamlit as st
import pandas as pd
import datetime
import os

CSV_FILE_PATH = "ai_tools_database.csv"
EXPECTED_COLUMNS = ["Serial_Number", "Name", "Category", "Uploaded_By", "Date_Time", "Purpose"]

def initialize_csv():
    """Creates the CSV file with headers if it doesn't exist."""
    if not os.path.exists(CSV_FILE_PATH):
        try:
            df = pd.DataFrame(columns=EXPECTED_COLUMNS)
            df.to_csv(CSV_FILE_PATH, index=False)
        except Exception as e:
            st.error(f"Failed to initialize CSV file: {e}")
            # If initialization fails, it's a critical error, might want to stop the app or handle appropriately.
            # For now, we'll let Streamlit show the error.

@st.cache_data(ttl=600) # Cache data for 10 minutes
def load_data():
    """Loads data from the CSV file with error handling and schema validation."""
    initialize_csv() # Ensure file exists
    try:
        df = pd.read_csv(CSV_FILE_PATH)
        # Validate columns - if file exists but is malformed
        if not all(col in df.columns for col in EXPECTED_COLUMNS):
            st.warning(f"CSV file has missing columns. Re-initializing. Expected: {EXPECTED_COLUMNS}, Found: {list(df.columns)}. Please check your CSV or it will be reset.")
            # Option: Try to fix or just re-initialize
            df_template = pd.DataFrame(columns=EXPECTED_COLUMNS) # Create a template
            # For any existing valid columns, try to preserve data, otherwise fill with NaN or default
            for col in EXPECTED_COLUMNS:
                if col not in df.columns:
                    df[col] = pd.NA # Or some default
            df = df[EXPECTED_COLUMNS] # Reorder and select expected columns
            df.to_csv(CSV_FILE_PATH, index=False) # Save corrected structure

        # Convert Date_Time to datetime objects, handling potential errors
        if 'Date_Time' in df.columns:
            df['Date_Time'] = pd.to_datetime(df['Date_Time'], errors='coerce')
        else: # Should not happen if initialize_csv and validation work
            df['Date_Time'] = pd.NaT

        return df.sort_values(by="Date_Time", ascending=False).reset_index(drop=True)

    except pd.errors.EmptyDataError:
        st.info("Database is empty. Add some tools!")
        return pd.DataFrame(columns=EXPECTED_COLUMNS)
    except Exception as e:
        st.error(f"Error loading data from CSV: {e}")
        return pd.DataFrame(columns=EXPECTED_COLUMNS) # Return empty df on error

def save_data(df):
    """Saves the DataFrame to the CSV file."""
    try:
        # Ensure Date_Time is in a consistent string format for CSV
        df_save = df.copy()
        if 'Date_Time' in df_save.columns and pd.api.types.is_datetime64_any_dtype(df_save['Date_Time']):
             df_save['Date_Time'] = df_save['Date_Time'].dt.strftime('%Y-%m-%d %H:%M:%S')

        df_save.to_csv(CSV_FILE_PATH, index=False)
        st.cache_data.clear() # Clear cache after saving new data
    except Exception as e:
        st.error(f"Error saving data to CSV: {e}")

def get_next_serial_number(df):
    """Calculates the next serial number."""
    if df.empty or 'Serial_Number' not in df.columns or df['Serial_Number'].isnull().all():
        return 1
    return int(df['Serial_Number'].max()) + 1

def add_entry(name, category, uploaded_by, purpose):
    """Adds a new tool entry to the database."""
    df = load_data()
    
    # Ensure Serial_Number column exists and is numeric, otherwise reset (edge case for corrupted file)
    if 'Serial_Number' not in df.columns or not pd.api.types.is_numeric_dtype(df['Serial_Number']):
        df['Serial_Number'] = range(1, len(df) + 1) # Basic re-numbering if corrupted
        if not df.empty:
             st.warning("Serial_Number column was missing or non-numeric. It has been reset.")


    next_sn = get_next_serial_number(df)
    
    new_entry = pd.DataFrame([{
        "Serial_Number": next_sn,
        "Name": name,
        "Category": category,
        "Uploaded_By": uploaded_by,
        "Date_Time": datetime.datetime.now(), # Store as datetime object
        "Purpose": purpose
    }])
    
    df = pd.concat([df, new_entry], ignore_index=True)
    save_data(df)
    return True

def get_all_categories():
    """Gets all unique categories from the data, plus predefined ones."""
    df = load_data()
    data_categories = []
    if not df.empty and 'Category' in df.columns:
        data_categories = df['Category'].dropna().unique().tolist()
    
    # Combine predefined with data categories and ensure uniqueness
    combined_categories = sorted(list(set(helpers.PREDEFINED_CATEGORIES + data_categories)))
    return combined_categories

# Import helpers at the end to avoid circular dependency if helpers imports data_manager
from utils import helpers