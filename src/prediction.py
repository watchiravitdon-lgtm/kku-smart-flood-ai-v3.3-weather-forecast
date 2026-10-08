import joblib
import pandas as pd

def load_model():
    return joblib.load("models/flood_model.pkl")

def predict_risk(data):
    bundle=load_model(); model=bundle["model"]; features=bundle["features"]
    X=pd.DataFrame([{f:float(data.get(f,0) or 0) for f in features}])
    pred=model.predict(X)[0]
    proba=model.predict_proba(X)[0]
    return pred,{c:float(v) for c,v in zip(model.classes_,proba)}

def apply_realtime_safety_layer(prediction, probabilities, data):
    # The ML model is a prototype. Real-time ThaiWater alert evidence must never be ignored.
    p=dict(probabilities)
    reasons=[]
    over=int(data.get("overbank_count") or 0)
    crit=int(data.get("critical_station_count") or 0)
    warn=int(data.get("warning_station_count") or 0)
    sit=int(data.get("max_situation_level") or 0)
    r24=float(data.get("rainfall_24h") or 0)
    r3=float(data.get("rainfall_3d") or 0) if data.get("rainfall_3d") is not None else 0
    trend=float(data.get("water_trend_m") or 0)
    final=prediction
    # Conservative real-time escalation: over-bank or critical station => HIGH.
    if over>0 or sit>=5:
        final="HIGH"; reasons.append(f"พบสถานีน้ำล้นตลิ่ง {over} สถานี")
    elif crit>0 or sit>=4:
        final="HIGH"; reasons.append(f"พบสถานีระดับวิกฤต {crit} สถานี")
    elif warn>=2 or sit>=3:
        final="MEDIUM" if prediction=="LOW" else prediction; reasons.append(f"พบสถานีเฝ้าระวัง/เตือนภัย {warn} สถานี")
    if r24>=70 or (r3 and r3>=120):
        if final=="LOW": final="MEDIUM"
        reasons.append("ปริมาณฝนสะสมอยู่ในระดับสูง")
    if trend>=0.20:
        if final=="LOW": final="MEDIUM"
        reasons.append("ระดับน้ำมีแนวโน้มเพิ่มขึ้น")
    # Display probabilities after the safety layer without pretending these are pure model probabilities.
    adjusted={"LOW":p.get("LOW",0.0),"MEDIUM":p.get("MEDIUM",0.0),"HIGH":p.get("HIGH",0.0)}
    if final!=prediction:
        adjusted={k:v*0.35 for k,v in adjusted.items()}
        adjusted[final]+=0.65
    s=sum(adjusted.values()) or 1
    adjusted={k:v/s for k,v in adjusted.items()}
    return final,adjusted,reasons
