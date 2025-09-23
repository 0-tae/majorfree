# 전공차차

## 프로젝트 소개

충남대학교에서 2025년도에 신설된 창의융합대학 자율전공학부 학생들의 강의 기반의 전공 탐색을 도와주고, 학습 자료를 제공하는 AI Agent Platform 입니다.

## 문제 정의 및 프로젝트 목표

이 프로젝트의 목표와 상세한 문제 정의는 [Notion](https://zircon-locust-4fc.notion.site/277094faf755805e996dee8bfe90378d?source=copy_link) 에 정리 해두었습니다.

## 주요 기능

### AI 챗봇 기능

(이미지)

- Langchain, Langgraph를 활용한 LLM 답변 생성 파이프라인 정의
- WebSocket 기반 실시간 스트리밍 통신
- 실시간 스트리밍을 활용한 파이프라인 작업 현황 출력
- 별도의 페이지 이동 없이, 내부 챗봇을 이용할 수 있는 아이콘 추가
- 교내 공공데이터를 데이터베이스에 저장하고, MCP서버로 조회하여 답변할 수 있도록 구성 (ex. "컴퓨터융합학부에서 3학년이 가장 많이 듣는 과목이 뭐야?", "우리학교 이산 수학 과목은 어떤 걸 배워?")

### 학과별 커리큘럼 & 학습 자료 제공

(이미지)

- 교내 공공데이터를 활용하여 학과/학부의 1~4학년이 수강하는 과목을 정리
- Youtube, Naver, Local Database(KOCW) MCP Server를 활용한 강의명 키워드 기반 학습자료 제공

### 강의 계획서 AI 요약

(이미지)

- 강의계획서의 내용을 LLM 으로 요약하여 출력
- 실제 강의를 수강할 때 들었던 생각을 바탕으로, '이 강의를 수강하면 좋은 점' 항목 추가

### 학과 정보 탐색

(이미지)

- 커리어넷 전공별 교수 인터뷰 데이터를 활용한 RAG 방식의 질의 응답 수행
- "질문: ..., 답변: ..." 형식으로, 답변에 대해 chunk data를 나누고, 질문 반복하는 헤더 형식으로 구성하여 Vector DB에 Embedding 후 저장
- 학과명과 질문을 클라이언트로부터 입력받음 (학과명 기반 질문)

## 시스템 아키텍처

(이미지)

## 동작 흐름

### 1) 사용자 질문 - 답변 흐름

(이미지)

### 2) 답변 파이프라인 그래프

자세한 출력 과정은 `langgraph_introduce.ipynb`를 통해 확인해주세요
(이미지)

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
