from google import search
from sqlalchemy import create_engine
import pandas as pd

REDSHIFT_CONNECTION_URL = ''

"""Generate IMDB links based on Google search"""
data_frame = None

try:
    data_frame = pd.read_pickle('data_dump/imdb_svod_mapping.p')
except IOError:
    engine = create_engine(REDSHIFT_CONNECTION_URL)

    data_frame = pd.read_sql_query("SELECT content_id, "
                               "content_name,"
                               "production_year as year,"
                               "split_part(directors,', ',1) director "
                               "from summary.data_for_content_recommendation "
                               "WHERE vod_type='svod' "
                                "AND content_type='movie';", engine)

    data_frame['imdb_id'] = ""
    data_frame['imdb_url'] = ""

    data_frame.to_pickle('data_dump/imdb_svod_mapping.p')


for index, row in data_frame[data_frame['imdb_url'] == ""].iterrows():
    search_q = row[1] + ' ' + str(row[2]) + ' imdb movie'
    google_result_list = []
    for url in search(search_q.encode('UTF-8'), stop=1):
        google_result_list.append(url)

    print row[1], google_result_list[0]

    try:
        data_frame.set_value(index, 'imdb_id', google_result_list[0].split('/')[4])
    except IndexError:
        data_frame.set_value(index, 'imdb_id', None)

    data_frame.set_value(index, 'imdb_url', google_result_list[0])

    data_frame.to_pickle('data_dump/imdb_svod_mapping.p')


# IMDB Data map imdb_cleaning.
df_imdb_url = data_frame.loc[data_frame['imdb_url'].str.contains('http://www.imdb.com/title/')]
df_without_imdb_url = data_frame.loc[~data_frame['imdb_url'].str.contains('http://www.imdb.com/title/')]
len(df_imdb_url)
len(df_without_imdb_url)

df_imdb_url.to_pickle("data_dump/svod/df_imdb_url.p")
df_without_imdb_url.to_pickle("data_dump/svod/df_without_imdb_url.p")


df = pd.read_pickle("data_dump/svod/df_imdb_url.p")
df['imdb_title'] = ''


df.to_pickle("data_dump/svod/df_imdb_url_add_title.p")
df = pd.read_pickle("data_dump/svod/df_imdb_url_add_title.p")
df = df[['content_id','content_name','imdb_title','year', 'imdb_id', 'imdb_url']]


import pandas as pd

pd.read_pickle('data_dump/svod/01_imdb_svod_mapping_raw.p')