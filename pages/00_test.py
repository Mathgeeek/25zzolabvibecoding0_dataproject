import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import plotly.express as px

st.set_page_config(layout="wide")

st.title("Python 인기 repository TOP 10 - 이슈 버블 차트(Bubble Chart)")

# GitHub 토큰은 secrets에서 불러옴 (Streamlit Cloud 권장 방식)
token = st.secrets["GITHUB_TOKEN"]

def get_top_repos_and_issues(token, language='python', top_n=10):
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
    items = r.json().get("items", [])
    data = []
    for repo in items:
        data.append({
            "이름": repo["full_name"],
            "Stars": repo["stargazers_count"],
            "오픈이슈수": repo["open_issues_count"],
            "Forks": repo["forks_count"],
            "설명": repo["description"],
            "링크": repo["html_url"]
        })
    return pd.DataFrame(data)

df = get_top_repos_and_issues(token)
st.dataframe(df)

st.markdown("## ⭐️ Bubble Chart: repository Stars, Issues, Forks")

fig = px.scatter(
    df,
    x="Stars",
    y="오픈이슈수",
    size="Forks",
    color="이름",
    hover_name="이름",
    hover_data=["설명", "링크"],
    title="Python TOP 10 레포지토리: Stars vs Open Issues (Bubble Chart)",
    size_max=60,
)

fig.update_layout(
    xaxis_title="Stars (별 개수)",
    yaxis_title="Open Issues (오픈 이슈 개수)"
)

st.plotly_chart(fig, use_container_width=True)

# TOP 3 오픈이슈수 순위 표기
st.markdown("### 🔥 오픈 이슈가 많은 TOP 3")
for i, row in df.sort_values(by="오픈이슈수", ascending=False).head(3).iterrows():
    st.markdown(f"- [{row['이름']}]({row['링크']}): 오픈 이슈 {row['오픈이슈수']}건, ⭐️ {row['Stars']}")


