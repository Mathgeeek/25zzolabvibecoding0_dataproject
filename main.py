import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import plotly.express as px

#...페이지 세팅
st.set_page_config(
    page_title="Github Top10",
    page_icon="👍",
    layout="wide",
)

#...폰트 설정
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Gowun+Batang&family=Noto+Serif+KR:wght@200..900&family=Orbit&family=Poor+Story&display=swap');
    html, body, [class*="css"]  {
        font-family: 'Orbit', sans-serif !important;
    }
    * {
        font-family: 'Orbit', sans-serif !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# 메인 페이지
# 페이지 이름: 🏠 대시보드

#...page title
st.title("GitHub 인기👍 repository TOP 10 (최근 1주일, Python)")

#...secrets에 저장된 토큰 불러오기
token = st.secrets["GITHUB_TOKEN"]

def get_github_trending_repos(token, language='python', top_n=10):
    last_week = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    url = "https://api.github.com/search/repositories"
    headers = {"Authorization": f"token {token}"}
    params = {
        "q": f"language:{language} created:>{last_week}",
        "sort": "stars",
        "order": "desc",
        "per_page": top_n
    }
    r = requests.get(url, headers=headers, params=params)
    if r.status_code != 200:
        st.error("API 호출 에러: " + str(r.text))
        return pd.DataFrame()
    items = r.json().get("items", [])
    data = []
    for repo in items:
        data.append({
            "이름": repo["full_name"],
            "설명": repo["description"],
            "Stars": repo["stargazers_count"],
            "Forks": repo["forks_count"],
            "링크": repo["html_url"]
        })
    return pd.DataFrame(data)

df = get_github_trending_repos(token)
if not df.empty:
    st.dataframe(df)
    fig = px.bar(df, x="이름", y="Stars", hover_data=["설명"], title="TOP 10 Star repository")
    st.plotly_chart(fig)
    st.markdown("---")
    for i, row in df.iterrows():
        st.markdown(f"- [{row['이름']}]({row['링크']}): ⭐ {row['Stars']} | {row['설명']}")
else:
    st.info("데이터를 불러올 수 없습니다. 토큰과 API 상태를 확인하세요.")
