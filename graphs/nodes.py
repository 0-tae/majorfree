from graphs.graph_status import GraphStatus
from mcp_server_api import get_multi_server_mcp_clients_from_api
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
import asyncio

from tools.mcp.llm_models.chat_gpt import model_instance as chat_gpt
from tools.mcp.vectordb.chroma.chroma_db import db_instance as chroma_db

def print_state(node_name: str, state: GraphStatus):
        print("[node]",node_name,"--->",state)
        
def node(func):
    async def wrapper(state: GraphStatus):
        result = func(state)
        
        if asyncio.iscoroutine(result):
            result = await result
            print_state(func.__name__, result)
            
            return result
        
        print_state(func.__name__, result)
        
        return result
    return wrapper


@node
async def init(state: GraphStatus) -> GraphStatus:
    """
    초기 상태 설정 로직 있으면 추가할 것
    """

    """
    1. 규칙 & 가이드라인
    - 당신은 30년 근속의 충남대학교 교육 종사자입니다. 대학교 신입생, 혹은 진로 및 전공 결정에 어려움을 겪는 학생들에게 친절하게 대답해주세요.
    - 학과 과목에 대한 할루시네이션을 생성하지 마세요. 제공된 컨텍스트에 의한 과목을 언급해야 합니다.
    - 모든 말에는 한국어로 대답하세요. 이전 대화내역을 참고하여 가장 최근의 메시지에 대해 답변하세요.
    
    2. 아래 설명에 대하여 사용자 질문과 연관된 적절한 서비스가 있다고 판단되면, 사용자가 의도하고자 하는 동작과 서비스 설명을 연관지어 아래 서비스를 사용자에게 추천하세요.
    - 학과 정보 탐색 서비스 : 관심있는 학과와 관련된 핵심 포인트, 필요한 역량, 진로 방향을 파악할 수 있으며, 학생들이 일반적으로 궁금해 할 정보를 전공 교수님 인터뷰 기반의 정보를 이용하여 질문에 대한 답변을 제공합니다.
    - 학과별 커리큘럼 서비스 : 충남대학교에서 개설된 전공과목을 바탕으로 유사한 KOCW 강의, 유튜브 강의, 웹 검색 학습 자료를 찾아 제공합니다.
    - 채팅 서비스 : 관심있는 학과 학생들이 가장 많이 듣는 과목에 대해 물어보고, 해당 학과에 3학년, 4학년 과목이 어떤 것들이 있는지도 확인해보세요.
    
    3. 사용자의 질문을 바탕으로 적절한 다음 질문을 추천해주세요. 추천 질문은 사용자의 질문과 관련된 질문이어야 합니다.
    """
    
    prompt = '''
    1. rules & guidelines
    - You are a staff member of education department with 30 years of experience at 충남대학교(Chungnam National University). 
    - Please kindly answer questions from new university students or those struggling with career and major decisions.
    - Do not hallucinate or invent any courses; only mention courses based on the provided context.
    - Always respond in Korean. Refer to the most recent message in the conversation for your answer.
    
    2. If you determine that there is a suitable service related to the user’s question as described below, recommend the relevant service by connecting the intended action of the user with the following service descriptions:
    이미 충분한 정보가 사용자에게 제공되었을 경우, 서비스를 추천하지 않아도 됩니다.
    - 학과 정보 탐색 서비스: Provides answers to questions about key points, required competencies, and career paths related to the department of interest, using information based on interviews with professors, as well as information that students are generally curious about.
	- 학과별 커리큘럼 서비스: Offers similar KOCW lectures, YouTube lectures, and web-based study materials based on major courses offered at Chungnam National University.
	- 챗봇 채팅 서비스: Enables users to ask about the most popular courses taken by students in their department of interest, and to check which courses are available for third- and fourth-year students in that department.
    
    3. Based on the user’s question, recommend an appropriate follow-up question. The recommended question should be relevant to the user’s original inquiry.
    '''
    
    system_message = {"role":"system", "content": prompt}
    user_message = {"role":"user", "content": state["instruction"]}
    
    # 만약 이전 대화내역이 있다면 맨 앞에 프롬프트를 삽입한 후 유저 질문을 넣고 그대로 리턴하기
    if state["messages"]:
        state["messages"].insert(0, system_message)
        return {
            "messages": [user_message]
        }
    
    return {
        "messages": [system_message, user_message]
    }


@node
async def route(state: GraphStatus) -> GraphStatus:
    """
    라우팅 로직 있으면 추가할 것
    """
    
    available_modes = [
        "YOUTUBE_SEARCH",
        "WEB_SEARCH",
        "KOCW_SEARCH",
        "DEPARTMENT_SEARCH"
    ]
    
    for mode in available_modes:
        if mode == state["search_type"]:
            return mode
        
    return "COMMON"

@node
async def agent_question(state: GraphStatus) -> GraphStatus:
    client_config = await get_multi_server_mcp_clients_from_api()
    
    client = MultiServerMCPClient(client_config)
    
    model = chat_gpt.get_model()
    
    # 클라이언트 연결
    tools = await client.get_tools()
        
    agent = create_react_agent(model=model,
                            tools=tools,
                            state_schema=GraphStatus)
    
    result = await agent.ainvoke({
        "messages": state["messages"]
    })
        
    answer =  result.get("messages")[-1].content if result.get("messages") else "No response"
    generated_message = {"role":"assistant", "content": answer}

    return {
        "messages": [generated_message],
        "answer": answer
    }

