from langgraph.graph import StateGraph, END, MessagesState, START
from typing import TypedDict
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langchain_aws import ChatBedrockConverse, ChatBedrock
from langgraph.prebuilt import ToolNode, tools_condition # 툴을 노드로 변환, 조건에 따라 툴적용함수
from dotenv import load_dotenv
import os
load_dotenv()
import boto3

# 툴
@tool # LLM이 알수 있는(이해할 수 있는) 형식(포멧)으로 자동 변환됨
def multiply( a: int, b: int ) -> int:
    '''두 수를 곱한 후 반환'''
    print(f'        [Tool 실행] {a} x {b} 계산 중..')
    return a * b

#llm = ChatBedrockConverse(model      =os.getenv('BEDROCK_MODEL_ID'),                          
#                          region_name=os.getenv('AWS_REGION'))
# 모델 ID는 anthropic.claude-3-5-sonnet-20240620-v1:0 사용
llm = ChatBedrock(model =os.getenv('BEDROCK_MODEL_ID'), 
                  client=boto3.client('bedrock-runtime', region_name=os.getenv('AWS_REGION')))
tools = [multiply]
llm_with_tools = llm.bind_tools(tools) # llm에게 이런 툴을 사용할수 있다라는 것을 알림(등록)

# 노드 신규 구성
def chatbot_node(state:MessagesState):
    print( 'chatbot_node pre   => ', state )
    # 계속된 대화 내용이 `누적`되어서 LLM에게 전달 하여 추론행위가 진행됨
    # 누적 => 히스토리 => 대화 내용을 계속해서 LLM에게 전달하여 대화가 이어지게됨
    state2 = {"messages":[llm_with_tools.invoke(state['messages'])] }
    print( 'chatbot_node after => ', state2 )
    return state2

# 그래프 구성상 상태 -> MessagesState 상태값의 맴버는 "messages"
# 그래프 생성
workflow = StateGraph(MessagesState)
# 노드 추가
workflow.add_node("chatbot", chatbot_node)    # 대화 내용을 보고 생각 -> 뇌담당 노드
workflow.add_node("tools",   ToolNode(tools)) # 툴을 노드로 변환하여 그래프에 추가 -> 행동(수단) 노드
# 시작점
workflow.add_edge(START,"chatbot")  # 서비스 가동 => 가장 먼저 챗봇 가동됨
# 조건에 따라 행동을 다르게 수행
workflow.add_conditional_edges(     # 조건부
    "chatbot",          # 이전노드가 텍스트를 응답했으면 => 끝(END)
    tools_condition     # 이전노드가 도구가 필요하다록 응답하면 => 도구 노드로 이동
)
# 도구 사용 -> 결과획득(추론을 위한 보충 자료 획득) -> 챗봇으로 전달 -> 다시 추론행위
workflow.add_edge("tools", "chatbot")
# 사이클 case 2종류
# 질의 -> chatbot_node -> llm 호출 -> 응답 -> end
# 질의 -> chatbot_node -> llm 호출 -> 부족함 도구 사용 필요 -> 툴 -> 툴사용 -> 결과 -> 
#         chatbot_node -> llm 호출 -> 응답 -> end

app = workflow.compile()

# 테스트
if __name__ == '__main__':
    print('Agent 시작, 종료시 q 입력')

    while True:
        # 1. 질의 획득
        user_input = input('\n사용자: ')
        # 2. 탈출 코드
        if user_input.lower() == 'q':break
        # 3. 프럼프트 구성 (단순하게)
        prompt = {"messages":[HumanMessage(content=user_input)]} # 상태와 동일행태로 구성
        # 4. 그래프 작동(invoke:동기식, stream:비동기식,실시간중계,스트리밍 )
        #    휘발성으로 이전 대화 내용이 모두 초기화됨 -> 최초 프럼프트 형태로 구성됨
        #    그래프상에서 계속 움직이면서 대화하는 것은 기억하지만(히스토리가 있음)->신규질문하면 초기화됨
        #    단기기억 필요함!!
        for evt in app.stream( prompt, stream_mode='values'):
            msg = evt['messages'][-1] # 가장 최근에 추가된 내용 -> 실시간 응답
        # 5. 출력 (실시간 출력 x, 마지막값 한번에 출력)
        print( "Agent", msg.content)

        