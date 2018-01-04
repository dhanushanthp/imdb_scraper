import bs4
import urllib
import json
import pandas as pd
import random

""" 
The Process of scraping only work with movies. Not for TV Shows. Each function represent the
page level extractions. The pages are,
        1. Titles page (www.imdb.com/title/)
        2. Cast page (www.imdb.com/name/)
        3. Oscar awards page (http://www.imdb.com/title/<id>/awards)
        4. Production companies page (http://www.imdb.com/title/<id>/companycredits)
"""

__author__ = "Dhanushanth"
__version__ = "1.0.1"
__email__ = "dhanushanthp@gmail.com"
__status__ = "Production"


def page_extraction(soup_object, content_type):
    """
    Extraction from titles page
    :param soup_object: HTML object for scraping.
    :param content_type: Type of the content.
    :return: Extracted data from IMDB titles page.
    """
    countries = []

    languages = []

    genres = []

    imdb_title = soup_object.find_all('h1', itemprop="name")[0].text.split('(')[0].lower().strip()

    release_year = None

    if content_type == 'movie':
        tmp_release = soup_object.find_all('h1', itemprop="name")[0].text.split('(')
        release_year = tmp_release[len(tmp_release) - 1].lower().replace(')', '').strip()
    else:
        # Pick Tvshow latest year.
        all_series_attributes = soup_object.find_all("div", {"class": "seasons-and-year-nav"})
        tvshow_year = []

        # Some Tvshow don't have episodes.
        if len(all_series_attributes) > 0:
            for entry in all_series_attributes[0]:
                if type(entry) == bs4.element.Tag:
                    element = entry.find("a")
                    if element is not None:
                        tvshow_year.append(element.text)

            release_year = int(tvshow_year[len(tvshow_year)-1])

    # Some content don't have the ratings
    try:
        rating = float(soup_object.find_all(itemprop="ratingValue")[0].text)
    except (IndexError, ValueError):
        rating = 0.0

    imdb_recommended_movies = [{element.find('a')['href'].split('/')[2].strip(): element.find('img')['title']
        .strip().lower()} for element in soup_object.find_all('div', {'class': 'rec_item'})
                               if element.find('img') is not None]

    # When movies don't have recommendations.
    try:
        imdb_recommended_movies.pop(0)
    except IndexError:
        pass

    try:
        short_description = soup_object.find_all('div', {'class':'summary_text'})[0].text.replace('\n', '')\
            .strip().lower()
    except IndexError:
        short_description = None

    try:
        story_line = soup_object.find_all('div', {'class':'inline canwrap'})[0].text.lower().replace('\n', '')\
            .split('written by')[0].strip()
    except IndexError:
        story_line = None

    all_details_attributes = soup_object.find_all("div", {"class": "txt-block"})

    for entry in all_details_attributes:
        try:
            if entry.h4.text.strip()=='Country:':
                countries = [value.text.lower() for value in entry.find_all(itemprop="url")]
            if entry.h4.text.strip()=='Language:':
                languages = [value.text.lower() for value in entry.find_all(itemprop="url")]
        except Exception:
            pass

    all_genre_attributes = soup_object.find_all("div", {"class": "see-more inline canwrap"})

    for entry in all_genre_attributes:
        try:
            if entry.h4.text.strip() == 'Genres:':
                genres = [value.text.strip().lower() for value in entry.find_all("a")]
        except Exception:
            pass

    return {'imdb_title': imdb_title,
            'release_year': release_year,
            'rating': rating,
            'countries': countries,
            'languages': languages,
            'genres': genres,
            'recommended_movies': imdb_recommended_movies,
            'short_description': short_description,
            'story_line': story_line}


