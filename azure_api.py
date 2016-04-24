from urllib import request
import urllib
import json

def request_prediction(data):
    ColumnNames = ["Column 0", "Unnamed: 0", "Year", "Month", "DayofMonth", "DayOfWeek", "UniqueCarrier", "Origin", "Dest", "CRSDepTime", "DepDelayMinutes", "DepDel15", "CRSArrTime", "ArrTime", "ArrDelay", "ArrDelayMinutes", "ArrDel15", "CRSElapsedTime", "ActualElapsedTime", "Distance", "WeatherDelay", "station", "valid", "lon", "lat", "tmpf", "dwpf", "relh", "drct", "sknt", "p01i", "alti", "mslp", "vsby", "gust", "skyc1", "skyc2", "skyc3", "skyc4", "skyl1", "skyl2", "skyl3", "skyl4", "presentwx", "station.1", "valid.1", "lon.1", "lat.1", "tmpf.1", "dwpf.1", "relh.1", "drct.1", "sknt.1", "p01i.1", "alti.1", "mslp.1", "vsby.1", "gust.1", "skyc1.1", "skyc2.1", "skyc3.1", "skyc4.1", "skyl1.1", "skyl2.1", "skyl3.1", "skyl4.1", "presentwx.1"]
    DefaultValues = [ "0", "0", "0", "0", "0", "0", "value", "value", "value", "", "0", "0", "", "0", "0", "0", "0", "0", "0", "0", "0", "value", "", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "value", "value", "value", "value", "0", "0", "0", "0", "value", "value", "", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "value", "value", "value", "value", "0", "0", "0", "0", "value" ]
    Values = []
    for idx, col in enumerate(ColumnNames):
        if col in data:
            Values.append(data[col])
        else:
            Values.append(DefaultValues[idx])

    req_data = {
        "Inputs": {
            "input1":
                {
                    'ColumnNames': ColumnNames, 
                    'Values': [Values]   
                },
        },
            "GlobalParameters": {}
    }
    body = str.encode(json.dumps(req_data))

    url = 'https://ussouthcentral.services.azureml.net/workspaces/4ac864b09c184c928968125d17de1918/services/d31ef481a61e475da4aebaf3a7ec796a/execute?api-version=2.0&details=true'
    api_key = 'yS4CTo8cnd3p/NzhPRGSDlDGkmP3eUiq1gKa9y0c1YDupV5lA+hXFRCTTCE8ugEUSXjxR/LfpWFMxSav79ORIQ==' # Replace this with the API key for the web service
    headers = {'Content-Type':'application/json', 'Authorization':('Bearer ' + api_key)}
    req = request.Request(url, body, headers)
    try:
        response = request.urlopen(req)
        result = response.read()
        parsed = json.loads(result.decode())
        values = parsed['Results']['output1']['value']['Values'][0]
        return {'label': values[-2], 'prob': values[-1]}
    except urllib.error.HTTPError as error:
        print("The request failed with status code: " + str(error.code))
        print(error.info())
        print(json.loads(error.read())) 


if __name__ == '__main__':
    sample_data = {
        'DayOfWeek': '1', 
        'UniqueCarrier': '0',
        'Origin': 'LAX',
        'Dest': 'JFK',
        'CRSDepTime': '2016-01-12T18:20:00',
        'Distance': '2482',
        'lat': '33.9425',
        'lon': '-118.40805',
        'tmpf': '61',
        'drct': '350',
        'sknt': '7',
        'vsby': '10',
        'skyc1': 'CLR',
        'skyl1': '25000'
    }
    r = request_prediction(sample_data)
    print(r)
