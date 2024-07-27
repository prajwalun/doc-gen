from flask import Flask, request, jsonify, render_template_string
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import json

app = Flask(__name__)
API_KEY = 'YOUR_API_KEY'

def create_prompt(code_content, doc_type):
    """Generates a custom prompt based on the selected documentation style."""
    base_prompt = f"### Code\n{code_content}\n###"
    prompts = {
        'overview': f"{base_prompt}\nProvide a brief overview of what the code does.",
        'detailed': f"{base_prompt}\nProvide a detailed explanation of the code.",
        'usage': f"{base_prompt}\nDemonstrate how to use the main functions.",
        'faq': f"{base_prompt}\nList frequently asked questions."
    }
    return prompts.get(doc_type, base_prompt)

def api_call(data):
    """Makes an API call to the OpenAI API."""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    try:
        response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=data)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except requests.RequestException as e:
        error_message = str(e.response.text) if e.response else str(e)
        print(f"API call failed: {error_message}")
        return None  # Returns None to indicate failure

def process_chunk(chunk, doc_type):
    """Processes a single chunk of code using concurrent processing."""
    prompt = create_prompt(chunk, doc_type)
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "system", "content": prompt}, {"role": "user", "content": chunk}]
    }
    result = api_call(data)
    if result is None:
        return "Error: Processing failed for a chunk"
    return result

@app.route('/', methods=['GET', 'POST'])
def generate_documentation():
    if request.method == 'POST':
        if 'file' not in request.files or 'doc_type' not in request.form:
            return jsonify({'error': 'Missing file or documentation type'}), 400
        
        file = request.files['file']
        doc_type = request.form['doc_type']
        
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        code_content = file.read().decode('utf-8')
        chunks = [code_content[i:i + 4000] for i in range(0, len(code_content), 4000)]
        results = []

        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_chunk = {executor.submit(process_chunk, chunk, doc_type): chunk for chunk in chunks}
            for future in as_completed(future_to_chunk):
                result = future.result()
                if "Error" in result:
                    continue  # Optionally handle or log the error
                results.append(result)

        if not results:
            return jsonify({'error': 'All chunks failed to process'}), 500

        formatted_documentation = "<pre>" + "\n\n".join(results) + "</pre>"
        return jsonify({'documentation': formatted_documentation})
    else:
        return render_template_string(html_form())

def html_form():
    return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Upload File and Select Documentation Style</title>
        </head>
        <body>
            <h1>Upload Code File</h1>
            <form method="post" enctype="multipart/form-data">
                <input type="file" name="file" required>
                <select name="doc_type">
                    <option value="overview">Overview</option>
                    <option value="detailed">Detailed</option>
                    <option value="usage">Usage</option>
                    <option value="faq">FAQ</option>
                </select>
                <input type="submit" value="Generate Documentation">
            </form>
        </body>
        </html>
    '''

if __name__ == '__main__':
    app.run(debug=True)
