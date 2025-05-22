import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import plotly.express as px

st.set_page_config(layout="wide")
st.title("Python Best repository - 기여자별 커밋 수 분포")

token = st.secrets["GITHUB_TOKEN"]

def get_top_repo(token, language='python'):
    last_week = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    url = "https://api.github.com/search/repositories"
    headers = {"Authorization": f"token {token}"}
    params = {
        "q": f"language:{language} created:>{last_week}",
        "sort": "stars",
        "order": "desc",
        "per_page": 1
    }
    r = requests.get(url, headers=headers, params=params)
    items = r.json().get("items", [])
    if items:
        return items[0]["full_name"], items[0]["html_url"]
    return None, None

def get_contributors(token, repo_full_name, top_n=10):
    url = f"https://api.github.com/repos/{repo_full_name}/contributors"
    headers = {"Authorization": f"token {token}"}
    params = {"per_page": top_n}
    r = requests.get(url, headers=headers, params=params)
    contributors = r.json()
    data = []
    for user in contributors:
        data.append({
            "기여자": user["login"],
            "커밋수": user["contributions"],
            "프로필": user["html_url"],
            "avatar_url": user["avatar_url"],
        })
    return pd.DataFrame(data)

repo_full_name, repo_url = get_top_repo(token)

if repo_full_name:
    st.markdown(f"**Best Python repository:** [{repo_full_name}]({repo_url})")
    df_contrib = get_contributors(token, repo_full_name, top_n=15)
    st.dataframe(df_contrib)
    fig = px.bar(
        df_contrib,
        x="기여자",
        y="커밋수",
        hover_data=["프로필"],
        title=f"{repo_full_name}의 기여자별 커밋 수",
        color="기여자"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("#### 🏆 TOP 3 기여자 (프로필 사진 포함)")
    top3 = df_contrib.sort_values(by="커밋수", ascending=False).head(3)
    for i, row in top3.iterrows():
        st.markdown(
            f'<div style="display:flex;align-items:center;margin-bottom:1em">'
            f'<img src="{row["avatar_url"]}" width="48" style="border-radius:50%;margin-right:12px">'
            f'<a href="{row["프로필"]}" target="_blank" style="font-size:1.1em;font-weight:bold">{row["기여자"]}</a>'
            f'<span style="margin-left:12px;font-size:1em">({row["커밋수"]}회 커밋)</span>'
            f'</div>',
            unsafe_allow_html=True
        )
else:
    st.warning("레포지토리를 찾을 수 없습니다.")
