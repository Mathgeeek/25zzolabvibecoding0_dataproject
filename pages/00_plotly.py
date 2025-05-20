import streamlit as st
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px

st.set_page_config(layout="wide")
st.title('서울시 인구 데이터 시각화 (Plotly, 한글지원)')

st.markdown("#### 먼저 두 CSV 파일을 업로드하세요.")
uploaded_total = st.file_uploader("1. 남여합계.csv 파일 업로드", type=['csv'], key="합계")
uploaded_gender = st.file_uploader("2. 남여구분.csv 파일 업로드", type=['csv'], key="구분")

if uploaded_total is not None and uploaded_gender is not None:
    # 데이터 읽기 (한글 깨짐 방지)
    try:
        df_total = pd.read_csv(uploaded_total, encoding='cp949')
        df_gender = pd.read_csv(uploaded_gender, encoding='cp949')
    except:
        df_total = pd.read_csv(uploaded_total, encoding='utf-8')
        df_gender = pd.read_csv(uploaded_gender, encoding='utf-8')
    
    # 연령 컬럼 리스트 자동 추출
    age_cols = [col for col in df_gender.columns if "남_0세" in col or "남_1세" in col]
    if not age_cols:
        age_cols = [col for col in df_gender.columns if "남_" in col and "세" in col]
    age_list = [col.replace("2025년04월_남_", "").replace("세", "").replace("_", "") for col in df_gender.columns if "남_" in col and "세" in col]

    # --- Streamlit select ---
    st.markdown("## 시각화 옵션 선택")
    opt = st.radio("아래에서 원하는 시각화 형태를 선택하세요.", 
                   ['① 서울시 전체 남녀 인구 피라미드', '② 구별 남녀 인구 피라미드', '③ 연령대별 인구 합계 Bar/Line'])

    # 서울시 전체/구별/동별 그룹 구분
    df_gender['구이름'] = df_gender['행정구역'].str.extract(r'([가-힣]+구)')

    # ---- 1. 서울시 전체 인구 피라미드 ----
    if opt.startswith('①'):
        st.subheader('서울시 전체 남녀 인구 피라미드')
        # 서울특별시 전체만 추출
        df_seoul = df_gender[df_gender['행정구역'].str.contains('서울특별시 ') & (~df_gender['행정구역'].str.contains('구'))].iloc[0]
        male_cols = [col for col in df_seoul.index if '남_' in col and '세' in col]
        female_cols = [col for col in df_seoul.index if '여_' in col and '세' in col]

        # 연령(숫자), 남/여 인구
        ages = [int(col.split('_')[2].replace('세','').replace('이상','100')) for col in male_cols]
        males = [-int(str(df_seoul[col]).replace(',','')) for col in male_cols]
        females = [int(str(df_seoul[col.replace('남_','여_')]).replace(',','')) for col in male_cols]

        fig = go.Figure()
        fig.add_trace(go.Bar(y=ages, x=males, name='남자', orientation='h', marker_color='blue'))
        fig.add_trace(go.Bar(y=ages, x=females, name='여자', orientation='h', marker_color='red'))
        fig.update_layout(
            yaxis=dict(title='연령', dtick=5),
            xaxis=dict(title='인구수'),
            barmode='relative',
            title='서울특별시 남녀 연령별 인구 피라미드',
            font=dict(family="Malgun Gothic, NanumGothic, sans-serif"), # 한글폰트!
            height=900
        )
        st.plotly_chart(fig, use_container_width=True)

    # ---- 2. 구별 피라미드 ----
    elif opt.startswith('②'):
        gu_list = sorted(df_gender['구이름'].dropna().unique())
        selected_gu = st.selectbox('구를 선택하세요.', gu_list)
        st.subheader(f'{selected_gu} 남녀 인구 피라미드')

        df_gu = df_gender[df_gender['행정구역'].str.contains(selected_gu) & (~df_gender['행정구역'].str.contains('동'))]
        if len(df_gu) == 0:
            st.error("구 데이터가 없습니다. 파일 구조를 확인하세요.")
        else:
            df_gu_row = df_gu.iloc[0]
            male_cols = [col for col in df_gu_row.index if '남_' in col and '세' in col]
            ages = [int(col.split('_')[2].replace('세','').replace('이상','100')) for col in male_cols]
            males = [-int(str(df_gu_row[col]).replace(',','')) for col in male_cols]
            females = [int(str(df_gu_row[col.replace('남_','여_')]).replace(',','')) for col in male_cols]

            fig = go.Figure()
            fig.add_trace(go.Bar(y=ages, x=males, name='남자', orientation='h', marker_color='blue'))
            fig.add_trace(go.Bar(y=ages, x=females, name='여자', orientation='h', marker_color='red'))
            fig.update_layout(
                yaxis=dict(title='연령', dtick=5),
                xaxis=dict(title='인구수'),
                barmode='relative',
                title=f'{selected_gu} 남녀 연령별 인구 피라미드',
                font=dict(family="Malgun Gothic, NanumGothic, sans-serif"),
                height=900
            )
            st.plotly_chart(fig, use_container_width=True)

    # ---- 3. 연령대별 인구 합계 ----
    elif opt.startswith('③'):
        st.subheader("연령대별 인구 합계 (전체/구별)")
        kind = st.radio("구별/전체 선택", ['서울시 전체', '구별'])
        # 연령 구간(10세 단위)
        bins = list(range(0, 101, 10)) + [150]
        bin_labels = [f"{b}~{b+9}세" for b in bins[:-2]] + ["100세 이상"]
        
        # 전체/구별 합계 테이블
        if kind == '서울시 전체':
            df_seoul = df_gender[df_gender['행정구역'].str.contains('서울특별시 ') & (~df_gender['행정구역'].str.contains('구'))].iloc[0]
            ages = [int(col.split('_')[2].replace('세','').replace('이상','100')) for col in df_seoul.index if '남_' in col and '세' in col]
            total = [int(str(df_seoul[col]).replace(',','')) + int(str(df_seoul[col.replace('남_','여_')]).replace(',','')) for col in df_seoul.index if '남_' in col and '세' in col]
            df_temp = pd.DataFrame({'연령': ages, '인구수': total})
            df_temp['연령대'] = pd.cut(df_temp['연령'], bins=bins, labels=bin_labels, right=False)
            df_group = df_temp.groupby('연령대')['인구수'].sum().reset_index()
            fig = px.bar(df_group, x='연령대', y='인구수', text='인구수', title='서울시 연령대별 인구 합계',
                         labels={'인구수': '인구수', '연령대': '연령대'})
            fig.update_layout(font=dict(family="Malgun Gothic, NanumGothic, sans-serif"), height=500)
            st.plotly_chart(fig, use_container_width=True)
        else:
            gu_list = sorted(df_gender['구이름'].dropna().unique())
            selected_gu = st.selectbox('구를 선택하세요.', gu_list)
            df_gu = df_gender[df_gender['행정구역'].str.contains(selected_gu) & (~df_gender['행정구역'].str.contains('동'))]
            if len(df_gu) == 0:
                st.error("구 데이터가 없습니다. 파일 구조를 확인하세요.")
            else:
                df_gu_row = df_gu.iloc[0]
                ages = [int(col.split('_')[2].replace('세','').replace('이상','100')) for col in df_gu_row.index if '남_' in col and '세' in col]
                total = [int(str(df_gu_row[col]).replace(',','')) + int(str(df_gu_row[col.replace('남_','여_')]).replace(',','')) for col in df_gu_row.index if '남_' in col and '세' in col]
                df_temp = pd.DataFrame({'연령': ages, '인구수': total})
                df_temp['연령대'] = pd.cut(df_temp['연령'], bins=bins, labels=bin_labels, right=False)
                df_group = df_temp.groupby('연령대')['인구수'].sum().reset_index()
                fig = px.bar(df_group, x='연령대', y='인구수', text='인구수', title=f'{selected_gu} 연령대별 인구 합계',
                             labels={'인구수': '인구수', '연령대': '연령대'})
                fig.update_layout(font=dict(family="Malgun Gothic, NanumGothic, sans-serif"), height=500)
                st.plotly_chart(fig, use_container_width=True)

    st.info('한글 폰트 깨짐 현상이 있으면 서버에 "Malgun Gothic" 또는 "NanumGothic" 한글 폰트를 설치하세요. 일반 윈도우/맥은 기본 지원됨!')
else:
    st.info("csv 두 개 모두 업로드해야 시각화할 수 있습니다.")

st.markdown("""
---
**문의 및 개선 요청**  
- 한글 깨짐/그래프 추가 요청은 언제든 환영합니다!
""")
