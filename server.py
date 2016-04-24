from flask import Flask
from flask import request, redirect, url_for

import json
import arrow

from azure_api import request_prediction
from weather_api import request_weather

app = Flask(__name__)

from functools import wraps
from flask import request, current_app


def jsonp(func):
    """Wraps JSONified output for JSONP requests."""
    @wraps(func)
    def decorated_function(*args, **kwargs):
        callback = request.args.get('callback', False)
        if callback:
            data = str(func(*args, **kwargs))
            content = str(callback) + '(' + data + ')'
            mimetype = 'application/javascript'
            return current_app.response_class(content, mimetype=mimetype)
        else:
            return func(*args, **kwargs)
    return decorated_function

@app.route('/predict', methods=['GET'])
@jsonp
def predict():
    print(request.method, 'request')
    if request.method == 'GET':
        print(request.args.get('latitude'))
        data = request.args
        depTime = arrow.get(data.get('DepartureTime'))
        weather = request_weather(data['origin'], depTime)
        mldata = {
            'DayOfWeek': str(depTime.isoweekday()), 
            'UniqueCarrier': '0',
            'Origin': data['origin'],
            'Dest': data['destination'],
            'CRSDepTime': depTime.isoformat(),
            'Distance': data['distance'],
            'lat': weather['lat'],
            'lon': weather['lon'],
            'tmpf': '61', #!!!!!!!!!!!!!
            'drct': weather['drct'],
            'sknt': weather['sknt'],
            'vsby': weather['vsby'],
            'skyc1': weather['skyc1'],
            'skyl1': weather['skyl1']
        }
        return json.dumps(request_prediction(mldata))
        
    else:
        return 'You can only POST to this endpoint'

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static/', path)

#@app.route('/scripts/<path:path>')
#def send_scripts(path):
#    return send_from_directory('static/scripts/', path)

@app.route('/')
def main_page():
    return redirect(url_for('static', filename='HtmlPage.html'))

if __name__ == '__main__':
    #app.debug=True
    app.run(host='0.0.0.0', port=80)
