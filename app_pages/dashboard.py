import hashlib
from datetime import date, timedelta

import altair as alt
import numpy as np
import pandas as pd
from streamlit_float import float_css_helper, float_init

import streamlit as st
from chatbot_core import get_response, stream_response

TIME_RANGES = ["1M", "6M", "1Y", "QTD", "YTD", "All"]
CHART_HEIGHT = 300
CHAT_PANEL_HEIGHT = "26rem"


def generate_metric_data(
    metric_name: str,
    start_date: date,
    end_date: date,
    base_value: float = 1000,
    growth_rate: float = 0.001,
    noise_factor: float = 0.1,
) -> pd.DataFrame:
    """合成の時系列データを生成する。実際はDB/APIからの取得に置き換える。"""
    seed = int(hashlib.sha256(metric_name.encode()).hexdigest(), 16) % 2**32
    rng = np.random.default_rng(seed)

    dates = pd.date_range(start=start_date, end=end_date, freq="D")
    n_days = len(dates)

    trend = base_value * (1 + growth_rate) ** np.arange(n_days)
    day_of_week = dates.dayofweek
    seasonality = np.where(day_of_week >= 5, 0.7, 1.0)
    trend *= seasonality

    noise = rng.normal(1, noise_factor, n_days)
    values = trend * noise

    df = pd.DataFrame({"ds": dates, "value": values})
    df["value_7d_ma"] = df["value"].rolling(7, min_periods=1).mean()
    return df


@st.cache_data(ttl=3600)
def load_all_metrics() -> dict[str, pd.DataFrame]:
    end_date = date.today() - timedelta(days=1)
    start_date = end_date - timedelta(days=365)

    return {
        "users": generate_metric_data("users", start_date, end_date, base_value=5000, growth_rate=0.002),
        "sessions": generate_metric_data(
            "sessions", start_date, end_date, base_value=15000, growth_rate=0.003
        ),
        "revenue": generate_metric_data(
            "revenue", start_date, end_date, base_value=50000, growth_rate=0.001
        ),
        "orders": generate_metric_data("orders", start_date, end_date, base_value=800, growth_rate=0.0015),
    }


def filter_by_time_range(df: pd.DataFrame, x_col: str, time_range: str) -> pd.DataFrame:
    """time_range に応じてデータフレームを絞り込む。"""
    if time_range == "All" or df.empty:
        return df

    df = df.copy()
    df[x_col] = pd.to_datetime(df[x_col])
    max_date = df[x_col].max()

    if time_range == "1M":
        min_date = max_date - timedelta(days=30)
    elif time_range == "6M":
        min_date = max_date - timedelta(days=180)
    elif time_range == "1Y":
        min_date = max_date - timedelta(days=365)
    elif time_range == "QTD":
        quarter_month = ((max_date.month - 1) // 3) * 3 + 1
        min_date = pd.Timestamp(date(max_date.year, quarter_month, 1))
    elif time_range == "YTD":
        min_date = pd.Timestamp(date(max_date.year, 1, 1))
    else:
        return df

    filtered: pd.DataFrame = df[df[x_col] >= min_date]
    return filtered


def render_line_chart(df: pd.DataFrame, height: int = CHART_HEIGHT) -> alt.Chart:
    return (
        alt.Chart(df)
        .mark_line()
        .encode(
            x=alt.X("ds:T", title=None),
            y=alt.Y("value:Q", title=None, scale=alt.Scale(zero=False)),
            tooltip=[
                alt.Tooltip("ds:T", title="Date", format="%Y-%m-%d"),
                alt.Tooltip("value:Q", title="Value", format=",.0f"),
            ],
        )
        .properties(height=height)
    )


def compute_delta(df: pd.DataFrame) -> tuple[float, float]:
    """直近値と、直近7日平均に対する変化率を返す。"""
    latest = df["value"].iloc[-1]
    baseline = df["value_7d_ma"].iloc[-8] if len(df) > 8 else df["value_7d_ma"].iloc[0]
    pct_change = (latest - baseline) / baseline * 100 if baseline else 0
    return latest, pct_change


def render_page_header(title: str) -> None:
    with st.container(horizontal=True, horizontal_alignment="distribute", vertical_alignment="center"):
        st.markdown(title)
        time_range = st.segmented_control(
            "期間", options=TIME_RANGES, default="1M", key="dashboard_time_range"
        )
    return time_range or "1M"


def render_floating_chatbot() -> None:
    """画面右下に常駐するフローティングチャットボットを描画する (streamlit-float)。"""
    if "dashboard_chat_open" not in st.session_state:
        st.session_state.dashboard_chat_open = False

    if st.session_state.dashboard_chat_open:
        panel = st.container(border=True)
        with panel:
            with st.container(
                horizontal=True, horizontal_alignment="distribute", vertical_alignment="center"
            ):
                st.markdown("**:material/chat: Chatbot**")
                if st.button(":material/close:", key="dashboard_chat_close", type="tertiary"):
                    st.session_state.dashboard_chat_open = False
                    st.rerun()

            messages = st.container(height=200)
            with messages:
                for msg in st.session_state.chat_messages:
                    with st.chat_message(msg["role"]):
                        st.write(msg["content"])

            prompt = st.chat_input("質問を入力してください", key="dashboard_chat_input")

        panel.float(
            float_css_helper(
                width="22rem",
                height=CHAT_PANEL_HEIGHT,
                right="2rem",
                bottom="6rem",
                background="var(--default-backgroundColor)",
                shadow=9,
                z_index="998",
            )
        )

        if prompt:
            st.session_state.chat_messages.append({"role": "user", "content": prompt})
            with messages, st.chat_message("user"):
                st.write(prompt)
            with messages, st.chat_message("assistant"):
                response = st.write_stream(stream_response(get_response(prompt)))
            st.session_state.chat_messages.append({"role": "assistant", "content": response})
            st.rerun()

    toggle = st.container()
    with toggle:
        icon = ":material/close:" if st.session_state.dashboard_chat_open else ":material/chat:"
        if st.button(icon, key="dashboard_chat_toggle", type="primary"):
            st.session_state.dashboard_chat_open = not st.session_state.dashboard_chat_open
            st.rerun()
    toggle.float(
        float_css_helper(
            width="3.2rem",
            right="2rem",
            bottom="2rem",
            shadow=9,
            z_index="999",
        )
    )


float_init()

metrics_data = load_all_metrics()

time_range = render_page_header("# :material/monitoring: Dashboard")

filtered = {name: filter_by_time_range(df, "ds", time_range) for name, df in metrics_data.items()}

with st.container(horizontal=True):
    for label, key, fmt in [
        ("Active Users", "users", "{:,.0f}"),
        ("Sessions", "sessions", "{:,.0f}"),
        ("Revenue", "revenue", "${:,.0f}"),
        ("Orders", "orders", "{:,.0f}"),
    ]:
        df = filtered[key]
        latest, pct_change = compute_delta(df)
        st.metric(
            label,
            fmt.format(latest),
            f"{pct_change:+.1f}%",
            border=True,
            chart_data=df["value"].tolist(),
            chart_type="line",
        )

col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.subheader("Users")
        st.altair_chart(render_line_chart(filtered["users"]))

with col2:
    with st.container(border=True):
        st.subheader("Revenue")
        st.altair_chart(render_line_chart(filtered["revenue"]))

with st.container(border=True):
    st.subheader("Recent data")
    recent = filtered["orders"].rename(
        columns={"ds": "Date", "value": "Orders", "value_7d_ma": "7-day avg"}
    )
    st.dataframe(recent, hide_index=True)

render_floating_chatbot()
