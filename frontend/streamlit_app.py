import streamlit as st
import requests
import pandas as pd
import time

st.set_page_config(
    page_title="DB QueryPilot AI",
    page_icon="🗄️",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_BASE_URL = "http://localhost:8000"

if 'selected_database' not in st.session_state:
    st.session_state.selected_database = None
if 'query_history' not in st.session_state:
    st.session_state.query_history = []
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

# Toggle Dark Mode Function
def toggle_dark_mode():
    st.session_state.dark_mode = not st.session_state.dark_mode

# Dynamic CSS based on theme
if st.session_state.dark_mode:
    # Dark Mode CSS
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
        
        * {
            font-family: 'Poppins', sans-serif;
        }
        
        .stApp {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        }
        
        .main-header {
            font-size: 3.5rem;
            font-weight: 700;
            text-align: center;
            background: linear-gradient(135deg, #00d4ff 0%, #7b2ff7 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 1rem;
            animation: fadeInDown 0.8s ease-in-out;
        }
        
        .subtitle {
            text-align: center;
            color: #a0aec0;
            font-size: 1.2rem;
            margin-bottom: 3rem;
        }
        
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        }
        
        [data-testid="stSidebar"] .stSelectbox label,
        [data-testid="stSidebar"] .stMarkdown,
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] p {
            color: white !important;
        }
        
        /* Fix dropdown text visibility */
        [data-testid="stSidebar"] [data-baseweb="select"] > div {
            background-color: rgba(255, 255, 255, 0.9) !important;
            color: #1a202c !important;
        }
        
        [data-testid="stSidebar"] [data-baseweb="select"] input {
            color: #1a202c !important;
        }
        
        .info-card {
            background: linear-gradient(135deg, #00d4ff 0%, #7b2ff7 100%);
            padding: 1.5rem;
            border-radius: 15px;
            color: white;
            margin-bottom: 1rem;
            box-shadow: 0 10px 30px rgba(0, 212, 255, 0.3);
        }
        
        .table-card {
            background: rgba(255, 255, 255, 0.05);
            padding: 2rem;
            border-radius: 20px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
            margin-bottom: 2rem;
            border: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
        }
        
        .stButton>button {
            width: 100%;
            border-radius: 10px;
            font-weight: 600;
            transition: all 0.3s ease;
            border: none;
            padding: 0.75rem 1.5rem;
        }
        
        [data-testid="stMetricValue"] {
            font-size: 2rem;
            font-weight: 700;
            color: #00d4ff !important;
        }
        
        [data-testid="stMetricLabel"] {
            color: #a0aec0 !important;
        }
        
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: rgba(255, 255, 255, 0.05);
            padding: 0.5rem;
            border-radius: 10px;
        }
        
        .stTabs [data-baseweb="tab"] {
            border-radius: 8px;
            padding: 0.5rem 1.5rem;
            font-weight: 600;
            color: #a0aec0;
        }
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #00d4ff 0%, #7b2ff7 100%);
            color: white !important;
        }
        
        .stDataFrame {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 10px;
        }
        
        h1, h2, h3, h4, h5, h6, p, label, .stMarkdown {
            color: white !important;
        }
        
        @keyframes fadeInDown {
            from { opacity: 0; transform: translateY(-20px); }
            to { opacity: 1; transform: translateY(0); }
        }
    </style>
    """, unsafe_allow_html=True)
else:
    # Light Mode CSS
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
        
        * {
            font-family: 'Poppins', sans-serif;
        }
        
        .main-header {
            font-size: 3.5rem;
            font-weight: 700;
            text-align: center;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 1rem;
            animation: fadeInDown 0.8s ease-in-out;
        }
        
        .subtitle {
            text-align: center;
            color: #718096;
            font-size: 1.2rem;
            margin-bottom: 3rem;
        }
        
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #1e3a8a 0%, #312e81 100%);
        }
        
        [data-testid="stSidebar"] .stSelectbox label,
        [data-testid="stSidebar"] .stMarkdown,
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] p {
            color: white !important;
        }
        
        /* Fix dropdown text visibility */
        [data-testid="stSidebar"] [data-baseweb="select"] > div {
            background-color: white !important;
            color: #1a202c !important;
        }
        
        [data-testid="stSidebar"] [data-baseweb="select"] input {
            color: #1a202c !important;
        }
        
        .info-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1.5rem;
            border-radius: 15px;
            color: white;
            margin-bottom: 1rem;
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        }
        
        .table-card {
            background: white;
            padding: 2rem;
            border-radius: 20px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
            margin-bottom: 2rem;
            border: 1px solid #e2e8f0;
        }
        
        .stButton>button {
            width: 100%;
            border-radius: 10px;
            font-weight: 600;
            transition: all 0.3s ease;
            border: none;
            padding: 0.75rem 1.5rem;
        }
        
        [data-testid="stMetricValue"] {
            font-size: 2rem;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: #f7fafc;
            padding: 0.5rem;
            border-radius: 10px;
        }
        
        .stTabs [data-baseweb="tab"] {
            border-radius: 8px;
            padding: 0.5rem 1.5rem;
            font-weight: 600;
        }
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white !important;
        }
        
        @keyframes fadeInDown {
            from { opacity: 0; transform: translateY(-20px); }
            to { opacity: 1; transform: translateY(0); }
        }
    </style>
    """, unsafe_allow_html=True)

