# 전공차차

## 프로젝트 소개

충남대학교에서 2025년도에 신설된 창의융합대학 자율전공학부 학생들의 강의 기반의 전공 탐색을 도와주고, 학습 자료를 제공하는 AI Agent Platform 입니다.

## 문제 정의 및 프로젝트 목표

이 프로젝트의 목표와 상세한 문제 정의는 [Notion](https://zircon-locust-4fc.notion.site/277094faf755805e996dee8bfe90378d?source=copy_link) 에 정리 해두었습니다.

## 주요 기능

### 1) AI 챗봇 기능
![챗봇-교내데이터검색 중간](https://github.com/user-attachments/assets/7e3fcf2d-cb4d-402a-9237-96b2dedf499a) ![챗봇-교내데이터검색2 중간](https://github.com/user-attachments/assets/1df49d77-bb80-4fd5-a8e5-6185d5c011d1)
![챗봇-유튜브강의검색 중간](https://github.com/user-attachments/assets/52fd238e-db61-4599-b02b-f53f7108c9c9)
![챗봇-유튜브강의검색2 중간](https://github.com/user-attachments/assets/7bdc41fd-447f-4444-842a-e2b2454f99e9)
![챗봇-유튜브강의검색3 중간](https://github.com/user-attachments/assets/cfe19211-d841-43a4-b6a6-000082806fbc)
- Langchain, Langgraph를 활용한 LLM 답변 생성 파이프라인 정의
- WebSocket 기반 실시간 스트리밍 통신
- 실시간 스트리밍을 활용한 파이프라인 작업 현황 출력
- 교내 공공데이터를 데이터베이스에 저장하고, MCP서버로 조회하여 답변할 수 있도록 구성 (ex. "컴퓨터융합학부에서 3학년이 가장 많이 듣는 과목이 뭐야?", "우리학교 이산 수학 과목은 어떤 걸 배워?")

### 2) 학과별 커리큘럼 & 학습 자료 제공
![학과별커리큘럼-강의목록 중간](https://github.com/user-attachments/assets/5d6b9f1f-e2aa-440a-a2ca-ba3a3491b37e)
![학과별커리큘럼-강의상세 중간](https://github.com/user-attachments/assets/9971a844-4b16-4ec8-875b-c9a19e364597)
![학과별커리큘럼-KOCW 중간](https://github.com/user-attachments/assets/651b951c-20c2-4dcc-8cee-08338680fbc3)
![학과별커리큘럼-Youtube 중간](https://github.com/user-attachments/assets/50b0dd28-86c6-4292-8ed3-8da6d50383b5)
![학과별커리큘럼-Web 중간](https://github.com/user-attachments/assets/4e23901c-2b9b-4cef-82e6-50f1c8a71b1e)

- 교내 공공데이터를 활용하여 학과/학부의 1~4학년이 수강하는 과목을 분반별로 정리
- Youtube, Naver, Local Database(KOCW) MCP Server를 활용한 강의명 키워드 기반 학습자료 제공, LLM이 각 플랫폼과 데이터베이스에서의 자료 검색 및 생성 형식으로 동작
- "[[", "/]]" 등의 형태로 LLM이 검색 결과를 응답으로 재생성, 프론트 측에서 태그를 파싱하여 렌더링
  - ```
    [[WEB_SEARCH]]
    [[LINK]]
      https://kin.naver.com/qna/detail.naver?d1id=11&dirId=1111&docId=233058998&qb=66y07IqoIOyghOqzteydhCDshKDtg53tlbTslbwg7KKL7J2E6rmM7JqU&enc=utf8
    [[/LINK]]
    [[TITLE]]
     심리학과생인데 복수 전공으로 뭘 선택하면 좋을까요?
    [[/TITLE]]
    [[DESCRIPTION]]
      복수 전공을 선택했을 때의 진로나 전망에 대한 설명을 요청하는 질문입니다.
    [/DESCRIPTION]]
    [[/WEB_SEARCH]]

### 3) 강의 계획서 AI 요약
![학과별커리큘럼-강의계획서 및 요약 중간](https://github.com/user-attachments/assets/cc6f63bc-b43a-4dd8-8c50-c877d0c3c8e5)

- 강의계획서의 내용을 LLM 으로 요약하여 출력
- 실제 강의를 수강할 때 들었던 생각을 바탕으로, '이 강의를 수강하면 좋은 점' 항목 추가

### 4) 학과 정보 탐색
![학과정보탐색 - 질문입력 중간](https://github.com/user-attachments/assets/9a78ac27-5d34-4d0e-a4de-572bf0cb0c23)
![학과정보탐색 - 질문입력2 중간](https://github.com/user-attachments/assets/33d8e292-6c76-4742-b8e3-be15b0eca58e)
- 커리어넷 전공별 교수 인터뷰 데이터를 활용한 RAG 방식의 질의 응답 수행
- "질문: ..., 답변: ..." 형식으로, 답변에 대해 chunk data를 나누고, 질문 반복하는 헤더 형식으로 구성하여 Vector DB에 Embedding 후 저장
- 학과명과 질문을 클라이언트로부터 입력받음 (학과명 기반 질문)

## 시스템 아키텍처
![front](https://github.com/user-attachments/assets/74ce1965-c950-4bdc-9de7-6d6820f6bd4e)
![server](https://github.com/user-attachments/assets/6990562f-e822-48bc-894e-b18022c4b6ef)


## LLM 동작 흐름

### 1) 사용자 질문 - 답변 흐름
![슬라이드12](https://github.com/user-attachments/assets/473968e5-0a30-48a1-9535-9e3b8a712736)

### 2) 답변 파이프라인 그래프
자세한 출력 과정은 `langgraph_introduce.ipynb`를 통해 확인해주세요
![슬라이드13](https://github.com/user-attachments/assets/2881df93-3907-4993-977f-dde1fc6ed444)

## 기술 스택

### Backend Server & Database

![MySQL](https://img.shields.io/badge/mysql-%2300f.svg?style=for-the-badge&logo=mysql&logoColor=white)
![Redis](https://img.shields.io/badge/redis-%23DD0031.svg?style=for-the-badge&logo=redis&logoColor=white)
![Java](https://img.shields.io/badge/java-%23ED8B00.svg?style=for-the-badge&logo=openjdk&logoColor=white)
![Spring Boot](https://img.shields.io/badge/spring%20boot-%236DB33F.svg?style=for-the-badge&logo=spring-boot&logoColor=white)

### LLM Backend Server & Database

![LangChain](https://img.shields.io/badge/langchain-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-74aa9c?style=for-the-badge&logo=openai&logoColor=white)
![ChromaDB](https://img.shields.io/badge/ChromaDB-FF6B35?style=for-the-badge&logo=chroma&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)

### Frontend Server

![React](https://img.shields.io/badge/react-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB)
![Next JS](https://img.shields.io/badge/Next-black?style=for-the-badge&logo=next.js&logoColor=white)
![TypeScript](https://img.shields.io/badge/typescript-%23007ACC.svg?style=for-the-badge&logo=typescript&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/tailwindcss-%2338B2AC.svg?style=for-the-badge&logo=tailwind-css&logoColor=white)

### Infra Structure

![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
![Nginx](https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white)
![Ubuntu](https://img.shields.io/badge/Ubuntu-E95420?style=for-the-badge&logo=ubuntu&logoColor=white)
