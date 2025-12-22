# vectordb에 거대한 말뭉치 삽입
# 말뭉치 -> 특정 크기의 청크 단위로 분할해서 처리 ->토큰제한
# 최근 LLM은 거대한양 입력 가능함( 백터 디비의 크기 단위 체크 필요)

# 1. 모듈 가져오기
from langchain_community.vectorstores import FAISS
from langchain_aws import BedrockEmbeddings
import boto3
from dotenv import load_dotenv
import os
#    대량의 말뭉치(문서들) 로드, 특정 단위로 분할
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()
AWS_REGION = os.getenv('AWS_REGION')
print( AWS_REGION )

# 2. 파일 목록 가져오기
#    [ "xxx.txt", "", ..]
import glob
#    경로법은 상대경로인 이상 프로젝트 루트부터 경로를 따짐
file_paths = glob.glob('./test/data/*.txt')
#print( file_paths )

# 3. TextLoader를 이용하여 문서 로드
raw_docs = [ TextLoader( file, encoding='utf-8').load() for file in file_paths ] 
print( "파일로드 완료", len(raw_docs), raw_docs[0] )

# 4. 텍스트 분할 (특정 크기의 청크 단위로 데이터를 분할하여 준비)
#    성능을 위해 적절한 크기 설정 필요
splitter = RecursiveCharacterTextSplitter(
    chunk_size    = 512, #  자를 문자수 
    chunk_overlap = 100  # 문맥 유지를 위해 겹치는 구간
)
splites = splitter.split_documents( raw_docs )
# print( "총 청크수 ", len(splites), splites[0] )
