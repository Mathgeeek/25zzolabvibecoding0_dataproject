import streamlit as st
import yfinance as yf
import plotly.graph_objs as go
from datetime import datetime, timedelta

# 글로벌 시가총액 Top 4 기업 (2024년 기준)
companies = {
    "Apple": "AAPL",
    "Microsoft": "MSFT",
    "Nvidia": "NVDA",
    "Alphabet (Google)": "GOOGL",
}

# 1년 전 날짜 구하기
end_date = datetime.today()
start_date = end_date - timedelta(days=365)

# 데이터 불러오기
data = {}
for name, ticker in companies.items():
    df = yf.download(ticker, start=start_date, end=end_date)
    data[name] = df['Close']

# Plotly 그래프 생성
fig = go.Figure()
for name in companies.keys():
    fig.add_trace(go.Scatter(x=data[name].index, y=data[name].values, mode='lines', name=name))

fig.update_layout(
    title='글로벌 시가총액 TOP 4 (Apple, Microsoft, Nvidia, Alphabet) 최근 1년 주가 변화',
    xaxis_title='날짜',
    yaxis_title='종가 (USD)',
    hovermode='x unified',
    template='plotly_white'
)

st.title("글로벌 시가총액 Top 4 기업의 최근 1년 주가 변화")
st.plotly_chart(fig, use_container_width=True)

