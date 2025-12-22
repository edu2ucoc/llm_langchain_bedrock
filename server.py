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

# 4. LLM 관련 모든 작업
# 4-1. aws bedrock 접근 객체 획득(bedrock 등록된 모든 LLM사와 중계 담당)
bedrock_client = boto3.client(service_name = 'bedrock-runtime', 
                              region_name  = os.getenv('AWS_REGION')
                             )
# 4-2. bedrock를 통해서 특정(google, gemma) 회사 llm 객체(접근 권한을 가진) 획득
llm = ChatBedrockConverse(
    client = bedrock_client,
    model  = os.getenv('BEDROCK_MODEL_ID'),
    temperature = 0.7,
    max_tokens  = 500 # 비용 부분 해당
)

# 4-3. 프럼프트 엔지니어링 
#      => 개발사쪽에서 커스텀(고객의 질의 + 예시(퓨샷) + 페르소나 지정 + .... )
# 4-3-1. 퓨샷 샘플 준비 => 개발사 준비사항
#        LLM(AI)에게 몇개의 데이터(이런 상황에는 이렇게 응답하라고)를 주입하여 훈련
#        개발사의 의도대로 AI 방향성 설정
fewshot_samples = [
    # input => human, output: => ai 매칭 가능함
{
        "input": "오늘 점심 메뉴 추천해줘. 비가 오고 있어서 나가기 귀찮아. 혼자 먹을 거야.",
        "output": "비 오는 날, 집에서 편하게 즐길 수 있는 **'따뜻한 김치수제비와 해물파전'**을 추천합니다! 빗소리와 부침개 부치는 소리가 비슷해 감성을 자극하고, 칼칼한 국물은 가라앉은 기분을 전환해줄 거예요. 배달 앱을 이용하신다면 근처 칼국수 맛집의 세트 메뉴를 확인해보세요."
    },
    {
        "input": "직장 동료들 5명이랑 저녁 회식 메뉴 골라줘. 날씨는 맑고 다들 기분 최고야! 고기 종류면 좋겠어.",
        "output": "기분 좋은 저녁 회식에는 역시 **'제주 흑돼지 오겹살'**이 제격입니다! 5명이라면 고기를 직접 구워주는 전문점에 가셔서 편하게 대화를 나눠보세요. 맑은 날씨에 어울리는 시원한 '김치말이 국수'를 후식으로 곁들이면 완벽한 마무리가 될 거예요."
    },
    {
        "input": "내일 점심에 데이트가 있어. 날씨는 화창하대. 여자친구가 가벼운 걸 먹고 싶어 하는데 분위기 좋은 메뉴 없을까?",
        "output": "화창한 날 데이트라면 신선한 **'부라타 치즈 샐러드를 곁들인 바질 페스토 파스타'**는 어떨까요? 건강하고 가벼우면서도 색감이 예뻐 사진 찍기에도 좋습니다. 통창이 있는 이탈리안 레스토랑에서 화이트 와인 한 잔을 곁들이면 로맨틱한 분위기가 배가될 거예요."
    },
    {
        "input": "금요일 퇴근길인데 너무 스트레스 받아. 매운 거 먹고 싶은데 혼자 먹기 좋은 저녁 메뉴 추천해줘.",
        "output": "일주일 동안 정말 고생 많으셨어요! 스트레스를 한 방에 날려줄 **'마라탕과 꿔바로우 소(小)'**를 추천합니다. 원하는 재료를 듬뿍 넣어 아주 매운 단계로 즐겨보세요. 얼얼한 매운맛이 엔도르핀을 돌게 해줄 거예요. 시원한 캔맥주 하나 사서 집에서 넷플릭스를 보며 드시는 건 어떨까요?"
    }
]


# 5. pydantic => 요청 혹은 응답의 구조를 정의한 클레스 설계
#    요청 데이터를 => 특정 클레스로 바로 받아서 객체 생성
#    응답 데이터를 => 특정 클레스로 바로 세팅해서 객체 생성 => 응답
class UserRequest(BaseModel): # 4-1. BaseModel 클레스를 반드시 상속
    # 4-2. 구조 커스텀 설계 -> 맴버 구성
    question:str # 맴버명:타입힌트 => 클라이언트는 {"question":prompt} 보냄

# 6. API 엔드포인트 구성
@app.post('/chat')
def llm_endpoint( req:UserRequest):# req => 매개변수 :UserRequest => 타입힌트
    return {"response":f"에코 응답:{ req.question }"}
    # 5-1. `LLM 호출`하여 유저의 질의(프럼프트)를 전달 -> 결과를 받아서 -> 응답
