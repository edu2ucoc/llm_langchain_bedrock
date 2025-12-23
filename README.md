# llm_langchain_bedrock
    - llm 기반 서비스
    - 키워드
        - bedrock 사용
            - llm 호출 담당
        - llm 모델
            - `claude`, openai, gemma 모델 사용
        - streamlit을 이용하여 UI 구성 (프런트 담당)
            - 파이썬으로만 구성(html x, css x, js x)
        - fastapi를 이용하여 bedrock 호출
            - 화면 x
            - 백엔드에서 api 역활만 담당
        - langchain
            - 프럼프트 엔지니어링 담당
            - 프럼프트 + llm 호출 체인 연결 파이프라인 구축
    - 서비스 주제
        - 점심/저녁등 메뉴 해결사 (메뉴 추천)
    - model_id
        - google : google.gemma-3-27b-it
        - openai : openai.gpt-oss-120b-1:0
        - Anthropic : anthropic.claude-3-5-sonnet-20240620-v1:0

# 구조
/
L .env              : 각종 키, bedrock 단기키
L .gitignore        : 깃허브에 업로드 x 파일,디렉토리 명시
L requirements.txt  : 패키지 설치 내용 -> 추후 버전 표기
L app.py            : 프런트 담당, streamlit 주로 사용
L server.py         : 백엔드 담당, fastapi 주로 사용

# 설치
    - 가상환경 구축 (경로 주의:현재 작업 디렉토리)
        - python -m venv llm_venv
        - 가상환경 활성화
            - 윈도우기준
                ```
                .\llm_venv\Scripts\activate
                or
                ..\llm_venv\Scripts\activate
                ```
        - 패키지 설치
            - (llm_venv) llm> pip install -r requirements.txt
        
    - .gitignore 가상환경폴더 추가
        ```
            ...
            # 가상환경제외
            llm_venv
        ```

    - 패키지 설치
        - pip install -r requirements.txt
        ``` 
            # bedrock 호출 API 구성
            fastapi
            uvicorn
            # 프런트 UI 구성
            streamlit
            # 프런트 -> fastapi로 요청(채팅 메세지) -> 응답처리
            requests
            # AWS 엑세스, bedrock 사용
            boto3
            # 랭체인 AWS용도, 코어(프럼프트 기능만 사용)
            langchain-aws
            langchain-core
            # 환경변수 로드 하여 OS단에 세팅
            python-dotenv
        ```

# 구동
    - 백엔드 : server.py
        ```
            uvicorn server:app --reload --port 8000
        ```
    - 프런트 : app.py
        ```
            streamlit run app.py
        ```

# 환경변수
    - .env
    - 리전, 모델 ID 추가
        - 모델 ID : 
            - 앤트로픽사의 클로드는 단시간 연속 질의에 쿼터 제한있는듯함.(이슈)
            - 구글 혹은 오픈AI 제품으로 진행
        ```
            AWS_REGION=ap-northeast-1
            BEDROCK_MODEL_ID=google.gemma-3-27b-it
            AWS_BEARER_TOKEN_BEDROCK=...
        ```

# server.py
    ```
        백엔드 코드
        - fastapi로 기본 코드 구성
        - url 1개만 정의 "/llm"
            - http://localhost:8000/llm
            - post 방식
            - json 데이터가 전달 -> pydantic  사용 (클레스로 요청객체 1개 구성)
            - 함수 내부에서 bedrock 호출 -> llm 호출 -> 응답 -> {'response':응답값}

        - 나머지는 랭체인 퓨샷등 프럼프트 구성 사용 (코랩 사용 코드 활용)
        - model은 gemma(google) 사용 (다른 모델도 가능)
    ```

