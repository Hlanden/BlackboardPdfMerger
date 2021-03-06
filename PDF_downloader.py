import requests
from bs4 import BeautifulSoup, SoupStrainer
import time
from mergePDF import *
import shutil
import os
import re

def get_content_from_url(url, cookiejar):
    """Get dowload links for all pdfs in the given blackboard-url
    Keyword arguments:
        url[String] -- url to the blackboard page containing the pdf-files
        cookiejar[browser_cookie3.Cookiejar] -- cookiejar containg cookies required to log in to BB

    Return:
         pdflink[list] -- list of download-urls for the pdf-files in the given url
    """
    resp = requests.get(url, cookies=cookiejar)
    download_link = 'https://ntnu.blackboard.com'
    content = str(resp.content)
    pdfdict = {}
    for link in BeautifulSoup(content, parse_only=SoupStrainer('a'), features="lxml"):
        try:
            if link.attrs['href'].startswith('/bbcswebdav/'):
                tmp = int(str(link.attrs['href']).split('pid-')[1][0:6])
                while pdfdict.__contains__(tmp):
                    tmp += 1
                pdfdict[tmp] = download_link + link['href']
            elif str(link.attrs['href']).startswith('/webapps/blackboard/content/listContent.jsp'):
                if not str(link.attrs['href']).__contains__('reset'):
                    url = download_link +  str(link.attrs['href'])
                    resp = requests.get(url, cookies=cookiejar)
                    content = str(resp.content)
                    for link2 in BeautifulSoup(content, parse_only=SoupStrainer('a'), features="lxml"):
                        try:
                            if link2.attrs['href'].startswith('/bbcswebdav/'):
                                tmp = int(str(link2.attrs['href']).split('pid-')[1][0:6])
                                while pdfdict.__contains__(tmp):
                                    tmp += 1
                                pdfdict[tmp] = download_link + link2['href']
                        except Exception as e:
                            print(e)
                            pass

        except Exception:
            pass
    sorted(pdfdict)
    pdflink = list(pdfdict.values())

    return pdflink

def get_names(url, cookiejar):
    links = get_content_from_url(url, cookiejar)
    names = []
    for link in links:
        response = requests.get(link, cookies=cookiejar, stream=True)
        filename = os.path.basename(response.url)
        if filename.__contains__('.pdf'): 
            names.append(filename)
    return names

def generate_pdf(url, output_folder, output_name, cookiejar, count=None, progressbar=None, selection=None):
    """Downlaods all pds in the given url and merges them to an output file

    Keyword arguments:
        url[String] -- url to the blackboard page containing the pdf-files
        output_folder[String] -- path to the output-folder of the merged pdf
        output_name[String] -- name of the merged pdf (NOTE: Do not includ ".pdf" in the name)
        cookiejar[browser_cookie3.Cookiejar] -- cookiejar containg cookies required to log in to BB
    """
    links = get_content_from_url(url, cookiejar)
    filenames = []
    try:
        path = os.path.join(os.getcwd(), 'tmp')
        if not os.path.exists(path):
            os.makedirs(path)
        else:
            shutil.rmtree(path)
            os.makedirs(path)
        if count is None:
            names = []
            for link in links:
                response = requests.get(link, cookies=cookiejar, stream=True)
                filename = os.path.basename(response.url)
                if filename.__contains__('.pdf'): 
                    names.append(filename)

            count = len(names)

        

        i = 0
        for link in links:
            response = requests.get(link, cookies=cookiejar, stream=True)
            filename = os.path.basename(response.url)
            if selection is None:
                if filename.__contains__('.pdf'):
                    with open(os.path.join(path, str(i) + '.pdf'), 'wb+') as fd:
                        for chunk in response.iter_content(2000):
                            fd.write(chunk)
                    filenames.append(filename)
                    i += 1
                    if progressbar is not None:
                        progressbar['value'] = int(i/count*100)
            else:
                if filename.__contains__('.pdf') and not selection.__contains__(filename):
                    with open(os.path.join(path, str(i) + '.pdf'), 'wb+') as fd:
                        for chunk in response.iter_content(2000):
                            fd.write(chunk)
                    filenames.append(filename)
                    i += 1
                    if progressbar is not None:
                        progressbar['value'] = int(i/count*100)
                else:
                    print('Excluding; ', filename)

        sort_and_merge_pdfs(os.path.join(path, '*.pdf'), output_folder, output_name, filenames)
        if links:
            print('Successfully merged PDF to folder: {}'.format(output_folder))
            return True
        else:
            return False
    except Exception as e:
        raise e
    finally:
        time.sleep(5)
        shutil.rmtree(path)
