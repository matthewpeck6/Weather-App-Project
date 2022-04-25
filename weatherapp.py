import streamlit as st
import numpy as np
import requests, json, numpy as np
from datetime import datetime as dt
from datetime import date
from datetime import timedelta
from geopy.geocoders import Nominatim # for finding latitude, longitude of city
from bs4 import BeautifulSoup # for web scraping
import matplotlib
matplotlib.use('TkAgg') # for streamlit compatibility
import matplotlib.pyplot as plt

st.title('MAD2502 Weather App')
top_text = st.empty()
city = top_text.text_input("Please enter 'City, ST'") # asks user for city or zip code. City can be in form of CITY, STATE
geolocator = Nominatim(user_agent="weather_app") # these four lines takes the city or zip co de and finds its latitude and longitude
location = geolocator.geocode(city)

# these blocks catch a strange error where it tries to set latitude/longitude without waiting for location input
try:
    latitude = location.latitude
except AttributeError:
    st.stop()
try:
    longitude = location.longitude
except AttributeError:
    st.stop()
    
current_date = str((date.today()).strftime("%m-%d-%Y")) # gives today's date in format MM-DD-YYYY
currentSplitUp = current_date.split("-")
current_day = int(currentSplitUp[0])
current_month = int(currentSplitUp[1])
current_year = int(currentSplitUp[2])

api_key = "0c981865ac3b99b146db363335c9cf90" # this is my API key from openweathermap.org. I think we will use this key to access weather data

def unix_to_datetime(unix_time): # converts from unix time to standard date and time

    standard_date = (dt.fromtimestamp(unix_time)).strftime('%m-%d-%Y %H:%M:%S')

    return standard_date

def datetime_to_unix(year,month,day,hour,minute): # converts from standard date and time to unix time

    d = dt(year,month,day,hour,minute)

    unix_time = int((d - dt(1970, 1, 1)).total_seconds()) + 16*3600

    return unix_time

def current(latitude, longitude, data): # Gives data about weather at this very moment

    current_url = f"http://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={api_key}&units=imperial" # this is the link that will give us the JSON file of the current weather data

    response = requests.get(current_url) # requests the website data

    response_text = response.text # converts website data into text

    current_json = json.loads(response_text) # converts text into json format

    if data == "temp":
        return current_json["main"]["temp"]
    elif data == "temp_low":
        return current_json["main"]["temp_min"]
    elif data == "temp_high":
        return current_json["main"]["temp_max"]
    elif data == "feels_like":
        return current_json["main"]["feels_like"]
    elif data == "weather":
        return current_json["weather"][0]["description"]
    elif data == "humidity":
        return current_json["main"]["humidity"]
    elif data == "wind_speed":
        return current_json["wind"]["speed"]
    elif data == "wind_direction":
        if current_json["wind"]["deg"] < 90:
            return "Northeast"
        elif 90 <= current_json["wind"]["deg"] < 180:
            return "Southeast"
        elif 180 <= current_json["wind"]["deg"] < 270:
            return "Southwest"
        elif 270 <= current_json["wind"]["deg"] < 360:
            return "Northwest"

