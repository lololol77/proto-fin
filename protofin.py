# 장애 유형과 직무 능력 매칭 프로그램

import pandas as pd
import streamlit as st
import sqlite3

# SQLite 데이터베이스 경로
db_path = 'db1.sqlite'

# DB1 초기화 (SQLite 사용)
def load_db1():
    conn = sqlite3.connect(db_path)
    query = 'SELECT * FROM abilities'
    df = pd.read_sql(query, conn)
    conn.close()
    return df

db1 = load_db1()

# Streamlit 세션 상태로 DB 관리
if 'db2' not in st.session_state:
    st.session_state['db2'] = pd.DataFrame(columns=['회사명', '업무이름', '요구능력'])
if 'response' not in st.session_state:
    st.session_state['response'] = ''

db2 = st.session_state['db2']

# 회사 정보 등록 함수
def register_job(company, job_name, required_abilities):
    new_entry = pd.DataFrame([[company, job_name, ', '.join(required_abilities)]], columns=['회사명', '업무이름', '요구능력'])
    st.session_state['db2'] = pd.concat([st.session_state['db2'], new_entry], ignore_index=True)
    st.success('일자리 등록 완료')

# 지원자 정보 입력 및 매칭 함수
def match_job(name, disability_type, disability_degree):
    matching_results = []
    for _, row in st.session_state['db2'].iterrows():
        company, job_name, abilities = row['회사명'], row['업무이름'], row['요구능력'].split(', ')
        score = 0
        for ability in abilities:
            ability_score = db1[(db1['능력'] == ability) & (db1['장애유형'] == disability_type) & (db1['정도'] == disability_degree)]['점수'].sum()
            score += ability_score
        matching_results.append((company, job_name, score))
    matching_results.sort(key=lambda x: x[2], reverse=True)
    return matching_results

# 기업에게 적합한 장애유형 추천 함수
def recommend_disability(required_abilities):
    recommendations = []
    for ability in required_abilities:
        best_fit = db1[db1['능력'] == ability].sort_values(by='점수', ascending=False).iloc[0]
        recommendations.append((ability, best_fit['장애유형'], best_fit['정도']))
    return recommendations

# Streamlit UI 구현
st.title('ABLEMATCH"')

user_type = st.selectbox('사용자 유형을 선택하세요', ['회사', '지원자'])

if user_type == '회사':
    company = st.text_input('회사명')
    job_name = st.text_input('업무이름')
    abilities = st.multiselect('요구 능력 선택', db1['능력'].unique())
    if st.button('일자리 등록'):
        register_job(company, job_name, abilities)
        recommendations = recommend_disability(abilities)
        st.write("가장 적합한 장애유형 추천:")
        for ability, disability_type, level in recommendations:
            st.write(f'능력: {ability}, 추천 장애유형: {disability_type}, 장애 정도: {level}')

elif user_type == '지원자':
    name = st.text_input('이름')
    disability_type = st.selectbox('장애 유형', db1['장애유형'].unique())
    disability_degree = st.selectbox('장애 정도', ['심하지 않은', '심한'])
    if st.button('매칭 결과 확인'):
        results = match_job(name, disability_type, disability_degree)
        for company, job_name, score in results:
            st.write(f'회사: {company}, 업무: {job_name}, 적합도 점수: {score}')

# 유료 서비스 확인
if st.button('유료서비스'):
    st.session_state['response'] = ''

if st.session_state['response'] == '':
    if user_type == '회사':
        st.session_state['response'] = st.radio('유료 직무개발 서비스 이용하시겠습니까?', ['예', '아니오'])
    elif user_type == '지원자':
        st.session_state['response'] = st.radio('유료 취업확인 서비스 이용하시겠습니까?', ['예', '아니오'])

if st.session_state['response'] != '':
    st.button('확인')
