import os
from pathlib import Path
from dotenv import load_dotenv

# Updated imports to ensure compatibility with modern LangChain/LangGraph standards
from langchain.agents import create_react_agent
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_openai import ChatOpenAI

# =====================================================================
# STEP 1: LOAD ENVIRONMENT VARIABLES FROM WINDOWS DESKTOP
# =====================================================================
home_dir = Path(os.path.expanduser("~"))

# Dynamically target the .env.txt file found on your Desktop
desktop_env_path = home_dir / "Desktop" / ".env.txt"
if not desktop_env_path.exists():
    desktop_env_path = home_dir / "OneDrive" / "Desktop" / ".env.txt"

print(f"🔍 System: Reading API keys from {desktop_env_path}...")
load_dotenv(dotenv_path=desktop_env_path)

# Sanitize input keys
openai_key = os.environ.get("OPENAI_API_KEY", "").strip().strip("'\"")
tavily_key = os.environ.get("TAVILY_API_KEY", "").strip().strip("'\"")

if not openai_key or not tavily_key:
    raise ValueError("❌ Error: Verification failed. Please ensure valid API keys exist in your .env.txt file.")

# Inject sanitized keys into active memory
os.environ["OPENAI_API_KEY"] = openai_key
os.environ["TAVILY_API_KEY"] = tavily_key

# =====================================================================
# STEP 2: INITIALIZE AI BRAIN AND SEARCH EXTENSION
# =====================================================================
# Configure search engine to look for routes, transit, and operator schedules
search_tool = TavilySearchResults(
    max_results=4, 
    description="Use this tool to find bus schedules, transit routes, travel operators, NH highway details, and travel times."
)
tools = [search_tool]

# Initialize GPT-4o as our analytical router
llm = ChatOpenAI(model="gpt-4o", temperature=0.2)

# =====================================================================
# STEP 3: CONSTRUCT THE TRAVEL ROUTING AGENT
# =====================================================================
# Build the ReAct workflow
agent_executor = create_react_agent(llm, tools)

# Prompt engineering to pull the best routes, highway details, and booking tips
prompt = (
    "Find the best bus route options from Chennai to Salem (Tamil Nadu) for travel in May 2026. "
    "Identify the primary National Highways used, typical travel duration, major government/private bus operators, "
    "and provide a structured breakdown of the most efficient route versus alternatives."
)

print("\n🚌 Routing AI activated. Analyzing Chennai to Salem transit options...\n")

try:
    # Stream the analytical steps taken by the AI agent
    events = agent_executor.stream(
        {"messages": [("user", prompt)]},
        stream_mode="values"
    )

    for event in events:
        if "messages" in event and event["messages"]:
            last_message = event["messages"][-1]
            last_message.pretty_print()
            print("\n" + "="*60 + "\n")

except Exception as e:
    print(f"\n❌ Execution stopped due to error: {e}")
