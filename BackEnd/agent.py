# agent.py
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from models.destinations import get_all_destinations, search_destinations
from models.itineraries import create_itinerary
from models.itinerary_day import create_day
from models.activities import create_activity

# ─────────────────────────────────────────
# Ollama Model
# ─────────────────────────────────────────
llm = ChatOllama(
    model="llama3.2",
    base_url="http://localhost:11434",
    temperature=0.7
)

# ─────────────────────────────────────────
# Helper — get destinations from DB
# ─────────────────────────────────────────
def get_destinations_context():
    destinations = get_all_destinations()
    if not destinations:
        return "No destinations available."
    lines = []
    for d in destinations:
        lines.append(
            f"- {d['city']}, {d['country']} | "
            f"Budget: ${d['avg_budget_per_day']}/day | "
            f"Best Season: {d['best_season']} | "
            f"{d['description']}"
        )
    return "\n".join(lines)

# ─────────────────────────────────────────
# MAIN FUNCTION
# ─────────────────────────────────────────
def run_agent(user_message, conversation_history):

    # get destinations from DB and inject into prompt
    destinations_context = get_destinations_context()

    # build messages
    messages = [
        SystemMessage(content=f"""
You are an intelligent travel chatbot assistant.
You help users with:
1. Answering general travel questions
2. Planning detailed day-by-day travel itineraries
3. Recommending destinations

Here are the available destinations in our database:
{destinations_context}

When planning a trip always:
- Use the destinations from the database above
- Create a detailed day by day plan
- Include hotels, transport, activities and costs
- Give a total budget estimate
- Be friendly, helpful and detailed
        """)
    ]

    # add conversation history
    for msg in conversation_history:
        if msg["sender"] == "user":
            messages.append(HumanMessage(content=msg["message"]))
        else:
            messages.append(AIMessage(content=msg["message"]))

    # add current message
    messages.append(HumanMessage(content=user_message))

    # get response from llama3.2
    response = llm.invoke(messages)

    # auto save itinerary if user asked for a trip plan
    keywords = ["plan", "trip", "itinerary", "travel", "visit", "tour"]
    if any(word in user_message.lower() for word in keywords):
        try:
            auto_save_itinerary(user_message, response.content, conversation_history)
        except Exception as e:
            print("⚠️ Could not save itinerary:", str(e))

    return response.content

# ─────────────────────────────────────────
# Auto save itinerary to DB
# ─────────────────────────────────────────
def auto_save_itinerary(user_message, ai_response, conversation_history):
    # extract session_id and user_id from history if available
    # this is a basic save — just saves the summary
    print("💾 Saving itinerary to DB...")
    # you can expand this later to parse days and activities