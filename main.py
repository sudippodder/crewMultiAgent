from crewai import Agent, Task, Crew, Process
from tools.serper_tool import SerperTool
from dotenv import load_dotenv
# from tools.wordpress_tool import WordPressPublisher
# agents["publisher"].tools = [WordPressPublisher()]
import os

load_dotenv()

# Initialize Serper Tool
serper_tool = SerperTool()

# Define Agents
researcher = Agent(
    role="Web Researcher",
    goal="Search and summarize the best information from the web using given keywords.",
    backstory=(
        "You're great at finding reliable, relevant, and up-to-date information online. "
        "You use the Serper API to search and extract key points that help the writer."
    ),
    tools=[serper_tool]
)

writer = Agent(
    role="Blog Writer",
    goal="Write an engaging, SEO-friendly blog post using the research provided.",
    backstory="You're an experienced content writer who turns insights into engaging blog posts."
)

editor = Agent(
    role="Editor and Proofreader",
    goal="Polish and refine the blog content for tone, clarity, grammar, and readability.",
    backstory="You're a skilled editor who ensures the content reads naturally and professionally."
)

publisher = Agent(
    role="Content Publisher",
    goal="Publish the final content to the blog platform or save it for review.",
    backstory="You handle formatting and publishing the final version of the article."
)

# Define Tasks
research_task = Task(
    description="Use the Serper API to find and summarize blog content and insights about the topic: {topic}",
    agent=researcher,
    expected_output="A structured summary of insights and key points from the web."
)

writing_task = Task(
    description="Using the research summary, write a detailed and SEO-friendly blog post.",
    agent=writer,
    expected_output="A complete blog post ready for editing."
)

editing_task = Task(
    description="Review and edit the drafted blog content for grammar, flow, and readability.",
    agent=editor,
    expected_output="A polished and professional version of the article."
)

publishing_task = Task(
    description="Save the final edited content to a text file named after the topic.",
    agent=publisher,
    expected_output="Confirmation that the content was successfully saved."
)

# Define Crew
crew = Crew(
    agents=[researcher, writer, editor, publisher],
    tasks=[research_task, writing_task, editing_task, publishing_task],
    process=Process.sequential
)

def run_pipeline(topic: str):
    print(f"Starting multi-agent blog creation for: {topic}")
    result = crew.kickoff(inputs={"topic": topic})
    
    final_text = None
    
    if hasattr(result, "raw_output"):
        final_text = result.raw_output
    # Older CrewAI (<0.45)
    elif hasattr(result, "output"):
        final_text = result.output
    # Just in case
    else:
        final_text = str(result)
        
    
    # Save final result to a text file
    output_dir = "outputs"
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, f"{topic.replace(' ', '_')}.txt")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(final_text)

    print(f"\n✅ Blog post saved to: {file_path}\n")
    print("=== Final Blog Output ===\n")
    print(final_text)
    
    # if hasattr(result, "tasks_output"):
    #     for i, task_output in enumerate(result.tasks_output, 1):
    #         step_path = os.path.join(output_dir, f"step_{i}.txt")
    #         with open(step_path, "w", encoding="utf-8") as f:
    #             f.write(str(task_output.output))

if __name__ == "__main__":
    run_pipeline("Top 5 General AI Agents that Can Make Your Life Easy!")
