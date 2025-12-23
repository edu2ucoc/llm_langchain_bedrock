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
app = workflow.compile()
if __name__ == '__main__':
    print('Agent 시작, 종료시 q 입력')
    while True:
        user_input = input('\n사용자: ')
        if user_input.lower() == 'q':break
        
        prompt = {"messages":[HumanMessage(content=user_input)]}
        for evt in app.stream( prompt, stream_mode='values'):
            msg = evt['messages'][-1]
        print( "Agent", msg.content)

        