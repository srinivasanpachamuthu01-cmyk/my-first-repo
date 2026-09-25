Python 3.14.4 (tags/v3.14.4:23116f9, Apr  7 2026, 14:10:54) [MSC v.1944 64 bit (AMD64)] on win32
Enter "help" below or click "Help" above for more information.
>>> import os
... from dotenv import load_dotenv
... from langchain_community.tools.tavily_search import TavilySearchResults
... from langchain_openai import ChatOpenAI
... from langgraph.prebuilt import create_react_agent
... 
... # 1. Load the API keys safely from your hidden .env file
... load_dotenv()
... 
... # 2. Define the tool (The agent's internet access)
... search_tool = TavilySearchResults(max_results=3)
... tools = [search_tool]
... 
... # 3. Choose the "Brain" (The LLM that will handle the reasoning)
... llm = ChatOpenAI(model="gpt-4o", temperature=0)
... 
... # 4. Create the Agent using LangGraph
... agent_executor = create_react_agent(llm, tools)
... 
... # 5. Define the high-level goal you want the agent to achieve
... prompt = (
...     "Research the current state of Apple's stock and any major recent announcements in 2026. "
...     "Provide a concise 3-bullet-point summary report."
... )
... 
... # 6. Run the Agent and stream its step-by-step thinking process
... print("🤖 Agent is thinking and executing its plan...\n")
... events = agent_executor.stream(
...     {"messages": [("user", prompt)]},
...     stream_mode="values"
... )
... 
... # Print the agent's internal monologue and actions to the console
... for event in events:
...     last_message = event["messages"][-1]
