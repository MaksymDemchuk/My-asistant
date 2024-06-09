import requests
import json
import re
from datetime import datetime, timedelta


def get_date(n=0):
    date = datetime.now() + timedelta(days=n)
    yyyy = date.year
    mm = date.month
    dd = date.day

    if dd < 10:
        dd = '0' + str(dd)
    if mm < 10:
        mm = '0' + str(mm)

    formatted_date = f"{dd}.{mm}.{yyyy}"
    return formatted_date


def extract_json_from_jsonp(jsonp_string):
    match = re.search(r'\((.*?)\)', jsonp_string)
    if match:
        json_data = match.group(1)
        schedule_data = json.loads(json_data)
        print(schedule_data)
        return schedule_data
    else:
        print("Error: JSONP format not recognized.")


def get_schedule(startDate=get_date(), endDate=get_date(7)):
    url = "https://vnz.osvita.net/WidgetSchedule.asmx/GetScheduleDataX"
    params = {
        'callback': 'jsonp1717010024814',
        '_': '1717010054860',
        'aVuzID': '11613',
        'aStudyGroupID': '"VX3LAF8VK3J9"',
        'aStartDate': '"01.03.2024"',
        'aEndDate': '"01.03.2024"',
        'aStudyTypeID': 'null'
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    response = requests.get(url, params=params, headers=headers)
    print(response.url)  # Додатково можна роздрукувати остаточний URL для перевірки
    print(response.status_code)
    if response.status_code == 200:
        jsonp_string = response.text
        print(jsonp_string)
        return extract_json_from_jsonp(jsonp_string)
    else:
        print(f"Error: Unable to fetch data. Status code: {response.status_code}")


