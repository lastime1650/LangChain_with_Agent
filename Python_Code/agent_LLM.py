from logging import PlaceHolder
from typing import Optional, List, Any, Dict, Union

from langchain.chains.question_answering.map_rerank_prompt import output_parser
from langchain.llms.ollama import Ollama # ollama LLM모델
from langchain.llms import OpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains.llm import LLMChain
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
)
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.callbacks import BaseCallbackManager
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables.utils import Input

# 에이전트 관련
from langchain.tools import BaseTool
from langchain.agents import initialize_agent, Tool, create_react_agent, AgentExecutor, AgentType, \
    ConversationalAgent  # 함수 호출
from langchain.agents.agent import AgentOutputParser


# 2. 도구 설정
def add(query: str) -> str:
    query = query.split(',')
    print('add함수 호출됨@', query)
    return f"result: {int(query[0]) + int(query[1])}"


def sub(query: str) -> str:
    query = query.split(',')
    print('sub함수 호출됨@', query)
    return f"result: {int(query[0]) - int(query[1])}"

class Agent_LLM_Manager():
    def __init__(self):
        self.Agents = {}

    def Init_Agent(self, Agent_ID:str,  LLM_Model:Any)->bool:
        if(self.Check_exists_Agent(Agent_ID)):
            return False

        self.Agents[Agent_ID] = {
            "Model":LLM_Model,
            "Conversation_Memory_inst":None,
            'Prompt':None,
            'Agent':{
                'Agent_react_inst':None,
                'Agent_tools':[],
                'Agent_executor':None
            }
        }

        return True

    def Add_Agent_Tool(self, Agent_ID:str, tool_name:str, tool_func:Any, tool_description:str)->bool:
        if(not self.Check_exists_Agent(Agent_ID)):
            return False

        self.Agents[Agent_ID]['Agent']['Agent_tools'].append(Tool(name=tool_name, func=tool_func, description=tool_description) ) # 실제 툴)

        return True

    '''
        메모리 관련
    '''
    def Init_Conversation_Memory(self, ConversationID: str, return_messages: bool) -> bool:
        if (not self.Check_exists_Agent(ConversationID)):
            return False  # 이미 존재하지 않으면 실패
        self.Agents[ConversationID]["Conversation_Memory_inst"] = ConversationBufferMemory(memory_key=ConversationID,return_messages=return_messages)
        return True
    def Conversation_Memory_add_SystemMessage(self, ConversationID: str, Input: str ) -> bool:
        if (not self.Check_exists_Agent(ConversationID)):
            return False  # 이미 존재하지 않으면 실패

        if (not self.Agents[ConversationID]["Conversation_Memory_inst"]):
            return False # 이미 존재하지 않으면 실패

        self.Agents[ConversationID]["Conversation_Memory_inst"].chat_memory.add_message(SystemMessage(content=Input))
        return True
    def Conversation_Memory_add_userMessage(self, ConversationID: str, Input: str ) -> bool:
        if (not self.Check_exists_Agent(ConversationID)):
            return False  # 이미 존재하지 않으면 실패

        if (not self.Agents[ConversationID]["Conversation_Memory_inst"]):
            return False # 이미 존재하지 않으면 실패

        self.Agents[ConversationID]["Conversation_Memory_inst"].chat_memory.add_user_message(Input)
        return True
    def Conversation_Memory_add_aiMessage(self, ConversationID: str, Input: str ) -> bool:
        if (not self.Check_exists_Agent(ConversationID)):
            return False  # 이미 존재하지 않으면 실패

        if (not self.Agents[ConversationID]["Conversation_Memory_inst"]):
            return False # 이미 존재하지 않으면 실패

        self.Agents[ConversationID]["Conversation_Memory_inst"].chat_memory.add_ai_message(Input)

        return True

    '''
        프롬프트 관련
    '''
    def Set_Prompt(self, ConversationID: str) -> bool:
        if (not self.Check_exists_Agent(ConversationID)):
            return False  # 이미 존재하지 않으면 실패

        PREFIX = """You are a helpful assistant that can remember previous conversations and use tools when necessary.

        You have access to the following tools: {tools}

        Previous conversation:
        {"""+ConversationID+"""}

        Always respond to the user's questions based on the chat history when relevant. If you need to perform calculations, use the appropriate tool."""

        FORMAT_INSTRUCTIONS = """Use the following format:

        Question: the input question you must answer
        Thought: you should always think about what to do
        Action: the action to take, should be one of [{tool_names}] or just respond directly if no tool is needed
        Action Input: the input to the action if using a tool
        Observation: the result of the action if a tool was used
        ... (this Thought/Action/Action Input/Observation can repeat N times)
        Thought: I now know the final answer
        Final Answer: the final answer to the original input question"""

        SUFFIX = """Begin!

        Question: {input}
        Thought:{agent_scratchpad}"""

        # 5. 프롬프트 구성
        prompt_template = PromptTemplate(
            input_variables=["tools", "tool_names", "input", "agent_scratchpad", ConversationID],
            template=PREFIX + FORMAT_INSTRUCTIONS + SUFFIX
        )

        self.Agents[ConversationID]["Prompt"] = prompt_template
        return True

    '''
        에이전트 생성
    '''
    def Set_Agent(self, ConversationID:str)->bool:
        if (not self.Check_exists_Agent(ConversationID)):
            return False  # 이미 존재하지 않으면 실패
        if (not self.Agents[ConversationID]["Model"]):
            return False  # 이미 존재하지 않으면 실패
        if (not len(self.Agents[ConversationID]["Agent"]["Agent_tools"]) > 0):
            return False  # 이미 존재하지 않으면 실패
        if (not self.Agents[ConversationID]["Conversation_Memory_inst"]):
            return False
        if (not self.Agents[ConversationID]["Prompt"]):
            return False

        # 6. 에이전트 생성
        self.Agents[ConversationID]["Model"].bind(stop=["\nObservation:"])
        react_agent = create_react_agent(
            llm=self.Agents[ConversationID]["Model"],
            tools=self.Agents[ConversationID]["Agent"]["Agent_tools"],
            prompt=self.Agents[ConversationID]["Prompt"]
        )
        self.Agents[ConversationID]["Agent"]["Agent_react_inst"] = react_agent
        self.Agents[ConversationID]["Agent"]["Agent_executor"] = AgentExecutor.from_agent_and_tools(
            agent=react_agent,
            tools=self.Agents[ConversationID]["Agent"]["Agent_tools"],
            memory=self.Agents[ConversationID]["Conversation_Memory_inst"],
            verbose=True,
            handle_parsing_errors=True  # 파싱 에러 처리 추가
        )
        return True

    '''
        에이전트 실행
    '''
    def Start_Agent_Conversation(self, ConversationID:str, Input:str)->Optional[Dict]:
        if (not self.Check_exists_Agent(ConversationID)):
            return None  # 이미 존재하지 않으면 실패
        if (not self.Agents[ConversationID]["Agent"]["Agent_executor"]):
            return None

        return self.Agents[ConversationID]["Agent"]["Agent_executor"].invoke({
            "input": Input
        })


    def Check_exists_Agent(self, Agent_ID:str)->bool:
        if(Agent_ID in self.Agents):
            return True
        else:
            return False

inst = Agent_LLM_Manager()
inst.Init_Agent("ABC", Ollama(base_url='http://192.168.0.100:11434', model='gemma2'))
inst.Init_Conversation_Memory('ABC', True)
inst.Add_Agent_Tool('ABC', 'add', add, '3개의 인자를 모두 더하는 함수. 만약 인수가 부족하면, 나머지는 0으로 패딩하여 호출하라.')
inst.Set_Prompt('ABC')
inst.Set_Agent('ABC')
r = inst.Start_Agent_Conversation('ABC', '1+5 더하라')['output']
print(r)
r = inst.Start_Agent_Conversation('ABC', '처음에 내가 무슨 값을 더하라고 했지?')['output']
print(r)