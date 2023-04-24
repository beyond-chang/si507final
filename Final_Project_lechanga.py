#########################################
##### Name: Le Chang                #####
##### Uniqname: lechanga            #####
#########################################

import networkx as nx
import requests
import xmltodict
import json
import matplotlib.pyplot as plt
from prettytable import PrettyTable
import matplotlib.pyplot as plt


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
    while True:
        input1 = input('Select an option, or enter "exit" to quit: \n'
                        'A. Enter a country name to get country code or enter a country code to get country name. \n'
                        "B. Get a country's all import or export partners. \n"
                        "C. Get the import and export facts between two countries. \n"
                        "D. Get a country's top 5 import and export partners. \n"
                        "E. Get a country's import or export piechart. \n")
        if input1.lower().strip() == 'exit':
            break
        elif input1.lower().strip() == 'a':
            interactive_a()
        elif input1.lower().strip() == 'b':
            interactive_b()
        elif input1.lower().strip() == 'c':
            interactive_c()
        elif input1.lower().strip() == 'd':
            interactive_d()
        elif input1.lower().strip() == 'e':
            interactive_e()
        else:
            print('Invalid input. Please try again.')

def interactive_a():
    """interactive option A.
    Enter a country name to get country code or enter a country code to get country name.

    Parameters:
        None

    Returns:
        None
    """
    while True:
        inputa1 = input('Please enter a country name or a country code, or enter "exit" to get back to upper menu: ')
        if inputa1.lower().strip() == 'exit':
            break
        elif inputa1.strip().upper() in reporter_dict.keys():
            print(f"{inputa1.strip().upper()} is the country code of '{reporter_dict[inputa1.strip().upper()]}'")
            break
        elif inputa1.strip().lower().title() in reverse_list.keys():
            print(f"'{inputa1.strip().lower().title()}' has the country code {reverse_list[inputa1.strip().lower().title()]}")
            break
        else:
            print('Sorry, the country name or country code is not listed in the reporter list, please try again.')

def interactive_b():
    """interactive option B.
    Enter a country name or country code to get a country's import or export partners.

    Parameters:
        None

    Returns:
        None
    """
    while True:
        inputb1 = input("Please enter 'im' for import, 'ex' for export, then the country code, seperate them with comma, or enter 'exit' to get back to upper menu: ")
        if inputb1.lower().strip() == 'exit':
            break
        elif inputb1.split(',')[0].strip().lower() == 'im':
            if inputb1.split(',')[1].strip().upper() in reporter_dict.keys():
                listb = list(mprt_graph.successors(inputb1.split(',')[1].strip().upper()))
                listb1 = []
                for code in listb:
                    if code in reporter_dict.keys():
                        listb1.append(reporter_dict[code])
                print(f"The import partners of {reporter_dict[inputb1.split(',')[1].strip().upper()]} are {listb1}")
                break
            else:
                print('Invalid input. Please try again.')
        elif inputb1.split(',')[0].strip().lower() == 'ex':
            if inputb1.split(',')[1].strip().upper() in reporter_dict.keys():
                listb = list(xprt_graph.successors(inputb1.split(',')[1].strip().upper()))
                listb1 = []
                for code in listb:
                    if code in reporter_dict.keys():
                        listb1.append(reporter_dict[code])
                print(f"The export partners of {reporter_dict[inputb1.split(',')[1].strip().upper()]} are {listb1}")
                break
        else:
            print('Invalid input. Please try again.')

