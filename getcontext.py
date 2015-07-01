import pandas as pd
import numpy as np
from pandas.io.json import json_normalize
import random
import bandits

import multiprocessing
import time
import requests
import json

import urllib


credentials = {'teamid' : 'Coffeeblack',
               'teampw' : '23e88f60c155804c79cfd1af83e47fc8'}

# from http://stackoverflow.com/questions/312443/
# how-do-you-split-a-list-into-evenly-sized-chunks-in-python
def chunks(l, n):
    """ Yield successive n-sized chunks from l.
    """
    for i in xrange(0, len(l), n):
        yield l[i:i+n]

def getcontext_r(i, runid):

    baseurl = "http://krabspin.uci.ru.nl/getcontext.json/"
    payload = {'i' : i,
               'runid' : runid}

    payload.update(credentials)  # Add credentials
    r = requests.get(baseurl, params=payload)  # GET request

    return r


def process_thread(ids, runid):

    rs = []  # responses
    for i in ids:
        rs.append(getcontext_r(i, runid).json())

    df = json_normalize(rs)
    df.columns = ['Age', 'Agent', 'ID', 'Language', 'Referer']
    df.to_csv(str(runid) + "_" + str(ids[0]) + ".csv", index=False)
        

def process_all_threads(runid, target):

    num_ids = 100000
    ids = np.arange(num_ids)
    threads = 100
    split_ids = chunks(ids, num_ids / threads)

    # If something breaks start at that chunk
    startchunk = 27000
    
    jobs = []

    # Perform chunks in parallel or sequentially?
    do_multithreading = False
    
    for chunk in split_ids:

        if chunk[0] < startchunk:
            continue
        
        if do_multithreading:
            p = multiprocessing.Process(target=target, args=(chunk, runid,))
            jobs.append(p)
            p.start()        
        else:
            target(chunk, runid)

    if do_multithreading:            
        [p.join() for p in jobs]

def join_df(runid):

    """
    Join chunks to big df
    """

    dfs = [pd.read_csv(str(runid) + "_" + str(i) + ".csv") for i in np.arange(0, 100000, 1000)]
    big_df = pd.concat(dfs, ignore_index=True)

    return big_df

        
def proposepage(i, runid, header, adtype, color, productid, price):

    payload = {'i' : i,
               'runid': runid,
               'price': price,
               'header': header,
               'adtype': adtype,
               'color': color,
               'productid': productid,
               'price': price}

    
    
    payload.update(credentials)  # Add credentials

    # Propose page and get JSON answer
    r = requests.get("http://krabspin.uci.ru.nl/proposePage.json/", params=payload)
    return r


def propose_ad_thread(ids, runid):


    rs = []

    headers = [5, 15, 35]
    adtypes = ['skyscraper', 'square', 'banner']
    colors = ['green', 'blue', 'red', 'black', 'white']
    productids = range(10, 25)

    # TODO create dataframe instead of proposing it on the fly
    
    for i in ids:
        rs.append(proposepage(i=i,
                              runid=runid,
                              header=random.choice(headers),
                              adtype=random.choice(adtypes),
                              color=random.choice(colors),
                              productid=random.choice(productids),
                              price=float(str(np.around(np.random.uniform(50), 2)))).json())
        time.sleep(1)

        # TODO SAVE PRICE
        
    df = json_normalize(rs)
    df.columns = ['Error', 'Success']
    df.to_csv("rewards" + str(runid) + "_" + str(ids[0]) + ".csv", index=False)


if __name__ == "__main__":

    headers = [5, 15, 35]
    adtypes = ['skyscraper', 'square', 'banner']
    colors = ['green', 'blue', 'red', 'black', 'white']
    productids = range(10, 26)

    process_all_threads(335, process_thread)

    big_df = join_df(335)
    big_df.to_csv("context_335.csv", index=False)
