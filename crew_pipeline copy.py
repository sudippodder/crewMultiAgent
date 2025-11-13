from crewai import Agent, Task, Crew
#from tools.serper_tool import SerperTool
from dotenv import load_dotenv
import os
from langchain.agents import Tool, initialize_agent
from langchain.chat_models import ChatOpenAI
from langchain.tools import StructuredTool
import http.client
import json

load_dotenv()


@tool("Serper_Search", return_direct=True)
def serper_search(topic: str) -> str:
    conn = http.client.HTTPSConnection("google.serper.dev")
    payload = json.dumps({
        "q": topic
    })
    headers = {
        'X-API-KEY': 'eeabdbbd085e48c7a9b78e8a44f306bf8d6ba545',
        'Content-Type': 'application/json'
    }
    conn.request("POST", "/search", payload, headers)
    res = conn.getresponse()
    response = res.read()
    return response.decode("utf-8")
    #data.raise_for_status()
    #data = response.decode("utf-8")
    # data = json.loads(response)
    # #return data
    # snippets = [r.get("snippet", "") for r in data.get("organic", [])]
    # return "\n".join(snippets) if snippets else "No results found."
    #return data.decode("utf-8")


SerperTool = StructuredTool.from_function(
    func=serper_search,
    name="Serper_Search",
    description="Searches Google using Serper.dev API. Input should be a topic string."
)

def run_pipeline(
    topic: str,
    researcher_goal: str,
    researcher_backstory: str,
    writer_goal: str,
    writer_backstory: str,
    editor_goal: str,
    editor_backstory: str
):
    # serper_tool = SerperTool()
    # return serper_tool
    #serper_tool = SerperTool(topic)
    # serper_tool = Tool(
    #     name=topic,
    #     func=SerperTool,
    #     description="Search Google data via Serper API. Input should be a search topic string."
    # )
    #tool = [SerperTool]
    llm = ChatOpenAI(model="gpt-4-turbo")
    # st.markdown(f"""
    # topic to search: **{topic}**
    # {serper_tool}
    # """,unsafe_allow_html=True)
    researcher = Agent(
        role="Researcher",
        llm=llm,
        goal=researcher_goal,
        backstory=researcher_backstory,
        tools=[SerperTool.to_langchain_tool()],
        agent_type="zero-shot-react-description",
        verbose=True,
    )

    writer = Agent(
        role="Content Writer",
        goal=writer_goal,
        backstory=writer_backstory,
        verbose=True,
    )

    editor = Agent(
        role="Editor and Proofreader",
        goal=editor_goal,
        backstory=editor_backstory,
        verbose=True,
    )

    publisher = Agent(
        role="Publisher",
        goal="Prepare the final content for publication.",
        backstory="You finalize formatting and make sure the post looks clean.",
        verbose=True,
    )

    research_task = Task(
        description=f"Research information on '{topic}' using Serper.",
        expected_output="A concise research summary containing relevant facts and sources about the topic.",
        agent=researcher,
    )

    writing_task = Task(
        description=f"Write a blog post on '{topic}' using the research summary.",
        expected_output="A detailed, well-structured draft of the blog post.",
        agent=writer,
    )

    editing_task = Task(
        description="Edit and proofread the blog post for clarity and tone.",
        expected_output="A polished, final version of the blog post.",
        agent=editor,
    )

    publish_task = Task(
        description="Finalize the blog for publication.",
        expected_output="A formatted blog post ready for publishing.",
        agent=publisher,
    )

    crew = Crew(
        agents=[researcher, writer, editor, publisher],
        tasks=[research_task, writing_task, editing_task, publish_task],
        verbose=True,
    )

    result = crew.kickoff()
    return str(result)
