import indicoio
import json
import pandas
from itertools import chain
from pprint import pprint


indicoio.config.api_key = '43c624474f147b8b777a144807e7ca95'




def write(path, link):


    x = indicoio.keywords(link)

    with open(path, 'w') as fp:
        json.dump(x, fp)



def read(path):

    with open(path, 'r') as fp:

        data = json.load(fp)

    series = pandas.Series(data)


    return series



def read_write(path, link):


    write(path, link)

    read(path)


def lower(x: str):

    return x.lower()


def main():


    a = read("ptopic_keywords.json").to_dict()

    normalized = { lower(key): a[key] for key in a}

    with open("ptopic_keywords.json", 'w') as fp:

        json.dump(normalized, fp, indent= 2)



    # print(x)



main()

