from flask import Flask,  render_template
import requests

app = Flask(__name__)

@app.route('webhook', methods=['POST'])
def webhook(): 
    if requests.method == 'POST': 
        content = requests.json()
        print(f"Data received from webhook: {requests.json()}")
        return render_template('upload_success.html', content=content)