def interactive_c():
    """interactive option C.
    Get the import and export facts between two countries.

    Parameters:
        None

    Returns:
        None
    """
    while True:
        inputc1 = input("Please enter two country codes, seperate with comma, or enter 'exit' to get back to upper menu: ")
        if inputc1.lower().strip() == 'exit':
            break
        elif inputc1.split(',')[0].strip().upper() in reporter_dict.keys() and inputc1.split(',')[1].strip().upper() in reporter_dict.keys():
            try:
                ima2b = mprt_graph.get_edge_data(inputc1.split(',')[0].strip().upper(), inputc1.split(',')[1].strip().upper())['weight']
                imb2a = mprt_graph.get_edge_data(inputc1.split(',')[1].strip().upper(), inputc1.split(',')[0].strip().upper())['weight']
                exa2b = xprt_graph.get_edge_data(inputc1.split(',')[0].strip().upper(), inputc1.split(',')[1].strip().upper())['weight']
                exb2a = xprt_graph.get_edge_data(inputc1.split(',')[1].strip().upper(), inputc1.split(',')[0].strip().upper())['weight']
                namea = reporter_dict[inputc1.split(',')[0].strip().upper()]
                nameb = reporter_dict[inputc1.split(',')[1].strip().upper()]
                print(f"{namea} has {ima2b} percent import from {nameb} and {exa2b} percent export to {nameb}, while {nameb} has {imb2a} percent import from {namea} and {exb2a} percent export to {namea}")
                break
            except:
                print('Sorry, data is not valid for these two countries. Please try again. ')
        else:
            print('Invalid input. Please try again.')

def interactive_d():
    """interactive option D.
    Get a country's top 5 import and export partners.

    Parameters:
        None

    Returns:
        None
    """
    while True:
        inputd1 = input("Please enter a country code, or enter 'exit' to get back to upper menu: ")
        if inputd1.lower().strip() == 'exit':
            break
        elif inputd1.strip().upper() in reporter_dict.keys():
            dat = dict(xprt_graph[inputd1.strip().upper()])
            sorted_dat = sorted(dat.items(), key=lambda x: x[1]['weight'], reverse=True)
            table = PrettyTable(['Country', 'Percentage'])
            for d in sorted_dat[:5]:
                table.add_row([reporter_dict[d[0]], d[1]['weight']])
            print("Export Data")
            print(table)
            dat1 = dict(mprt_graph[inputd1.strip().upper()])
            sorted_dat1 = sorted(dat1.items(), key=lambda x: x[1]['weight'], reverse=True)
            table1 = PrettyTable(['Country', 'Percentage'])
            for d in sorted_dat1[:5]:
                table1.add_row([reporter_dict[d[0]], d[1]['weight']])
            print("Import Data")
            print(table1)
            break
        else:
            print('Invalid input. Please try again.')

def interactive_e():
    """interactive option E.
    Get a country's import or export piechart.

    Parameters:
        None

    Returns:
        None
    """
    while True:
        inpute1 = input("Please enter 'im' for import, 'ex' for export, then the country code, seperate them with comma, or enter 'exit' to get back to upper menu: ")
        if inpute1.lower().strip() == 'exit':
            break
        elif inpute1.split(',')[1].strip().upper() in reporter_dict.keys() and inpute1.split(',')[0].strip().lower() == 'ex':
            dat = dict(xprt_graph[inpute1.split(',')[1].strip().upper()])
            sorted_dat = sorted(dat.items(), key=lambda x: x[1]['weight'], reverse=True)[:5]
            sm = 0
            new_list = []
            for item in sorted_dat:
                sm += item[1]['weight']
                new_list.append((reporter_dict[item[0]], item[1]))
            new_list.append(('Other', {'weight': 100-sm}))
            labels = [x[0] for x in new_list]
            values = [x[1]['weight'] for x in new_list]
            fig, ax = plt.subplots()
            ax.pie(values, labels=labels, autopct='%1.1f%%')
            ax.set_title('Export Share Piechart')
            plt.show()
            break
        elif inpute1.split(',')[1].strip().upper() in reporter_dict.keys() and inpute1.split(',')[0].strip().lower() == 'im':
            dat = dict(mprt_graph[inpute1.split(',')[1].strip().upper()])
            sorted_dat = sorted(dat.items(), key=lambda x: x[1]['weight'], reverse=True)[:5]
            sm = 0
            new_list = []
            for item in sorted_dat:
                sm += item[1]['weight']
                new_list.append((reporter_dict[item[0]], item[1]))
            new_list.append(('Other', {'weight': 100-sm}))
            labels = [x[0] for x in new_list]
            values = [x[1]['weight'] for x in new_list]
            fig, ax = plt.subplots()
            ax.pie(values, labels=labels, autopct='%1.1f%%')
            ax.set_title('Import Share Piechart')
            plt.show()
            break
        else:
            print('Invalid input. Please try again.')


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

    reverse_list = {}
    for k,v in reporter_dict.items():
        reverse_list[v] = k

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

    interactive()