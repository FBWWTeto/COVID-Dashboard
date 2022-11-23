from flask import Flask
from flask import render_template
from covid_news_handling import *
from covid_data_handler import *
from flask import request
from DateTime import *

# Instantiation of the Flask application
app = Flask(__name__)

# Grabbing latest news articles and data
news = news_API_request()
if len(news) > 5:
    for i in range(5, len(news)):
        news.pop()

data = covid_API_request()

# List to hold the name of the updates
update = []


"""Adds the latest scheduled news update from the user to the dashboard 
Parameters:
update_name (str): Name given by the user for the update on the dashboard form 

Returns:
None 
"""


def add_update_news(update_name):
    cross = request.args.get('update_item')
    update_interval = request.args.get('update')
    update.append({
        'title': update_name,
        'content': "Scheduled news update time: " + update_interval
    })
    if cross:
        update.pop()


def add_news_article():
    for p in range(0, 5):
        news.append({
            'title': news[p].get('title'),
            'content': news[p].get('content')
        })


"""Adds the latest scheduled data update from the user to the dashboard 
Parameters:
update_name (str): Name given by the user for the update on the dashboard form 

Returns:
None 
"""


def add_update_cd(update_name):
    update_interval = request.args.get('update')
    update.append({
        'title': update_name,
        'content': "Scheduled covid data update time: " + update_interval
    })


"""Adds the latest scheduled update for both data and news from the user to the dashboard 
Parameters:
update_name (str): Name given by the user for the update on the dashboard form 

Returns:
None 
"""


def add_update_both(update_name):
    update_interval = request.args.get('update')
    update.append({
        'title': update_name,
        'content': "Scheduled update time for covid data and news: " + update_interval
    })


"""Adds the latest scheduled repeated update from the user to the dashboard 
Parameters:
update_name (str): Name given by the user for the update on the dashboard form 

Returns:
None 
"""


def add_repeated_update(update_name):
    update_interval = request.args.get('update')
    update.append({
        'title': update_name,
        'content': "Scheduled repeat time: " + update_interval
    })


""" Function to remove the last update 
Parameters:
update_name (str): Name given by the user for the update on the dashboard form 

Returns:
None 
"""


def remove_update():
    update.remove(update[0])


def time_calc(update_interval):
    update_time = hhmm_to_seconds(update_interval)
    hours = DateTime().hour()
    minutes = DateTime().minute()
    hours = mins_to_secs(str(hours_to_mins(str(hours))))
    minutes = mins_to_secs(str(minutes))
    current_time = hours + minutes
    if current_time > update_time:
        update_time = int(current_time - update_time) - 1
    else:
        update_time = int(update_time - current_time) - 1
    return update_time


def scheduling_update_removal(update_interval):
    if len(update) > 0:
        e4 = s.enter(update_interval, 3, remove_update, ())


""" Function to render the HTML template and allow for
    scheduled events to take place 

Parameters:
data_api (dict): Dictionary of the latest data from the covid API 


Returns:
render_template('index.html',
                           title='Daily update',
                           news_articles=news,
                           updates=update,
                           location='Exeter',
                           local_7day_infections=data_api['last7days_cases_loc'],
                           nation_location='England',
                           national_7day_infections=data_api['last7days_cases_nat'],
                           hospital_cases=data_api['hosp_cases'],
                           deaths_total=data_api['tot_deaths']): Renders the template /
                           and assigns the data to the corresponding part of the HTML file
"""


@app.route('/index')
def index():
    s.run(blocking=False)

    # Assigning HTML elements to a variable to allow them to be edited with Python
    update_interval = request.args.get('update')
    word = request.args.get('two')
    cross_news = request.args.get('notif')
    cross_update = request.args.get('update_item')
    repeat = request.args.get('repeat')
    news_up = request.args.get('news')
    data_up = request.args.get('covid-data')

    # Checking to see whether the user entered an update label and what update they want to schedule
    if word and news_up and data_up:
        add_update_both(word)
        scheduling_update_removal(time_calc(update_interval))
    elif word and data_up:
        add_update_cd(word)
        schedule_covid_updates(time_calc(update_interval), word)
        scheduling_update_removal(time_calc(update_interval))
    elif word and news_up:
        add_update_news(word)
        schedule_news_updates(time_calc(update_interval), word)
        add_news_article()
        scheduling_update_removal(time_calc(update_interval))
    elif word and repeat:
        add_repeated_update(word)
        scheduling_update_removal(time_calc(update_interval))

    # Removing an article from the dashboard when the user clicks the cross
    if cross_news:
        news.remove(news[0])

    # Removing the update from the dashboard when the user clicks the cross
    if cross_update:
        remove_update()

    return render_template('index.html',
                           title='Daily update',
                           news_articles=news,
                           updates=update,
                           location='Exeter',
                           local_7day_infections=data['last7days_cases_loc'],
                           national_location='England',
                           national_7day_infections=data['last7days_cases_nat'],
                           hospital_cases=data['hosp_cases'],
                           deaths_total=data['tot_deaths'])


""" Checks to see if the module is the main module, if it isn't, then the application won't run

Parameters:
None

Returns:
None 
"""
if __name__ == "__main__":
    app.run()