def cast_extraction(soup_object):
    """
    Extraction from cast page [Actors, Directors, Writers]
    :param soup_object:
    :return:
    """
    directors = []
    actors = []
    writers = []
    producers = []
    musicians = []
    cinematographers = []

    cast_attributes = soup_object.findAll('div', {'id': "fullcredits_content"})[0]

    headers = cast_attributes.find_all('h4')
    tables = cast_attributes.find_all('table')

    for element in range(0, len(headers)):
        header = headers[element].text.lower().replace("\n", '').replace(" ", "_").strip()
        if 'directed_by' in header:
            directors = [{value['href'].split('/')[2]: value.text.lower().strip()}
                         for value in tables[element].find_all('a')]
        if 'writing_credits' in header:
            writers = [{value['href'].split('/')[2]: value.text.lower().strip()}
                       for value in tables[element].find_all('a')]
        if '_cast_' in header:
            actors = [{value['href'].split('/')[2]: value.text.lower().strip()}
                      for value in tables[element].find_all(itemprop="url")]
            actors = actors[:20]
        if 'produced_by' in header:
            producers = [{value['href'].split('/')[2]: value.text.lower().strip()}
                         for value in tables[element].find_all('a')]
        if 'music_by' in header:
            musicians = [{value['href'].split('/')[2]: value.text.lower().strip()}
                         for value in tables[element].find_all('a')]
        if 'cinematography_by' in header:
            cinematographers = [{value['href'].split('/')[2]: value.text.lower().strip()}
                                for value in tables[element].find_all('a')]

    return {'directors': directors,
            'actors': actors,
            'writers': writers,
            'producers': producers,
            'musicians': musicians,
            'cinematographers': cinematographers}


def prod_company_extraction(soup_object):
    """
    Extraction from Production companies page
    :param soup_object:
    :return:
    """
    production_companies = []
    company_attributes = soup_object.find_all('div', {'id': "company_credits_content"})[0]

    com_headers = company_attributes.find_all('h4')
    com_tables = company_attributes.find_all('ul')

    for element in range(0, len(com_headers)):
        header = com_headers[element].text.lower().replace("\n", '').replace(" ", "_").strip()
        if 'production_companies' in header:
            production_companies = [{value['href'].split('/')[2].split("?")[0].strip():value.text.lower().strip()}
                                    for value in com_tables[element].find_all('a')]

    return production_companies


def awards_extraction(soup_object):
    """
    Extraction from Oscar Awards page
    :param soup_object:
    :return:
    """
    oscar_awards = []

    awards_attributes = soup_object.find_all('div', {'class': 'article listo'})[0]

    try:
        all_headers = [element.text.replace('\n', '').strip().split(', ')[0] for element in
                       awards_attributes.find_all('h3')]
        oscar_locations = [i for i, x in enumerate(all_headers) if x == 'Academy Awards']

        for oscar_position in oscar_locations:
            oscar_awards_att = awards_attributes.find_all('table')[oscar_position - 1]
            oscar_enabler = False
            for element in oscar_awards_att.find_all('td'):
                each_line = [element.strip().lower() for element in element.text.split('\n')][1]
                if each_line == 'won':
                    oscar_enabler = True
                if each_line != 'won' and each_line in 'best':
                    oscar_enabler = True
                if each_line == 'nominated':
                    break

                if oscar_enabler:
                    oscar_awards.append(each_line)

        oscar_awards = filter(lambda x: x != 'won', oscar_awards)
    except ValueError:
        oscar_awards = []

    return oscar_awards


