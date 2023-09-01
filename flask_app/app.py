import sys
import aiohttp
import asyncio
from datetime import timedelta

from flask import Flask, render_template, request, session
from pymongo import MongoClient

client = MongoClient('mongodb://mongodb:27017/') 
db = client['mydatabase']
query_response_collection = db['query_response']

if sys.platform == "win32" and (3, 8, 0) <= sys.version_info < (3, 9, 0):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

app = Flask(__name__)
app.secret_key = "super secret key"
app.permanent_session_lifetime = timedelta(minutes=10)

TARGET_SERVICE_URL = "http://badlisted-words:8018/badlisted_words"

async def send_to_target(data):
    async with aiohttp.ClientSession() as session:
        async with session.post(TARGET_SERVICE_URL, json=data) as response:
            return await response.json()

@app.route("/", methods=["GET", "POST"])
async def index():
    if "messages" not in session:
        session["messages"] = []

    if not session.modified:
        session.modified = True

    response_message = ""

    if request.method == "POST":
        action = request.form.get("action")
        message = request.form.get("message")

        if action == "add" and message:
            session["messages"].append(message)
        elif action == "send":
            response_message = await send_to_target({"sentences": session["messages"]})
            query_response_collection.insert_one({"query": session["messages"], "response": response_message})
        elif action == "clear":
            session["messages"] = []

    return render_template("index.html", messages=session["messages"], response_message=response_message)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
