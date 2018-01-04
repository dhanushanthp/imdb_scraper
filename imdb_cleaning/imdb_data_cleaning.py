import pandas as pd

raw_svod_imdb_data = pd.read_pickle('data_dump/complted_extractions/02_raw_svod_imdb_data.p')
raw_tvod_imdb_data = pd.read_pickle('data_dump/complted_extractions/02_raw_tvod_imdb_data.p')


# Some contents have string as prod year.
def check_string(input):
    try:
        int(input)
        return True
    except Exception:
        return False


# Clean SVOD
raw_svod_imdb_data.loc[~raw_svod_imdb_data.release_year.apply(check_string), 'release_year'] = 0

# Clean TVOD
raw_tvod_imdb_data.release_year = raw_tvod_imdb_data.release_year.apply(int)

# Clean the short_decription with some charactors.
raw_svod_imdb_data.loc[raw_svod_imdb_data['short_description'].str.contains('add a plot'), 'short_description'] = ''
raw_tvod_imdb_data.loc[raw_tvod_imdb_data['short_description'].str.contains('add a plot'), 'short_description'] = ''

# content id as int
raw_svod_imdb_data.content_id = raw_svod_imdb_data.content_id.astype(int)
raw_tvod_imdb_data.content_id = raw_tvod_imdb_data.content_id.astype(int)

# Adding a content type since all are movies
raw_svod_imdb_data['content_type'] = 'movie'
raw_tvod_imdb_data['content_type'] = 'movie'

# Adding a vod type since all are movies
raw_svod_imdb_data['vod_type'] = 'svod'
raw_tvod_imdb_data['vod_type'] = 'tvod'

all_mapped_contents = pd.concat([raw_svod_imdb_data, raw_tvod_imdb_data])

# remove duplicates
all_mapped_contents = all_mapped_contents[~all_mapped_contents.content_id.duplicated()]

raw_tvod_imdb_data.to_pickle('data_dump/complted_extractions/03_cleaned_tvod_imdb_data.p')
raw_svod_imdb_data.to_pickle('data_dump/complted_extractions/03_cleaned_svod_imdb_data.p')
all_mapped_contents.to_pickle('data_dump/complted_extractions/imdb_data.p')
