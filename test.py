import pandas as pd
from bs4 import BeautifulSoup
import mplfinance as mpf
import requests

code=input('company_code : ')
try:
    url=f'https://finance.naver.com/item/sise_day.naver?code={code}' #code={company_code}
    soup=BeautifulSoup(requests.get(url,headers={'User-agent':'Mozilla/5.0'}).text,'lxml')
    pgrr=soup.find('td',class_='pgRR')
    if pgrr is None:
        last_page=1
    else:
        last_page=int(str(pgrr.a['href']).split('=')[-1])
    df=pd.DataFrame()
    for i in range(1,last_page+1):
        pg_url=f'{url}&page={i}'
        df=df.append(pd.read_html(requests.get(pg_url,headers={'User-agent':'Mozilla/5.0'}).text)[0])
    df=df.rename(columns={'날짜':'date','종가':'close','시가':'open','고가':'high','저가':'low','거래량':'volume','전일비':'diff'})
    df=df.dropna()
    df[['open','high','low','close','diff','volume']]=df[['open','high','low','close','diff','volume']].astype(int)
    df.index=pd.to_datetime(df.date)
    df=df[['open','high','low','close','volume']]
    df=df.sort_index()
    kwargs=dict(title=code,type='candle',mav=(2,4,6),ylabel='ohlc',volume=True)
    mc=mpf.make_marketcolors(up='r',down='b',inherit=True)
    ms=mpf.make_mpf_style(marketcolors=mc)
    mpf.plot(df,**kwargs,style=ms)
except Exception as e:
    print(f'Error has occured : {e}')
        
        

        