def get_data(imdb_id, ip_proxy, content_type):
    """
    Data extraction and proxy management
    :param imdb_id: IMDB id of the title.
    :param ip_proxy: proxy address of each request.
    :return: combined data_dump of IMDB
    """
    soup_content = None
    soup_cast = None
    soup_awards = None
    soup_company = None
    try:
        if ip_proxy is None:
            html_content = urllib.urlopen('http://www.imdb.com/title/' + imdb_id).read()
            soup_content = bs4.BeautifulSoup(html_content, 'html.parser')

            html_cast = urllib.urlopen('http://www.imdb.com/title/' + imdb_id + '/fullcredits').read()
            soup_cast = bs4.BeautifulSoup(html_cast, 'html.parser')

            html_awards = urllib.urlopen('http://www.imdb.com/title/' + imdb_id + '/awards').read()
            soup_awards = bs4.BeautifulSoup(html_awards, 'html.parser')

            html_company = urllib.urlopen('http://www.imdb.com/title/' + imdb_id + '/companycredits').read()

            soup_company = bs4.BeautifulSoup(html_company, 'html.parser')
        else:
            html_content = urllib.urlopen('http://www.imdb.com/title/' + imdb_id,
                                          proxies={'http': ip_proxy[0]}).read()
            soup_content = bs4.BeautifulSoup(html_content, 'html.parser')

            html_cast = urllib.urlopen('http://www.imdb.com/title/' + imdb_id + '/fullcredits',
                                       proxies={'http': ip_proxy[1]}).read()
            soup_cast = bs4.BeautifulSoup(html_cast, 'html.parser')

            html_awards = urllib.urlopen('http://www.imdb.com/title/' + imdb_id + '/awards',
                                         proxies={'http': ip_proxy[2]}).read()
            soup_awards = bs4.BeautifulSoup(html_awards, 'html.parser')

            html_company = urllib.urlopen('http://www.imdb.com/title/' + imdb_id + '/companycredits',
                                          proxies={'http': ip_proxy[3]}).read()

            soup_company = bs4.BeautifulSoup(html_company, 'html.parser')

        page = page_extraction(soup_content, content_type)
        cast = cast_extraction(soup_cast)
        companies = prod_company_extraction(soup_company)
        awards = awards_extraction(soup_awards)
    except (IOError, IndexError) as e:
        raise e

    output = {'page': page,
              'cast': cast,
              'companies': companies,
              'awards': awards}

    return output


def generate_imdb_data(imdb_id, content_id, content_type, vod_type, proxy=None):
    result_dic = get_data(imdb_id, proxy, content_type)

    data_out = pd.DataFrame({'_id': [content_id],
                'imdb_id': [imdb_id],
                'imdb_title': [result_dic['page']['imdb_title']],
                'production_year': [result_dic['page']['release_year']],
                'rating': [result_dic['page']['rating']],
                'countries': [json.dumps(result_dic['page']['countries']).replace('\n', ' ').replace('\r', '')],
                'languages': [json.dumps(result_dic['page']['languages']).replace('\n', ' ').replace('\r', '')],
                'genres': [json.dumps(result_dic['page']['genres']).replace('\n', ' ').replace('\r', '')],
                'recommended_movies': [json.dumps(result_dic['page']['recommended_movies']).replace('\n', ' ').replace('\r', '')],
                'short_description': [result_dic['page']['short_description']],
                'story_line': [result_dic['page']['story_line']],
                'directors': [json.dumps(result_dic['cast']['directors']).replace('\n', ' ').replace('\r', '')],
                'actors': [json.dumps(result_dic['cast']['actors']).replace('\n', ' ').replace('\r', '')],
                'writers': [json.dumps(result_dic['cast']['writers']).replace('\n', ' ').replace('\r', '')],
                'producers': [json.dumps(result_dic['cast']['producers']).replace('\n', ' ').replace('\r', '')],
                'musicians': [json.dumps(result_dic['cast']['musicians']).replace('\n', ' ').replace('\r', '')],
                'cinematographers': [json.dumps(result_dic['cast']['cinematographers']).replace('\n', ' ').replace('\r', '')],
                'content_provider': [json.dumps(result_dic['companies']).replace('\n', ' ').replace('\r', '')],
                'oscar_awards': [json.dumps(result_dic['awards']).replace('\n', ' ').replace('\r', '')],
                'content_type': [content_type],
                'vod_type': [vod_type]})

    return data_out


if __name__ == '__main__':
    proxies = ['http://204.13.204.125:8080',
               'http://192.95.18.162:8080',
               'http://70.35.197.74:80',
               'http://204.13.204.125:8080']
    result = generate_imdb_data(imdb_id='tt7005104', content_id=18673, content_type='tvshow', vod_type='tvod', proxy=None)
