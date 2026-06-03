import streamlit as st
from get_data import get_polling_data, get_MRP_data
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib import ticker
import numpy as np
from make_predictions import make_pred
from scipy.signal import savgol_filter
import plotly.express as px
import plotly.graph_objects as go
import constituency_estimate
import sys


party_colours = {
    'Labour':'#E4003B',
    'Conservative':"#0087DC",
    'LD':"#FF6600",
    'Green':"#02A95B",
    'Reform':'#12B6CF',
    'SNP':'#FDF38E',
    'PC':'#008672',
    'Others':"#C0C0C098"
}


def style_seat(row):
    styles = []
    for col in row.index:
        if col == 'Party' or col == 'Seats':
            color = party_colours[row['Party']]
            styles.append(f'background-color: {color}; color: {"black" if row["Party"] == "SNP" or row['Party'] == 'Others' else "white"}; font-weight: bold;')
        else:
            styles.append('')
    return styles


def highlight_max_with_party_colors(row):
    """Highlight max value in row with party color"""
    # Find the max value (excluding date)
    numeric_cols = [col for col in row.index if col != 'date']
    max_val = row[numeric_cols].max()
    
    # Create style list
    styles = []
    for col in row.index:
        if col not in party_cols:
            styles.append('')
        elif row[col] == max_val and col in party_colours:
            color = party_colours[col]
            styles.append(f'background-color: {color}; color: white; font-weight: bold;')
        else:
            styles.append('')
    return styles

def MRP_data_style(row):
    styles = []

    for col in row.index:
        if col == 'Party':
            color = party_colours[row[col]]
            styles.append(f'background-color: {color}; color: white; font-weight: bold;')
        elif col == 'Change':
            color = '#82FAA9' if row[col] > 0 else '#FAA091'
            text_color = '#006B00' if row[col] > 0 else '#D1002A'
            styles.append(f'background-color: {color}; color: {text_color}')
        else:
            styles.append('')
    return styles


# for the future predictions with prophet
periods = 180

#savgol arguments
savgol_w = 50
savgol_p = 10

st.title('UK Polling')
st.markdown('Data obtained from [Wikipedia](https://en.wikipedia.org/wiki/Opinion_polling_for_the_next_United_Kingdom_general_election#)')

data = get_polling_data()

df = pd.DataFrame(data)

df.replace(to_replace=['—\n', '–'], value='0', inplace=True, regex=False)
df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')


print(df.Labour)

for col in df.columns:
    if col == 'date':
        continue
    df[col] = pd.to_numeric(df[col].astype(str).str.replace(r'[^0-9.]', '', regex=True), errors='coerce')

df.fillna(0, inplace=True)


print(df.head(20))

alpha = 0.3

fig, ax = plt.subplots()
ax.scatter(df.date, df.Labour, color = party_colours['Labour'], s=2, alpha = alpha)
ax.scatter(df.date, df.Conservative, color = party_colours['Conservative'], s=2, alpha = alpha)
ax.scatter(df.date, df['Reform'], color = party_colours['Reform'], s=2, alpha = alpha)
ax.scatter(df.date, df['Green'], color = party_colours['Green'], s=2, alpha = alpha)
ax.scatter(df.date, df['SNP'], color = party_colours['SNP'], s=2, alpha = alpha)
ax.scatter(df.date, df['PC'], color = party_colours['PC'], s=2, alpha = alpha)
ax.scatter(df.date, df['LD'], color = party_colours['LD'], s=2, alpha = alpha)
ax.set_ylabel(r'\%')
ax.tick_params("x", rotation = 45)


party_cols = ['Labour', 'Conservative', 'LD', 'Green', 'Reform', 'SNP', 'PC']
df = df.sort_values('date')
df_ma = df.set_index('date')[party_cols].rolling(window=50, min_periods=1).mean().reset_index()

smoothed_end_points = {}
Pred_180_days = {}

for party in party_cols:
    y = savgol_filter(df_ma[party], window_length=savgol_w, polyorder=savgol_p)

    smoothed_end_points[party] = y[-1]

    ax.plot(df_ma.date, y, color = party_colours[party], label = party, linewidth = 2)

    ds = df_ma.date

    input_dict = {
        'ds':ds,
        'y':y
    }

    input_df = pd.DataFrame(input_dict)

    forecast = make_pred(input_df, periods=periods)

    Pred_180_days[party] = forecast.yhat.iloc[-1]
    
    ax.plot(forecast.ds[-periods:], forecast.yhat[-periods:], '--', color = party_colours[party])
    ax.fill_between(forecast.ds[-periods:], forecast.yhat_lower[-periods:], forecast.yhat_upper[-periods:], color = party_colours[party], alpha = 0.2)


ax.legend()

df = df.sort_values(by='date', ascending=False)

styled_df = (df.style.apply(highlight_max_with_party_colors, axis=1)
             .format({col: '{:.0f} %' for col in party_cols})
)

st.dataframe(styled_df, use_container_width=True)


st.pyplot(fig)

st.markdown('Dashed lines and shaded regions represent future extrapolations using [Prophet](https://facebook.github.io/prophet/) from Meta')


# ----------- MRP POLL -----------------------




MRP_data = get_MRP_data()
parties, current_seats, pred_seats = MRP_data['Party'], MRP_data['Current Seats'], MRP_data['Pred. Seats']

