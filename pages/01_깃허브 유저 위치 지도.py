import streamlit as st
import pandas as pd
import requests
import folium
from streamlit_folium import st_folium

st.title("깃허브 레포 기여자 위치 지도")

# 1. Streamlit으로 레포 경로 입력받기
repo = st.text_input("레포 전체 이름을 입력하세요 (예: python/cpython)", "python/cpython")

def get_contributors(repo, top_n=20):
    url = f"https://api.github.com/repos/{repo}/contributors"
    r = requests.get(url)
    if r.status_code != 200:
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

# 2. contributors 자동 추출
usernames = get_contributors(repo)

rows = []
for user in usernames:
    info = requests.get(f"https://api.github.com/users/{user}").json()
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
