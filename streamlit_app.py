import base64
import streamlit as st
import requests
import os

# Set the API base URL
if os.getenv('ENV') == 'prod':
    API_BASE_URL = "http://app:8000/v1"
else:
    API_BASE_URL = "http://localhost:8000/v1"
    
# Initialize session state
if "pdf_id" not in st.session_state:
    st.session_state.pdf_id = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = {}
if "new_chat" not in st.session_state:
    st.session_state.new_chat = False

def upload_pdf(file):
    url = f"{API_BASE_URL}/pdf"
    files = {"file": (file.name, file.getvalue(), "application/pdf")}
    response = requests.post(url, files=files)
    return response 

def chat_with_pdf(pdf_id, message):
    url = f"{API_BASE_URL}/chat/{pdf_id}"
    payload = {"message": message}
    response = requests.post(url, json=payload)
    return response

def get_chat_history(pdf_id):
    url = f"{API_BASE_URL}/history/{pdf_id}"
    response = requests.get(url)
    return response

def delete_chat_history(pdf_id):
    url = f"{API_BASE_URL}/history/{pdf_id}"
    response = requests.delete(url)
    return response

def get_documents():
    url = f"{API_BASE_URL}/pdf/all"
    response = requests.get(url)
    return response

def get_static_pdf(pdf_id):
    url = f"{API_BASE_URL.rstrip('v1')}/static/{pdf_id}.pdf"
    response = requests.get(url)
    return response

def displayPDF(pdf_id):
    response = get_static_pdf(pdf_id)
    if response.status_code == 200:
        base64_pdf = base64.b64encode(response.content).decode("utf-8")
        pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf">'
        st.markdown(pdf_display, unsafe_allow_html=True)
    else:
        st.error(f"Failed to retrieve PDF file. Status code: {response.status_code}")

st.title("PDF Chat Application")

# Sidebar for uploaded PDFs
if st.sidebar.button("New chat", use_container_width=True):
    st.session_state.new_chat = True
    st.session_state.pdf_id = None
    st.session_state.chat_history = {}

if st.session_state.new_chat:    
    uploaded_file = st.file_uploader("Upload a PDF file (only one upload allowed)", type=["pdf"])
    if uploaded_file is not None and not st.session_state.pdf_id:
        if st.button("Upload PDF"):
            response = upload_pdf(uploaded_file)
            if response.status_code == 202:
                pdf_id = response.json().get("pdf_id")
                st.session_state.pdf_id = pdf_id
                st.success("PDF uploaded successfully! Please wait for document to be processed (50~ seconds at most)")
                st.rerun()  # Refresh the app to update the view
            else:
                st.error(f"Error uploading PDF: {response.status_code}")
            st.session_state.new_chat = False

st.sidebar.header("Uploaded PDFs")
response = get_documents()
for pdf_id in response.json():
    if st.sidebar.button(str(pdf_id)):
        st.session_state.pdf_id = pdf_id
        st.session_state.new_chat = False
        st.session_state.chat_history = {}

if st.session_state.pdf_id:
    pdf_id = st.session_state.pdf_id

    st.subheader(pdf_id)

    history_response = get_chat_history(pdf_id)
    if history_response.status_code == 200:
        history = history_response.json()
        st.session_state.chat_history = [(item[1], item[0]) for item in history]
    else:
         st.session_state.chat_history = {}

    if st.session_state.chat_history:
        if st.button("Clear Chat History"):
            response = delete_chat_history(pdf_id)
            if response.status_code == 206:
                st.session_state.chat_history = []
                st.success("Chat history cleared successfully!")
            else:
                st.error("Error deleting chat history.")

        for chat in st.session_state.chat_history:
            align = "right" if chat[1] == "human" else "left"
            background_color = "#3c3c3c" if chat[1] == "human" else "#1f1f1f"
            st.markdown(
                f'<div style="text-align: {align}; margin: 20px 0 5px 0;">{chat[1]}</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div style="text-align: {align}; padding: 20px 10px; background: {background_color}; border-radius: 20px;">{chat[0]}</div>',
                unsafe_allow_html=True,
            )

    message = st.text_area("Chat with the PDF")
    if st.button("Send") and message:
        response = chat_with_pdf(pdf_id, message)
        st.rerun()  # Refresh the app to update the chat history

    displayPDF(pdf_id)
