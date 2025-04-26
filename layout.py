import streamlit as st

def setup_page_config():
    """Sets up the basic Streamlit page configuration."""
    st.set_page_config(page_title="Chatyfile", page_icon="📄", layout="wide")


def apply_custom_styles():
    """Applies the custom CSS styles provided by the user."""
    st.markdown("""
        <style>
            .stApp {
                background-color: #f1f5f9;
                color: #1f2937;
                font-family: 'Inter', 'Segoe UI', sans-serif;
            }

            .header {
                text-align: center;
                margin-bottom: 20px;
            }

            .header img {
                border-radius: 12px;
                margin-bottom: 10px;
            }

            .chat-container {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                padding: 20px;
                max-height: 400px; /* Keep a max height with scroll */
                overflow-y: auto;
                margin-bottom: 10px;
                display: flex;
                flex-direction: column;
                gap: 10px;
            }

            .chat-message {
                padding: 10px;
                border-radius: 10px;
                max-width: 80%;
                word-wrap: break-word;
                /* Remove explicit width to allow flexbox to manage */
                /* width: fit-content; */
            }

            .user-message {
                background-color: #0077b5;
                color: white;
                align-self: flex-end;
                margin-left: auto; /* Push to the right */
            }

            .assistant-message {
                background-color: #e2e8f0;
                color: #1f2937;
                align-self: flex-start;
                margin-right: auto; /* Push to the left */
            }

            .input-container {
                background-color: #f1f5f9;
                padding-top: 10px;
                 /* Ensure input container doesn't interfere with main content width */
                 max-width: 800px; /* Match main content max-width */
                 margin-left: auto;
                 margin-right: auto;
            }

            .footer {
                text-align: center;
                margin-top: 30px;
                font-size: 0.8rem;
                color: #64748b;
            }

            .stButton > button {
                background-color: #0077b5;
                color: white;
                border: none;
                padding: 0.75em 1.5em;
                border-radius: 8px;
                font-size: 1rem;
                transition: background-color 0.3s;
            }

            .stButton > button:hover {
                background-color: #005f8d;
                color: white;
            }

            .stFileUploader {
                border: 2px dashed #0077b5;
                padding: 1rem;
                border-radius: 10px;
                background-color: #e6f0f8;
                text-align: center;
                color: #0077b5;
                font-weight: 600;
                font-size: 1rem;
            }

            .stFileUploader:hover {
                background-color: #d0e7f5;
                color: #005f8d;
            }

            /* Targeting the chat input specifically */
            /* Using a more specific selector based on Streamlit's structure */
            /* This might need adjustment based on F12 if it doesn't apply */
             div[data-testid="stChatInputTextArea"] textarea {
                 background-color: white !important;
                 color: #1f2937 !important;
                 border: 1px solid #cbd5e1 !important;
                 border-radius: 8px;
                 padding: 0.5em;
                 box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.05);
                 width: 100%; /* Ensure it takes available width */
                 box-sizing: border-box; /* Include padding and border in element's total width */
             }

             /* Style for the container holding the chat input elements */
             div[data-testid="stChatInput"] {
                 padding: 10px 0; /* Add some padding around the input area */
                 margin-top: 10px; /* Space above the input */
                 background-color: #f1f5f9; /* Match app background */
                 border-top: 1px solid #e2e8f0; /* Separator line */
             }


        </style>
    """, unsafe_allow_html=True)

def show_header():
    """Displays the application header with logo and title."""
    # Assuming you have a 'logo.jpeg' file in your app directory
    st.markdown('<div class="header">', unsafe_allow_html=True)
    try:
        st.image("logo.jpeg", width=500)
    except FileNotFoundError:
        st.warning("Logo file 'logo.jpeg' not found. Please add it to your project directory.")
    st.title("Chatyfile")
    st.caption("Tu asistente de análisis de datos CSV, rápido y sencillo.")
    st.markdown('</div>', unsafe_allow_html=True)

def show_footer():
    """Displays the application footer."""
    st.markdown('<div class="footer">© 2025 Chatyfile. Todos los derechos reservados. Propiedad intelectual protegida.</div>', unsafe_allow_html=True)

# Note: Functions for displaying chat history and getting input will be handled in app.py
# using Streamlit's built-in components and the custom CSS classes defined here.
