import streamlit as st

def apply_custom_styles():
    st.markdown("""
        <style>
        .stApp { background-color: #f0f2f6; }
        .header {
            display: flex; align-items: center; padding: 10px;
            background-color: #1f77b4; border-radius: 10px;
        }
        .header img { width: 400px; margin-right: 20px; }
        h1 { color: #ffffff; font-family: 'Arial', sans-serif; margin: 0; }
        .footer {
            text-align: center; padding: 10px; background-color: #1f77b4;
            color: white; position: fixed; bottom: 0; width: 100%;
            border-top: 2px solid #ffffff;
        }
        </style>
    """, unsafe_allow_html=True)

def show_header():
    st.markdown('<div class="header">', unsafe_allow_html=True)
    st.image("logo.jpeg", width=400)
    st.title("📄 Chatyfile")
    st.markdown('</div>', unsafe_allow_html=True)

def show_footer():
    st.markdown("""
        <div class="footer">
            <p>© 2025 Chatyfile. Todos los derechos reservados. Propiedad intelectual protegida.</p>
        </div>
    """, unsafe_allow_html=True)

def show_welcome_message():
    st.markdown("""
        <h3 style='text-align: center; color: #1f77b4;'>¡Bienvenido a Chatyfile!</h3>
        <p style='text-align: center;'>Sube tu archivo y haz preguntas sobre tus datos</p>
    """, unsafe_allow_html=True)

def sidebar_file_uploader():
    with st.sidebar:
        st.header("🤖 DATOS")
        return st.file_uploader("Sube tu archivo", type=["csv"])
