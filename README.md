# Graph-Social-Network-Analysis

This project can also be opened by Visual Studio with the Python Tools for VS (https://www.visualstudio.com/en-us/features/python-vs.aspx)

## Title
Refugee Crisis: A Graph Network Analysis.

## Description
This project was created in the context of the M.Sc Course Data Mining and Information Retrieval on the Web of the Informatics Department of the Aristotle University of Thessaloniki

## Categories
1. Streaming from Twitter by TweetStreaming.py
2. Preprocessing of Data by TweetProcessing.py

## Prerequisites

### Python
In order to run this programme one need already have:

* tweepy (pip install tweepy)
* pymongo (pip install pymongo)

### Other
* Your OWN twitter API Consumer Key (API Key), Consumer Secret (API Secret), Access Token, and Access Token Secret https://apps.twitter.com/app/new
* NLTK https://pypi.python.org/pypi/nltk
* After having the NLTK, open python through a console or an IDE and do the following:
```python
  import nltk
  nltk.download()
```
From (Tab) Corpora, go to -> (Row) Stopwords, and download them

* Mongo DB: https://www.mongodb.org
  the folder C:\Data\db should be available (let alone created) at all times
  run "mongod"
* Mongoclient (is recommended, yet not a prerequisite) https://github.com/rsercano/mongoclient/releases
