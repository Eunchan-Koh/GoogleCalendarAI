# GoogleCalendarAI
add/delete/check my google calendar's events via gpt-4.1-nano(chatting)

# this is....
My first agentic ai project. I started studying how to create agentic Ai a week ago.(started Sept 9th, 2025.)

# Why google calendar ai?
I uses it often, and I wanted to create an agentic ai by myself to study about it. This was the first thing I could thought of as a small ai project.

# Used...
LangChain</br>
OpenAI</br>
GOOGLE API - Calendar API</br>

# Goal is to...
- create an agentic ai that adds/deletes events on my google calendar
- get used to LangChain and OpenAI more

# Achievement
- learned how agentic AI works
- learned why langchain is beneficial
- learned that similarity between words can be calculated by myself using embedding_models of the foundation LLM models
- Still, calling embedding function frequently can cause huge latency. It is best to collect all documents and embed them at once if possible.
- Treating AI as a human makes things much easier to understand. It somewhat feels like being a senior developer/manager, although I never used to be yet.
    - by realizing this, I could expect by myself of hierarchical agentic ai structure. Make AI agents that are specialized on each task, and giving task to their manager agent ai. I will try to make this project have such format in the future, creating more agentic ais

# How it looks like...
https://www.youtube.com/watch?v=TDvGk521RSU</br>

# Plan (can be delayed)
- add voice-to-text ai so these functions can be done using human voice. Adding tts can be beneficial since if that can be made, I don't really need to look into the screen to add a new schedule!
- create more agentic ais and create a manager ai, so try building hierarchical structure by myself.

!!!.env file or environment variable settings are requried for:</br>

GOOGLE_API_KEY <----- Not necessary yet</br>
LANGSMITH_API_KEY <-- Only if you want to trace its process from langsmith</br>
LANGSMITH_PROJECT</br>
LANGSMITH_TRACING_V2</br>
OPEN_API_KEY <------- Must be set</br>

!!! also needs to get:</br>

credential.json <---- can be obtained from google cloud console</br>

How To Use:
1. needs to add yourself into your google cloud's project test user
     - if you don't have a project, you should create one to use it.
2. create OAuth client ID as desktop app and download json file. rename it to credential.json.
3. place all those files in the same dir. R
     - Recommendation is to create a new folder and put all these files in the same folder since it will automatically create token.json.
