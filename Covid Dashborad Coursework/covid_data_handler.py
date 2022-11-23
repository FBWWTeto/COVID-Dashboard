from uk_covid19 import Cov19API
import requests
import json
import sched
import time
import logging


# Instantiation of scheduler for asynchronous events
s = sched.scheduler(time.time, time.sleep)

""" Function to read the data from the CSV file and store it in a list

Parameters:
csv_filename (str): The name of the CSV that will have its data read from and stored in a list 


Returns:
ret (list): A list of all the data stored in the CSV file 
"""


def parse_csv_data(csv_filename: str) -> list:
    ret = open(csv_filename, 'r').readlines()
    return ret


""" Function to process the data in the CSV file to get 
cases over the last seven days, current hospital cases and current deaths 

Parameters: 
covid_csv_data (list): List of the data from parsing the CSV file

Returns:
last7days_cases (int):Returning value of the cases from the last seven days
cur_hosp_case (int):Returning value of the current hospital cases 
total_deaths (int):Returning value of the total deaths 


"""


def process_covid_csv_data(covid_csv_data: list) -> tuple[int, int, int]:
    last7days_cases = 0
    cur_hosp_case = 0
    total_deaths = 0

    # List to get the data over the past seven days
    case_list = []

    # Lists to split the data to get current hospital cases
    hosp_splitter = []

    # Getting all the data in the CSV in list form so it can be iterated over
    csv_data = [covid_csv_data[1]]

    latest_deaths_entry = []

    for data in csv_data:
        hosp_splitter = data.split(',', maxsplit=6)

    cur_hosp_case = int(hosp_splitter[5])
    for date in range(1, 10):
        if date >= 3:
            case_list.append(covid_csv_data[date])

    for data in case_list:
        case_list_splitter = data.split(',', maxsplit=6)
        last7days_cases += int(case_list_splitter[6])

    for data in range(1, 15):
        if data > 13:
            latest_deaths_entry.append(covid_csv_data[data])

    for data in latest_deaths_entry:
        deaths = data.split(',', maxsplit=6)
        total_deaths = int(deaths[4])

    return last7days_cases, cur_hosp_case, total_deaths


""" Function to access live Covid data from the UK government API for the
entire country and a city 

Parameters:
location (str): The location to be used in the filter
location_type (str): The type of location, which will also be used in the filter

Returns:
covid_dict (dict): Contains the processed covid data from the API 


"""


def covid_API_request(location: str = "Exeter", location_type: str = "ltla") -> dict:

    """ Gathering the API data """
    # Requesting the API
    covid_data = requests.get("https://api.coronavirus.data.gov.uk/v1/data")
    # Filters to get data only from Exeter and England
    exeter_only = ["areaType=" + location_type, "areaName=" + location]
    england_only = ["areaType=nation", "areaName=England"]

    cases_and_deaths = {
        "cumDailyNsoDeathsByDeathDate": "cumDailyNsoDeathsByDeathDate",
        "hospitalCases": "hospitalCases",
        "newCasesBySpecimenDate": "newCasesBySpecimenDate"
    }

    cases = {
        "newCasesBySpecimenDate": "newCasesBySpecimenDate"
    }

    local_api = Cov19API(filters=exeter_only, structure=cases)
    national_api = Cov19API(filters=england_only, structure=cases_and_deaths)
    local_data = local_api.get_json()['data']
    national_data = national_api.get_json()['data']

    """ Processing the Covid API data """
    # Variables to hold the number of cases (both national and local)
    last7days_cases_loc = 0
    last7days_cases_nat = 0

    # For loops to get the data for the last seven days
    for i in range(2, 9):
        last7days_cases_loc += local_data[i - 1].get('newCasesBySpecimenDate')
        last7days_cases_nat += national_data[i].get('newCasesBySpecimenDate')

    # Variables to hold the number of hospital cases and deaths nationally
    hosp_cases = 0
    tot_deaths = 0

    """ For loops to check whether the data is an integer so the dashboard always displays the latest numbers for
    the total deaths in the country and the cumulative number of hospital cases 
    """
    for i in range(0, len(national_data)):
        if type(national_data[i].get('cumDailyNsoDeathsByDeathDate')) == int:
            tot_deaths = national_data[i].get('cumDailyNsoDeathsByDeathDate')
            break

    for i in range(0, len(national_data)):
        if type(national_data[i].get('hospitalCases')) == int:
            hosp_cases = national_data[i].get('hospitalCases')
            break

    # Storing all of the data into a dictionary
    covid_dict = {
        'last7days_cases_loc': last7days_cases_loc,
        'last7days_cases_nat': last7days_cases_nat,
        'hosp_cases': hosp_cases,
        'tot_deaths': tot_deaths
    }

    # Writing the data to a file so that it can be properly updated
    json_obj = json.dumps(covid_dict, indent=4)
    with open('covid-data.json', 'w') as outfile:
        outfile.write(json_obj)

    return covid_dict


"""Returns minutes in seconds 
Parameters: 
minutes (str): Character(s) between 1 and 59 (inclusive)


Returns:
int(minutes) * 60 (int): Converts minutes to type int and multiplies it by 60 """


def mins_to_secs(minutes: str) -> int:
    return int(minutes) * 60


"""Returns hours in minutes
Parameters: 
hours (str): Character(s) between 0 and 23 (inclusive)


Returns:
int(hours) * 60 (int): Converts hours to type int and multiplies it by 60 """


def hours_to_mins(hours: str) -> int:
    return int(hours) * 60


"""Returns time in the format hh:mm in seconds
Parameters: 
hhmm (str): Character(s) between 0 and 23 (inclusive)


Returns:
mins_to_secs(hours_to_mins(hhmm.split(':')[0])) + mins_to_secs(hhmm.split(':')[1]) (int): Splits the hours and the 
minutes up """


def hhmm_to_seconds(hhmm: str) -> int:
    if len(hhmm.split(':')) != 2:
        return None
    return mins_to_secs(str(hours_to_mins(hhmm.split(':')[0]))) + mins_to_secs(hhmm.split(':')[1])


""" Updates the covid data by calling it again 

 Parameters:
 None
 
 
 Returns:
 None
 """


def update_covid_data():
    covid_API_request()


""" Schedules the covid data updates to the dashboard
 
 Parameters: 
 update_interval (int): Time (in seconds) of how long until the next update will occur
 update_name: Function called to update the data
 
 Returns:
 None:Returning value
 """


def schedule_covid_updates(update_interval, update_name):
    e1 = s.enter(update_interval, 1, update_covid_data, (update_name, ))
