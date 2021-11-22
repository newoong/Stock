import matplotlib.pyplot as plt
import Analyzer
import pandas as pd

#중간밴드: 이동평균선 // 상단밴드: 이동평균선+(2*표준편차) // 하단밴드: 이동평균선-(2*표준편차)
mk=Analyzer.MarketDB()
company=input('company or code :')
start=input('start date:')
end=input('end date:')
if start=='':
    start=None
if end=='':
    end=None
df=mk.get_daily_price(company,start,end)
df['MA20']=df['close'].rolling(window=20).mean()
df['stddev']=df['close'].rolling(window=20).std()
df['upper']=df.MA20+2*df.stddev
df['lower']=df.MA20-2*df.stddev
df['PB']=(df.close-df.lower)/(df.upper-df.lower)
df['bandwidth']=(df.upper-df.lower)/df.MA20*100
df['TP']=(df['high']+df['low']+df['close'])/3
df['PMF']=df['NMF']=0 #긍정적,부정적 현금흐름
for i in range(len(df)-1):
    if df.TP.values[i]<df.TP.values[i+1]:
        df.PMF[i+1]=df.TP.values[i+1]*df.volume.values[i+1]
    else:
        df.NMF[i+1]=df.TP.values[i+1]*df.volume.values[i+1]
df['MFI10']=100-(100/(1+df.PMF.rolling(window=10).sum()/df.NMF.rolling(window=10).sum()))
df=df.dropna()

plt.suptitle(company) #Big title
plt.subplot(2,1,1)
plt.title(f'Bollinger Band of {company}') #볼린저밴드 그래프
plt.plot(df.index,df.close,color='#0000ff',label='close')
plt.plot(df.index,df.MA20,'k--',label='MA20')
plt.plot(df.index,df.upper,'r--',label='upper_band')
plt.plot(df.index,df.lower,'c--',label='lower_band')
plt.fill_between(df.index,df.upper,df.lower,color='0.9')
for i in range(len(df)):    
    if df.PB.values[i]>0.8 and df.MFI10.values[i]>80:
        plt.plot(df.index[i],df.close[i],'r^')
    elif df.PB.values[i]<0.2 and df.MFI10.values[i]<20:
        plt.plot(df.index[i],df.close[i],'bv')
plt.legend(loc='best')
plt.subplot(212)
plt.title('BollingerBand %b*100 and MFI10') #%b
plt.plot(df.index,df['PB']*100,'b',label='%B*100')
plt.plot(df.index,df['MFI10'],'g--',label='MFI 10day') #MFI10
plt.yticks([-20,0,20,40,60,80,100,120])
for i in range(len(df)):    
    if df.PB.values[i]>0.8 and df.MFI10.values[i]>80:
        plt.plot(df.index[i],0,'r^')
    elif df.PB.values[i]<0.2 and df.MFI10.values[i]<20:
        plt.plot(df.index[i],0,'bv')
plt.grid(True)
plt.legend(loc='best')
'''plt.subplot(313)
plt.title('Bandwidth')
plt.plot(df.index,df.bandwidth,'m',label='bandwidth')
plt.grid(True)
plt.legend(loc='best')'''

plt.show()




