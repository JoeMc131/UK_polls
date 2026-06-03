from prophet import Prophet
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

@st.cache_data
def make_pred(df, periods = 15):
    """
    Description
    -----------------

    Uses prophet to make future predictions of the future polling numbers
    
    """
    model = Prophet()
    model.fit(df)

    future = model.make_future_dataframe(periods = periods)
    
    forecast = model.predict(future)

    return forecast

if __name__=='__main__':

    # test prophet
    x = np.linspace(0, 10, 1000)
    y = x**5 + 2**3 + x
    ds = pd.date_range('2018-01-01', periods = 1000, freq='d')

    d = {
        'ds':ds,
        'y':y
    }

    df = pd.DataFrame(d)
    forecast = make_pred(df)

    print(forecast.tail())

    plt.plot(ds, y)
    plt.plot(forecast.ds[-91:], forecast.yhat[-91:], '--', color = 'black')
    plt.show()

    