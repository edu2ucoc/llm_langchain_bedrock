'''
pip install mcp

TODO역활 MCP Host
- AI 모델(LLM)과 MCP 클라이언트를 연결하는 주체 애플리케이션
- LLM의 "뇌"를 사용하여 어떤 도구를 쓸지 결정하고, 실제 실행을 지시
- 파이썬 파일 전체가 Host - mcp_test2.py (해당 프로그램 자체)
- AWS Bedrock(Claude)에게 질문을 던지고, 답변을 받아 MCP Client에게 전달하는 "중개자" 역할

MCP Client (클라이언트)
- Host 내부에서 MCP Server와 실제로 통신하는 모듈
- ClientSession 객체
- "이 도구 실행해줘"라는 Host의 명령을 Server가 알아들을 수 있는 언어로 `변환하여 전달`

MCP Server (서버)
- 실제 데이터(파일, DB 등)에 접근할 수 있는 권한을 가진 `독립된 프로세스`
- 도구(Tool)의 실제 기능을 수행
- npx ... server-filesystem 명령어로 실행되는 Node.js 프로세스
- 실제 컴퓨터의 파일을 읽거나(read_file) 목록을 조회(list_directory)
- 종류
    - 공식(Official) MCP 서버 -> Model Context Protocol 공식 팀에서 개발, 유지보수
    - 커뮤니티 MCP 서버 -> 개발자들이 필요에 의해 생성
    - 기업 공식 서버 -> 벤더(DB, 노션, 슬랙, ...)
- LLM + 기능 결합하여 하나의 도구를 생성 => MCP

'''
import asyncio
import boto3
import json
import os
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()

# 1. AWS Bedrock 클라이언트 설정
# (주의: 리전이 올바른지 확인하세요. Claude 3.5 Sonnet은 us-east-1 등에서 주로 지원됩니다.)
bedrock = boto3.client(service_name='bedrock-runtime', 
                       region_name=os.getenv('AWS_REGION')) 

# [추가된 함수] MCP 도구 형식을 Bedrock 도구 형식으로 변환
def convert_mcp_to_bedrock_format(tools_list):
    bedrock_tools = []
    for tool in tools_list.tools:
        bedrock_tools.append({
            "toolSpec": {
                "name": tool.name,
                "description": tool.description,
                "inputSchema": {
                    "json": tool.inputSchema
                }
            }
        })
    return bedrock_tools

