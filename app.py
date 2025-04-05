from flask import Flask, render_template, request
import boto3
import os
from dotenv import load_dotenv
import json

load_dotenv()

app = Flask(__name__)

# Initialize Bedrock client
bedrock = boto3.client(
    service_name='bedrock-runtime',
    region_name=os.getenv("AWS_REGION"),
)

MODEL_ID = os.getenv("MODEL_ID")  # e.g., 'anthropic.claude-v2'

@app.route('/', methods=['GET', 'POST'])
def index():
    answer = ""
    if request.method == 'POST':
        question = request.form['question']
        if question:
            answer = get_bedrock_answer(question)
    return render_template('index.html', answer=answer)

def get_bedrock_answer(question):
    prompt = f"\n\nHuman: {question}\n\nAssistant:"
    try:
        response = bedrock.invoke_model(
            body=json.dumps({
                "prompt": prompt,
                "max_tokens_to_sample": 200,
                "temperature": 0.7,
            }),
            modelId=MODEL_ID,
            accept="application/json",
            contentType="application/json"
        )
        result = json.loads(response['body'].read())
        return result['completion']
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
