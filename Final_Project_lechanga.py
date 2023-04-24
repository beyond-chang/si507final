#########################################
##### Name: Le Chang                #####
##### Uniqname: lechanga            #####
#########################################

import networkx as nx
import requests
import xmltodict
import pprint as pp
import json
import matplotlib.pyplot as plt
from networkx.readwrite import json_graph

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

def interactive():
    """users can enter their own requests and receive nicely formatted results.

    Parameters:
        None

    Returns:
        None
    """
    input1 = input('Enter a search term, or "exit" to quit: ')
    if input1.lower().strip() != 'exit':
        dat1 = categorize(search(input1))
        print_result(dat1)
        while True:
            input2 = input('Enter a number for more info, or another search term, or exit: ')
            if input2.lower().strip() == 'exit':
                break
            else:
                try:
                    launch_url(dat1, int(input2))
                except ValueError:
                    dat1 = categorize(search(input2))
                    print_result(dat1)


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


    # proccess the data and use cache if possible
    im_ex_dict = {}
    for key in reporter_dict.keys():
        im_ex_dict[key] = {}

    if create_cache('imexdata.json'):
        im_ex_dict = read_json('imexdata.json')
    else:
        for key in xprt_data.keys():
            if xprt_data[key]:
                im_ex_dict[key]["export"] = {}
                for data in xprt_data[key]["message:GenericData"]["message:DataSet"]["generic:Series"]:
                    for series in data["generic:SeriesKey"]["generic:Value"]:
                        if series["@id"] == "PARTNER" and series["@value"] in reporter_dict.keys():
                            im_ex_dict[key]["export"][series["@value"]] = data["generic:Obs"]["generic:ObsValue"]["@value"]

        for key in mprt_data.keys():
            if mprt_data[key]:
                im_ex_dict[key]["import"] = {}
                for data in mprt_data[key]["message:GenericData"]["message:DataSet"]["generic:Series"]:
                    for series in data["generic:SeriesKey"]["generic:Value"]:
                        if series["@id"] == "PARTNER" and series["@value"] in reporter_dict.keys():
                            im_ex_dict[key]["import"][series["@value"]] = data["generic:Obs"]["generic:ObsValue"]["@value"]
        write_json('imexdata.json', im_ex_dict)

    # create graphs
    if create_cache('xprtgraph.json'):
        data = read_json('xprtgraph.json')
        xprt_graph = nx.node_link_graph(data)
    else:
        xprt_graph = nx.DiGraph()
        for key in reporter_dict.keys():
            xprt_graph.add_node(key)
        for key in reporter_dict.keys():
            if im_ex_dict[key].get("export"):
                for partner in im_ex_dict[key]["export"].keys():
                    xprt_graph.add_weighted_edges_from([(key, partner, float(im_ex_dict[key]["export"][partner]))])
        data = json_graph.node_link_data(xprt_graph)
        write_json('xprtgraph.json', data)

    if create_cache('mprtgraph.json'):
        data = read_json('mprtgraph.json')
        mprt_graph = nx.node_link_graph(data)
    else:
        mprt_graph = nx.DiGraph()
        for key in reporter_dict.keys():
            mprt_graph.add_node(key)
        for key in reporter_dict.keys():
            if im_ex_dict[key].get("import"):
                for partner in im_ex_dict[key]["import"].keys():
                    mprt_graph.add_weighted_edges_from([(key, partner, float(im_ex_dict[key]["import"][partner]))])
        data = json_graph.node_link_data(mprt_graph)
        write_json('mprtgraph.json', data)



