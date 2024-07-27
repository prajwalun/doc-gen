from flask import Flask, request, jsonify, render_template_string
import openai
import json
import requests

app = Flask(__name__)

# Directly setting the API key
API_KEY = 'YOUR_API_KEY'

def create_prompt(code_content, doc_type):
    """Generates a custom prompt for the AI based on the selected documentation style."""
    base_prompt = f"### Code\n{code_content}\n###"
    
    if doc_type == 'overview':
        return f"{base_prompt}\nProvide a brief overview of what the code does, highlighting its main functionalities."
    elif doc_type == 'detailed':
        return f"{base_prompt}\nProvide a detailed explanation of the code, including all functions and classes. Describe parameters, return values, and any exception handling."
    elif doc_type == 'usage':
        return f"{base_prompt}\nDemonstrate how to use the main functions of the code. Include example code snippets and describe configuration requirements."
    elif doc_type == 'faq':
        return f"{base_prompt}\nList frequently asked questions and their answers about using this code. Include troubleshooting tips and common issues."
    else:
        return f"{base_prompt}\nProvide a general explanation of the code."

@app.route('/', methods=['GET', 'POST'])
def generate_documentation():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files or 'doc_type' not in request.form:
            return jsonify({'error': 'Missing file or documentation type'}), 400
        
        file = request.files['file']
        doc_type = request.form['doc_type']
        
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        code_content = file.read().decode('utf-8')
        prompt = create_prompt(code_content, doc_type)
        
        # Prepare the payload for the chat API
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": prompt},
                {"role": "user", "content": code_content}
            ]
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}"
        }

        # Using OpenAI's chat completion API endpoint
        response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, data=json.dumps(data))
        
        if response.status_code == 200:
            documentation = response.json()['choices'][0]['message']['content']
            formatted_documentation = f"<pre>{documentation}</pre>"
            return jsonify({'documentation': formatted_documentation})
        else:
            return jsonify({'error': response.json()}), response.status_code

    else:
        # GET request, show the upload form and documentation style options
        return render_template_string('''
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
        ''')

if __name__ == '__main__':
    app.run(debug=True)
