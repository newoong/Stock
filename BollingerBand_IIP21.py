import matplotlib.pyplot as plt
import Analyzer

mk=Analyzer.MarketDB()
company=input('company or code: ')
start=input('start date: ')
end=input('end date: ')
if start=='':
    start=None
if end=='':
    end=None
df=mk.get_daily_price(company,start,end)
df['MA20']=df['close'].rolling(window=20).mean()
df['stddev']=df['close'].rolling(window=20).std()
df['upper']=df['MA20']+2*df['stddev']
df['lower']=df['MA20']-2*df['stddev']
df['PB']=(df['close']-df['lower'])/(df['upper']-df['lower'])
df['II']=((2*df.close-df.high-df.low)/(df.high-df.low))*df.volume
df['IIP21']=(df['II'].rolling(window=21).sum()/df['volume'].rolling(window=21).sum())*100
df.dropna()

plt.suptitle(company) #Big title
plt.subplot(3,1,1)
plt.title(f'Bollinger Band of {company}') #볼린저밴드 그래프
plt.plot(df.index,df.close,color='#0000ff',label='close')
plt.plot(df.index,df.MA20,'k--',label='MA20')
plt.plot(df.index,df.upper,'r--',label='upper_band')
plt.plot(df.index,df.lower,'c--',label='lower_band')
plt.fill_between(df.index,df.upper,df.lower,color='0.9')
for i in range(len(df)):
    if df.PB.values[i]<0.05 and df.IIP21.values[i]>0:
        plt.plot(df.index[i],df.close.values[i],'r^')
    elif df.PB.values[i]>0.95 and df.IIP21.values[i]<0:
        plt.plot(df.index[i],df.close.values[i],'bv')
plt.legend(loc='best')
plt.subplot(312)
plt.plot(df.index,df.PB,'b',label='%B')
for i in range(len(df)):
    if df.PB.values[i]<0.05 and df.IIP21.values[i]>0:
        plt.plot(df.index[i],df.PB.values[i],'r^')
    elif df.PB.values[i]>0.95 and df.IIP21.values[i]<0:
        plt.plot(df.index[i],df.PB.values[i],'bv')
plt.grid(True)
plt.legend(loc='best')
plt.subplot(313)
plt.bar(df.index,df.IIP21,color='g',label='II% 21day')
for i in range(len(df)):
    if df.PB.values[i]<0.05 and df.IIP21.values[i]>0:
        plt.plot(df.index[i],df.IIP21.values[i],'r^')
    elif df.PB.values[i]>0.95 and df.IIP21.values[i]<0:
        plt.plot(df.index[i],df.IIP21.values[i],'bv')
plt.grid(True)
plt.legend(loc='best')
plt.show()

