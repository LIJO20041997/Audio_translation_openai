import openai
import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "static"

@app.route('/', methods=['GET', 'POST'])
def main():
    if request.method == "POST":
        language = request.form['language']
        file = request.files['file']
        
        if file:
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # Open the uploaded audio file
            audio_file = open(os.path.join(app.config['UPLOAD_FOLDER'], filename), 'rb')
            output = openai.Audio.translate("whisper-1", audio_file)

            # Create a chat completion request for translation
            response = openai.ChatCompletion.create(
                model='gpt-4',
                messages=[{
                    "role": "system", 
                    "content": f"You will be provided with a sentence in English. Your task is to translate it into {language}."
                }, {
                    "role": "user", 
                    "content": output['text']  # Use output['text'] to get the English text
                }],
                temperature=0, 
            )

            # Extract the translated content from the response
            translated_content = response['choices'][0]['message']['content']

            # Return the translated text as a JSON response
            return jsonify({
                "translated_text": translated_content,
                "original_text": output['text'],  # Optional: Return original text too
                "language": language
            })
    
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=8080)
