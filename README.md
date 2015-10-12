# WMATAWatcherApp
A Flask app that monitors Tweets to make delay predictions on the Washington DC MetroRail

Searches Tweets on 13 hashtags and user account mentions, producing a feature array consisting of Tweet volume, time information, and the frequency of key words (e.g. "delay" or "offloading").  Implements two trained Random Forest Classifiers - one that makes predictions when Tweet content exists in the search and one that makes a time-only prediction for when no Tweets are returned by the search.
