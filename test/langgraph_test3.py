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
# 1. 모듈 가져오기 (메모리 저장(단기기억, 프로그램 종료되면 삭제됨))
from langgraph.checkpoint.memory import MemorySaver
# 2. 메모리 생성 -> RAM에 공간을 할당함 -> 실제는 물리적 디비에 저장(백터디비, RDB등)
memory = MemorySaver()

@tool
def multiply( a: int, b: int ) -> int:
    '''두 수를 곱한 후 반환'''
    print(f'        [Tool 실행] {a} x {b} 계산 중..')
    return a * b

# 모델 ID는 anthropic.claude-3-5-sonnet-20240620-v1:0 사용
llm = ChatBedrock(model =os.getenv('BEDROCK_MODEL_ID'), 
                  client=boto3.client('bedrock-runtime', region_name=os.getenv('AWS_REGION')))
tools = [multiply]
llm_with_tools = llm.bind_tools(tools)

def chatbot_node(state:MessagesState):
    #print( 'chatbot_node pre   => ', state )
    state2 = {"messages":[llm_with_tools.invoke(state['messages'])] }
    #print( 'chatbot_node after => ', state2 )
    return state2

workflow = StateGraph(MessagesState)
workflow.add_node("chatbot", chatbot_node)
workflow.add_node("tools",   ToolNode(tools))
workflow.add_edge(START,"chatbot")
workflow.add_conditional_edges(
    "chatbot",
    tools_condition
)
workflow.add_edge("tools", "chatbot")
# 랭그래프 생성시 컴파일 옵션으로 단기기억 공간 제공
# 실행될때마다 memory에 자동 저장됨
app = workflow.compile(checkpointer=memory)

if __name__ == '__main__':
    print('Agent 시작, 종료시 q 입력')
    # 메모리 저장시 설정값
    '''
        현재는 ID를 고정값으로 구성 -> ID가 같은면 같은 대화방/채팅으로 인식하고 기억 설정
        로드-> 병합 -> 실행 단계로 메모리에 기억 => [과거기록 + 새 질문]
    '''
    config = {"configurable":{"thread_id":"user-1"}} # 사용자별 아이디로 관리 -> user-1
    while True:
        user_input = input('\n사용자: ')
        if user_input.lower() == 'q':break

        prompt = {"messages":[HumanMessage(content=user_input)]}
        # 스트림 진행시 설정값 세팅
        for evt in app.stream( prompt, stream_mode='values', config=config):
            msg = evt['messages'][-1]
        print( "Agent", msg.content)

        