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
#      RunnablePassthrough 질문을 검색하면서 동시에 사용자 질문을 세팅함
from langchain_core.runnables import RunnablePassthrough
#      StrOutputParser llm의 응답을 파싱하여 문자열만 추출 
from langchain_core.output_parsers import StrOutputParser

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
    model_id = 'openai.gpt-oss-120b-1:0', # os.getenv('BEDROCK_MODEL_ID'), 구글은 ChatBedrock 미지원
    model_kwargs = {
        "temperature": 0.7,
        "max_tokens" : 500
    }
)
# 3. prompt 구성
prompt = ChatPromptTemplate.from_template('''
다음의 제공된 context(문맥, 참고)을 사용하여 질문에 답변해 주세요.
만약, 문맥에서 답을 찾을 수 없다면, "잘 모르겠다"고 대답 하세요.
                                          
<context>
{context}
</context>
                                          
질문: {user_input}
''')

# 4. 체인 구성 : 초기스타일 <-> 최근 스타일:파이프 연산자(|) 사용하여 LCEL(Langchain Expression Language)
# 4-1. 리트리버 생성      : DB에서 유사도 높은 문서를 찾아온다 -> top 3 제한
retriever = db.as_retriever(search_kwargs={"k":3}) # 상위 3개 문서 참조
# 4-2. 문서 결합 체인     : 검색된 문서들을 프럼프트의 {context} 세팅한다
def format_docs(docs):
    # 탑 3개 검색 => 한문장으로 결합
    return "\n\n".join(doc.page_content for doc in docs)
# 4-3. 최종 RAG 체인 구성 : 질문->검색->프럼프트 결합->LLM 질의->답변획득
rag_chain = (
    {"context": retriever | format_docs, "user_input": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# --- 8. 실행 ---
query = "해리포터의 적은?"
print(f"질문: {query}\n")

response = rag_chain.invoke(query)

print("=== AI 답변 ===" )
print(response)