async def run_mcp_host():
    # ... (이전 설정 코드는 동일) ...
    command = "npx.cmd" # 맥 "npx"
    # 경로 설정 주의 (사용자 환경에 맞게)
    docs_path = r"c:\\Users\\Dell5371\\Desktop\\projects\\llm\\llm_langchain_bedrock\\test\\data"
    
    # TODO역활 MCP Server (서버) - 독립된 프로세스
    # MCP 서버(Node.js)를 실행할 명령어와 인자 설정
    # 파이썬이 npx 명령어를 몰래 실행해서 백그라운드에 파일 시스템 서버를 띄웁
    # https://www.npmjs.com/package/@modelcontextprotocol/server-filesystem
    # Node.js server implementing Model Context Protocol (MCP) for filesystem operations.
    server_params = StdioServerParameters(
        command = command,
        args    = ["-y", "@modelcontextprotocol/server-filesystem", docs_path],
        env     = os.environ
    )
    print("MCP 서버 구동 중.. => 독립적 프로세스 생성")
    # Server는 "나 파일 읽기, 쓰기, 목록 보기 할 줄 알아"라고 답합니다. 
    # 파이썬은 이 리스트를 AWS Bedrock내의 특정 모델(claude)이 읽을 수 있는 양식으로 포장합니다.
    async with stdio_client(server_params) as (read, write):
        # TODO역활 MCP Client (클라이언트) 객체 생성
        # "이 도구 실행해줘"라는 Host의 명령을 Server가 알아들을 수 있는 언어로 변환하여 전달
        # 파일 경로상에 특정 파일을 읽고 쓰기 기능을 가지고  MCP Client (클라이언트) 객체 생성
        async with ClientSession(read, write) as session:
            # 클라이언트를 초기화
            await session.initialize()
            # Server가 가진 도구 목록(read_file 등)을 가져옴
            tools_list = await session.list_tools()
            # 도구를 MCP 형식의 도구 정의를 AWS Bedrock이 이해할 수 있는 JSON 포맷으로 변환
            bedrock_tools = convert_mcp_to_bedrock_format(tools_list)
            
            # 사용자 질문
            user_query = "내 문서 폴더에 있는 모든 파일을 읽고 요약해줘."
            
            # 대화 기록 초기화, 대화 기록을 담을 리스트 (계속 누적됨)
            messages = [{"role": "user", "content": [{"text": user_query}]}]
            
            # [중요] 루프 시작: 모델이 도구 사용을 멈추고 텍스트 답변을 줄 때까지 반복
            should_continue = True
            
            while should_continue:
                # Bedrock 호출
                # "문서 폴더 요약해줘"라는 질문과 함께 도구 상자(bedrock_tools)를 Claude에게 건넴
                response = bedrock.converse(
                    modelId     = "anthropic.claude-3-5-sonnet-20240620-v1:0",
                    messages    = messages,
                    toolConfig  = {"tools": bedrock_tools}
                )
                # 응답 메세지 획득
                output_message = response['output']['message']
                
                # 모델의 응답(도구 요청 포함)을 대화 기록에 추가 (매우 중요!)
                messages.append(output_message)
                # 응답중 머추는 이유 획득
                stop_reason = response['stopReason']
                
                # 1. 모델이 도구 사용을 요청한 경우 ('tool_use')
                if stop_reason == 'tool_use': # Claude: "도구가 필요해!"
                    tool_results = []
                    
                    # 모델이 요청한 모든 도구 순회 (한 번에 여러 도구를 요청할 수도 있음)
                    for content in output_message['content']:
                        if 'toolUse' in content: # 도구 사용
                            tool_use    = content['toolUse'] # 아룸
                            tool_id     = tool_use['toolUseId'] # ID 필수
                            tool_name   = tool_use['name']
                            tool_input  = tool_use['input'] # 입력
                            
                            print(f"\n[Bedrock 요청] 도구 사용: {tool_name}")
                            print(f"입력값: {tool_input}")

                            # MCP 서버 도구 실행
                            # (주의: 에러 처리를 위해 try-except 블록 권장)
                            try:
                                # MCP Client를 통해 Server에 실제 명령 전달
                                result = await session.call_tool(tool_name, arguments=tool_input)
                                # Claude가 "먼저 폴더에 무슨 파일이 있는지 봐야겠어. 
                                # list_allowed_directories 실행해줘"라고 응답합니다. 
                                # 파이썬(Host)은 이 요청을 받아 MCP Server에게 실제 실행
                                tool_result_text = result.content[0].text
                                print(f"[MCP 결과] {tool_result_text[:100]}...") # 로그 확인용
                            except Exception as e:
                                tool_result_text = f"Error: {str(e)}"

                            # Bedrock에 돌려줄 결과 포맷 구성
                            # 실행 결과를 Bedrock 메시지 포맷으로 포장
                            tool_results.append({
                                "toolResult": {
                                    "toolUseId": tool_id, # 요청했던 ID와 일치해야 함
                                    "content"  : [{"text": tool_result_text}],
                                    "status"   : "success"
                                }
                            })
                    
                    # 도구 실행 결과를 User role 메시지로 추가하여 Bedrock에 전달
                    messages.append({
                        "role": "user",
                        "content": tool_results
                    })
                    print(">> 결과를 Bedrock에 전달하고 다음 단계 진행 중...")
                
                # 2. 모델이 최종 답변을 완료한 경우 ('end_turn')
                elif stop_reason == 'end_turn':
                    final_text = output_message['content'][0]['text']
                    print("\n[최종 요약 결과]")
                    print(final_text)
                    should_continue = False
                
                # 3. 그 외 (토큰 제한 등)
                else:
                    print(f"중단 사유: {stop_reason}")
                    should_continue = False

# 윈도우 비동기 루프 정책 설정 (필수)
if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    asyncio.run(run_mcp_host())