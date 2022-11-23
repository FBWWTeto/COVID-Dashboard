from covid_data_handler import *
from covid_news_handling import *


def test_parse_csv_data():
    data = parse_csv_data('nation_2021-10-28.csv')
    assert len(data) == 639


def test_process_covid_csv_data():
    last7days_cases, current_hospital_cases, total_deaths = \
        process_covid_csv_data(parse_csv_data('nation_2021-10-28.csv'))
    assert last7days_cases == 240_299
    assert current_hospital_cases == 7_019
    assert total_deaths == 141544


def test_covid_api_request():
    api_data = covid_API_request()
    assert isinstance(api_data, dict)


def test_news_api_request():
    assert news_API_request()
    assert news_API_request('Covid COVID-19 coronavirus') == news_API_request()


def test_covid_updates():
    update_covid_data()


def test_schedule_covid_updates():
    schedule_covid_updates(update_interval=10, update_name='update test')


def test_update_news():
    update_news('test')


test_parse_csv_data()
test_process_covid_csv_data()
test_covid_api_request()
test_news_api_request()
test_schedule_covid_updates()
test_update_news()
test_covid_updates()
