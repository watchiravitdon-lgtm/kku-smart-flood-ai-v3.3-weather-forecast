from pathlib import Path
import joblib
import pandas as pd
import streamlit as st
import folium
from branca.element import Element
from streamlit_folium import st_folium

from src.prediction import predict_risk, apply_realtime_safety_layer
from src.data_analysis import load_data, feature_importance, create_feature_importance_chart
from src.weather_api import PROVINCES, fetch_province_data, fetch_rain_map, fetch_weather_forecast_7days

st.set_page_config(page_title="KKU Smart Flood AI V3", page_icon="🌊", layout="wide")
st.title("🌊 KKU Smart Flood AI")
st.subheader("ระบบ AI สำหรับประเมินความเสี่ยงน้ำท่วมจากข้อมูลฝน ระดับน้ำ และสถานีตรวจวัดจริง")
st.info("V3 เชื่อมข้อมูล ThaiWater + Open-Meteo และแสดง Weather Forecast 7 วันตามจังหวัดที่เลือก พร้อม Real-time Water Safety Layer")

if not Path("models/flood_model.pkl").exists(): st.error("ไม่พบโมเดล กรุณารัน generate_data.py และ train_model.py"); st.stop()
bundle=joblib.load("models/flood_model.pkl"); df=load_data()
if "history" not in st.session_state: st.session_state.history=[]

st.header("1. เลือกจังหวัดและอัปเดตข้อมูล API")
province=st.selectbox("จังหวัดของพื้นที่ที่ต้องการวิเคราะห์ (77 จังหวัด)",list(PROVINCES.keys()),index=list(PROVINCES.keys()).index("ฉะเชิงเทรา"))
if st.button("🔄 อัปเดตข้อมูล ThaiWater + สภาพอากาศ",use_container_width=True):
    try:
        with st.spinner(f"กำลังดึงข้อมูลล่าสุดของ {province}..."):
            st.session_state.province_data=fetch_province_data(province)
            st.session_state.weather_forecast=fetch_weather_forecast_7days(province)
            st.session_state.province_data_province=province
            st.session_state.weather_forecast_province=province
            st.session_state.api_error=None
    except Exception as e: st.session_state.api_error=str(e)
if st.session_state.get("api_error"): st.error("ดึงข้อมูล API ไม่สำเร็จ: "+st.session_state.api_error)

data=st.session_state.get("province_data")
if data and st.session_state.get("province_data_province")==province:
    c=st.columns(4)
    c[0].metric("ฝน 1 ชม.",f"{data['rainfall_1h']:.1f} mm")
    c[1].metric("ฝน 24 ชม.",f"{data['rainfall_24h']:.1f} mm")
    c[2].metric("ฝนสะสม 3 วัน",f"{data['rainfall_3d']:.1f} mm" if data['rainfall_3d'] is not None else "ไม่มีข้อมูล")
    c[3].metric("ฝนสะสม 7 วัน",f"{data['rainfall_7d']:.1f} mm" if data['rainfall_7d'] is not None else "ไม่มีข้อมูล")

    c=st.columns(4)
    c[0].metric("ระดับน้ำสูงสุด",f"{data['water_level_m']:.2f} m" if data['water_level_m'] is not None else "ไม่มีข้อมูล")
    c[1].metric("แนวโน้มระดับน้ำ",f"{data['water_trend_m']:+.2f} m")
    c[2].metric("สถานีล้นตลิ่ง",str(data['overbank_count']))
    c[3].metric("สถานีเตือน/วิกฤต",str(data['warning_station_count']))
    st.caption(f"ThaiWater: {data['water_station_count']} สถานีระดับน้ำ | อัปเดตข้อมูลเมื่อ {data['updated_at']}")
    if data['overbank_count']>0: st.error(f"⚠️ พบสถานีน้ำล้นตลิ่ง {data['overbank_count']} สถานีในจังหวัด {province}")
    elif data['critical_station_count']>0: st.warning(f"⚠️ พบสถานีระดับวิกฤต {data['critical_station_count']} สถานี")
    if data['water_stations']:
        st.subheader("สถานีระดับน้ำล่าสุด")
        st.dataframe(pd.DataFrame(data['water_stations']),use_container_width=True,hide_index=True)

    forecast=st.session_state.get("weather_forecast")
    if forecast and st.session_state.get("weather_forecast_province")==province:
        st.subheader("🌤️ Weather Forecast 7 วัน")
        st.caption(f"เริ่มจากวันนี้ • จังหวัด {province} • ข้อมูลพยากรณ์จาก Open-Meteo")
        cards=[]
        for day in forecast["forecast"]:
            tmax="-" if day["temp_max"] is None else f"{day['temp_max']:.0f}°"
            tmin="-" if day["temp_min"] is None else f"{day['temp_min']:.0f}°"
            p="-" if day["rain_probability"] is None else f"{day['rain_probability']:.0f}%"
            cards.append(f"""<div style='flex:1;min-width:135px;background:#fff;border:1px solid #d9e2ec;border-radius:12px;padding:12px 10px;text-align:center;box-shadow:0 1px 3px rgba(0,0,0,.06)'>
<div style='font-size:15px;font-weight:700;color:#17324d'>{day['label']}</div>
<div style='font-size:12px;color:#64748b'>{day['date']}</div>
<div style='font-size:34px;margin:6px 0'>{day['icon']}</div>
<div style='font-size:12px;min-height:36px;color:#334155'>{day['description']}</div>
<div style='font-size:17px;font-weight:700;margin-top:6px'>{tmax} / {tmin}C</div>
<div style='font-size:12px;color:#2563eb;margin-top:5px'>🌧️ ฝน {day['rain_mm']:.1f} mm</div>
<div style='font-size:12px;color:#475569'>โอกาสฝน {p}</div>
</div>""")
        st.markdown("<div style='display:flex;gap:10px;overflow-x:auto;padding:4px 0 12px'>"+"".join(cards)+"</div>",unsafe_allow_html=True)
