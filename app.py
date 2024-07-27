from flask import Flask, request, jsonify, render_template_string
import openai
import json
import requests

app = Flask(__name__)

# Directly setting the API key
API_KEY = 'YOUR_API_KEY'

@app.route('/', methods=['GET', 'POST'])
def generate_documentation():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            return jsonify({'error': 'No file part in the request'}), 400
        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        # Read the contents of the file
        code_content = file.read().decode('utf-8')

        # Prepare the payload for the chat API with enhanced prompt for better documentation
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "You are an assistant trained to explain code professionally. Provide concise, clear, and well-structured documentation."},
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
            # Format the output to be more readable and professional
            formatted_documentation = "<pre>" + documentation + "</pre>"
            return jsonify({'documentation': formatted_documentation})
        else:
            return jsonify({'error': response.json()}), response.status_code

    else:
        # GET request, show the upload form
        return render_template_string('''
            <!DOCTYPE html>
            <html>
            <head>
                <title>Upload new File</title>
            </head>
            <body>
                <h1>Upload new File</h1>
                <form method=post enctype=multipart/form-data>
                  <input type=file name=file>
                  <input type=submit value=Upload>
                </form>
            </body>
            </html>
        ''')

if __name__ == '__main__':
    app.run(debug=True)