def forecast(latitude, longitude, data, days): # Gives weekly forecast and today's weather

    forecast_url = f"https://api.openweathermap.org/data/2.5/onecall?lat={latitude}&lon={longitude}&exclude=minutely,hourly,current&appid={api_key}&units=imperial"

    response = requests.get(forecast_url)

    response_text = response.text

    forecast_json = json.loads(response_text)

    forecast_unix_date = forecast_json["daily"][days]["dt"]
    forecast_standard_date = unix_to_datetime(forecast_unix_date)

    def weekly_high(): # gives the highest temp for the next week

        highs = []

        for n in range(1,8):
            highs.append(forecast_json["daily"][n]["temp"]["max"])
        
        weekly_high = max(highs)

        return weekly_high

    def weekly_low(): # gives the lowest temp for the next week

        lows = []

        for n in range(1,8):
            lows.append(forecast_json["daily"][n]["temp"]["min"])
        
        weekly_low = min(lows)

        return weekly_low

    def weekly_average(): # gives average temperature for the next week
        
        temps = []

        for n in range(1,8):
            temps.append(forecast_json["daily"][n]["temp"]["day"])
        
        return np.round(np.average(temps), 2) # finds average of temps and rounds it to two decimal places

    if data == "temp":
        return forecast_json["daily"][days]["temp"]["day"]
    elif data == "temp_low":
        return forecast_json["daily"][days]["temp"]["min"]
    elif data == "temp_high":
        return forecast_json["daily"][days]["temp"]["max"]
    elif data == "temp_average":
        return np.round(((forecast_json["daily"][days]["temp"]["min"] + forecast_json["daily"][days]["temp"]["max"]) / 2), 2)
    elif data == "weekly_high":
        return weekly_high()
    elif data == "weekly_low":
        return weekly_low()
    elif data == "weekly_average":
        return weekly_average()
    elif data == "feels_like":
        return forecast_json["daily"][days]["feels_like"]["day"]
    elif data == "weather":
        return forecast_json["daily"][days]["weather"][0]["description"]
    elif data == "weather_main":
        if forecast_json["daily"][days]["weather"][0]["main"] == "Clouds":
            if forecast_json["daily"][days]["weather"][0]["description"] == "few clouds":
                return "few"
            elif forecast_json["daily"][days]["weather"][0]["description"] == "scattered clouds":
                return "some"
            elif forecast_json["daily"][days]["weather"][0]["description"] == "broken clouds":
                return "lots"
            elif forecast_json["daily"][days]["weather"][0]["description"] == "overcast clouds":
                return "lots"
        else:
            return forecast_json["daily"][days]["weather"][0]["main"]
    elif data == "humidity":
        return forecast_json["daily"][days]["humidity"]
    elif data == "wind_speed":
        return forecast_json["daily"][days]["wind_speed"]
    elif data == "wind_direction":
        if forecast_json["daily"][days]["wind_deg"] < 90:
            return "Northeast"
        elif 90 <= forecast_json["daily"][days]["wind_deg"] < 180:
            return "Southeast"
        elif 180 <= forecast_json["daily"][days]["wind_deg"] < 270:
            return "Southwest"
        elif 270 <= forecast_json["daily"][days]["wind_deg"] <= 360:
            return "Northwest"
    elif data == "sunrise":
        return unix_to_datetime(forecast_json["daily"][days]["sunrise"]) # sunrise time
    elif data == "sunset":
        return unix_to_datetime(forecast_json["daily"][days]["sunset"]) # sunset time
    elif data == "rain":
        try:
            return forecast_json["daily"][days]["rain"] # rainfall in mm
        except KeyError: # if rain doesn't exist in JSON, then there will be no rain
            return 0
    elif data == "snow":
        try:
            return forecast_json["daily"][days]["snow"] # snowfall in mm
        except KeyError: # if snow doesn't exist in JSON, then there will be no snow
            return 0

def history(latitude, longitude, data, date): # Gives history up to 5 days back. Data is from 1 PM EST on those days

    dateSplitUp = date.split("-")
    month = int(dateSplitUp[0])
    day = int(dateSplitUp[1])
    year = int(dateSplitUp[2])
    hour = 1
    minute = 0

    unix_time = datetime_to_unix(year,month,day,hour,minute)

    history_url = f"https://api.openweathermap.org/data/2.5/onecall/timemachine?lat={latitude}&lon={longitude}&dt={unix_time}&appid={api_key}&units=imperial" #API 

    response = requests.get(history_url)

    response_text = response.text

    history_json = json.loads(response_text)

    if data == "temp":
        return history_json["current"]["temp"]
    elif data == "humidity":
        return history_json["current"]["humidity"]
    elif data == "weather":
        return history_json["current"]["weather"][0]["description"]
    elif data == "wind_speed":
        return history_json["current"]["wind_speed"]
    elif data == "wind_direction":
        if history_json["current"]["wind_deg"] < 90:
            return "Northeast"
        elif 90 <= history_json["current"]["wind_deg"] < 180:
            return "Southeast"
        elif 180 <= history_json["current"]["wind_deg"] < 270:
            return "Southwest"
        elif 270 <= history_json["current"]["wind_deg"] <= 360:
            return "Northwest"
    elif data == "sunrise":
        return unix_to_datetime(history_json["current"]["sunrise"])
    elif data == "sunset":
        return unix_to_datetime(history_json["current"]["sunset"])

