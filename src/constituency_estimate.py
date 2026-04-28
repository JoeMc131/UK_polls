
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup

headers = {
    'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
}

labour_2024 = 33.7
con_2024    = 23.7
RUK_2024    = 14.3
LD_2024 = 12.2
SNP_2024 = 2.5
Green_2024 = 6.7
PC_2024 = 0.7
Other_2024 = 100 - labour_2024 - con_2024 - RUK_2024 - LD_2024 - SNP_2024 - Green_2024 - PC_2024

last_vector = np.array(
    [
        labour_2024,
        con_2024,
        RUK_2024,
        LD_2024,
        SNP_2024,
        Green_2024,
        PC_2024,
        Other_2024
    ]
)

map_parties = {
    0:'Labour',
    1:'Conservative',
    2:'Reform',
    3:'LD',
    4:'SNP',
    5:"Green",
    6:'PC',
    7:'Others'
}

def constituency_transform():
    df = pd.read_csv('data/constituency_data.csv')

    df['Other'] =  df['All other candidates']
    df['Other'] += df['DUP']
    df['Other'] += df['SF']
    df['Other'] += df['SDLP']
    df['Other'] += df['UUP']
    df['Other'] += df['APNI']

    per_changes = {}

    for i in range(len(df)):

        constituency_vector = np.array(
            [
                (df['Lab'][i])/df['Valid votes'][i] * 100,
                (df['Con'][i])/df['Valid votes'][i] * 100,
                (df['RUK'][i])/df['Valid votes'][i] * 100,
                (df['LD'][i])/df['Valid votes'][i] * 100,
                (df['SNP'][i])/df['Valid votes'][i] * 100,
                (df['Green'][i])/df['Valid votes'][i] * 100,
                (df['PC'][i])/df['Valid votes'][i] * 100,
                (df['Other'][i])/df['Valid votes'][i] * 100
            ]
        )

        # compare percent change of each constituency for each party (simple, make more advanced)
        per_change = (constituency_vector - last_vector)/last_vector 

        per_changes[df['Constituency name'][i]] = per_change


    return per_changes
        


def get_estimate(lab, con, ref, green, SNP, LD, PC):
    M = constituency_transform()

    test_lab = lab
    test_con = con
    test_ref = ref
    test_green = green 
    test_SNP = SNP
    test_LD = LD
    test_PC = PC
    test_other = 100 - test_lab - test_con - test_SNP - test_green - test_ref - test_PC - test_LD

    test_vector = np.array([
        test_lab,
        test_con,
        test_ref,
        test_LD,
        test_SNP,
        test_green,
        test_PC,
        test_other
    ])



    df_data = {
        'Constituency':[],
        'Winner':[]
    }

    for cons, m, in M.items():
        df_data['Constituency'].append(cons)

        y = test_vector + test_vector*m

        party = map_parties[int(np.argmax(y))]

        df_data['Winner'].append(party)

    df = pd.DataFrame(df_data)

    return df
    

# if __name__=='__main__':
#     return