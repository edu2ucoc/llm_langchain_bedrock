import streamlit as st
import requests as req

# 전역설정
st.set_page_config(page_title='식사 메뉴 해결사')#, page_icon='')
st.title('AI 식사 메뉴 해결사 - 킹')
st.caption('예상, 점심/저녁등 시점, 날씨, 기분, 단체여부등 알려주시면 메뉴를 추천해 드립니다.')

# session state 초기화

# 이전 대화 내용 화면 출력

# ui
st.chat_input('현재 상황을 자세히 입력하세요...')