import streamlit as st
import requests
import pandas as pd

def main():
    st.set_page_config(page_title="My Fleet Management App", layout="wide")
    st.title("Welcome to the Fleet Management System")
    st.write("""
        This is the **main page** of your multi-page Streamlit app.
        Use the navigation in the sidebar to explore:
        
        - **Car Sheet**: Detailed metrics and KPIs for each car
        - **Dashboard**: Overview with selected metrics and visualizations
    """)

if __name__ == "__main__":
    main()

st.title("Fleet Management System 🚛")

# Load API Key from Secrets
api_key = st.secrets["baserow"]["api_key"]
base_url = "https://api.baserow.io/api/database/rows/table/"
table_id = "463683"  # Your Cars table ID
endpoint = f"{base_url}{table_id}/?user_field_names=true"

headers = {
    "Authorization": f"Token {api_key}",
    "Content-Type": "application/json",
}

def fetch_baserow_data():
    """Fetch data from Baserow API"""
    response = requests.get(endpoint, headers=headers)
    if response.status_code == 200:
        return response.json()["results"]
    else:
        st.error(f"Error fetching data: {response.status_code}")
        return None

# Fetch data
data = fetch_baserow_data()

if data:
    df = pd.DataFrame(data)  # Convert JSON to DataFrame

    # Ensure correct column names based on your Baserow fields
    expected_columns = [
        "License Plate", "Make", "Model", "Year", "Status", "Total Kilometers",
        "Total Revenue", "Maintenance Cost", "Profitability", "Next Service Due (km)",
        "Next Service Due (date)", "Created On", "Active"
    ]

    # Remove unexpected fields (if any)
    df = df[[col for col in expected_columns if col in df.columns]]

    # ✅ FIX: Convert "Status" from a dictionary to a string
    if "Status" in df.columns:
        df["Status"] = df["Status"].apply(lambda x: x.get("value") if isinstance(x, dict) else x)

    # Show data in an interactive table
    st.subheader("Vehicle Data")
    st.dataframe(df)  # Use Streamlit's interactive dataframe

    # Add search functionality
    search_query = st.text_input("Search by License Plate or Model")

    if search_query:
        df = df[df["License Plate"].str.contains(search_query, case=False, na=False) |
                df["Model"].str.contains(search_query, case=False, na=False)]

    # ✅ FIX: Status Filter
    if "Status" in df.columns:
        status_options = df["Status"].dropna().unique().tolist()
        status_filter = st.selectbox("Filter by Status", ["All"] + status_options)

        if status_filter != "All":
            df = df[df["Status"] == status_filter]

    st.dataframe(df)  # Show filtered results