else:
    st.warning("กดปุ่มอัปเดตเพื่อดึงข้อมูลล่าสุดจาก ThaiWater และ Open-Meteo")

st.header("🗺️ แผนที่ฝน 24 ชั่วโมงย้อนหลัง")

# Load automatically on the first page visit; keep the manual refresh button.
if "rain_map" not in st.session_state and "rain_map_error" not in st.session_state:
    try:
        with st.spinner("กำลังโหลดข้อมูลสถานีฝน 24 ชั่วโมงย้อนหลัง..."):
            st.session_state.rain_map=fetch_rain_map()
            st.session_state.rain_map_error=None
    except Exception as e:
        st.session_state.rain_map=[]
        st.session_state.rain_map_error=str(e)

if st.button("📍 โหลด/รีเฟรชแผนที่ฝน",use_container_width=True):
    try:
        with st.spinner("กำลังอัปเดตแผนที่ฝน 24 ชั่วโมงย้อนหลัง..."):
            st.session_state.rain_map=fetch_rain_map()
            st.session_state.rain_map_error=None
    except Exception as e:
        st.session_state.rain_map=[]
        st.session_state.rain_map_error=str(e)

if st.session_state.get("rain_map_error"):
    st.error("โหลดแผนที่ไม่สำเร็จ: "+st.session_state.rain_map_error)

points=st.session_state.get("rain_map",[])
if points:
    st.caption(f"พบจุดข้อมูลฝน {len(points):,} จุด | แหล่งข้อมูล: {points[0].get('source', 'ไม่ระบุ')}")
    m=folium.Map(location=[13.5,101.0],zoom_start=6,tiles="OpenStreetMap")
    def rain_color(v):
        if v<=10:return "blue"
        if v<=20:return "lightblue"
        if v<=35:return "green"
        if v<=50:return "yellow"
        if v<=70:return "orange"
        if v<=90:return "darkorange"
        return "red"
    for p in points:
        popup=f"<b>{p['station']}</b><br>จังหวัด: {p['province']}<br>ฝน 24 ชม.: {p['rain_24h']:.1f} mm<br>เวลา: {p['time']}"
        folium.CircleMarker([p['lat'],p['lon']],radius=5,color=rain_color(p['rain_24h']),fill=True,fill_opacity=.8,popup=folium.Popup(popup,max_width=300)).add_to(m)
    legend = """<div style='position: fixed; bottom: 20px; left: 20px; z-index: 9999; background: white; padding: 10px 12px; border: 1px solid #999; border-radius: 6px; font-size: 12px; box-shadow: 0 1px 5px rgba(0,0,0,.25)'>
    <b>เกณฑ์ฝน 24 ชม. (mm)</b><br>
    <span style='color:blue'>●</span> ≤10 &nbsp; <span style='color:lightblue'>●</span> &gt;10–20 &nbsp; <span style='color:green'>●</span> &gt;20–35 &nbsp; <span style='color:#d6b400'>●</span> &gt;35–50 &nbsp; <span style='color:orange'>●</span> &gt;50–70 &nbsp; <span style='color:darkorange'>●</span> &gt;70–90 &nbsp; <span style='color:red'>●</span> &gt;90
    </div>"""
    m.get_root().html.add_child(Element(legend))
    st_folium(m,use_container_width=True,height=620,returned_objects=[])
    sources=sorted({p.get("source", "API") for p in points})
    st.caption(f"แสดงสถานีฝน {len(points):,} สถานี | แหล่งข้อมูล: {", ".join(sources)} | จุดสีแดง/ส้มเข้มแสดงสถานีที่มีฝนสะสม 24 ชั่วโมงสูง")
else:
    st.warning("ยังไม่สามารถโหลดข้อมูลสถานีฝน 24 ชั่วโมงย้อนหลังได้")
    st.caption("แหล่งข้อมูลแผนที่: RID SWOC/HII → ThaiWater → Open-Meteo (สำรองอัตโนมัติ)")

