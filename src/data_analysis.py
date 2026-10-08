from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import joblib

def load_data(): return pd.read_csv("data/flood_data.csv")

def feature_importance():
    b=joblib.load("models/flood_model.pkl"); m=b["model"]
    return pd.DataFrame({"Feature":b["features"],"Importance":m.feature_importances_}).sort_values("Importance",ascending=False)

def create_feature_importance_chart():
    imp=feature_importance().sort_values("Importance")
    Path("images").mkdir(exist_ok=True)
    plt.figure(figsize=(8,5)); plt.barh(imp["Feature"],imp["Importance"]); plt.xlabel("Importance"); plt.title("AI Feature Importance"); plt.tight_layout(); plt.savefig("images/feature_importance.png",dpi=160); plt.close()