def on_this_day(city,data,date): # returns data about the temperature on a certain day since 1970

    dateSplitUp = date.split("-")
    month = int(dateSplitUp[0])
    day = int(dateSplitUp[1])

    year_range = range(1970,current_year) # the website tracks from 1945 to 2 days ago. for now stick with up to 2021

    temp_average_list = []
    temp_min_list = []
    temp_max_list = []

    try:
        citySplitUp = city.split(", ") # for if user put space after comma
        city = citySplitUp[0]
        state = citySplitUp[1]

    except IndexError:
        citySplitUp = city.split(",") # for if user didn't put space after comma
        city = citySplitUp[0]
        state = citySplitUp[1]

    for year in year_range:

        on_this_day_url = f"https://www.almanac.com/weather/history/{state}/{city}/{year}-{month}-{day}"
        
        response = requests.get(on_this_day_url)

        response_content = response.content

        html = BeautifulSoup(response_content, 'html.parser') 

        temp_average = html.find(class_ = "weatherhistory_results_datavalue temp").find(class_ = "value").get_text()

        temp_min = html.find(class_ = "weatherhistory_results_datavalue temp_mn").find(class_ = "value").get_text()

        temp_max = html.find(class_ = "weatherhistory_results_datavalue temp_mx").find(class_ = "value").get_text()

        temp_units = (html.find(class_ = "weatherhistory_results_datavalue temp_mn").find(class_ = "units").get_text())[1]

        if data == "average":
            if temp_units == "C":
                temp_average_list.append((9/5)*float(temp_average) + 32)
            else:
                temp_average_list.append(float(temp_average))

        elif data == "min":
            if temp_units == "C":
                temp_min_list.append((9/5)*float(temp_min) + 32)
            else:
                temp_min_list.append(float(temp_min))

        elif data == "max":
            if temp_units == "C":
                temp_max_list.append((9/5)*float(temp_max) + 32)
            else:
                temp_max_list.append(float(temp_max))

    if data == "average":
        fig, av_plt = plt.subplots(figsize = (10, 5))
        av_plt.plot(year_range, temp_average_list)
        av_plt.scatter(year_range, temp_average_list)
        av_plt.set_title(f"Average temperatures in {city}, {state} on {date} from 1970 to 2021", fontsize = 18)
        av_plt.set_xlabel("Year", fontsize = 18)
        av_plt.set_ylabel("Temperature (°F)", fontsize = 18)
        graphs.pyplot(av_plt.figure)
        return np.round(np.average(temp_average_list), 2)

    if data == "min":
        fig, min_plt = plt.subplots(figsize = (10, 5))
        min_plt.plot(year_range, temp_min_list)
        min_plt.scatter(year_range, temp_min_list)
        min_plt.set_title(f"Minimum temperatures in {city}, {state} on {date} from 1970 to 2021", fontsize = 18)
        min_plt.set_xlabel("Year", fontsize = 18)
        min_plt.set_ylabel("Temperature (°F)", fontsize = 18)
        graphs.pyplot(min_plt.figure)
        return min(temp_min_list)

    if data == "max":
        fig, max_plt = plt.subplots(figsize = (10, 5))
        max_plt.plot(year_range, temp_max_list)
        max_plt.scatter(year_range, temp_max_list)
        max_plt.set_title(f"Maximum temperatures in {city}, {state} on {date} from 1970 to 2021", fontsize = 18)
        max_plt.set_xlabel("Year", fontsize = 18)
        max_plt.set_ylabel("Temperature (°F)", fontsize = 18)
        graphs.pyplot(max_plt.figure)
        return max(temp_max_list)

def weather_icon(weather):
    if weather == "Clear":
        return str("http://openweathermap.org/img/wn/01d@2x.png")
    elif weather == "Rain":
        return str("http://openweathermap.org/img/wn/10d@2x.png")
    elif weather == "few":
        return str("http://openweathermap.org/img/wn/02d@2x.png")
    elif weather == "some":
        return str("http://openweathermap.org/img/wn/03d@2x.png")
    elif weather == "lots":
        return str("http://openweathermap.org/img/wn/04d@2x.png")
    elif weather == "Thunderstorm":
        return str("http://openweathermap.org/img/wn/11d@2x.png")
    elif weather == "Drizzle":
        return str("http://openweathermap.org/img/wn/09d@2x.png")
    elif weather == "Snow":
        return str("http://openweathermap.org/img/wn/13d@2x.png")
    elif weather == "Mist" or "Smoke" or "Haze" or "Dust" or "Fog" or "Sand" or "Ash" or "Squall" or "Tornado":
        return str("http://openweathermap.org/img/wn/50d@2x.png")

top_text.subheader("Now displaying the weekly forecast for " + city + "!")
day1, day2, day3, day4, day5, day6, day7 = st.columns(7)
next7dates = np.empty(7, dtype=object)
for i in range(7):
    next7dates[i] = date.today() + timedelta(i)
with day1:
    st.header(str(next7dates[0].strftime("%m/%d")))
    st.image(str(weather_icon(forecast(latitude,longitude,"weather_main",0))))
    st.header(str(int(forecast(latitude,longitude,"temp_high",0))) + "°")
    st.subheader(str(int(forecast(latitude,longitude,"temp_low",0))) + "°")
