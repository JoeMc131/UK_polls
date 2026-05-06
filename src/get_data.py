from bs4 import BeautifulSoup
import pandas as pd
import requests
import json
import streamlit as st

headers = {
    'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
}

years=[
    '2024',
    '2025',
    '2026'
]

@st.cache_data
def get_polling_data(url = 'https://en.wikipedia.org/wiki/Opinion_polling_for_the_next_United_Kingdom_general_election#'):
    """
    Description
    -----------------

    Gets the polling data for the next UK general election from the data of the last general election.

    Parameters
    -----------------
    - url: Web address to the wikipedia article which contains all the polling data
    
    """

    response = requests.get(url, headers=headers)

    # print(response)
    soup = BeautifulSoup(response.content, 'html.parser')

    tables = soup.find_all("table",
                           class_=['wikitable', 'sortable', 'mw-datatable', 'jquery-tablesorter']
    )[:3]

    rows = [table.find_all('tr')[1:] for table in tables]
    # print(f"Length of rows = {len(rows)}")
    rows[-1].pop()
    rows[-1].pop()
    
    data = {
        'date':[],
        'Labour':[],
        'Conservative':[],
        'Reform':[],
        'LD':[],
        'Green':[],
        'SNP':[],
        'PC':[]
    }

    for row_box in rows:
        for row in row_box:
            # print(row)
            cols = row.find_all('td')
            if len(cols) < 14:
                continue
            # print(f"Length of cols = {len(cols)}")
            # print(cols[0].attrs['data-sort-value'])
            data['date'].append(cols[0].attrs['data-sort-value'])
            data['Labour'].append(cols[5].get_text())
            data['Conservative'].append(cols[6].get_text())
            data['Reform'].append(cols[7].get_text())
            data['LD'].append(cols[8].get_text())
            data['Green'].append(cols[9].get_text())
            data['SNP'].append(cols[10].get_text())
            data['PC'].append(cols[11].get_text())

    return data

@st.cache_data
def get_MRP_data(url = 'https://en.wikipedia.org/wiki/Opinion_polling_for_the_next_United_Kingdom_general_election#'):
    response = requests.get(url, headers=headers)

    # print(response)
    soup = BeautifulSoup(response.content, 'html.parser')

    table = soup.find_all("table",
                           class_=['wikitable', 'sortable', 'mw-datatable', 'jquery-tablesorter']
    )[3]

    rows = table.find_all('tr')[2:]

    pred_row = rows[0]
    last_row = rows[-1]

    pred_cols = pred_row.find_all('td')
    last_cols = last_row.find_all('td')

    data = {
        'date':pred_cols[0].attrs['data-sort-value'],
        'Party':[
            'Labour',
            'Conservative',
            'Reform',
            'LD',
            'Green',
            'SNP',
            'PC',
            'Others'
        ],
        'Pred. Seats':[
            pred_cols[5].get_text(),
            pred_cols[6].get_text(),
            pred_cols[9].get_text(),
            pred_cols[7].get_text(),
            pred_cols[10].get_text(),
            pred_cols[8].get_text(),
            pred_cols[11].get_text(),
            pred_cols[12].get_text()
        ],
        'Pollster':pred_cols[1].get_text().rstrip('['),
        'Current Seats':[
            last_cols[3].get_text(),
            last_cols[4].get_text(),
            last_cols[7].get_text(),
            last_cols[5].get_text(),
            last_cols[8].get_text(),
            last_cols[6].get_text(),
            last_cols[9].get_text(),
            last_cols[10].get_text()[:1]
        ]
    }


    return data



if __name__=='__main__':
    data = get_MRP_data()
    print(data)