# 검색 증강 생성 - RAG 

# 1. 모듈 가져오기
#    백터 디비
from langchain_community.vectorstores import FAISS
#    말뭉치 => 토큰화를 통한 백터 처리 => 토크나이저
from langchain_aws import BedrockEmbeddings
#    aws sdk
import boto3
#    환경변수
from dotenv import load_dotenv
import os

# 1-1 환경변수 로드
load_dotenv()

# 2. 데이터 준비
#    더미 임시 데이터. 짧게 구성
data = ["맥도널드 대표 제품은 빅맥이다",
        "버거킹의 대표 제품은 와퍼이다.",
        "맘스터치의 대표 제품은 휠레버거이다",
        "롯데리아의 대표 제품은 새우버거이다"]

# 3. 임베딩(말뭉치 => 분절화 => (사전화는 이미되어 있음) 백터화 => 패딩 => 임베딩)
tokenizer = BedrockEmbeddings( model_id    = "amazon.titan-embed-text-v1", 
                               region_name = os.getenv('AWS_REGION') )

# 4. 백터 디비에 토큰화된 내용을 입력
db = FAISS.from_texts( data, tokenizer ) # 디비 생성 완료, 데이터 삽입 완료

# 5. 백터 디비 => 검색 => 유사도 검사 후 응답
docs = db.similarity_search('버거킹의 대표 버거는?')

# 6. 검색 결과 확인
print( docs[0].page_content ) # 유사도 순으로 데이터가 검색되어 출력됨(docs)
# 의미론적으로 가장 가까중 의미를 가진 데이터 출력


