import requests
import os

class WordPressPublisher:
    name = "wordpress_publisher"
    description = "Publish content to WordPress via REST API."

    def run(self, title, content):
        url = os.getenv("WP_API_URL")
        auth = (os.getenv("WP_USERNAME"), os.getenv("WP_APP_PASSWORD"))
        data = {"title": title, "content": content, "status": "publish"}
        response = requests.post(url, auth=auth, json=data)
        return response.json()
