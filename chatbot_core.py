"""Chatbot ページとダッシュボードの常駐ウィジェットで共有するロジック。"""

import time
from collections.abc import Iterator

SUGGESTIONS = {
    ":material/monitoring: Dashboard について教えて": "Dashboard ページでは何ができますか？",
    ":material/home: Home について教えて": "Home ページでは何ができますか？",
    ":material/help: Streamlit とは？": "Streamlit とは何ですか？",
}


def get_response(prompt: str) -> str:
    """ユーザーの入力に対する応答を返す。

    デモ用のキーワードマッチング実装。実際のLLM (Anthropic API など) に
    差し替える場合はこの関数の中身を置き換える。
    """
    text = prompt.lower()
    if "dashboard" in text or "ダッシュボード" in prompt:
        return (
            "Dashboard ページでは、ユーザー数・セッション数・売上・注文数のKPIと"
            "時系列チャートを確認できます。期間セレクタで表示範囲を絞り込めます。"
        )
    if "home" in text or "ホーム" in prompt:
        return "Home ページはこのアプリの入り口です。Dashboard と Chatbot へのリンクや概要を表示します。"
    if "streamlit" in text:
        return "Streamlit は Python だけでインタラクティブな Web アプリを構築できるフレームワークです。"
    if any(greeting in text for greeting in ["こんにちは", "hello", "hi"]):
        return "こんにちは！何かお手伝いできることはありますか？"
    return "すみません、まだその質問には答えられません。「Dashboard」「Home」「Streamlit」について聞いてみてください。"


def stream_response(text: str) -> Iterator[str]:
    for word in text.split(" "):
        yield word + " "
        time.sleep(0.02)