current_seats = [int(c) for c in current_seats]
pred_seats = [int(p) for p in pred_seats]

MRP_df_data = {
    'Party':parties,
    'Current':current_seats,
    'Predicted':pred_seats
}
df_MRP = pd.DataFrame(MRP_df_data)
df_MRP['Change'] = df_MRP['Predicted'] - df_MRP['Current']

fig_current = px.pie(df_MRP, 
                    names = 'Party',
                    values='Current', 
                    color = 'Party',
                    color_discrete_map=party_colours,
)


fig_pred = px.pie(df_MRP,
                names = 'Party',
                values = 'Predicted',
                color = 'Party',
                color_discrete_map=party_colours
)

st.markdown('# Seat Predictions (MRP polls)')

styled_MRP = (df_MRP.style.apply(MRP_data_style, axis = 1))

st.dataframe(styled_MRP)
st.text(f'MRP conducted by {MRP_data['Pollster']} on {MRP_data['date']}')

pie_cols = st.columns(2)

pie_cols[0].subheader('Last Election')
pie_cols[0].plotly_chart(fig_current, use_container_width=False)

pie_cols[1].subheader('Predicted')
pie_cols[1].plotly_chart(fig_pred, use_container_width=False)


#  ----------- 180 day prediction -----------------

st.title('Seat predictions for predicted poll numbers 180 days from now')

labour_input = Pred_180_days['Labour']
con_input = Pred_180_days['Conservative']
LD_input = Pred_180_days['LD']
Reform_input = Pred_180_days['Reform']
Green_input = Pred_180_days['Green']
SNP_input = Pred_180_days['SNP']
PC_input = Pred_180_days['PC']

df = constituency_estimate.get_estimate(
    lab=labour_input,
    con = con_input,
    LD=LD_input,
    ref=Reform_input,
    green=Green_input,
    SNP=SNP_input,
    PC=PC_input
)

seats_df = df['Winner'].value_counts().rename_axis('Party').reset_index(name='Seats')

max_seats = seats_df['Seats'].max()
winner_index = seats_df['Seats'].idxmax()

if max_seats > 325:
    st.metric('Result', seats_df['Party'][winner_index], f'{max_seats - 325} seat majority', delta_arrow='off')
else:
    st.metric('Result', f'Hung ({seats_df['Party'][winner_index]} Minority)', f'{325 - max_seats} short of majority', delta_color='red', delta_arrow='off')


st.dataframe(df)

styled_seats = seats_df.style.apply(style_seat, axis = 1)

st.dataframe(styled_seats)

fig_user_input = px.pie(seats_df,
                        names = 'Party',
                        values='Seats',
                        color = 'Party',
                        color_discrete_map=party_colours)

st.plotly_chart(fig_user_input)

# -------------- USER INPUT --------------------

st.title('User defined input')
st.text('Data auto filled in with averages of most recent polling data')

user_cols = st.columns(7)

labour_input = user_cols[0].number_input(value=float(smoothed_end_points['Labour']), label = 'Labour (%)', max_value=100.)
con_input = user_cols[1].number_input(value=float(smoothed_end_points['Conservative']), label = 'Cons. (%)', max_value=100.)
LD_input = user_cols[2].number_input(value=float(smoothed_end_points['LD']), label = 'LD (%)', max_value=100.)
Reform_input = user_cols[3].number_input(value=float(smoothed_end_points['Reform']), label = 'Reform UK (%)', max_value=100.)
Green_input = user_cols[4].number_input(value=float(smoothed_end_points['Green']), label = 'Green (%)', max_value=100.)
SNP_input = user_cols[5].number_input(value=float(smoothed_end_points['SNP']), label = 'SNP (%)', max_value=100.)
PC_input = user_cols[6].number_input(value=float(smoothed_end_points['PC']), label = 'PC (%)', max_value=100.)


if st.button('Predict'):
    st.spinner("Calculating...", show_time=True)
    other = 100 - (labour_input + con_input + LD_input + Reform_input + Green_input + SNP_input + PC_input)
    
    # everything should add up to 100
    if other < 0:
        st.text(other)
        st.text('Invalid inputs')
    else:
        df = constituency_estimate.get_estimate(
            lab=labour_input,
            con = con_input,
            LD=LD_input,
            ref=Reform_input,
            green=Green_input,
            SNP=SNP_input,
            PC=PC_input
        )

        seats_df = df['Winner'].value_counts().rename_axis('Party').reset_index(name='Seats')

        max_seats = seats_df['Seats'].max()
        winner_index = seats_df['Seats'].idxmax()
        
        if max_seats > 325:
            st.metric('Result', seats_df['Party'][winner_index], f'{max_seats - 325} seat majority', delta_arrow='off')
        else:
            st.metric('Result', f'Hung ({seats_df['Party'][winner_index]} Minority)', f'{325 - max_seats} short of majority', delta_color='red', delta_arrow='off')


        st.dataframe(df)

        styled_seats = seats_df.style.apply(style_seat, axis = 1)

        st.dataframe(styled_seats)

        fig_user_input = px.pie(seats_df,
                                names = 'Party',
                                values='Seats',
                                color = 'Party',
                                color_discrete_map=party_colours)
        
        st.plotly_chart(fig_user_input)


