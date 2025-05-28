import os, re, sys, math, requests
from datetime import datetime

DATETIME_PATTERN = "%Y%m%dT%H%M%S"

def download_calendar_ics(url):
    query_params = {"downloadformat": "ics"}
    download = requests.get(url, query_params)
    with open("./calendar.ics", mode="wb") as file:
        file.write(download.content)

def calculate_calls_time_from_ics(path, year, month, deletion_name, exclusions, exclusions_day):
    exclusions_day_arr = []
    exclusions_day_dates = []
    exclusions_arr = []
    if (len(exclusions) != 0):
        exclusions_arr = exclusions.split(",")
    if (len(exclusions_day) != 0):
        exclusions_day_arr = exclusions_day.split(",")
        for day in exclusions_day_arr:
            exclusions_day_dates.append(datetime(year, month, int(day)))

    filtered_events = []
    filtered_events_dict = []

    if ("https" in path):
        download_calendar_ics(path)
        path = "./calendar.ics"

    with open(path, encoding="utf-8") as calendar:
        calendar_content = calendar.read()
        events = re.findall(r"SUMMARY:.*.*\nDTSTART.*\nDTEND.*", calendar_content, re.MULTILINE)
        filtered_events = [event for event in events]
    
    for event in filtered_events:
        summary = re.findall(r"SUMMARY:(.*?)\n", event)[0]
        start_time = datetime.strptime(re.findall(r"DTSTART;TZID=W. Europe Standard Time:(.*?)\n", event)[0], DATETIME_PATTERN)
        end_time = datetime.strptime(re.findall(r"DTEND;TZID=W. Europe Standard Time:(.*)", event)[0], DATETIME_PATTERN)
        time_delta = end_time - start_time
        event_dict = dict(summary = summary, start_time = start_time, end_time = end_time, time_delta = time_delta)
        if (deletion_name not in summary.lower() and start_time.year == year and start_time.month == month):
            if (len(exclusions_arr) > 0 or exclusions_day_arr > 0):
                if all(exclusion not in summary.lower() for exclusion in exclusions_arr):
                    if (event_dict["start_time"].date() not in [day.date() for day in exclusions_day_dates]):
                        filtered_events_dict.append(event_dict)

            else:
                filtered_events_dict.append(event_dict)

    total_seconds = 0
    for e in filtered_events_dict:
        total_seconds += e["time_delta"].seconds
    
    os.remove(path)
    return total_seconds

def hours_and_minutes_format(calls_time_seconds):
    hours = calls_time/3600
    decimal_hours = hours - int(hours)
    decimal_hours = decimal_hours * 60
    return str(int(hours)) + " and " + str(math.ceil(decimal_hours)) + " minutes"

if __name__ == "__main__":
    if len(sys.argv) == 5:
        calls_time = calculate_calls_time_from_ics(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4], "", "")
        print("You spent " + str(calls_time) + " seconds (" + hours_and_minutes_format(calls_time) + ") on calls in " + sys.argv[2] + "-" + sys.argv[3])
    elif len(sys.argv) == 6:
        calls_time = calculate_calls_time_from_ics(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4], sys.argv[5], "")
        print("You spent " + str(calls_time) + " seconds (" + hours_and_minutes_format(calls_time) + ") on calls in " + sys.argv[2] + "-" + sys.argv[3])
    elif len(sys.argv) == 7:
        calls_time = calculate_calls_time_from_ics(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4], sys.argv[5], sys.argv[6])
        print("You spent " + str(calls_time) + " seconds (" + hours_and_minutes_format(calls_time) + ") on calls in " + sys.argv[2] + "-" + sys.argv[3])
    else:
        print(f"Usage: python {sys.argv[0]} ./calendar.ics 2025 5 deleted (exlusion1,exclusion2) (8,9,10)\n\n- ./calendar.ics: path to .ics calendar file\n- 2025: year filter\n- 5: month filter (may)\n- deleted: string contained in summary when call was being deleted\n- exclusions: (optional) exclude date when summary containing specific words (case insensitive)\n- days exclusion (optional) exclude dates for specific days (in the example 8th, 9th, 10th may).")