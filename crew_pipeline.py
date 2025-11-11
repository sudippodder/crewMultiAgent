from crewai import Agent, Task, Crew
from tools.serper_tool import SerperTool
from dotenv import load_dotenv
import os

load_dotenv()

def run_pipeline(
    topic: str,
    researcher_goal: str,
    researcher_backstory: str,
    writer_goal: str,
    writer_backstory: str,
    editor_goal: str,
    editor_backstory: str
):
    serper_tool = SerperTool()

    researcher = Agent(
        role="Researcher",
        goal=researcher_goal,
        backstory=researcher_backstory,
        tools=[serper_tool],
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