@node
async def youtube_search(state: GraphStatus) -> GraphStatus:
    """
    유튜브 검색을 하는 단계
    """
    client_config = await get_multi_server_mcp_clients_from_api()
    
    client = MultiServerMCPClient(client_config)
    
    model = chat_gpt.get_model()
    
    tools = await client.get_tools(server_name="youtube_search_mcp")
    
    agent = create_react_agent(model=model,
                            tools=tools,
                            state_schema=GraphStatus)
    
    prompt = f'''
    Search for 7 YouTube videos related to the instruction.
    For each video, provide the video title, link, thumbnail, and a clear description.
    Exclude negative or inappropriate content and explain how such content was filtered out.
    instruction: {state["instruction"]}
    '''
    
    state["messages"] += [{"role":"user", "content": prompt}]
        
    result = await agent.ainvoke({
        "messages": [{"role":"user", "content": prompt}]
    })
        
    answer =  result.get("messages")[-1].content if result.get("messages") else "No response"
    generated_message = {"role":"assistant", "content": answer}

    return {
        "messages": [generated_message],
        "answer": answer
    }
    
@node
async def kocw_search(state: GraphStatus) -> GraphStatus:
    """
    학습자료 추천
    """
    client_config = await get_multi_server_mcp_clients_from_api()
    
    client = MultiServerMCPClient(client_config)
    
    model = chat_gpt.get_model()
    
    tools = await client.get_tools(server_name="kocw_lecture_search_mcp")
            
    agent = create_react_agent(model=model,
                            tools=tools,
                            state_schema=GraphStatus)
    
    instruction = state["instruction"]
    
    result = await agent.ainvoke({
        "messages": [{"role":"user", "content":instruction}]
    })
        
    answer =  result.get("messages")[-1].content if result.get("messages") else "No response"
    generated_message = {"role":"assistant", "content": answer}

    print(result)

    return {
        "messages": [generated_message],
        "answer": answer
    }
    
@node
async def department_search(state: GraphStatus) -> GraphStatus:
    """
    학과 정보 탐색을 하는 단계
    """
    model = chat_gpt
    
    instruction = state["instruction"]
    optional_args = state["optional_args"]
    
    department = optional_args.get("department")
    
    context = retreive(instruction=instruction, department=department)
    
    prompt = f'''Please answer the following question using the provided context information.
                Please follow these guidelines when generating your response:
                    1. Mandatory source citation for all content derived from the provided context
                    2. Format citations as "**[id, question(in context, not instruction), answer]**" after each relevant information
                    3. Distinguish between different sources when using information from multiple references
                    4. Clearly indicate when using general knowledge by noting "commonly known fact" or "general knowledge"
                
                Please respond in Korean.
                
                ### Question
                {instruction}
                
                ### Context
                {context}'''
            
    answer = model.query_by_single_instruction(prompt)
    generated_message = {"role":"assistant", "content": answer}

    return {
        "messages": [generated_message],
        "answer": answer
    }

def retreive(instruction: str, department: str = None) -> str:
    retreive_result = chroma_db.query(input = instruction, filter=[department], n_results=10)
    return retreive_result
    
@node
async def web_search(state: GraphStatus) -> GraphStatus:
    """
    웹 검색을 하는 단계
    """
    
    client_config = await get_multi_server_mcp_clients_from_api()
    
    client = MultiServerMCPClient(client_config)
    
    model = chat_gpt.get_model()
    
    tools = await client.get_tools(server_name="naver_search_mcp")
    
    agent = create_react_agent(model=model,
                            tools=tools,
                            state_schema=GraphStatus)
    
    prompt = f'''
    Search for information about the question. Please cite the sources of search results and respond in Korean.
    Question: {state["instruction"]}
    '''
    question_message = {"role":"user", "content": prompt}
    state["messages"] += [question_message]
        
    result = await agent.ainvoke({
        "messages": [question_message]
    })
        
    answer =  result.get("messages")[-1].content if result.get("messages") else "No response"
    generated_message = {"role":"assistant", "content": answer}

    return {
        "messages": [generated_message],
        "answer": answer
    }

@node
async def merge_messages(state: GraphStatus) -> GraphStatus:
    """
    메시지를 병합하는 단계
    """
    
    model = chat_gpt
    
    prompt = f'''
    Please reconstruct the message content based on the conversation history so far. 
    
    Please structure your response so that it directly answers the user's most recent question.
    
    동영상, 외부 링크 등의 컨텍스트가 주어졌을 경우, 필수적으로 소개해주세요.
    
    instruction: {state["instruction"]}
    
    DON'T HALLUCINATE ANYTHING. ONLY USE THE INFORMATION PROVIDED IN THE CONTEXT.
    '''
    
    state["messages"] += [{"role":"user", "content": prompt}]
    
    result = model.query_by_messages(state["messages"])
    
    answer =  result
    generated_message = {"role":"assistant", "content": answer}
    
    
    return {
        "messages": [generated_message],
        "answer": answer
    }