# Header with Dark Mode Toggle
col1, col2, col3 = st.columns([1, 3, 1])
with col1:
    if st.button("🌓 Toggle Theme"):
        toggle_dark_mode()
        st.rerun()

with col2:
    st.markdown('<div class="main-header">🗄️ DB QueryPilot AI</div>', unsafe_allow_html=True)

st.markdown('<div class="subtitle">Powered by AI • Natural Language to SQL • Real-time Database Access</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    
    # API Health Check
    try:
        health = requests.get(f"{API_BASE_URL}/health", timeout=3).json()
        st.markdown(f"""
        <div class="info-card">
            <h4>✅ System Status</h4>
            <p><strong>API:</strong> {health['status'].upper()}</p>
        </div>
        """, unsafe_allow_html=True)
    except Exception as e:
        st.error("❌ API not reachable!")
        st.stop()
    
    st.divider()
    
    # Table Selection
    st.markdown("### 📊 Select Table")
    try:
        databases_response = requests.get(f"{API_BASE_URL}/databases", timeout=3)
        if databases_response.status_code == 200:
            databases = databases_response.json()
            
            if databases and databases != ["default"]:
                selected_db = st.selectbox(
                    "Choose table:",
                    databases,
                    key="database_selector",
                    label_visibility="collapsed"
                )
                st.session_state.selected_database = selected_db
                
                st.info(f"📋 Active: **{selected_db}**")
            else:
                st.error("⚠️ No tables found!")
                st.stop()
    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.stop()
    
    st.divider()
    
    # Query History
    st.markdown("### 📜 Recent Queries")
    if st.session_state.query_history:
        for i, query in enumerate(reversed(st.session_state.query_history[-5:])):
            with st.expander(f"Query #{len(st.session_state.query_history) - i}", expanded=False):
                st.markdown(f"**Prompt:** {query['prompt'][:60]}...")
                st.code(query['sql'], language="sql")
    else:
        st.info("No queries yet")
    
    if st.button("🗑️ Clear History"):
        st.session_state.query_history = []
        st.rerun()
    
    st.divider()
    
    # Quick Reference Guide
    with st.expander("📖 Quick Reference", expanded=False):
        st.markdown("""
        **Required Fields by Table:**
        
        **Users Table:**
        - username (required)
        - email (required)  
        - full_name (required)
        - is_active (optional, default: 1)
        
        **Products Table:**
        - name (required)
        - price (required)
        - description (optional)
        - stock_quantity (optional)
        - category (optional)
        
        **Orders Table:**
        - user_id (required)
        - product_id (required)
        - quantity (required)
        - total_price (required)
        - status (optional)
        """)

if not st.session_state.selected_database:
    st.warning("⚠️ Select a table from sidebar")
    st.stop()

# Database Overview - ALL ROWS, NO SCHEMA
st.markdown("## 📊 Database Tables")

try:
    tables_response = requests.get(f"{API_BASE_URL}/databases", timeout=3)
    
    if tables_response.status_code == 200:
        all_tables = tables_response.json()
        
        if len(all_tables) > 0 and all_tables != ["default"]:
            tab_list = st.tabs([f"📋 {table.upper()}" for table in all_tables])
            
            for idx, table_name in enumerate(all_tables):
                with tab_list[idx]:
                    try:
                        # Fetch ALL data (no limit)
                        all_data_query = {
                            "prompt": f"SELECT * FROM {table_name}",
                            "database_name": table_name,
                            "execute": True
                        }
                        
                        data_response = requests.post(
                            f"{API_BASE_URL}/query",
                            json=all_data_query,
                            timeout=10
                        )
                        
                        if data_response.status_code == 200:
                            result = data_response.json()
                            
                            if result.get('success') and result.get('results'):
                                df_all = pd.DataFrame(result['results'])
                                
                                # Show metrics
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.metric("📊 Total Records", f"{len(df_all):,}")
                                with col2:
                                    st.metric("📋 Columns", len(df_all.columns))
                                with col3:
                                    st.metric("✅ Status", "Active")
                                
                                st.divider()
                                
                                # Display ALL data
                                st.dataframe(
                                    df_all,
                                    width='stretch',
                                    hide_index=False,
                                    height=500
                                )
                                
                                # Download button
                                csv = df_all.to_csv(index=False)
                                st.download_button(
                                    label=f"📥 Download {table_name} as CSV",
                                    data=csv,
                                    file_name=f"{table_name}_data.csv",
                                    mime="text/csv"
                                )
                            else:
                                st.warning("No data in this table")
                        else:
                            st.error("Failed to fetch data")
                            
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        else:
            st.error("No tables found")
            
except Exception as e:
    st.error(f"Error: {str(e)}")

st.divider()

# Query Interface
st.markdown("## 💬 Natural Language Query")

user_prompt = st.text_area(
    "What would you like to know?",
    placeholder="Example: Show all active users\nExample: Products with price > 100\nExample: Recent orders",
    height=100
)

col1, col2 = st.columns(2)
with col1:
    generate_btn = st.button("🔍 Generate SQL Only", type="secondary", key="gen_btn")
with col2:
    execute_btn = st.button("▶️ Generate & Execute", type="primary", key="exec_btn")

if generate_btn or execute_btn:
    if not user_prompt:
        st.error("⚠️ Please enter a query")
    else:
        with st.spinner("🤖 Processing..."):
            try:
                payload = {
                    "prompt": user_prompt,
                    "database_name": st.session_state.selected_database,
                    "execute": execute_btn
                }
                
                response = requests.post(f"{API_BASE_URL}/query", json=payload, timeout=15)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if result['success']:
                        st.markdown("### 📝 Generated SQL")
                        st.code(result['sql_query'], language="sql")
                        
                        st.info(f"💡 {result['explanation']}")
                        
                        st.session_state.query_history.append({
                            'prompt': user_prompt,
                            'sql': result['sql_query']
                        })
                        
                        if result.get('results'):
                            st.markdown("### 📊 Results")
                            
                            df_results = pd.DataFrame(result['results'])
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("📈 Rows", len(df_results))
                            with col2:
                                st.metric("📋 Columns", len(df_results.columns))
                            with col3:
                                st.metric("⏱️ Status", "Success")
                            
                            st.dataframe(df_results, width='stretch', height=400)
                            
                            csv = df_results.to_csv(index=False)
                            st.download_button(
                                label="📥 Download CSV",
                                data=csv,
                                file_name=f"results_{int(time.time())}.csv",
                                mime="text/csv"
                            )
                        
                        st.success(f"✅ {result['message']}")
                    else:
                        st.error(f"❌ {result['message']}")
                        
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

st.divider()

# Modifications
st.markdown("## ✏️ Database Modifications")
st.warning("⚠️ Changes are permanent!")

# Example queries
with st.expander("💡 Example Modification Queries", expanded=False):
    st.markdown("""
    **Add New User:**
    ```
    Add a new user with username ghanshyam_joshi, email gs@example.com, and full_name Ghanshyam Joshi
    ```
    
    **Update Product:**
    ```
    Update the price to 1599.99 for product with id 1
    ```
    
    **Delete Order:**
    ```
    Delete orders where status is cancelled and id is 5
    ```
    
    **Update User Status:**
    ```
    Set is_active to 0 for user with username charlie_davis
    ```
    """)

modification_prompt = st.text_area(
    "Modification Query:",
    placeholder="Example: Add new user with username john_doe, email john@test.com, and full_name John Doe\nExample: Update product price to 150 where id is 5\nExample: Delete orders where status is cancelled",
    height=100
)

col1, col2 = st.columns([1, 2])
with col1:
    confirm = st.checkbox("✅ Confirm")
with col2:
    if st.button("🔧 Execute", disabled=not confirm, key="mod_btn"):
        if not modification_prompt:
            st.error("Enter a query")
        else:
            with st.spinner("Executing..."):
                try:
                    # Get table schemas first
                    schema_response = requests.get(f"{API_BASE_URL}/tables/{st.session_state.selected_database}", timeout=5)
                    
                    payload = {
                        "prompt": modification_prompt,
                        "database_name": st.session_state.selected_database
                    }
                    
                    response = requests.post(f"{API_BASE_URL}/execute", json=payload, timeout=20)
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        st.markdown("### Generated SQL")
                        st.code(result['sql_query'], language="sql")
                        st.success(result['message'])
                        
                        if 'affected_rows' in result:
                            st.metric("✅ Rows Affected", result['affected_rows'])
                        
                        st.info("🔄 Refresh the page to see changes in the database")
                        
                    else:
                        error_msg = response.text
                        
                        # Check for specific errors and provide helpful messages
                        if "NOT NULL constraint failed" in error_msg:
                            st.error("❌ Missing required fields!")
                            
                            # Extract which field is missing
                            if "FULL_NAME" in error_msg:
                                st.warning("💡 Tip: When adding a user, you must provide username, email, AND full_name")
                                st.info("Try: Add new user with username john_doe, email john@example.com, and full_name John Doe")
                            else:
                                st.warning("💡 Make sure to provide all required fields for this table")
                        else:
                            st.error(f"Failed to execute: {error_msg}")
                        
                except Exception as e:
                    st.error(f"Error: {str(e)}")

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; padding: 2rem 0;'>
    <p style='color: #94a3b8; font-size: 0.9rem;'>
        🚀 Powered by <strong>OpenAI GPT-4</strong> • <strong>LangChain</strong> • <strong>FastAPI</strong>
    </p>
</div>
""", unsafe_allow_html=True)