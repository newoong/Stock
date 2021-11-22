from datetime import datetime
import pymysql
import pandas as pd
import re
import mplfinance as mpf

class MarketDB():
    def __init__(self):
        self.conn=pymysql.connect(host='127.0.0.1',user='root',passwd='@kimjh102644',database='INVESTAR',charset='utf8')
        self.codes={}
        self.get_comp_info()
        
    
    def __del__(self):
        self.conn.close()

    def get_comp_info(self):
        sql='SELECT * FROM company_info'
        df=pd.read_sql(sql,self.conn) #code:str type
        for idx in range(len(df)):
            self.codes[df.code.values[idx]]=df.company.values[idx]
        
            

    def get_daily_price(self,code,start=None,end=None): #no date input : None
        #code: code or company
        code_key=list(self.codes.keys())
        code_value=list(self.codes.values())
        if code in code_key:
            pass
        elif code in code_value:
            idx=code_value.index(code) #index(value) : return idx of value
            code=code_key[idx]        
        else:
            print('Wrong input !')
        today=datetime.today()
        if start is None:
            start=today.replace(year=today.year-1).strftime('%Y-%m-%d') # price of 1year ago
            print(f"start_date is initialized to {start}")
        else:
            start_lst=re.split('\D+',start) #\D+ : split into one and more none integer type
            if start_lst[0]=='':
                start_lst=start_lst[1:]
            start_year=int(start_lst[0])
            start_month=int(start_lst[1])
            start_day=int(start_lst[2])
            start=f"{start_year}-{start_month}-{start_day}"
            if start_year<1900 or start_year>2200 or start_month>12 or start_month<1 or start_day>31 or start_day<1:
                print('ValueError : start_date({start}) is wrong')
                return

        if end is None:
            end=today.strftime('%Y-%m-%d')
            print(f"end_date is initialized to {end}")
        else:
            end_lst=re.split('\D+',end)
            if end_lst[0]=='':
                end_lst=end_lst[1:]
            end_year=int(end_lst[0])
            end_month=int(end_lst[1])
            end_day=int(end_lst[2])
            end=f"{end_year}-{end_month}-{end_day}"
            if end_year<1900 or end_year>2200 or end_month>12 or end_month<1 or end_day>31 or end_day<1:
                print('ValueError : end_date({end}) is wrong')
                return
        
        sql=f"SELECT * FROM daily_price WHERE code='{code}' and date >='{start}' and date <='{end}'"
        df=pd.read_sql(sql,self.conn)
        df.index=pd.to_datetime(df['date'])
        return df
    
    def showplot(self,df,company):
         #df.index=df.date 이렇게 하면 그래프 안그려짐
        df=df[['open','high','low','close','volume']]
        kwargs=dict(title=company,type='candle',mav=(2,4,6),volume=True,ylabel='ohlc')
        mc=mpf.make_marketcolors(up='r',down='b',inherit=True)
        s=mpf.make_mpf_style(marketcolors=mc)
        mpf.plot(df,**kwargs,style=s)   


if __name__ =='__main__':
    mdb=MarketDB()
    code=input('회사명 또는 종목코드 입력 : ')
    df=mdb.get_daily_price(code,'2021-08-08')
    mdb.showplot(df,code)

