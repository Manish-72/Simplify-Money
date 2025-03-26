import streamlit as st
import requests
import pandas as pd
from io import StringIO
import os
import time

# Configuration
API_BASE_URL = "http://localhost:8000"  # Change in production
TEMP_UPLOAD_DIR = "./temp_uploads"
os.makedirs(TEMP_UPLOAD_DIR, exist_ok=True)

st.set_page_config(page_title="CSV Chat Analyzer", layout="wide")

# Initialize session state
if "conversation" not in st.session_state:
    st.session_state.conversation = []
if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None
if "file_id" not in st.session_state:
    st.session_state.file_id = None

# Sidebar - File Upload
with st.sidebar:
    st.header("File Management")
    upload_option = st.radio(
        "Upload Method",
        ["Direct Upload", "From Path"],
        help="Choose how to provide your CSV file"
    )

    if upload_option == "Direct Upload":
        uploaded_file = st.file_uploader(
            "Upload CSV File",
            type=["csv"],
            accept_multiple_files=False
        )
        if uploaded_file:
            # Save temporarily for preview
            temp_path = os.path.join(TEMP_UPLOAD_DIR, uploaded_file.name)
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.session_state.uploaded_file = temp_path
    else:
        file_path = st.text_input(
            "Enter CSV File Path",
            placeholder="/path/to/your/file.csv"
        )
        if file_path and os.path.exists(file_path):
            st.session_state.uploaded_file = file_path

    if st.session_state.uploaded_file:
        if st.button("Process File"):
            with st.spinner("Processing..."):
                try:
                    # Send to FastAPI
                    if upload_option == "Direct Upload":
                        files = {"file": open(st.session_state.uploaded_file, "rb")}
                        response = requests.post(
                            f"{API_BASE_URL}/upload",
                            files=files
                        )
                    else:
                        response = requests.post(
                            f"{API_BASE_URL}/upload",
                            data={"file_path": st.session_state.uploaded_file}
                        )
                    
                    if response.status_code == 200:
                        st.session_state.file_id = response.json()["file_id"]
                        preview_data = response.json().get("preview", [])
                        
                        st.success("File processed successfully!")
                        st.subheader("File Preview")
                        st.dataframe(pd.DataFrame(preview_data))
                    else:
                        st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
                
                except Exception as e:
                    st.error(f"Failed to process file: {str(e)}")

# Main Chat Interface
st.title("CSV Chat Analyzer")

if st.session_state.file_id:
    st.subheader("Chat with Your Data")
    
    # Display conversation history
    for msg in st.session_state.conversation:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            
            if msg.get("data"):
                st.dataframe(pd.DataFrame(msg["data"]))
    
    # User input
    if prompt := st.chat_input("Ask about your data..."):
        # Add user message to history
        st.session_state.conversation.append({
            "role": "user",
            "content": prompt
        })
        
        with st.chat_message("user"):
            st.write(prompt)
        
        # Get API response
        with st.spinner("Thinking..."):
            try:
                response = requests.post(
                    f"{API_BASE_URL}/query",
                    json={
                        "file_id": st.session_state.file_id,
                        "query": prompt,
                        "stream": False
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Add assistant response to history
                    st.session_state.conversation.append({
                        "role": "assistant",
                        "content": result["response"],
                        "data": result.get("relevant_data", [])
                    })
                    
                    # Display response
                    with st.chat_message("assistant"):
                        st.write(result["response"])
                        if result.get("relevant_data"):
                            st.subheader("Relevant Data")
                            st.dataframe(pd.DataFrame(result["relevant_data"]))
                else:
                    st.error(f"API Error: {response.json().get('detail', 'Unknown error')}")
            
            except Exception as e:
                st.error(f"Connection failed: {str(e)}")

else:
    st.info("Please upload and process a CSV file to start chatting")
    st.image("https://via.placeholder.com/600x300?text=Upload+CSV+to+Begin", use_column_width=True)

# Sidebar - File Management
with st.sidebar:
    if st.session_state.file_id:
        st.divider()
        st.subheader("File Actions")
        
        if st.button("Refresh Preview"):
            try:
                response = requests.get(
                    f"{API_BASE_URL}/file/{st.session_state.file_id}/preview"
                )
                if response.status_code == 200:
                    st.dataframe(pd.DataFrame(response.json()["preview"]))
                else:
                    st.error("Failed to get preview")
            except:
                st.error("Connection error")
        
        if st.button("Delete Current File", type="primary"):
            try:
                response = requests.delete(
                    f"{API_BASE_URL}/file/{st.session_state.file_id}"
                )
                if response.status_code == 200:
                    st.session_state.file_id = None
                    st.session_state.conversation = []
                    st.success("File deleted")
                    st.rerun()
                else:
                    st.error("Deletion failed")
            except:
                st.error("Connection error")

# Footer
st.sidebar.divider()
st.sidebar.markdown("""
**RAG CSV Analyzer**  
Version 1.0  
[API Docs](http://localhost:8000/docs)  
""")