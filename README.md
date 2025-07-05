# MCP Server & SQL Agent Dashboard

MCP 서버와 SQL Agent의 로그를 시각화하고 관리하는 웹 대시보드입니다.

## 주요 기능

### 1. SQL Agent 중간 출력 저장 및 시각화

- SQL Agent의 중간 단계 출력을 데이터베이스에 자동 저장
- 각 단계별 도구 이름, 입력, 출력, 실행 시간 표시
- 실시간 로그 확인 및 분석

### 2. MCP 서버 로그 관리

- MCP 서버의 실행 로그 저장 및 시각화
- 서버별 로그 필터링
- 실행 결과 및 응답 시간 추적

### 3. MCP 서버 관리

- 서버 정보 수정 (name, description, prompt)
- 웹 UI를 통한 서버 실행
- 실시간 서버 상태 모니터링

### 4. 웹 대시보드

- 직관적인 웹 인터페이스
- 실시간 데이터 업데이트
- 반응형 디자인

## 설치 및 실행

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. 데이터베이스 설정

MySQL 데이터베이스가 필요합니다. `database_connector.py`에서 연결 정보를 확인하세요.

### 3. 환경 변수 설정

```bash
export OPENAI_API_KEY="your-openai-api-key"
```

### 4. 애플리케이션 실행

```bash
python app.py
```

웹 브라우저에서 `http://localhost:8000`으로 접속하세요.

## API 엔드포인트

### SQL Agent 관련

- `POST /api/sql-agent/execute` - SQL Agent 실행
- `GET /api/sql-agent/logs` - SQL Agent 로그 조회
- `POST /api/sql-agent/logs/date-range` - 날짜 범위로 로그 조회

### MCP 서버 관련

- `GET /api/mcp-servers` - MCP 서버 목록 조회
- `GET /api/mcp-logs` - MCP 서버 로그 조회
- `POST /api/mcp-servers/update` - MCP 서버 정보 업데이트
- `POST /api/mcp-servers/execute` - MCP 서버 실행

## 데이터베이스 스키마

### sql_agent_log 테이블

- SQL Agent의 중간 단계 출력 저장
- tool_name, tool_input, tool_output, step_order 등 포함

### mcp_server 테이블

- MCP 서버 정보 저장
- server_name, name, description, prompt 등 포함

### mcp_answer_log 테이블

- MCP 서버 실행 로그 저장
- mcp_server, name, instruction, answer 등 포함

## 사용법

1. **SQL Agent 실행**: 웹 UI에서 지시사항과 허용된 테이블을 입력하여 SQL Agent를 실행
2. **로그 확인**: 실행 후 자동으로 저장된 로그를 실시간으로 확인
3. **MCP 서버 관리**: 서버 정보를 수정하고 웹 UI를 통해 실행
4. **로그 분석**: 각 단계별 실행 과정과 결과를 분석

## 개발 환경

- Python 3.8+
- FastAPI
- MySQL
- LangChain
- Bootstrap 5
