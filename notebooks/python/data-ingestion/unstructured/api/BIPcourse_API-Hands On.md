# Hands on: APIs interactions

---

## Table of contents

1) **Social media**: extract tweets of given users using [Twitter API](https://developer.twitter.com/en/docs.html)
2) **Weather**: extract current weather and weather forecasting using [OpenWeatherMap API](https://openweathermap.org/)
3) **Geographic data**: extract geolocated data from [OpenStreetMap API](https://wiki.openstreetmap.org/wiki/API)

---

# 1. Social Media
## Twitter API

---

## Twitter API

* The API allows to retrieve tweets and users data from Twitter in JSON format: each data point has all the features that are observable on the social network.
* API have **limitations**: each endpoint can be queried for a limited number of data points in a fixed time window of 15 minutes.
* Python API Wrapper: _tweepy_ (https://tweepy.readthedocs.io/en/3.7.0/api.html)

---

## Exercise

1) Generate an API key from Twitter (https://developer.twitter.com/en/docs/basics/authentication/guides/access-tokens.html)
2) Interact with Twitter: 
_"Retrieve account information, a sample of tweets and the list of followers of a given user."_

---

# 2. Weather
## OpenWeatherMap API

---

## OpenWeatherMap API

* It is possible to retrieve the current weather for any location, specified by its name or its geographical coordinates (latitute and longitude): the results are sent in JSON format.
* The API gives the **forecasting** for each location.
* Historical data can be queried, too.
* Python API Wrapper: _PyOWM_ (https://pyowm.readthedocs.io/en/latest/index.html)

---

## Exercise

1) Generate an API key from OpenWeatherMap (https://openweathermap.org/appid)
2) Interact with the API:
 _"Extract the weather of a specific location and show the forecasting for the next week."_

---


# 3. Geographic data
## OpenStreetMap API

---

## OpenStreetMap API

* [OpenStreetMap](https://www.openstreetmap.org/) is an open source map of the world, with an incredible amount of geographic and labeled data (around 800 GB the complete dataset).
* The data is fully-accessible through Web interface or through several APIs.
* [Overpass API](http://overpass-api.de/) allows to query specific data from the OSM dataset, exploiting labels attached to nodes.

---

## Exercise

1) Learn how the query language works on http://overpass-turbo.eu/
2) Interact with Overpass API:
_"Extract the location of all Biergarten in Germany and plot them on a map."_
