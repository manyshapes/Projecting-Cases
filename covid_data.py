import pandas as pd

# this is the link to the COVID-19 data
covid_url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'

raw_df = pd.read_csv(covid_url, index_col=0, dtype='object')

df = raw_df.reset_index()
temp_df = df.rename(columns = {'Province/State': 'state',
                               'Country/Region': 'country',
                               'Lat': 'lat',
                               'Long': 'long'
                              })

# removing the latitude and the logitude columns as they are not required
temp_df = temp_df.drop(columns = ['lat', 'long'])

# unpivoting the table to see the cases per country and the date
df = pd.melt(temp_df, id_vars = ['country','state'], var_name='date', value_name = 'no_cases')