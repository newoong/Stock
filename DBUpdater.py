import pymysql,requests, calendar,time,json
from threading import Timer
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup
import mplfinance as mpf

class DBUpdater:
    def __init__(self):
        #생성자 : MariaDB 연결 및 종목코드 딕셔너리 생성
        self.conn=pymysql.connect(host='127.0.0.1',user='root',password='@kimjh102644',db='INVESTAR',charset='utf8')

        with self.conn.cursor() as curs:
            sql='''
            CREATE TABLE IF NOT EXISTS company_info(
                code VARCHAR(20),
                company VARCHAR(40),
                last_update DATE,
                PRIMARY KEY(code))'''
            curs.execute(sql)
            sql='''
            CREATE TABLE IF NOT EXISTS daily_price(
                code VARCHAR(20),
                date DATE,
                open BIGINT(20),
                high BIGINT(20),
                low BIGINT(20),
                close BIGINT(20),
                diff BIGINT(20),
                volume BIGINT(20),
                PRIMARY KEY(code,date))'''
            curs.execute(sql)
        self.conn.commit()
        self.codes=dict() #매번 상정법인목록 파일 읽어오지 않고 미리 딕셔너리에 저장하고 코드 내 활용
        
    def __del__(self):
        self.conn.close()

    def read_krx_code(self):
        #KRX로부터 상장기업 목록 파일을 읽어와서 데이터프레임으로 반환
        url='http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13'
        krx=pd.read_html(url)[0]
        krx=krx[['종목코드','회사명']]
        krx=krx.rename(columns={'종목코드':'code','회사명':'company'})
        krx.code=krx['code'].map('{:06d}'.format) #krx.code->str change
        return krx 
    
    def update_comp_info(self): 
        #종목코드를 company_info 테이블에 업데이트한 후 딕셔너리에 저장
        sql='SELECT * FROM company_info'
        df=pd.read_sql(sql,self.conn) #str type
        for idx in range(len(df)):
            self.codes[df.code.values[idx]]=df.company.values[idx] #딕셔너리에 이미 company_info에 있는 목록 업데이트{code num : company}
        with self.conn.cursor() as curs:
            sql='SELECT max(last_update) FROM company_info'
            curs.execute(sql)
            rs=curs.fetchone()
            today=datetime.today().strftime('%Y-%m-%d')
        
            if rs[0] is None or rs[0].strftime('%Y-%m-%d')<today:
                krx=self.read_krx_code()
                for idx in range(len(krx)):
                    code=krx.code.values[idx] #str type
                    company=krx.company.values[idx]
                    sql=f'REPLACE INTO company_info(code,company,last_update) VALUES ("{code}", "{company}","{today}")' 
                    curs.execute(sql)
                    self.codes[code]=company #딕셔너리 재업데이트, 추가
                    tmnow=datetime.now().strftime('%Y-%m-%d %H:%M')
                    print(f'[{tmnow}] {idx:04d} REPLACE INTO company_info VALUES ({code}, {company},{today})')
                self.conn.commit()
                print('')

    def read_naver(self,code,company,pages_to_fetch):
        try:
            url=f'https://finance.naver.com/item/sise_day.naver?code={code}' #HTTPError
            html=BeautifulSoup(requests.get(url,headers={'User-agent':'Mozilla/5.0'}).text,'lxml') 
            
            pgrr=html.find('td',class_='pgRR') #AttributeError 10일치 이상 없으면 다음페이지 없어서 pgRR없음
            if pgrr is None:
                last_page=1
            else:
                last_page=str(pgrr.a['href']).split('=')[-1]
            pages=min(int(last_page),pages_to_fetch)
        
            df=pd.DataFrame()
            for page in range(1,pages+1):
                pg_url=f'{url}&page={page}'
                df=df.append(pd.read_html(requests.get(pg_url,headers={'User-agent':'Mozilla/5.0'}).text)[0])
                tmnow=datetime.now().strftime('%Y-%m-%d %H:%m')
                print(f'[{tmnow}] {company} {code} : {page}/{pages} pages are downloading...',end='\r') #'the next string will start at the beginning of the line\r'
            df=df.rename(columns={'날짜':'date','종가':'close','전일비':'diff','시가':'open','고가':'high','저가':'low','거래량':'volume'})
            df.date=df.date.replace('.','-')
            df=df.dropna()
            df[['close', 'diff', 'open', 'high', 'low', 'volume']] = df[['close','diff', 'open', 'high', 'low', 'volume']].astype(int)  #values to int
            df = df[['date', 'open', 'high', 'low', 'close', 'diff', 'volume']]
            return df
        
        except Exception as e:
            print(f'Exception has occured : {e}')
            return None

    def replace_into_db(self,df,num,code,company): # 인수로 받은 df(한 종목)만 업데이트
        with self.conn.cursor() as curs:
            for r in df.itertuples():
                sql=f"REPLACE INTO daily_price VALUES ('{code}','{r.date}',{r.open},{r.high},{r.low},{r.close},{r.diff},{r.volume})"
                curs.execute(sql)
            self.conn.commit()
            tmnow=datetime.now().strftime('%Y-%m-%d %H:%M')
            print("[{}] #{:04d} {} ({}) : {} rows > REPLACE INTO daily_price [OK]".format(tmnow,num+1,company,code,len(df)))
    
    def update_daily_price(self,pages_to_fetch): #replace_into_db를 여러번 반복해 상장법인목록에 있는 모든 종목 업데이트
        for idx,code in enumerate(self.codes):
            df=self.read_naver(code,self.codes[code],pages_to_fetch)
            if df is None: #read_naver한 df가 None(http or attribute Error)이면 업데이트 안하고 다음 종목으로 넘어가
                continue 
            self.replace_into_db(df,idx,code,self.codes[code])

    def execute_daily(self): #config.json 파일 이용해 첫 업데이트인지 아닌지 따라 달라짐
        self.update_comp_info()
        try:
            with open('config.json','r') as in_file:
                config=json.load(in_file) #딕셔너리 형식으로 load
                pages_to_fetch=config['pages_to_fetch']
        except FileNotFoundError : #json파일이 없으면 작성해줌 -> 맨 처음 업데이트 할 땐 파일 없고 첫 업데이트 이후 파일 생성
            with open('config.json','w') as out_file: 
                pages_to_fetch=100 #100페이지는 1000일 이므로 1년에 250일 장 여므로 4년치
                config={'pages_to_fetch':1}
                json.dump(config,out_file)
        self.update_daily_price(pages_to_fetch)

        tmnow=datetime.now()
        lastday=calendar.monthrange(tmnow.year,tmnow.month)[1] #30일인지 31일인지
        if tmnow.month==12 and tmnow.day==lastday: #timer를 위해 다음 날 구하기
            tmnext=tmnow.replace(year=tmnow.year+1,month=1,day=1,hour=17,minute=0,second=0)
        elif tmnow.day==lastday:
            tmnext=tmnow.replace(month=tmnow.month+1,day=1,hour=17,minute=0,second=0)
        else:
            tmnext=tmnow.replace(day=tmnow.day+1,hour=17,minute=0,second=0)
        tmdiff=tmnext-tmnow
        sec=tmdiff.seconds
        t=Timer(sec,self.execute_daily)
        print("Waiting for next update ({}) ...".format(tmnext.strftime('%Y-%m-%d %H:%M')),end='\r')
        t.start() #자동실행 위한 타이머 시작
        

if __name__ == '__main__':
    dbu=DBUpdater()
    dbu.execute_daily()
    
    
    
