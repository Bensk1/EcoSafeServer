import sys
sys.path.append(".env/lib/python2.7/site-packages")

from flask import Flask
import requests
app = Flask(__name__)

@app.route("/")
def hello():
    payload = {
        'access_token': '08beec989bccb333439ee3588583f19f02dd6b7e',
        'asset': '357322040163096',
        'filter': 'BEHAVE_ID'
    }
    r = requests.post('http://api.mycarcloud.de/resource.php', data=payload)
    return r.text

if __name__ == "__main__":
    app.debug = True
    app.run()