import requests
from bs4 import BeautifulSoup, SoupStrainer
import time
from mergePDF import *
import shutil
import os



def get_content_from_url(url, cookiejar):
    """Get dowload links for all pdfs in the given blackboard-url
    Keyword arguments:
        url[String] -- url to the blackboard page containing the pdf-files

    Return:
         pdflink[list] -- list of download-urls for the pdf-files in the given url
    """
    resp = requests.get(url, cookies=cookiejar)
    download_link = 'https://ntnu.blackboard.com'
    content = str(resp.content)
    pdflink = []
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

def generate_pdf(url, output_folder, output_name, cookiejar):
    """Downlaods all pds in the given url and merges them to an output file

    Keyword arguments:
        url[String] -- url to the blackboard page containing the pdf-files
        output_folder[String] -- path to the output-folder of the merged pdf
        output_name[String] -- name of the merged pdf (NOTE: Do not includ ".pdf" in the name)
    """
    links = get_content_from_url(url, cookiejar)
    try:
        path = '\\tmp'
        if not os.path.exists(os.getcwd() + path):
            os.makedirs(os.getcwd() + path)
        else:
            shutil.rmtree(os.getcwd() + path)
            os.makedirs(os.getcwd() + path)
        i = 0
        #i = 38
        for link in links:
            response = requests.get(link, cookies=cookiejar, stream=True)
            with open(path[1:] + '/' + str(i)+'.pdf', 'wb+') as fd:
                for chunk in response.iter_content(2000):
                    fd.write(chunk)
            i += 1

        sort_and_merge_pdfs(os.getcwd() + path + '\\*.pdf', output_folder, output_name)
        if links:
            print('Successfully merged PDF to folder: {}'.format(output_folder))
            return True
        else:
            return False
    except Exception as e:
        raise e
    finally:
        time.sleep(5)
        shutil.rmtree(os.getcwd() + path)
