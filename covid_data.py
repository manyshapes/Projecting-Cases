import pandas as pd

# this is the link to the COVID-19 data
covid_url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'
covid_death_url_global = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv'

raw_cases_df = pd.read_csv(covid_url, index_col=0, dtype='object')
raw_deaths_df = pd.read_csv(covid_death_url_global, index_col=0, dtype='object')

def clean_covid_dataframe(aDf, final_column_name):

    raw_df = aDf.copy()
    raw_df = raw_df.reset_index()
    temp_df = raw_df.rename(columns = {'Province/State': 'state',
                                       'Country/Region': 'country',
                                       'Lat': 'lat',
                                       'Long': 'long'
                                      })

    # removing the latitude and the logitude columns as they are not required
    temp_df = temp_df.drop(columns = ['lat', 'long'])

    # unpivoting the table to see the cases per country and the date
    df = pd.melt(temp_df, id_vars = ['country','state'], var_name='date', value_name = final_column_name)
    df.date = pd.to_datetime(df.date)
    df[final_column_name] = pd.to_numeric(df[final_column_name])

    return df

cases = clean_covid_dataframe(raw_cases_df, final_column_name ='no_cases')
deaths = clean_covid_dataframe(raw_deaths_df, final_column_name ='no_deaths')

covid = cases.set_index(['country','state','date']).join(
    deaths.set_index(['country','state','date']),
    how='left').reset_index()

covid['year'] = covid.date.dt.year
covid['month'] = covid.date.dt.month

covid.to_csv('Datasets/covid_19_data.csv.gz', index=False)
