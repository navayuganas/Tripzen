# agent.py
import requests
from models.destinations import get_all_destinations
from models.itineraries import create_itinerary
from models.itinerary_day import create_day
from models.activities import create_activity
import re
from datetime import date, timedelta

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "gemma4:31b-cloud"

SYSTEM_INSTRUCTION = """You are an intelligent travel chatbot assistant.
You help users with:
1. Answering general travel questions
2. Planning detailed day-by-day travel itineraries
3. Recommending destinations
4. Providing travel tips and advice

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
Keep responses concise."""


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


def run_agent(user_message, conversation_history, session_id=None, user_id=None):

    wants_itinerary = any(w in user_message.lower() for w in
                          ["plan", "trip", "itinerary", "travel", "visit", "tour"])

    # build messages
    messages = [{"role": "system", "content": SYSTEM_INSTRUCTION}]

    # only last 10 messages
    for msg in conversation_history[-10:]:
        role = "user" if msg["sender"] == "user" else "assistant"
        messages.append({"role": role, "content": msg["message"]})

    # only add destinations on first message
    if len(conversation_history) == 0:
        destinations_context = get_destinations_context()
        if destinations_context:
            full_message = f"Available destinations:\n{destinations_context}\n\nUser: {user_message}"
        else:
            full_message = user_message
    else:
        full_message = user_message

    messages.append({"role": "user", "content": full_message})

    print(f"🤖 {MODEL} thinking...")
    response = requests.post(OLLAMA_URL, json={
        "model": MODEL,
        "messages": messages,
        "stream": False,
        "options": {
            "num_predict": 1024,
            "temperature": 0.7
        }
    })

    # handle response safely
    result = response.json()
    print("RAW RESPONSE:", result)  # ← shows full response in terminal

    if "message" in result:
        reply = result["message"]["content"]
    elif "error" in result:
        reply = f"Error from Ollama: {result['error']}"
    else:
        reply = str(result)
    print("✅ Response received")

    if wants_itinerary and session_id and user_id:
        try:
            save_itinerary_to_db(reply, session_id, user_id)
        except Exception as e:
            print("⚠️ Could not save itinerary:", str(e))

    return reply


def save_itinerary_to_db(ai_response, session_id, user_id):
    print("💾 Saving itinerary to DB...")

    title       = extract(ai_response, "ITINERARY") or "My Trip"
    destination = extract(ai_response, "DESTINATION")
    duration    = extract(ai_response, "DURATION")
    budget      = extract(ai_response, "BUDGET").replace("$","").replace(",","")
    travelers   = extract(ai_response, "TRAVELERS")
    trip_type   = extract(ai_response, "TRIP_TYPE")
    summary     = extract(ai_response, "SUMMARY")

    total_days = int(re.search(r'\d+', duration).group()) if re.search(r'\d+', duration) else 1

    start_date = date.today()
    end_date   = start_date + timedelta(days=total_days)

    itinerary_id = create_itinerary(
        session_id, user_id, title, destination,
        str(start_date), str(end_date), total_days,
        float(budget) if budget.replace('.','').isdigit() else 0,
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
        cost        = extract(block, "COST").replace("$","").replace(",","")
        description = extract(block, "DESCRIPTION")

        day_id = create_day(
            itinerary_id, i, day_title, description,
            hotel, transport,
            float(cost) if cost.replace('.','').isdigit() else 0
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
                        float(parts[3].replace('$','').replace(',',''))
                        if len(parts) > 3 and parts[3].replace('$','').replace(',','').replace('.','').isdigit() else 0,
                        parts[4] if len(parts) > 4 else ''
                    )
    print("✅ Full itinerary saved to DB!")


def extract(text, field):
    match = re.search(rf'{field}:\s*(.+)', text)
    return match.group(1).strip() if match else ''