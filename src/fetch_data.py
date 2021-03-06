#!usr/bin/env python
# -*- coding: utf-8 -*-

"""
Stock data module
reads stock list from database
gets data from Yahoo Finance
and records data in table stock_data
"""

import urllib2
import urllib
import json
import datetime

import entry_classes


def db_time_format(string):
    yyyy = int(string[:4])
    MM = int(string[5:7])
    dd = int(string[8:10])
    hh = int(string[11:13])
    mm = int(string[14:16])
    ss = int(string[17:19])
    time = datetime.datetime(yyyy, MM, dd, hh, mm, ss)
    return time


def chop_microseconds(time):
    return time - datetime.timedelta(microseconds=time.microsecond)


# gets quotes from Yahoo Finance
def fetch_quotes():

    fetch_time = datetime.datetime.now()
    # read from db
    results = entry_classes.Stock.get()
    ticker_id_dict = {}
    for stock in results:
        ticker_id_dict[stock['ticker']] = stock['id']

    # build query url for api
    baseurl = "https://query.yahooapis.com/v1/public/yql?"
    yql_query = "select * from yahoo.finance.quote where symbol in ('"
    ticker_url = "','".join(ticker_id_dict.keys())
    yql_query = yql_query + ticker_url + "')"
    yql_url = baseurl + urllib.urlencode({'q': yql_query}) +\
        "&format=json&diagnostics=true&env=store://datatables.org/alltableswithkeys&callback="
    #print yql_url

    # get data
    result = urllib2.urlopen(yql_url).read()
    data = json.loads(result)

    ## time test
    #print 'fetch_time:', chop_microseconds(fetch_time)
    #print 'time before qyl:', chop_microseconds(datetime.datetime.now())
    #print 'yahoo time:', db_time_format(data['query']['created'])

    quote_data = data['query']['results']['quote']

    # create objects
    # todo: 按发起时间算
    quotes = [entry_classes.Quote(id=ticker_id_dict[q['symbol']],
                                  price=entry_classes.unicode2int(q['LastTradePriceOnly']),
                                  volume=q['Volume'],
                                  time=fetch_time)
              for q in quote_data]
    #print quotes

    # write results into db
    for q in quotes:
        q.add()


if __name__ == '__main__':
    fetch_quotes()
