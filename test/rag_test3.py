'''
- 저장된 백터 디비 로드
- llm 이용한 rag 사용 => 검색 증강 => llm 모르는 내용을 데아터를 전달하여 추론
- 질의 -> 검색 -> 결과획득 -> 프럼프트(질의 + 검색결과) -> 추론요청 -> 응답 -> 확인
- 랭체인과 연동되어서 체인 구성(파이프라인)
'''
# 1. 모듈 가져오기
from langchain_community.vectorstores import FAISS
from langchain_aws import BedrockEmbeddings
import boto3
from dotenv import load_dotenv
import os
from langchain_aws import ChatBedrock
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()
AWS_REGION = os.getenv('AWS_REGION')
print( AWS_REGION )

# 임베딩모델(토크나이저 역활)
tokenizer = BedrockEmbeddings( model_id    = "amazon.titan-embed-text-v1", 
                               region_name = os.getenv('AWS_REGION') )
# **디비로드**
db = FAISS.load_local('hp_story', tokenizer, allow_dangerous_deserialization=True)
# 검색(유사도 테스트, 유사도가 가장 높은 문장 1개만 출력)-마지막만 출력(20글자)
print( db.similarity_search("해리포터의 친구")[0].page_content[-20:])

# 1. aws bedrock 클라이언트 구성
bedrock_client = boto3.client(
  service_name = 'bedrock-runtime',
  region_name  = AWS_REGION
)
# 2. llm 생성
llm = ChatBedrock(
    client   = bedrock_client,
    model_id = 'anthropic.claude-3-5-sonnet-20240620-v1:0', # os.getenv('BEDROCK_MODEL_ID'), 구글은 ChatBedrock 미지원
    model_kwargs = {
        "temperature": 0.7,
        "max_tokens" : 500
    }
)
# 3. prompt 구성
