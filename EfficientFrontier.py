import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import Analyzer

mk=Analyzer.MarketDB()
df=pd.DataFrame()
stocks=['삼성전자','SK하이닉스','NAVER','카카오']
for s in stocks:
    df[s]=mk.get_daily_price(s,'2018-10-14')['close']

daily_ret=df.pct_change()
annual_ret=daily_ret.mean()*252
daily_cov=daily_ret.cov()
annual_cov=daily_cov*252

port_ret=[]
port_risk=[]
port_weights=[]
sharp_ratio=[] #샤프 지수

for _ in range(20000):
    weight=np.random.random(len(stocks)) #choose number of len(stocks) randomize float between 0~1
    weight /= np.sum(weight)

    returns=np.dot(weight,annual_ret) #return 1 float value
    risk=np.sqrt(np.dot(weight.T,np.dot(annual_cov,weight))) #return 1 float value
    
    port_ret.append(returns)
    port_risk.append(risk)
    port_weights.append(weight)
    sharp_ratio.append(returns/risk)
    
portfolio={'Returns':port_ret,'Risk':port_risk,'Sharpe':sharp_ratio}

for i,s in enumerate(stocks):
    portfolio[s]=[w[i] for w in port_weights]

df=pd.DataFrame(portfolio) #dict의 values가 리스트로만 이루어져 있기 때문에 DataFrame 인수로 dict 받아짐
df=df[['Returns','Risk','Sharpe']+[s for s in stocks]]
max_sharpe=df.loc[df.Sharpe==df.Sharpe.max()] #df.loc[bool type Series] (num of row same) -> return True row
min_risk=df.loc[df.Risk==df.Risk.min()]

print(max_sharpe)
print(min_risk)
df.plot.scatter('Risk','Returns',figsize=(11,7),grid=True,c='Sharpe',cmap='viridis',edgecolors='k')
plt.scatter(max_sharpe.Risk,max_sharpe.Returns,c='r',marker='*',s=300)
plt.scatter(min_risk.Risk,min_risk.Returns,c='r',marker='X',s=300)
plt.title('PORTFOLIO OPTIMIZATION')
plt.xlabel('RISK')
plt.ylabel('EXPECTATION RETURNS')
plt.show()


