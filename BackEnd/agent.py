# agent.py
import requests
import os
import re
from datetime import date, timedelta
from models.destinations import get_all_destinations
from models.itineraries import create_itinerary
from models.itinerary_day import create_day
from models.activities import create_activity

# ─────────────────────────────────────────
# Ollama Cloud Setup
# ─────────────────────────────────────────
os.environ["OLLAMA_API_KEY"] = "4d877094e2724901ad62b12d812634c9.vMGJhg4Q26CxeDnI4knZn090"  # ← paste your key here

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "gemma4:31b-cloud"

SYSTEM_INSTRUCTION = """You are an intelligent travel chatbot assistant named TravelBot.

You ALWAYS follow this ReAct thinking process before responding:

Thought: Analyze what the user wants. Consider their past preferences if available.
Action: Decide what to do — answer a question, recommend a destination, or plan an itinerary.
Observation: Note any important details from the user's message or history.
Answer: Give your final response to the user.

---

RULES:
- Always reason through Thought → Action → Observation → Answer internally.
- Only show the final Answer to the user. Never show Thought/Action/Observation in your reply.
- Use the user's past conversation history to personalize every response.
- Be friendly, concise, and helpful.

---

You help users with:
1. Answering general travel questions
2. Planning detailed day-by-day itineraries
3. Recommending destinations based on preferences
4. Providing travel tips and advice

---

When planning a trip, ALWAYS format your Answer EXACTLY like this:

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
"""

# ─────────────────────────────────────────
# Get destinations from DB
# ─────────────────────────────────────────
def get_destinations_context():
    destinations = get_all_destinations()
    if not destinations:
        return ""
    lines = []
    for d in destinations:
        lines.append(
            f"- {d['city']}, {d['country']} | "
            f"Budget: ${d['avg_budget_per_day']}/day | "
            f"Best Season: {d['best_season']}"
        )
    return "\n".join(lines)


# ─────────────────────────────────────────
# Main Agent Function
# ─────────────────────────────────────────
def run_agent(user_message, conversation_history, session_id=None, user_id=None):
    from db import get_user_history  # ← add this import

    wants_itinerary = any(w in user_message.lower() for w in
                          ["plan", "trip", "itinerary", "travel", "visit", "tour"])

    # ── Build messages ──────────────────────────────────────────
    messages = [{"role": "system", "content": SYSTEM_INSTRUCTION}]

    # 1. LONG-TERM MEMORY — all past sessions of this user
    if user_id:
        past_messages = get_user_history(user_id, limit=30)
        if past_messages:
            memory_lines = []
            for m in past_messages:
                prefix = "User" if m["sender"] == "user" else "Bot"
                memory_lines.append(f"{prefix}: {m['message']}")

            messages.append({
                "role": "system",
                "content": (
                    "This user's past conversation history across all sessions:\n\n"
                    + "\n".join(memory_lines)
                    + "\n\nUse this to remember their preferences and past trips."
                )
            })

    # 2. CURRENT SESSION — last 10 messages (short-term)
    for msg in conversation_history[-10:]:
        role = "user" if msg["sender"] == "user" else "assistant"
        messages.append({"role": role, "content": msg["message"]})

    # 3. Destinations context on first message of session
    if len(conversation_history) == 0:
        destinations_context = get_destinations_context()
        if destinations_context:
            full_message = f"Available destinations:\n{destinations_context}\n\nUser: {user_message}"
        else:
            full_message = user_message
    else:
        full_message = user_message

    messages.append({"role": "user", "content": full_message})

    print(f"🤖 {MODEL} thinking... (memory blocks: {len(messages)})")

    # ── Call model ───────────────────────────────────────────────
    try:
        response = requests.post(
            OLLAMA_URL,
            headers={"Authorization": f"Bearer {os.environ.get('OLLAMA_API_KEY', '')}"},
            json={
                "model": MODEL,
                "messages": messages,
                "stream": False,
                "options": {
                    "num_predict": 1024,
                    "temperature": 0.7
                }
            },
            timeout=60
        )

        result = response.json()
        print("RAW RESPONSE:", result)

        if "message" in result:
            reply = result["message"]["content"]
        elif "error" in result:
            reply = f"Error from Ollama: {result['error']}"
        else:
            reply = str(result)

    except requests.exceptions.Timeout:
        reply = "Request timed out. Please try again."
    except Exception as e:
        reply = f"Error: {str(e)}"

    print("✅ Response received")

    # ── Save itinerary if needed ─────────────────────────────────
    if wants_itinerary and session_id and user_id and "Error" not in reply:
        try:
            save_itinerary_to_db(reply, session_id, user_id)
        except Exception as e:
            print("⚠️ Could not save itinerary:", str(e))

    return reply

# ─────────────────────────────────────────
# Save Itinerary to DB
# ─────────────────────────────────────────
def save_itinerary_to_db(ai_response, session_id, user_id):
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

    # Save days
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

        # Save activities
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


# ─────────────────────────────────────────
# Helper
# ─────────────────────────────────────────
def extract(text, field):
    match = re.search(rf'{field}:\s*(.+)', text)
    return match.group(1).strip() if match else ''