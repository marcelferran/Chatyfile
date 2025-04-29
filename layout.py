import streamlit as st

# Función para mostrar el encabezado
def show_header():
    st.markdown('<div class="header">', unsafe_allow_html=True)
    col1, col2 = st.columns([2, 1])  
    with col1:
        st.image("logo.jpeg", width=800) 
    st.markdown('</div>', unsafe_allow_html=True)

# Función para mostrar el pie de página
def show_footer():
    st.markdown("""
        <div class="footer">
            <p>© 2025 Chatyfile. Todos los derechos reservados. Propiedad intelectual protegida.</p>
        </div>
    """, unsafe_allow_html=True)

# Función para aplicar los estilos personalizados
def apply_custom_styles():
    st.markdown("""
        <style>
        .stApp { 
            background-color: #f0f2f6; 
        }
        .header {
            display: flex; 
            align-items: center; 
            padding: 20px;
            background-color: #1f77b4; 
            border-radius: 10px;
            margin-bottom: 20px;  /* Añadido margen inferior */
        }
        .header img { 
            margin-right16px; 
        }
        h1 { 
            color: #ffffff; 
            font-family: 'Arial', sans-serif; 
            margin: 0; 
        }
        .footer {
            text-align: center;  /* Centrado */
            padding: 15px; 
            background-color: #1f77b4;
            color: white; 
            border-top: 2px solid #ffffff;
            margin-top: 30px;  /* Margen superior */
            border-radius: 10px;
        }
        .main-container {
            background-color: #ffffff;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .summary-box {
            background-color: #f9f9f9;
            padding: 15px;
            border-radius: 8px;
            border: 1px solid #e0e0e0;
            margin-bottom: 20px;
        }
        .plot-container {
            max-width: 800px !important;
            margin: auto;
        }
        </style>
    """, unsafe_allow_html=True)

# Función para mostrar mensaje de bienvenida
def show_welcome_message():
    st.markdown("""
        <h3 style='text-align: center; color: #1f77b4;'>¡Bienvenido a Chatyfile!</h3>
        <p style='text-align: center;'>Sube tu archivo y preguntame sobre tus datos</p>
    """, unsafe_allow_html=True)

# Función para el cargador de archivo en el sidebar
def sidebar_file_uploader():
    with st.sidebar:
        st.header("🤖 DATOS")
        return st.file_uploader("Sube tu archivo", type=["csv"])
