# 1. 모듈 가져오기
from langgraph.graph import StateGraph, END
from typing import TypedDict

# 2. 상태 정의 (데이터 담을 그릇 -> 차후 프럼프트 들어가는 재료등 포함)
#    클레스형, 클레스의 수퍼클레스로 TypedDict를 통상 사용
#    TypedDict상속 받은것은 fastapi의 pydantic과 거의 유사성을 가짐
class CustomState(TypedDict):
    msg: str

# 3. 노드 준비 (작업 내용 -> tool(rag등..)로 이해 => mcp 연계)
#    현재는 툴수준으로 설정하지 않고, 단순 함수로 구성
def add_prefix( state:CustomState ):
    # 기존 상태값에 앞에 특정 내용 추가함 -> `상태값 업데이트함`
    return { 'msg': "헬로 " + state['msg'] }
    
def add_surfix( state:CustomState ):
    # 기존 상태값에 뒤에 특정 내용 추가함 -> `상태값 업데이트함`
    return { 'msg': state['msg'] + " !!" }

# 4. 그래프 연결
# 4-1. 그래프 생성(구조적 껍대기)
workflow = StateGraph(CustomState) # CustomState의 형태로 상태가 관리되는 상태그래프 생성
# 4-2. 노드(tool등) 추가 -> 서클형 -> 시작과 끝을 모름
workflow.add_node("S1", add_prefix)
workflow.add_node("S2", add_surfix)
# 4-3. 시작점 설정
workflow.set_entry_point("S1")
# 4-4. 작업 순서를 설정(방향성)
workflow.add_edge("S1","S2") # s1이 끝나면 s2로 진입
# 4-5. 끝나는 방향성 설정
workflow.add_edge("S2",END)  # s2가 끝나면 종료
# 4-6. 컴파일 -> 수행가능 단위 구성 -> 완성
app = workflow.compile()

# 5. 실행 -> 그래프 기반 사용자 질의(데이터포함) -> 자율형을 그래프를 돌면서 해결
#    딕셔너리 형태여야한다 => 상태는 Typed`Dict`를 상속받음 => 키는 msg => msg: str 정의햇음
#    상태에 대한 형태를 정의 햇으므로 그에 맞게 입력
res = app.invoke( { "msg":"월드" } )
print( res )

'''
현재 코드는 invode를 통해서 상태값에 초기 세팅이 되면
입력 : 
    { "msg":"월드" }
작동 : -> 추후 에이전트 판단 LLM에 질의할 정도의 프럼프트가 아니면 보충(tool을 통해서)하는 방식 이해
    s1 노드에서 시작되어서 헬로가 추가됨(상태 업데이트) 끝나면
    s2 노드에 진입되어서 !! 추가됨(상태 업데이트) 끝나면 
    그래프 순환 작업 완료 -> 응답 -> 최종상태값 반환
응답 : 
    {'msg': '헬로 월드 !!'}
'''