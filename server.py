# 1. 필요한 패키지 가져오기
#    api 구성 용도
from fastapi import FastAPI
from pydantic import BaseModel
#    AWS SDK로 bedrock 사용을 위해서
import boto3
#    환경변수 로드 -> os단 환경변수 세팅
from dotenv import load_dotenv
#    랭체인
#    llm 모델을 호출하는 객체
from langchain_aws import ChatBedrockConverse
#    프럼프트 구성
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
import os

# 2. 환경변수 로드
load_dotenv()
print( '사용모델 확인', os.getenv('BEDROCK_MODEL_ID') )

# 3. fastapi 앱 생성
app = FastAPI(title='식사 메뉴 추천 AI')

# 4. API 엔드포인트 구성
@app.post('/chat')
def llm_endpoint():
    return {"response":"에코 응답"}
