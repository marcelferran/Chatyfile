import streamlit as st

def apply_custom_styles():
    st.markdown("""
        <style>
            .stApp {
                background-color: #0f172a;
                color: #ffffff;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            .header {
                text-align: center;
                margin-bottom: 20px;
            }
            .chat-container {
                height: 400px;
                overflow-y: auto;
                padding: 10px;
                background-color: #1e293b;
                border-radius: 10px;
                margin-bottom: 10px;
            }
            .input-container {
                position: sticky;
                bottom: 0;
                background-color: #0f172a;
                padding-top: 10px;
            }
            .footer {
                text-align: center;
                margin-top: 20px;
                font-size: 0.8rem;
                color: #94a3b8;
            }
        </style>
    """, unsafe_allow_html=True)

def show_header():
    st.markdown('<div class="header">', unsafe_allow_html=True)
    st.image("logo.jpeg", width=400)
    st.title("Chatyfile 📄🔵")
    st.markdown('</div>', unsafe_allow_html=True)

def show_footer():
    st.markdown('<div class="footer">© 2025 Chatyfile. Todos los derechos reservados. Propiedad intelectual protegida.</div>', unsafe_allow_html=True)
