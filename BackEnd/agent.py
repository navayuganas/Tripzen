# agent.py
import os
import re
from datetime import date, timedelta

from langchain_ollama import ChatOllama
from langchain_classic.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun

from models.destinations import get_all_destinations
from models.itineraries import create_itinerary
from models.itinerary_day import create_day
from models.activities import create_activity

# ─────────────────────────────────────────
# Ollama Cloud Setup
# ─────────────────────────────────────────
os.environ["OLLAMA_API_KEY"] = "your_ollama_api_key_here"  

llm = ChatOllama(
    model="gemma4:31b-cloud",
    temperature=0.7,
    num_predict=1024,
)

# ─────────────────────────────────────────
# Tools
# ─────────────────────────────────────────

search = DuckDuckGoSearchRun()

@tool
def web_search(query: str) -> str:
    """Search the web for real-time travel information like weather,
    flight prices, hotel availability, visa requirements, and current events."""
    try:
        print(f"🔍 Searching: {query}")
        result = search.run(query)
        print(f"✅ Search done")
        return result
    except Exception as e:
        return f"Search failed: {str(e)}"


@tool
def get_destinations(query: str = "") -> str:
    """Get all available travel destinations from the database."""
    try:
        destinations = get_all_destinations()
        if not destinations:
            return "No destinations found in database."
        lines = []
        for d in destinations:
            lines.append(
                f"- {d['city']}, {d['country']} | "
                f"Budget: ${d['avg_budget_per_day']}/day | "
                f"Best Season: {d['best_season']} | "
                f"{d['description']}"
            )
        return "\n".join(lines)
    except Exception as e:
        return f"Error fetching destinations: {str(e)}"


@tool
def save_itinerary(ai_response: str, session_id: int, user_id: int) -> str:
    """Save a generated itinerary to the database.
    Only call this when a full itinerary has been generated."""
    try:
        print("💾 Saving itinerary to DB...")

        title       = extract(ai_response, "ITINERARY") or "My Trip"
        destination = extract(ai_response, "DESTINATION")
        duration    = extract(ai_response, "DURATION")
        budget      = extract(ai_response, "BUDGET").replace("$", "").replace(",", "")
        travelers   = extract(ai_response, "TRAVELERS")
        trip_type   = extract(ai_response, "TRIP_TYPE")
        summary     = extract(ai_response, "SUMMARY")

        total_days = int(re.search(r'\d+', duration).group()) if re.search(r'\d+', duration) else 1
        start_date = date.today()
        end_date   = start_date + timedelta(days=total_days)

        itinerary_id = create_itinerary(
            session_id, user_id, title, destination,
            str(start_date), str(end_date), total_days,
            float(budget) if budget.replace('.', '').isdigit() else 0,
            int(travelers) if travelers.isdigit() else 1,
            trip_type, summary
        )
        print(f"✅ Itinerary saved: ID {itinerary_id}")

        day_blocks = re.split(r'DAY \d+:', ai_response)
        for i, block in enumerate(day_blocks[1:], start=1):
            lines       = block.strip().split('\n')
            day_title   = lines[0].strip() if lines else f"Day {i}"
            hotel       = extract(block, "HOTEL")
            transport   = extract(block, "TRANSPORT")
            cost        = extract(block, "COST").replace("$", "").replace(",", "")
            description = extract(block, "DESCRIPTION")

            day_id = create_day(
                itinerary_id, i, day_title, description,
                hotel, transport,
                float(cost) if cost.replace('.', '').isdigit() else 0
            )
            print(f"✅ Day {i} saved: ID {day_id}")

            activity_section = re.search(r'ACTIVITIES:(.*?)(?=DAY \d+:|$)', block, re.DOTALL)
            if activity_section:
                for line in activity_section.group(1).strip().split('\n'):
                    line  = line.strip().lstrip('- ')
                    parts = [p.strip() for p in line.split('|')]
                    if len(parts) >= 3:
                        create_activity(
                            day_id,
                            parts[0],
                            parts[1] if len(parts) > 1 else '',
                            parts[2] if len(parts) > 2 else '',
                            float(parts[3].replace('$', '').replace(',', ''))
                            if len(parts) > 3 and parts[3].replace('$', '').replace(',', '').replace('.', '').isdigit() else 0,
                            parts[4] if len(parts) > 4 else ''
                        )

        print("✅ Full itinerary saved to DB!")
        return f"Itinerary saved successfully with ID {itinerary_id}"

    except Exception as e:
        print(f"⚠️ Could not save itinerary: {str(e)}")
        return f"Failed to save itinerary: {str(e)}"


# ─────────────────────────────────────────
# Prompt
# ─────────────────────────────────────────
prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an intelligent travel chatbot assistant.
You help users with:
1. Answering general travel questions
2. Planning detailed day-by-day travel itineraries
3. Recommending destinations
4. Providing travel tips and advice

You have access to these tools:
- web_search: use for real-time info like weather, prices, visa, flights
- get_destinations: use to fetch available destinations from database
- save_itinerary: use ONLY after generating a full itinerary

When planning a trip ALWAYS format response EXACTLY like this:

ITINERARY: [Title]
DESTINATION: [City, Country]
DURATION: [X days]
BUDGET: $[total amount]
TRAVELERS: [number]
TRIP_TYPE: [leisure/adventure/business]
SUMMARY: [2-3 line summary]

DAY 1: [Day Title]
HOTEL: [Hotel name]
TRANSPORT: [Transport mode]
COST: $[estimated cost]
DESCRIPTION: [Day description]
ACTIVITIES:
- [Activity name] | [Location] | [Time] | $[cost] | [notes]

DAY 2: [Day Title]
...and so on

Always be friendly, helpful and detailed.
Keep responses concise."""),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

# ─────────────────────────────────────────
# Agent Setup
# ─────────────────────────────────────────
tools = [web_search, get_destinations, save_itinerary]

agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    max_iterations=5,
    handle_parsing_errors=True,
)


# ─────────────────────────────────────────
# Main Function
# ─────────────────────────────────────────
def run_agent(user_message, conversation_history, session_id=None, user_id=None):

    # build chat history
    chat_history = []
    for msg in conversation_history[-10:]:
        if msg["sender"] == "user":
            chat_history.append(HumanMessage(content=msg["message"]))
        else:
            chat_history.append(AIMessage(content=msg["message"]))

    # add session context
    full_message = user_message
    if session_id and user_id:
        full_message = f"{user_message} [session_id={session_id}, user_id={user_id}]"

    print(f"📩 User: {user_message}")
    print(f"🤖 Agent thinking...")

    try:
        result = agent_executor.invoke({
            "input": full_message,
            "chat_history": chat_history,
        })
        reply = result["output"]
        print(f"✅ Agent done")

    except Exception as e:
        print(f"⚠️ Agent error: {str(e)}")
        reply = "Sorry, I encountered an error. Please try again."

    return reply


# ─────────────────────────────────────────
# Helper
# ─────────────────────────────────────────
def extract(text, field):
    match = re.search(rf'{field}:\s*(.+)', text)
    return match.group(1).strip() if match else ''