with day2:
    st.header(str(next7dates[1].strftime("%m/%d")))
    st.image(str(weather_icon(forecast(latitude,longitude,"weather_main",1))))
    st.header(str(int(forecast(latitude,longitude,"temp_high",1))) + "°")
    st.subheader(str(int(forecast(latitude,longitude,"temp_low",1))) + "°")
with day3:
    st.header(str(next7dates[2].strftime("%m/%d")))
    st.image(str(weather_icon(forecast(latitude,longitude,"weather_main",2))))
    st.header(str(int(forecast(latitude,longitude,"temp_high",2))) + "°")
    st.subheader(str(int(forecast(latitude,longitude,"temp_low",2))) + "°")
with day4:
    st.header(str(next7dates[3].strftime("%m/%d")))
    st.image(str(weather_icon(forecast(latitude,longitude,"weather_main",3))))
    st.header(str(int(forecast(latitude,longitude,"temp_high",3))) + "°")
    st.subheader(str(int(forecast(latitude,longitude,"temp_low",3))) + "°")
with day5:
    st.header(str(next7dates[4].strftime("%m/%d")))
    st.image(str(weather_icon(forecast(latitude,longitude,"weather_main",4))))
    st.header(str(int(forecast(latitude,longitude,"temp_high",4))) + "°")
    st.subheader(str(int(forecast(latitude,longitude,"temp_low",4))) + "°")
with day6:
    st.header(str(next7dates[5].strftime("%m/%d")))
    st.image(str(weather_icon(forecast(latitude,longitude,"weather_main",5))))
    st.header(str(int(forecast(latitude,longitude,"temp_high",5))) + "°")
    st.subheader(str(int(forecast(latitude,longitude,"temp_low",5))) + "°")
with day7:
    st.header(str(next7dates[6].strftime("%m/%d")))
    st.image(str(weather_icon(forecast(latitude,longitude,"weather_main",6))))
    st.header(str(int(forecast(latitude,longitude,"temp_high",6))) + "°")
    st.subheader(str(int(forecast(latitude,longitude,"temp_low",6))) + "°")

st.subheader("Expand the tabs below for more details!")
temperature = st.expander("Temperature")
temperature.subheader("Current temperature: " + str(current(latitude,longitude,"temp")) + "°F")
temperature.subheader("High: " + str(current(latitude,longitude,"temp_high")) + "°F")
temperature.subheader("Low: " + str(current(latitude,longitude,"temp_low")) + "°F")
temperature.subheader("Humidity: " + str(current(latitude, longitude,"humidity")) + "%")
temperature.subheader("Feels like: " + str(current(latitude,longitude,"feels_like")) + "°F")
weather = st.expander("Weather/Wind")
weather.subheader("The current weather is: " + str(current(latitude,longitude,"weather")))
weather.subheader("Wind speed: " + str(current(latitude,longitude,"wind_speed")) + " mph")
weather.subheader("Wind direction: " + str(current(latitude,longitude,"wind_direction")))
weather.subheader("Rain: " + str(forecast(latitude,longitude,"rain",0)) + " mm")
weather.subheader("Snow: " + str(forecast(latitude,longitude,"snow",0)) + " mm")
sun = st.expander("Sunset/sunrise times")
sun.subheader("Sunrise time: " + str(forecast(latitude, longitude,"sunrise",0)))
sun.subheader("Sunset time: " + str(forecast(latitude, longitude,"sunset",0)))
sun.subheader("Tomorrow's sunrise time: " + str(forecast(latitude, longitude,"sunrise",1)))
weeklyforecast = st.expander("Weekly forecast")
weeklyforecast.subheader("Weekly average: " + str(forecast(latitude, longitude,"weekly_average",0)) + "°F")
weeklyforecast.subheader("Weekly high: " + str(forecast(latitude, longitude,"weekly_high",0)) + "°F")
weeklyforecast.subheader("Weekly low: " + str(forecast(latitude, longitude,"weekly_low",0)) + "°F")

st.subheader("Click below to see historical data for " + str((date.today()).strftime("%m/%d")) + " in previous years! (may take some time to display all 3 graphs)")
graphs = st.expander("Graphs")
all_time_average = on_this_day(city,"average",str((date.today()).strftime("%m-%d")))
today_average = forecast(latitude,longitude,"temp_average",0)
if all_time_average <= today_average:
    st.subheader("Here's a fun fact: today's temperature of " + str(today_average) + "°F is hotter than the historic average of " + str(all_time_average) + "°F!")
else:
    st.subheader("Here's a fun fact: today's temperature of " + str(today_average) + "°F is colder than the historic average of " + str(all_time_average) + "°F!")
on_this_day(city,"min",str((date.today()).strftime("%m-%d")))
on_this_day(city,"max",str((date.today()).strftime("%m-%d")))