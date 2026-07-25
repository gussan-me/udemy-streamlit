import streamlit as st

st.title(":material/home: Home")
st.caption("このアプリでできること")

st.write(
    "サイドバー上部のナビゲーションから各ページに移動できます。"
    "以下はそれぞれのページの概要です。"
)

col_dashboard, col_chatbot = st.columns(2, border=True)

with col_dashboard:
    st.subheader(":material/monitoring: Dashboard")
    st.write("主要指標（KPI）と時系列チャートを確認できます。")
    st.page_link("app_pages/dashboard.py", label="Dashboard を開く", icon=":material/arrow_forward:")

with col_chatbot:
    st.subheader(":material/chat: Chatbot")
    st.write("このアプリについて質問できるチャットボットです。")
    st.page_link("app_pages/chatbot.py", label="Chatbot を開く", icon=":material/arrow_forward:")

st.space("large")

with st.container(border=True):
    st.markdown("**このサンプルについて**")
    st.write(
        "Home / Dashboard / Chatbot の3ページで構成されたマルチページ Streamlit アプリのサンプルです。"
        " `st.navigation` と `st.Page` を使ってページを切り替えています。"
    )
