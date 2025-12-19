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