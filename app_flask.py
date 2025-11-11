from flask import Flask, render_template, request
from crew_pipeline import run_pipeline
import traceback

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    blog_content = None
    topic = ""

    if request.method == "POST":
        topic = request.form.get("topic")
        if topic:
            try:
                blog_content = run_pipeline(topic)
            except Exception:
                blog_content = f"<pre>{traceback.format_exc()}</pre>"
            
   
        
    return render_template("index.html", topic=topic, blog_content=blog_content)

if __name__ == "__main__":
    app.run(debug=True)
