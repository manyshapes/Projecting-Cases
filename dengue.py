import pandas as pd
import numpy as np

import glob
from epiweeks import Week, Year

all_files  = glob.glob("Datasets/Dengue/*")

def df_clean_columns(aDf):

    df = aDf.copy()
    df.columns = ['_'.join(c.lower().split(' ')) for c in df.columns]

    columns_to_rename = {'in_/_out_of_subregions': 'in/out_of_subregions',
                        'epi._week_(a)': 'epi_week',
                        'total_of_dengue_cases_(b)': 'total_dengue_cases',
                        'incidence_rate_(c)': 'incidence_rate',
                        'severe_dengue_(d)': 'severe_dengue',
                        'cfr_(f)': 'cfr'}

    df = df.rename(columns = columns_to_rename)
    return df


sample_df = pd.read_csv('Datasets/Dengue/dengue_epi_week_50.csv', dtype='object', encoding='iso-8859-1', nrows=10)
sample_df = df_clean_columns(sample_df)

root_columns = sample_df.columns

# have the data for these years
years = ['2015','2016','2017','2018','2019','2020']

data_ref = {}
for c in years:
    data_ref[c] = {}
    data_ref[c]['countries'] = []
    data_ref[c]['subregions'] = []

regions = ['North America','Central America Ithsmus and Mexico',
           'Andean Subregion','Southern Cone','Latin Caribbean',
           'Non-Latin Caribbean']

for file_path in all_files:
    df = pd.read_csv(file_path, dtype='object', encoding='iso-8859-1')
    df = df_clean_columns(df)

    assert df.columns.tolist() == root_columns.tolist()
    assert not df.year.isna().any()

    # removing the totals and americas
    df = df[~df.country_or_subregion.isin(['Total','The Americas'])]

    for year in years:
        df_a = df[df.year.isin([year])]

        subregions_series = df_a.country_or_subregion.isin(regions)

        df_subregions = df_a[subregions_series]
        df_countries = df_a[~subregions_series]

        assert not df_subregions.country_or_subregion.isna().any()
        assert not df_countries.country_or_subregion.isna().any()

        data_ref[year]['countries'].append(df_countries)
        data_ref[year]['subregions'].append(df_subregions)


all_years_data = []

numeric_columns = [c for c in root_columns if c not in ['country_or_subregion','serotype','in/out_of_subregions']]
for year in years:
    year_data = pd.concat(data_ref[year]['countries'])

    # removing the quotes
    year_data = year_data.apply(lambda s: s.str.replace('"', ""))
    for c in numeric_columns:

        # removing the comma in numeric columns
        year_data[c] = year_data[c].str.replace(',','')
        year_data[c] = pd.to_numeric(year_data[c])

    data_x = year_data.drop_duplicates()

    # when the epi week is NA then the columns
    # 'total_dengue_cases', 'incidence_rate', 'laboratory_confirmed',
    # 'severe_dengue', '(sd/d)_x100_(e)', 'deaths', 'cfr'
    # have no data in them

    null_data = data_x.epi_week.isna()

    null_data_x = data_x[null_data][['total_dengue_cases', 'incidence_rate', 'laboratory_confirmed',
                                    'severe_dengue', '(sd/d)_x100_(e)', 'deaths', 'cfr']]

    # checking the above assumption
    assert null_data_x.isna().all().all()

    non_null_data = data_x[~null_data]
    all_years_data.append(non_null_data)

# combining all the years and deriving the epi week start date
# and generating no cases per epi week
x_data = pd.concat(all_years_data)
x_data.epi_week = pd.to_numeric(x_data.epi_week, downcast ='integer', errors='coerce')
x_data['epi_week_start_date'] = x_data.apply(lambda x: pd.to_datetime(Week(x.year, x.epi_week).startdate()), axis=1)
x_data['date'] = x_data.epi_week_start_date
x_data['month'] = x_data.epi_week_start_date.dt.month
x_data['day'] = x_data.epi_week_start_date.dt.day

for a in ['epi_week_start_date','date']:
    x_data[a] = pd.to_datetime(x_data[a])

# and generating no cases per epi week
x_data = x_data.sort_values(by=['country_or_subregion','year','epi_week'])
x_data['previous_epi_week_cases'] = x_data.groupby(by=['country_or_subregion','year'])['total_dengue_cases'].shift(1)
x_data['dengue_cases_per_epi_week'] = x_data['total_dengue_cases'] - x_data.previous_epi_week_cases.fillna(0)

x_data['previous_epi_week_deaths'] = x_data.groupby(by=['country_or_subregion','year'])['deaths'].shift(1)
x_data['dengue_deaths_per_epi_week'] = x_data['deaths'] - x_data.previous_epi_week_deaths.fillna(0)

x_data = x_data.rename(columns = {'total_dengue_cases': 'cumulative_dengue_cases'})
x_data = x_data.drop(columns = ['previous_epi_week_cases'])

x_data = x_data.rename(columns = {'deaths': 'cumulative_deaths',
                                  'dengue_deaths_per_epi_week': 'no_deaths',
                                  'dengue_cases_per_epi_week': 'no_cases',
                                  'country_or_subregion': 'country',
                                  'cumulative_dengue_cases': 'cumulative_cases'
                                  })
x_df = x_data.copy()
x_df.to_csv('Datasets/dengue_data.csv.gz', index=False)
