import os
import pandas as pd
import numpy as np
import traceback
import datetime

from os.path import isfile, join

FOLDER = '../data/stock_prices/Data/Stocks'


def main():
    df = pd.DataFrame()
    i = 0
    for file in [f for f in os.listdir(FOLDER) if isfile(join(FOLDER, f))]:
        i += 1
        if i > 200:
            break
        try:
            tmp_df = pd.read_csv(join(FOLDER, file))
            tmp_df['dt'] = pd.to_datetime(tmp_df['Date'])
            tmp_df.set_index('Date',  inplace=True)
            stock_name = file[:file.find('.')]
            tmp_df.rename(columns={'Close': stock_name}, inplace=True)
            tmp_df = tmp_df[tmp_df['dt'] > datetime.datetime(2014, 1, 1)]
            if not df.empty:
                df = df.join(tmp_df[stock_name], how='outer')
            else:
                df = tmp_df[stock_name].copy(deep=True).to_frame()
        except Exception as e:
            print(file)
            traceback.print_exc()

    df.to_csv('../data/stocks.csv')


if __name__ == '__main__':
    main()