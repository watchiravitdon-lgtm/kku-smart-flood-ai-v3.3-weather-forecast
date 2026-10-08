import numpy as np
import pandas as pd
from pathlib import Path

rng=np.random.default_rng(2026); n=6000
r1=np.clip(rng.gamma(1.8,5,n),0,80)
r24=np.clip(r1+rng.gamma(2.2,18,n),0,250)
r3=np.clip(r24+rng.gamma(2.0,35,n),0,500)
r7=np.clip(r3+rng.gamma(2.0,55,n),0,900)
water=np.clip(rng.normal(1.0,0.45,n),0.05,4.0)
trend=np.clip(rng.normal(0.03,0.14,n),-0.5,0.8)
humidity=np.clip(rng.normal(78,11,n),35,100)
temp=np.clip(rng.normal(29,3.5,n),18,40)
sit=rng.choice([1,2,3,4,5],n,p=[.55,.18,.12,.10,.05])
over=(sit==5).astype(int)*rng.integers(1,4,n)
warning=((sit>=3).astype(int)*rng.integers(0,4,n))
critical=((sit>=4).astype(int)*rng.integers(0,3,n))
score=(r1*.35+r24*.18+r3*.10+r7*.035+water*24+trend*55+humidity*.20+(sit-1)*18+over*55+warning*8+critical*18-temp*0.6+rng.normal(0,7,n))
risk=np.select([score<65,score<120],["LOW","MEDIUM"],default="HIGH")
df=pd.DataFrame({"Rainfall_1h_mm":r1.round(2),"Rainfall_24h_mm":r24.round(2),"Rainfall_3d_mm":r3.round(2),"Rainfall_7d_mm":r7.round(2),"Water_Level_m":water.round(2),"Water_Trend_m":trend.round(3),"Humidity_percent":humidity.round(2),"Temperature_C":temp.round(2),"Max_Situation_Level":sit,"Overbank_Count":over,"Warning_Station_Count":warning,"Critical_Station_Count":critical,"Risk":risk})
Path("data").mkdir(exist_ok=True); df.to_csv("data/flood_data.csv",index=False)
print(len(df)); print(df["Risk"].value_counts())
