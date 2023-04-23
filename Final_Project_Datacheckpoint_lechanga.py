#########################################
##### Name: Le Chang                #####
##### Uniqname: lechanga            #####
#########################################

'''This is the code for the Final Project Data checkpoint
'''

import networkx as nx
import requests
import xmltodict
import pprint as pp
import json

def url_to_dict(url):
    '''access the url, get the xml file, turn the xml file into dictionary

    Parameters:
        url(str): the url of the data

    Returns:
        dict: data from the url
    '''
    response = requests.get(url)
    xml_data = response.content
    return xmltodict.parse(xml_data)

def read_json(filepath, encoding='utf-8'):
    """Reads a JSON document, decodes the file content, and returns a list or dictionary if
    provided with a valid filepath.

    Parameters:
        filepath (str): path to file
        encoding (str): name of encoding used to decode the file

    Returns:
        dict/list: dict or list representations of the decoded JSON document
    """

    with open(filepath, 'r', encoding=encoding) as file_obj:
        return json.load(file_obj)


def write_json(filepath, data, encoding='utf-8', ensure_ascii=False, indent=2):
    """Serializes object as JSON. Writes content to the provided filepath.

    Parameters:
        filepath (str): the path to the file
        data (dict)/(list): the data to be encoded as JSON and written to the file
        encoding (str): name of encoding used to encode the file
        ensure_ascii (str): if False non-ASCII characters are printed as is; otherwise
                            non-ASCII characters are escaped.
        indent (int): number of "pretty printed" indention spaces applied to encoded JSON

    Returns:
        None
    """

    with open(filepath, 'w', encoding=encoding) as file_obj:
        json.dump(data, file_obj, ensure_ascii=ensure_ascii, indent=indent)

def create_cache(filepath):
    """Attempts to retrieve cache contents written to the file system. If successful the
    cache contents from the previous script run are returned to the caller as the new
    cache. If unsuccessful an empty cache is returned to the caller.

    Parameters:
        filepath (str): path to the cache file

    Returns:
        dict: cache either empty or populated with resources from the previous script run
    """

    try:
        return read_json(filepath)
    except FileNotFoundError:
        return {}




if __name__ == "__main__":
    # request country list, use cache if possible
    if create_cache('countries.json'):
        countries = read_json('countries.json')
    else:
        countries = url_to_dict('http://wits.worldbank.org/API/V1/wits/datasource/trn/country/ALL')
        write_json('countries.json', countries)

    # create reporter dict (reporters are countries that will report trade data to world bank)
    reporter_dict = {}
    for item in countries["wits:datasource"]["wits:countries"]["wits:country"]:
        if item["@isreporter"] == "1" and item["@isgroup"] == "No":
            reporter_dict[item["wits:iso3Code"]] = item["wits:name"]

    # loop through all reporters, get export(XPRT)/import(MPRT) partner shares for each coutry with each partner, use cache if possible
    if create_cache('xprtdata.json'):
        xprt_data = read_json('xprtdata.json')
    else:
        xprt_data = {}
        for key in reporter_dict.keys():
            try:
                url = 'http://wits.worldbank.org/API/V1/SDMX/V21/rest/data/df_wits_tradestats_trade/A.' + key.lower() +'..999999.XPRT-PRTNR-SHR/?startPeriod=2020&endPeriod=2020'
                xprt_data[key] = url_to_dict(url)
            except:
                xprt_data[key] = {}
        write_json('xprtdata.json', xprt_data)

    if create_cache('mprtdata.json'):
        mprt_data = read_json('mprtdata.json')
    else:
        mprt_data = {}
        for key in reporter_dict.keys():
            try:
                url = 'http://wits.worldbank.org/API/V1/SDMX/V21/rest/data/df_wits_tradestats_trade/A.' + key.lower() +'..999999.MPRT-PRTNR-SHR/?startPeriod=2020&endPeriod=2020'
                mprt_data[key] = url_to_dict(url)
            except:
                mprt_data[key] = {}
        write_json('mprtdata.json', mprt_data)


