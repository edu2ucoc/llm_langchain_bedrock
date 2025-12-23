# LLM(AI)에서 수단을 제공함 -> 선택지(tool)를 다양하게 제공
# 차후 자율형/능동형 에이전트에 의해 mcp 통해 다양한 tool 사용하게됨
from langchain_core.tools import tool
from langchain_aws import ChatBedrockConverse
from dotenv import load_dotenv
import os
load_dotenv()

# 1. 도구 정의 (디비, rag, 파일, 외부자원 ......)
#    특정 업무를 하는 함수를 툴로 정의
@tool
def multiply( a: int, b: int ) -> int:
    '''두 수를 곱한 후 반환'''
    return a * b

# 2. LLM 모델에 도구 추가/설정/세팅/바인딩...
llm = ChatBedrockConverse(model      =os.getenv('BEDROCK_MODEL_ID'),
                          region_name=os.getenv('AWS_REGION'))
#    llm에 툴 세팅된 객체(실행 가능한 메세지?)
llm_with_tools = llm.bind_tools([multiply]) 

# 3. 고객 질의(간단 프럼프트)
q   = '12 곱하기 0.5는 몰까?'
res = llm_with_tools.invoke(q)

# 4. AI의 판단
print(f'질문 => {q}')
print(f'AI의 응답 => {res}')
print(f'AI의 행동 => {res.tool_calls}') # 어떤 툴을 사용했는가? 로그

'''
1.
google.gemma-3-27b-it
구글모델
질문을 해결하기 위해 도구의 필요성을 못느껴서 바로 llm에서 해결했음

2.
anthropic.claude-3-5-sonnet-20240620-v1:0
클로드 모델은 자율적으로 도구의 필요성을 느끼고 도구 사용!!
질문 => 12 곱하기 0.5는 몰까?
AI의 응답 => content=[{'type': 'text', 'text': '안녕하세요. 12와 0.5를 곱하는 계산을 도와드리겠습니다. \n\n우리가 사용할 수 있는 "multiply" 함수는 정수만을 입력으로 받을 수 있습니다. 따라서 0.5를 정수로 변환해야 합니다. 0.5는 1/2이므로, 12와 1을 곱한 후  그 결과를 2로 나누는 방식으로 계산할 수 있습니다.\n\n먼저 12와 1을 곱하는 계산을 해보겠습니다.'}, {'type': 'tool_use', 'name': 'multiply', 'input': {'a': 12, 'b': 1}, 'id': 'tooluse_pJ4As5gSS_epJEeSjHTRUA'}] additional_kwargs={} response_metadata={'ResponseMetadata': {'RequestId': '0dd88cf0-366c-43c7-bc53-699fd73b3cca', 'HTTPStatusCode': 200, 'HTTPHeaders': {'date': 'Tue, 23 Dec 2025 01:28:18 GMT', 'content-type': 'application/json', 'content-length': '715', 'connection': 'keep-alive', 'x-amzn-requestid': '0dd88cf0-366c-43c7-bc53-699fd73b3cca'}, 'RetryAttempts': 0}, 'stopReason': 'tool_use', 'metrics': {'latencyMs': [4641]}, 'model_provider': 'bedrock_convme': 'anthropic.claude-3-5-sonnet-20240620-v1:0'} id='lc_run--019b48d2-3649-7093-afe0-06e20f3ec18d-0' tool_calls=[{'name': 'multiply', 'args': {'a': 12, 'b': 1}, 'id': 'tooluse_pJ4As5gSS_epJEeSjHTRUA', 'type': 'tool_call'}] usage_metadata={'input_tokens': 412, 'output_tokens': 254, 'total_tokens': 666, 'input_token_details': {'cache_creation': 0, 'cache_read': 0}}  
AI의 행동 => [{'name': 'multiply', 'args': {'a': 12, 'b': 1}, 'id': 'tooluse_pJ4As5gSS_epJEeSjHTRUA', 'type': 'tool_call'}]

3.
openai.gpt-oss-120b-1:0
openai 모델
질문을 해결하기 위해 도구의 필요성을 못느껴서 바로 llm에서 해결했음
'''