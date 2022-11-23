import requests
from covid_data_handler import *

""" Returns a list of the titles for each of the related news articles from the API

Parameters:
covid_terms (str): Contains terms that will get the news that I am looking for

Returns:
title (list): Contains all of the relevant titles from the news API
"""


def news_API_request(covid_terms: str = 'Covid COVID-19 coronavirus') -> list:
    base_url = "https://newsapi.org/v2/everything?"
    api_key = "e30de33ada8846cda564576240854c89"
    start = '2021-12-01'
    complete_url = base_url + 'q='+covid_terms + '&from='+start + '&sortBy=publishedAt' + '&language=en' + '&apiKey=' +\
        api_key
    response = requests.get(complete_url)

    news = response.json()['articles']

    news_dict = [{}]

    for i in range(0, len(news)):
        news_dict.append({
            'title': news[i].get('title'),
            'content': news[i].get('description')
        })

    json_object = json.dumps(news_dict, indent=4)
    with open("news.json", "w") as outfile:
        outfile.write(json_object)

    return news_dict


""" Updates the news articles

 Parameters: 
 update_name: Filters to be used when getting the latest news articles 

 Returns:
 None:Returning value
 """


def update_news(update_name):
    news_API_request(update_name)


def schedule_news_updates(update_interval, update_name):
    e2 = s.enter(update_interval, 2, update_news, (update_name, ))


