from pathlib import Path
import joblib,pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score,classification_report,confusion_matrix
from sklearn.model_selection import train_test_split

features=["Rainfall_1h_mm","Rainfall_24h_mm","Rainfall_3d_mm","Rainfall_7d_mm","Water_Level_m","Water_Trend_m","Humidity_percent","Temperature_C","Max_Situation_Level","Overbank_Count","Warning_Station_Count","Critical_Station_Count"]
df=pd.read_csv("data/flood_data.csv"); X,y=df[features],df["Risk"]
Xtr,Xte,ytr,yte=train_test_split(X,y,test_size=.2,random_state=42,stratify=y)
model=RandomForestClassifier(n_estimators=250,max_depth=12,min_samples_leaf=2,random_state=42,class_weight="balanced_subsample",n_jobs=-1); model.fit(Xtr,ytr)
pred=model.predict(Xte); acc=accuracy_score(yte,pred); cm=confusion_matrix(yte,pred,labels=["LOW","MEDIUM","HIGH"])
print(f"Accuracy: {acc:.4f}"); print(classification_report(yte,pred)); print(cm)
Path("models").mkdir(exist_ok=True); joblib.dump({"model":model,"features":features,"classes":list(model.classes_),"accuracy":acc,"confusion_matrix":cm.tolist(),"version":"3.0"},"models/flood_model.pkl")
