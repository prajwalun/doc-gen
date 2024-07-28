from flask import Flask, request, jsonify, render_template, session
import requests
import secrets
import time
import os

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
API_KEY = os.getenv("OPENAI_API_KEY")


def create_prompt(code_content, doc_type):
    """Generates a custom prompt based on the selected documentation style."""
    base_prompt = f"### Code\n{code_content}\n###"
    prompts = {
        "overview": f"{base_prompt}\nProvide a brief overview of what the code does.",
        "detailed": f"{base_prompt}\nProvide a detailed explanation of the code.",
        "usage": f"{base_prompt}\nDemonstrate how to use the main functions.",
        "faq": f"{base_prompt}\nList frequently asked questions.",
    }
    return prompts.get(doc_type, base_prompt)


def api_call(data):
    """Makes an API call to the OpenAI API."""
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"}
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions", headers=headers, json=data
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except requests.RequestException as e:
        error_message = str(e.response.text) if e.response else str(e)
        print(f"API call failed: {error_message}")
        return None  # Returns None to indicate failure


def process_chunk(chunk, doc_type):
    """Processes a single chunk of code using concurrent processing."""
    prompt = create_prompt(chunk, doc_type)
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": chunk},
        ],
    }
    for attempt in range(2):  # Reduced retries to 2
        result = api_call(data)
        if result is not None:
            return result
        time.sleep(1 + attempt)  # Exponential backoff
    return "Error: Processing failed for a chunk"


@app.route("/", methods=["GET", "POST"])
def generate_documentation():
    if request.method == "POST":
        if "file" not in request.files or "doc_type" not in request.form:
            return jsonify({"error": "Missing file or documentation type"}), 400

        file = request.files["file"]
        doc_type = request.form["doc_type"]

        if file.filename == "":
            return jsonify({"error": "No selected file"}), 400

        code_content = file.read().decode("utf-8")

        try:
            # Process the entire content in one go
            result = process_chunk(code_content, doc_type)

            if "Error" in result:
                return jsonify({"error": "Processing error"}), 500

            return jsonify({"documentation": result})

        except Exception as e:
            print(f"Processing error: {e}")
            return jsonify({"error": "Internal server error"}), 500
    else:
        return render_template("index.html")


@app.route("/save-documentation", methods=["POST"])
def save_documentation():
    documentation = request.json.get("documentation", "")
    session["documentation"] = documentation
    return jsonify({"success": True})


@app.route("/documentation")
def display_documentation():
    documentation = session.get("documentation", "")
    return render_template("documentation.html", documentation=documentation)


if __name__ == "__main__":
    app.run(debug=True)