# advanced (발전적 확장) -> 프로젝트 구성 사항
- rag(검색 증강) : LLM 한번도 접하지 못함 사내 데이터(내부 데이터) 활용
    - 자체 구축(온-프레미스<->클라우드) -> 오픈소스(메타의 라마등) 활용 -> 사내데이터 학습(파인튜닝) -> llm 활용 -> `비용/시간 많이 발생`

    - rag : 
        - 특징 
            - 사내 데이터 유출 X(노출은 된다),
                - 노출은 LLM에게 추론 요청시 전달됨(LLM회사 특약, 계약 명시-> 사내 데이터는 수집 x, 학습활용 x -> 휘발성 처리) 
                - 공유한 정보, 보안을 필요로하는 데이터는 마스킹, 제외(직접처리)
                - bedrock로 기본은 수집, 사용 x 되어 있고 => 모델별로 확인 필요함
            - LLM 강력한 추론/생성 등 기능 활용
            - 검색 증강 => 추론/생성에 필요한 LLM 모르는 데이터를 추가 제공

        - 정의 및 장점
            - 검색 증강 생성(Retrieval-Augmented Generation)의 약자로, 대규모 언어 모델(LLM)이 외부 지식(데이터베이스, 문서 등)을 검색(Retrieval)하여 답변 생성 시 해당 정보를 참조하도록 하는 기술
            - LLM이 훈련되지 않은 최신 정보나 특정 기업 내부 데이터에 기반한 `정확하고 신뢰성 있는 답변을 생성`
            - 모델 자체를 재학습(파인튜닝)시키는 대신 `외부 데이터베이스만 업데이트하면 되므로 효율적(비용, 시간)`
        - 목표
            - 사내(특정) 데이터 노출 X
            - 사내(특정 서비스)에 llm 도입(사내 전용혹은 도구)
            - 사내(특정) 데이터에 적합한 답변 원함
            - llm 학습 x

- vectordb      : 
    - 대화 내욕 기록(장기기억 담당), rag등 데이터를 저장하는 공간 활용, 유사도 체크 기능 활용
    - 대량의 외부 데이터는 기존 방식대로 RDB나 No-SQL 계열 저장해 두는가?
        - 사용자 질의 에 대한 유사도 검사를 지원 x(일부 있을수 있음 제품별)
        - 디비 => 자연어를 백터화하여 저장하는 백터 디비가 필요함 => 유사도 계산 정확해짐 => 검색 정확해짐 => 이를 참고하는 LLM 답변 정확해짐
    - 제품
        - 메모리 베이스 디비(로컬) - faiss
            - 유사성 검색 및 벡터 클러스터링을 위한 오픈 소스 라이브러리
            - pip install -q faiss-cpu
            or
            - pip install -q faiss-gpu
        - 외부 디비
            - 파인콘 -> 무료 1개 스토리지 제공(1개 도메인 구성만 가능),2개부터는 유료 (https://www.pinecone.io/)
            - aws 존재하지만 비쌈 !!
    - 말뭉치(자연어) -> `토크나이저:정해진것 없음(알아서 선택)`를 이용한 백터화 -> 백터디비 저장
        - BedrockEmbeddings => 특정 토큰 단위로 비용 부과
            - 자연어 => BedrockEmbeddings => 백터 변환 => 비용 과금

- mcp           : 
    - 외부 자원(db, rag, 검색, 파일, 웹스크레핑,.. ... <- `tool`들 중계 호출 관리) -> 해당 내용의 결과물을 프럼프트에 적용
    - MCP HOST, SERVER, CLIENT -> 별도 주제로 다시 체크
    - 에이전트(Agent)가 지능형으로(지시형 x) 즉, 스스로 알아서 답변하기 부족한데 -> mcp를 통해서 (등록된 툴을 통해서) 외부 자원 요청(rag, db, 검색, 파일, ...) -> 데이터 획득 -> 프럼프트 보충

- 위의 flow( 질의 => LLM 대응하도록 구성하는 )를 graph로 설계
    - 위의 자원들 (프럼프트, llm, mcp(혹은 툴등), ...) -> 체인 연결 or 그래프 연결 가능
    - 이것을 지능형/능동형/자율형 agent 개발 -> 본 서비스에 반영

- 질의당 1개 agent 대응 or 질의당 여러개의 agent 대응(A2A)  -> Agent enginnering