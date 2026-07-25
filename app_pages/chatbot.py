import streamlit as st
from chatbot_core import SUGGESTIONS, get_response, stream_response

with st.container(horizontal=True, horizontal_alignment="distribute", vertical_alignment="center"):
    st.title(":material/chat: Chatbot")
    if st.button(":material/restart_alt: 会話をリセット", type="tertiary"):
        st.session_state.chat_messages = []
        st.rerun()

st.caption("このアプリについて質問できるアシスタントです（デモ用のルールベース応答）")

for msg in st.session_state.chat_messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

prompt = None

if not st.session_state.chat_messages:
    selected = st.pills(
        "こんな質問はいかがですか？", list(SUGGESTIONS.keys()), label_visibility="collapsed"
    )
    if selected:
        prompt = SUGGESTIONS[selected]

prompt = prompt or st.chat_input("質問を入力してください")

if prompt:
    st.session_state.chat_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        response = st.write_stream(stream_response(get_response(prompt)))

    st.session_state.chat_messages.append({"role": "assistant", "content": response})
