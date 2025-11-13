import http.client
import json
import streamlit as st

def run_pipeline(topic):
  conn = http.client.HTTPSConnection("google.serper.dev")
  payload = json.dumps({
    "q": "India travel guide"
  })
  headers = {
    'X-API-KEY': 'eeabdbbd085e48c7a9b78e8a44f306bf8d6ba545',
    'Content-Type': 'application/json'
  }
  conn.request("POST", "/search", payload, headers)
  res = conn.getresponse()
  data = res.read()
  #print(data.decode("utf-8"))
  st.json(data.decode("utf-8"))


if __name__ == "__main__":
    run_pipeline("Travel Guide to Kolkata")
