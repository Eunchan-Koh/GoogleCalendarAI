import os
from dotenv import load_dotenv
import time
from langchain.agents import initialize_agent
from langchain.agents.agent import AgentExecutor
from langchain_core.tools import StructuredTool
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from datetime import datetime, timezone
from langchain.callbacks.human import HumanApprovalCallbackHandler
from langchain_mongodb.vectorstores import MongoDBAtlasVectorSearch
from pymongo import MongoClient
import numpy as np

print(os.getcwd())

try:
    load_dotenv()
except:
    pass


#availability check
google_valid = False
openai_valid = False

if not os.getenv("GOOGLE_API_KEY"):
    print("GOOGLE_API_KEY_NOT_FOUND")
else:
    google_valid = True

if not os.getenv("LANGSMITH_API_KEY"):
    print("LANGSMITH_API_KEY_NOT_FOUND")
if not os.getenv("LANGSMITH_PROJECT"):
    print("LANGSMITH_PROJECT is set to default")
    os.environ["LANGSMITH_PROJECT"] = "default"
if not os.getenv("LANGSMITH_TRACING_V2"):
    print("LANGSMITH_TRACING_V2 is set to true")
    os.environ["LANGSMITH_TRACING_V2"] = "true"
    
if not os.getenv("OPENAI_API_KEY"):
    print("OPENAI_API_KEY_NOT_FOUND")
else:
    openai_valid = True
    
import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']

creds = None
if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)

if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    with open('token.json', 'w') as token:
        token.write(creds.to_json())

service = build('calendar', 'v3', credentials=creds)

#check for similarity between embeddings
def cosine_similarity(vec1, vec2):
    dot_product = np.dot(vec1, vec2)
    norm_vec1 = np.linalg.norm(vec1)
    norm_vec2 = np.linalg.norm(vec2)
    return dot_product / (norm_vec1 * norm_vec2)
    
#check specific day's schedule. Tool for the agent
def check_day_schedule(start_date:str) -> str:
    
    if not start_date or len(start_date) != 10:
        now = datetime.now(timezone.utc).isoformat()
    else:
        now = start_date+"T00:00:00+00:00"
        
    events_result = service.events().list(
        calendarId='primary',
        timeMin=now,
        maxResults=10,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    
    events = events_result.get('items', [])

    print("\n📋 recent event lists:")
    for evt in events:
        print("summary:", evt.get('summary'))
        print("event ID:", evt.get('id'))
        print("link:", evt.get('htmlLink'))
        print("---")
        
    return f"successfully checked."
    
# add a specific event on a specific day. Tool for the agent
def AddEvent(name:str, content:str, start_date:str, end_date:str) -> str:
    event = {
        'summary': name, 
        'location': 'online', 
        'description': content,
        'start': {
            'date': start_date,
            'timeZone': 'America/Toronto',
        },
        'end': {
            'date': end_date,
            'timeZone': 'America/Toronto',
        },
    }
    
    event = service.events().insert(calendarId='primary', body=event).execute()
    print('created event link: %s' % (event.get('htmlLink')))
    print(f"Event {name} has been created on {start_date}.")
    print(f"description: {event.get('description')}")
    return "success!"


# delete specific day's event by name. Tool for the agent
def DeleteEvent(name:str, start_date:str) -> str:

    if not start_date or len(start_date) != 10:
        now = datetime.now(timezone.utc).isoformat()
    else:
        now = start_date+"T00:00:00+00:00"
    events_result = service.events().list(
        calendarId='primary',
        timeMin=now,
        maxResults=10,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    
    events = events_result.get('items', [])

    embedding_model = OpenAIEmbeddings();

    event_summaries = [name] + [evt.get('summary', '') for evt in events]
    tempEmbeddingList = embedding_model.embed_documents(event_summaries)

    highest_sim = 0
    highest_index = 0
    
    for i in range(1, len(tempEmbeddingList)):
        similarity = cosine_similarity(tempEmbeddingList[0], tempEmbeddingList[i])
        # print("Cosine Similarity:", similarity)
        if similarity > highest_sim:
            highest_sim = similarity
            highest_index = i

    print(f"selected event: {events[highest_index-1].get('summary')}")
    
    event_id = events[highest_index-1].get('id')
    print(f"eventid: {event_id}")
    if similarity < 0.7:
        print(f"failed. similarity is: {similarity}")
        return "failed"
    service.events().delete(calendarId='primary', eventId=event_id).execute()
    print("event deleted.")
    
    return "success!"



model = ChatOpenAI(model="gpt-4.1-nano", temperature=0)

# StructuredTool since multiple inputs are required from the functions
tools = [
    StructuredTool.from_function(name="DayChecker", func=check_day_schedule, description=". Check schedules of days from start_date. start_date must have 0000-00-00 format. for example, 2025, September 5th into 2025-09-05."),
    StructuredTool.from_function(name="AddEvent", func=AddEvent, description="Tool to add a schedule on a specific date. start_date and end_date must have 0000-00-00 format. for example, 2025, September 5th into 2025-09-05. name is the short description about the schedule and content shows the detailed description. content can be empty but name must be filled in. Also answer final answer based on observation."),
    StructuredTool.from_function(name="DeleteEvent", func=DeleteEvent, description="used to remove a schedule on a specific date or around that date. start_date must have 0000-00-00 format. for example, 2025, September 5th into 2025-09-05. name is the name of schedule that user wants to remove. start_date can be empty but name must be filled in. Also answer final answer based on observation.")
]

agent = initialize_agent(tools, model, agent="openai-functions", agent_kwargs={"prefix": "You must always give a polite, full-sentence final answer."})

# To interrupt and check if the AI agent has selected correct dates and event when calling tools via agent.
handler = HumanApprovalCallbackHandler()
while True:
    print("fill in request related to the schedule:",end="")
    user_input = input()
    today = datetime.datetime.now(timezone.utc).isoformat()
    extra_prompt = f"today's date is {today}."

    outSen = agent.run(f"{extra_prompt} {user_input}", callbacks=[handler])
    print(outSen)