st.header("2. AI Flood Risk Analysis")
if data and data.get("water_level_m") is not None:
    if st.button("🔎 วิเคราะห์ความเสี่ยงด้วย AI",type="primary",use_container_width=True):
        model_pred,model_probs=predict_risk(data); final,final_probs,reasons=apply_realtime_safety_layer(model_pred,model_probs,data)
        st.session_state.prediction=final; st.session_state.model_prediction=model_pred; st.session_state.probabilities=final_probs; st.session_state.reasons=reasons
        st.session_state.history.insert(0,{"จังหวัด":province,"ฝน1ชม.(mm)":data['rainfall_1h'],"ฝน24ชม.(mm)":data['rainfall_24h'],"ฝน3วัน(mm)":data['rainfall_3d'],"ระดับน้ำ(m)":data['water_level_m'],"ล้นตลิ่ง":data['overbank_count'],"AI Model":model_pred,"Final Risk":final})
else:
    st.warning("ต้องมีข้อมูลระดับน้ำจาก ThaiWater ก่อนจึงจะวิเคราะห์อัตโนมัติได้")
if "prediction" in st.session_state:
    labels={"LOW":"🟢 ความเสี่ยงต่ำ","MEDIUM":"🟡 ความเสี่ยงปานกลาง","HIGH":"🔴 ความเสี่ยงสูง"}
    st.success(f"ผลการประเมิน: {labels[st.session_state.prediction]}")
    if st.session_state.get("model_prediction")!=st.session_state.prediction:
        st.warning(f"AI Model เดิมประเมิน {st.session_state.model_prediction} แต่ Real-time Water Safety Layer ปรับเป็น {st.session_state.prediction} จากข้อมูลสถานีจริง")
    if st.session_state.get("reasons"):
        st.write("**เหตุผลจากข้อมูลปัจจุบัน:**")
        for r in st.session_state.reasons: st.write("• "+r)
    p=st.session_state.probabilities; a,b,c=st.columns(3); a.metric("LOW",f"{p.get('LOW',0)*100:.2f}%"); b.metric("MEDIUM",f"{p.get('MEDIUM',0)*100:.2f}%"); c.metric("HIGH",f"{p.get('HIGH',0)*100:.2f}%")

st.header("3. AI Model Performance")
a,b,c=st.columns(3); a.metric("Model Accuracy",f"{bundle['accuracy']*100:.2f}%"); b.metric("Decision Trees",bundle['model'].n_estimators); c.metric("Training Dataset",len(df))
st.caption("Accuracy มาจาก Synthetic Prototype Dataset ไม่ใช่ความแม่นยำที่ผ่านการรับรองจากข้อมูลน้ำท่วมจริง")

st.header("4. AI Feature Importance")
imp=feature_importance(); st.dataframe(imp.style.format({"Importance":"{:.4f}"}),use_container_width=True,hide_index=True)
if not Path("images/feature_importance.png").exists(): create_feature_importance_chart()
st.image("images/feature_importance.png",use_container_width=True)

st.header("5. วิเคราะห์ข้อมูล")
x,y=st.columns(2)
with x: st.subheader("จำนวนข้อมูลแต่ละระดับ"); st.bar_chart(df["Risk"].value_counts())
with y: st.subheader("ตัวอย่าง Training Dataset"); st.dataframe(df.head(10),use_container_width=True)

st.header("6. ประวัติการวิเคราะห์")
if st.session_state.history:
    st.dataframe(pd.DataFrame(st.session_state.history),use_container_width=True,hide_index=True)
    if st.button("ล้างประวัติ"): st.session_state.history=[]; st.rerun()
else: st.write("ยังไม่มีประวัติ")

st.header("7. แหล่งข้อมูลและข้อจำกัด")
st.markdown("""**ThaiWater** — ข้อมูลฝนและระดับน้ำจากสถานีตรวจวัดของคลังข้อมูลน้ำแห่งชาติ

**Open-Meteo** — อุณหภูมิ ความชื้น สภาพอากาศปัจจุบัน และ Weather Forecast 7 วันของพิกัดตัวแทนจังหวัด

**AI Model** — Random Forest ที่ฝึกด้วย Synthetic Prototype Dataset ที่ออกแบบให้เรียนรู้หลายตัวแปรด้านฝนและน้ำ

**Real-time Water Safety Layer** — ชั้นตรวจสอบข้อมูลสถานีจริง เช่น น้ำล้นตลิ่ง ระดับวิกฤต และแนวโน้มระดับน้ำ เพื่อไม่ให้โมเดลต้นแบบให้ LOW ทั้งที่ข้อมูลภาคสนามอยู่ในภาวะอันตราย

**ข้อจำกัด:** โปรเจกต์นี้ยังไม่ใช่ระบบเตือนภัยอย่างเป็นทางการ และโมเดลยังไม่ได้รับการ validate ด้วยชุดข้อมูลน้ำท่วมจริงในระยะยาว จึงไม่ควรใช้แทนประกาศเตือนภัยจากหน่วยงานรัฐ""")
st.warning("⚠️ ใช้เพื่อการศึกษาและพัฒนา Portfolio ไม่ใช่ระบบตัดสินใจด้านความปลอดภัยในสถานการณ์จริง")
