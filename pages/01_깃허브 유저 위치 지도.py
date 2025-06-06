import streamlit as st
import pandas as pd
import requests
import folium
from streamlit_folium import st_folium

st.title("깃허브 레포 기여자 위치 지도")
repo = st.text_input("레포 전체 이름을 입력하세요 (예: python/cpython)", "python/cpython").strip()

st.write("입력 repo:", repo)  # 입력값 확인
st.write(f"API URL: https://api.github.com/repos/{repo}/contributors")  # API URL 확인

token = st.secrets.get("GITHUB_TOKEN")
headers = {"Authorization": f"token {token}"} if token else {}

def get_contributors(repo, top_n=15):
    url = f"https://api.github.com/repos/{repo}/contributors"
    r = requests.get(url, headers=headers)
    st.write("Contributors API status code:", r.status_code)  # 상태코드 출력
    if r.status_code != 200:
        st.error(f"깃허브 API 에러: {r.text}")
        return []
    return [item["login"] for item in r.json()][:top_n]

def get_location_coords(location):
    if not location:
        return None, None
    url = f"https://nominatim.openstreetmap.org/search?q={location}&format=json"
    try:
        res = requests.get(url)
        data = res.json()
        if data:
            return float(data[0]['lat']), float(data[0]['lon'])
    except Exception:
        return None, None
    return None, None

usernames = get_contributors(repo)
rows = []
for user in usernames:
    info = requests.get(f"https://api.github.com/users/{user}", headers=headers).json()
    loc = info.get("location")
    lat, lon = get_location_coords(loc)
    if lat and lon:
        rows.append({
            "user": user,
            "location": loc,
            "lat": lat,
            "lon": lon,
            "url": info.get("html_url"),
            "avatar_url": info.get("avatar_url"),
        })

df = pd.DataFrame(rows)
st.write(df)  # 데이터 확인용

if not df.empty:
    m = folium.Map(location=[df.lat.mean(), df.lon.mean()], zoom_start=2)
    for i, row in df.iterrows():
        html = f"""<a href="{row['url']}" target="_blank"><b>{row['user']}</b></a><br>
        <img src="{row['avatar_url']}" width="60"/><br>
        {row['location']}"""
        folium.Marker(
            location=[row['lat'], row['lon']],
            popup=folium.Popup(html, max_width=200)
        ).add_to(m)
    st_folium(m, width=700, height=500)
else:
    st.info("위치 정보가 있는 기여자가 없습니다.")
