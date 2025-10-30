from crewai import Agent, Task, Crew
from tools.serper_tool import SerperTool
from dotenv import load_dotenv
import os

load_dotenv() 

def run_pipeline(topic: str):
    serper_tool = SerperTool()

    researcher = Agent(
        role="Researcher",
        goal="Find and summarize useful blog content for the given topic.",
        backstory="You're great at finding relevant sources online.",
        tools=[serper_tool],
        verbose=True,
    )

    writer = Agent(
        role="Content Writer",
        goal="Write a detailed, SEO-friendly blog post using the research.",
        backstory="You're a professional writer skilled at clarity and engagement.",
        verbose=True,
    )

    editor = Agent(
        role="Editor and Proofreader",
        goal="Polish and refine the blog content for tone, clarity, and grammar.",
        backstory="You ensure every piece reads naturally and professionally.",
        verbose=True,
    )

    publisher = Agent(
        role="Publisher",
        goal="Prepare the final content for publication.",
        backstory="You finalize formatting and make sure the post looks clean.",
        verbose=True,
    )

    # Define tasks
    # research_task = Task(
    #     description=f"Research information on '{topic}' using Serper.",
    #     agent=researcher,
    # )

    # writing_task = Task(
    #     description=f"Write a blog post on '{topic}' using the research summary.",
    #     agent=writer,
    # )

    # editing_task = Task(
    #     description="Edit and proofread the blog post for clarity and style.",
    #     agent=editor,
    # )

    # publish_task = Task(
    #     description="Finalize the content and prepare it for publishing.",
    #     agent=publisher,
    # )
    research_task = Task(
        description=f"Research information on '{topic}' using Serper.",
        expected_output="A concise research summary containing relevant facts and sources about the topic.",
        agent=researcher,
    )

    writing_task = Task(
        description=f"Write a blog post on '{topic}' using the research summary.",
        expected_output="A well-structured, detailed blog draft written in a natural, engaging style.",
        agent=writer,
    )

    editing_task = Task(
        description="Edit and proofread the blog post for clarity, tone, and grammar.",
        expected_output="A polished, final version of the blog post free of language or style issues.",
        agent=editor,
    )

    publish_task = Task(
        description="Prepare the final content for publication on the blog platform.",
        expected_output="The final, formatted blog post ready to be published.",
        agent=publisher,
    )

    crew = Crew(
        agents=[researcher, writer, editor],
        tasks=[research_task, writing_task, editing_task],
        verbose=True,
    )

    result = crew.kickoff()
    return str(result)  # ensure it's a string for Flask rendering
