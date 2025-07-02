# agent/setup_agent.py
import os
from dotenv import load_dotenv
from typing import Tuple, List

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain.memory import ConversationBufferWindowMemory
from langchain_groq.chat_models import ChatGroq

from prompts import SYSTEM_PROMPT
from tools.openweathermap_query import OpenWeatherMapQuery

load_dotenv()

def check_groq_key() -> bool:
    key = os.getenv("GROQ_API_KEY", "")
    return bool(key and len(key) >= 16)

if not check_groq_key():
    raise RuntimeError("🔑 Missing or invalid GROQ_API_KEY!")

def setup_agent(
    model: str = "llama3-70b-8192",
    temperature: float = 0.7,
    verbose: bool = False,
) -> Tuple[AgentExecutor, List]:
    llm = ChatGroq(
        model=model,
        temperature=temperature,
        max_retries=2,
        max_tokens=500,
        n=1,
        streaming=False,
    )
    tools = [OpenWeatherMapQuery()]
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])
    memory = ConversationBufferWindowMemory(
        k=4, memory_key="chat_history", return_messages=True
    )
    agent = create_tool_calling_agent(llm, tools, prompt)
    executor = AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=verbose,
        handle_parsing_errors=True,
        max_iterations=3,
    )
    return executor, tools

def query_llm(agent: AgentExecutor, question: str) -> str:
    res = agent.invoke({"input": question})
    return res["output"]
