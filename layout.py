import streamlit as st

def setup_page_config():
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
                max-height: 400px;
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
            }

            .user-message {
                background-color: #0077b5;
                color: white;
                align-self: flex-end;
                margin-left: auto;
            }

            .assistant-message {
                background-color: #e2e8f0;
                color: #1f2937;
                align-self: flex-start;
                margin-right: auto;
            }

            .input-container {
                background-color: #f1f5f9;
                padding-top: 10px;
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

            input[type="text"] {
                background-color: white !important;
                color: #1f2937 !important;
                border: 1px solid #cbd5e1 !important;
                border-radius: 8px;
                padding: 0.5em;
                box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.05);
            }
        </style>
    """, unsafe_allow_html=True)

def show_header():
    st.markdown('<div class="header">', unsafe_allow_html=True)
    st.image("logo.jpeg", width=500)
    st.title("Chatyfile")
    st.caption("Tu asistente de análisis de datos CSV, rápido y sencillo.")
    st.markdown('</div>', unsafe_allow_html=True)

def show_footer():
    st.markdown('<div class="footer">© 2025 Chatyfile. Todos los derechos reservados. Propiedad intelectual protegida.</div>', unsafe_allow_html=True)
