'''
랭그래프 기반 LLM 사용에 대한 모듈
'''
from dotenv import load_dotenv
import os
load_dotenv()

from typing import TypedDict, List
from langgraph.graph import StateGraph, END, MessagesState, START
from langchain_core.tools import tool
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
tools = [ rag_search ] 

# 랭그래프 상태 (커스텀)
class AgentState(TypedDict):
    messages: List[BaseMessage]

# 노드 정의

# 랭그래프 연결
workflow = StateGraph(AgentState) # 에이전트 상태 그래프 연동

# 랭그래프 컴파일 -> 워크 플로우 객체
# 랭그래프객체 => 전역변수
랭그래프객체 = workflow.compile()
