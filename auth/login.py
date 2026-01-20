import streamlit as st
import base64
from auth.security import verify_password

guest_user = {
    "username": "guestuser",
    "password_hash": "$2b$12$3.PlxP4L.J6zKKUFWZodduhxWtKyGjyw57/2tL18XUVfdG47Eq4Gy"
        }
def load_bg_image(image_path):
    with open(image_path, "rb") as img:
        return base64.b64encode(img.read()).decode()

def login_page():
    bg_img = load_bg_image("data/stock_bg.jpg")

    st.markdown(
        f"""
        <style>
        /* Hide Streamlit header & footer */
        header {{visibility: hidden;}}
        footer {{visibility: hidden;}}

        .stApp {{
            background-image: url("data:image/jpg;base64,{bg_img}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }}

        .login-container {{
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            z-index: 9999;
        }}

        .login-box {{
            background: rgba(0, 0, 0, 0.78);
            padding: 2.5rem;
            border-radius: 14px;
            width: 380px;
            box-shadow: 0px 0px 40px rgba(0,0,0,0.9);
        }}

        .login-title {{
            text-align: center;
            font-size: 26px;
            color: white;
            margin-bottom: 25px;
            font-weight: bold;
        }}

        label {{
            color: white !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    st.markdown('<div class="login-title">📊 Stock Analytics Login</div>', unsafe_allow_html=True)

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login", use_container_width=True):
        if username == guest_user["username"] and verify_password(password, guest_user["password_hash"]):
            st.session_state["logged_in"] = True
            st.session_state["user"] = username
            st.rerun()
        else:
            st.error("Invalid username or password")

    st.markdown('</div></div>', unsafe_allow_html=True)

def logout_button():
    if st.sidebar.button("🚪 Logout"):
        st.session_state.clear()
        st.rerun()