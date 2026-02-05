AWS_REGION = "ap-south-2"
S3_BUCKET = "quest-mithlesh"

COVID_TIMESERIES_URL = (
    "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/"
    "csse_covid_19_data/csse_covid_19_time_series/"
)

COVID_TIMESERIES_API = (
    "https://api.github.com/repos/"
    "CSSEGISandData/COVID-19/contents/"
    "csse_covid_19_data/csse_covid_19_time_series"
)

WEATHER_API_URL = "https://api.open-meteo.com/v1/forecast"

CITIES = {
    "london": {"lat": 51.5074, "lon": -0.1278},
    "new_york": {"lat": 40.7128, "lon": -74.0060},
    "tokyo": {"lat": 35.6762, "lon": 139.6503}
}
