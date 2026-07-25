import streamlit as st

st.set_page_config(
    page_title="Streamlit サンプル",
    page_icon="assets/icon.png",
    layout="wide",
)

st.logo("assets/logo.png", icon_image="assets/icon.png")

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

page = st.navigation(
    [
        st.Page("app_pages/home.py", title="Home", icon=":material/home:"),
        st.Page("app_pages/dashboard.py", title="Dashboard", icon=":material/monitoring:"),
        st.Page("app_pages/chatbot.py", title="Chatbot", icon=":material/chat:"),
    ],
    position="top",
)

page.run()
