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
    # Extract JSON data from the JSONP string
    match = re.search(r'\((.*?)\)', jsonp_string)
    if match:
        json_data = match.group(1)  
        schedule_data = json.loads(json_data)
        print(schedule_data)
        return schedule_data
    else:
        print("Error: JSONP format not recognized.")


def get_schedule(startDate=get_date(), endDate=get_date(7)):
    # Replace 'your_api_endpoint' with the actual API endpoint you are using
    response = requests.get(f"https://vnz.osvita.net/WidgetSchedule.asmx/GetScheduleDataX?callback=jsonp1713552062155&_=1713552086424&aVuzID=11613&aStudyGroupID=%22VX3LAF8VK3J9%22&aStartDate=%22{startDate}%22&aEndDate=%22{endDate}%22&aStudyTypeID=null")

    if response.status_code == 200: 
        jsonp_string = response.text  # Extract the content from the response
        myDate = extract_json_from_jsonp(jsonp_string)
        return myDate
    else:
        print(f"Error: Unable to fetch data. Status code: {response.status_code}")