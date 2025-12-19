'''
백엔드 코드 (리뷰때 시도 해보셔 됨)
- fastapi로 기본 코드 구성
- url 1개만 정의 "/llm"
    - http://localhost:8000/llm
    - post 방식
    - json 데이터가 전달 -> pydantic  사용 (클레스로 요청객체 1개 구성)
    - 함수 내부에서 bedrock 호출 -> llm 호출 -> 응답 -> {'response':응답값}

- 나머지는 랭체인 퓨샷등 프럼프트 구성 사용 (코랩 사용 코드 활용)
- model은 claude 사용 (다른 모델도 가능)
'''