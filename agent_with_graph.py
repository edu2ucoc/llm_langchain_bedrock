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


# 5. 랭그래프 상태 (커스텀)
class AgentState(TypedDict):
    messages: List[BaseMessage]

# 6. 노드 정의
# 6-1. 사용자의 질의(말)을 듣고 생각하는 단계 구성 (메뉴 추천 + 도구 사용 결정)
def thinking_node(state:AgentState):
    # 6-1-1. 현재 상태의 프럼프트 실제 내용 획득 (페르소나+퓨샷+사용자질의)
    messages = state['messages']
    # 6-1-2. 랭체인구성 ( prompt + llm ) => 랭그래프의 특정 노드에 랭체인결합되어 있는 구조
    chain    = final_prompt | llm_with_tools
    # 6-1-3. LLM 질의 요청
    res      = chain.invoke( {"messages":messages} )
    return {"messages":[ res ]}

# 6-2. LLM이 도구 사용을 결정했다면 - 실제로 도구 사용 - 간단한 MCP개념 - RAG 호출
def tool_node(state:AgentState):
    print('tool_node 호출')
    # 툴사용 -> rag 이용한 검색증강
    last_msg = state['messages'][-1]
    # 툴사용 체크
    print('last_msg.tool_calls', last_msg.tool_calls)
    if last_msg.tool_calls: # 없으면 []
        tool = last_msg.tool_calls[0] # 등록된 도구가 1개 => 인덱스 번호 0번
        # 검색 증강 (백터디비 검색->유사도 1개획득(가게데이터)=>응답)
        # 사내 데이터 검색, 판례 검색, 
        '''
            last_msg.tool_calls [
                {
                    'name': 'rag_search', 
                    'args': {'cate': '가벼운 식사'}, 
                    'id': 'tooluse_HPRr7vMBQc2e5nG332Gfig',
                    'type': 'tool_call'
                }
            ]
        '''
        tool_output = rag_search.invoke( tool['args'] ) 
        # 해결 결과를 프럼프트에 추가
        print( tool_output )
        return {"messages":[ 
            HumanMessage(content=f'[사내데이터 검색결과]: {tool_output}\n 제공된 정보를 기반으로 최종 답변을 해주세요.')
        ]}
    return {"messages":[]}

# 6-3. 검색의 결과를 바탕으로 최종 답변(추론) 생성
def final_answer_node(state:AgentState):
    # 최종 프럼프트 획득(기존 주고 받은 내용 + 검생증강 내용)
    final_msg = state['messages']
    print('final_msg', final_msg)
    # LLM 질의 -> TOOL 필요 없음
    res = llm.invoke( final_msg )
    return {"messages":[ res ]}

# 7. 랭그래프 연결
workflow = StateGraph(AgentState) # 에이전트 상태 그래프 연동
workflow.add_node("thinking",       thinking_node)
workflow.add_node("tools",           tool_node)
workflow.add_node("final_answer",   final_answer_node)
workflow.set_entry_point("thinking") # 사용자 질의후 최초 invoke이 진입할 노드

def check_tool_node(state:AgentState): # 도구 사용 여부 체크 (초대형 LLM은 도구 사용 필요 거의 x)
    # LLM의 마지막 응답결과 추출 - 대화 내용중 마지막 내용은 LLM이 대답한 것임
    last_msg = state['messages'][-1]
    print( "1차 노드 수행후 LLM의 응답값 : ", last_msg)
    print( "1차 노드 수행후 도구 사용 여부 : ", last_msg.tool_calls)
    # 대답의 내용 구조중 툴에 대한 언급, 표현등이 있는지 체크 -> 
    # llm.bind_tools(tools) 사용으로 인해서 생기는 표현   -> 특정표식을 하게됨
    if last_msg.tool_calls: # 문자열로 툴에 대한 값이 세팅됨
        print('툴사용 -> 툴노드로 이동')
        return "tools"      # 커스텀 지정값(노드의 이름 지정) -> 툴노드로 가라는 의미
    return END # LLM의 답변으로 충분하다. 도구 사용 x, 대화를 마무리한다

workflow.add_conditional_edges("thinking", check_tool_node) # 조건부 엣
workflow.add_edge("tools","final_answer")
workflow.add_edge("final_answer",END)  # 추론과정 마무리

# 8. 랭그래프 컴파일 -> 워크 플로우 객체
# 랭그래프객체 => 전역변수
랭그래프객체 = workflow.compile()
