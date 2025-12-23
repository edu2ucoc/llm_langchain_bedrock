'''
랭그래프 기반 LLM 사용에 대한 모듈
'''
from dotenv import load_dotenv
import os
load_dotenv()

from typing import TypedDict, List
from langgraph.graph import StateGraph, END, MessagesState, START
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
from langchain_core.messages import HumanMessage, BaseMessage
from langchain_aws import ChatBedrockConverse, ChatBedrock
from langgraph.prebuilt import ToolNode, tools_condition
from tools import rag_search

# 1. LLM 모델 구성, client 생략
llm = ChatBedrockConverse(model      = os.getenv('BEDROCK_MODEL_ID'),
                         region_name = os.getenv('AWS_REGION'),
                         temperature = 0.5,
                         max_tokens  = 1000)

# 2. 외부 도구 가져오기 및 llm에 등록
tools          = [ rag_search ] 
llm_with_tools = llm.bind_tools(tools)

# 3. 퓨샷   프럼프트 -> 참고용
examples = [
    {"input":"비 오는날 국물이 땡겨",              "output":"국룰이죠. 칼국수와 잔치국수가 좋습니다."},
    {"input":"다이어트를 위해 오늘 칼로리 낮은것으로","output":"관리하시는군요. 닭가슴, 샐러드 드세요"},
]
example_format = ChatPromptTemplate.from_messages([
  ('human',"{input}"),
  ('ai',   "{output}")
])
few_shot_prompt = FewShotChatMessagePromptTemplate(
  examples       = examples,
  example_prompt = example_format
)
# 4. 시스템 프럼프트
final_prompt = ChatPromptTemplate.from_messages([
    # 페르소나
    # 도구 사용 => 현재는 rag => rag에는 LLM 모르는 식당 정보 준비되어 있음.
    ('system','당신의 센스 있는 식사 메뉴 추천 전문가입니다. 사용자의 상황에 맞춰서 메뉴를 추천하고, 필요하면 도구를 사용하여 식당을 찾으세요'),
    # 퓨샷
    few_shot_prompt,
    # 사용자 입력
    ('human','{messages}')
])


# 랭그래프 상태 (커스텀)
class AgentState(TypedDict):
    messages: List[BaseMessage]

# 노드 정의

# 랭그래프 연결
workflow = StateGraph(AgentState) # 에이전트 상태 그래프 연동

# 랭그래프 컴파일 -> 워크 플로우 객체
# 랭그래프객체 => 전역변수
랭그래프객체 = workflow.compile()
