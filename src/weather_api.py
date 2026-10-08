import requests
from datetime import datetime

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

# Representative coordinates for 77 Thai provinces. Used only for Open-Meteo weather grid lookup.
PROVINCES = {
    "กรุงเทพมหานคร": (13.7563, 100.5018), "กระบี่": (8.0863, 98.9063), "กาญจนบุรี": (14.0228, 99.5328),
    "กาฬสินธุ์": (16.4314, 103.5059), "กำแพงเพชร": (16.4828, 99.5227), "ขอนแก่น": (16.4322, 102.8236),
    "จันทบุรี": (12.6113, 102.1038), "ฉะเชิงเทรา": (13.6904, 101.0779), "พระนครศรีอยุธยา": (14.3532, 100.5689), "ชลบุรี": (13.3611, 100.9847),
    "ชัยนาท": (15.1852, 100.1251), "ชัยภูมิ": (15.8068, 102.0310), "ชุมพร": (10.4930, 99.1800),
    "ตรัง": (7.5594, 99.6114), "ตราด": (12.2428, 102.5175), "ตาก": (16.8830, 99.1258),
    "นครนายก": (14.2069, 101.2131), "นครปฐม": (13.8199, 100.0622), "นครพนม": (17.3920, 104.7695),
    "นครราชสีมา": (14.9799, 102.0977), "นครศรีธรรมราช": (8.4304, 99.9631), "นครสวรรค์": (15.7047, 100.1372),
    "นนทบุรี": (13.8621, 100.5144), "นราธิวาส": (6.4255, 101.8253), "น่าน": (18.7756, 100.7730),
    "บึงกาฬ": (18.3609, 103.6464), "บุรีรัมย์": (14.9930, 103.1029), "ปทุมธานี": (14.0208, 100.5250),
    "ประจวบคีรีขันธ์": (11.8100, 99.7971), "ปราจีนบุรี": (14.0500, 101.3700), "ปัตตานี": (6.8698, 101.2500),
    "พะเยา": (19.1664, 99.9019), "พังงา": (8.4509, 98.5255), "พัทลุง": (7.6167, 100.0740),
    "พิจิตร": (16.4420, 100.3488), "พิษณุโลก": (16.8211, 100.2659), "ภูเก็ต": (7.8804, 98.3923),
    "มหาสารคาม": (16.1851, 103.3020), "มุกดาหาร": (16.5453, 104.7235), "ยะลา": (6.5411, 101.2804),
    "ยโสธร": (15.7926, 104.1453), "ร้อยเอ็ด": (16.0538, 103.6520), "ระนอง": (9.9529, 98.6085),
    "ระยอง": (12.6814, 101.2816), "ราชบุรี": (13.5283, 99.8134), "ลพบุรี": (14.7995, 100.6534),
    "ลำปาง": (18.2888, 99.4909), "ลำพูน": (18.5745, 99.0087), "ศรีสะเกษ": (15.1186, 104.3220),
    "สกลนคร": (17.1546, 104.1348), "สงขลา": (7.1898, 100.5954), "สตูล": (6.6238, 100.0674),
    "สมุทรปราการ": (13.5991, 100.5998), "สมุทรสงคราม": (13.4098, 99.9925), "สมุทรสาคร": (13.5475, 100.2744),
    "สระบุรี": (14.5289, 100.9101), "สระแก้ว": (13.8240, 102.0645), "สิงห์บุรี": (14.8936, 100.3967),
    "สุพรรณบุรี": (14.4745, 100.1177), "สุราษฎร์ธานี": (9.1382, 99.3217), "สุรินทร์": (14.8818, 103.4936),
    "สุโขทัย": (17.0078, 99.8265), "หนองคาย": (17.8783, 102.7413), "หนองบัวลำภู": (17.2041, 102.4407),
    "อำนาจเจริญ": (15.8657, 104.6258), "อุดรธานี": (17.4138, 102.7875), "อุตรดิตถ์": (17.6201, 100.0993),
    "อุทัยธานี": (15.3835, 100.0246), "อุบลราชธานี": (15.2287, 104.8564), "อ่างทอง": (14.5896, 100.4551),
    "เชียงราย": (19.9105, 99.8406), "เชียงใหม่": (18.7883, 98.9853), "เพชรบุรี": (13.1119, 99.9398),
    "เพชรบูรณ์": (16.4190, 101.1606), "เลย": (17.4860, 101.7223), "แพร่": (18.1446, 100.1403),
    "แม่ฮ่องสอน": (19.3010, 97.9685),
}
PROVINCES = dict(sorted(PROVINCES.items()))

THAIWATER_BASE = "https://api-v3.thaiwater.net/api/v1/thaiwater30"

# Official Thai province codes used by ThaiWater filtering.
PROVINCE_CODES = {
"กรุงเทพมหานคร":10,"สมุทรปราการ":11,"นนทบุรี":12,"ปทุมธานี":13,"พระนครศรีอยุธยา":14,"อ่างทอง":15,"ลพบุรี":16,"สิงห์บุรี":17,"ชัยนาท":18,"สระบุรี":19,"ชลบุรี":20,"ระยอง":21,"จันทบุรี":22,"ตราด":23,"ฉะเชิงเทรา":24,"ปราจีนบุรี":25,"นครนายก":26,"สระแก้ว":27,"นครราชสีมา":30,"บุรีรัมย์":31,"สุรินทร์":32,"ศรีสะเกษ":33,"อุบลราชธานี":34,"ยโสธร":35,"ชัยภูมิ":36,"อำนาจเจริญ":37,"บึงกาฬ":38,"หนองบัวลำภู":39,"ขอนแก่น":40,"อุดรธานี":41,"เลย":42,"หนองคาย":43,"มหาสารคาม":44,"ร้อยเอ็ด":45,"กาฬสินธุ์":46,"สกลนคร":47,"นครพนม":48,"มุกดาหาร":49,"เชียงใหม่":50,"ลำพูน":51,"ลำปาง":52,"อุตรดิตถ์":53,"แพร่":54,"น่าน":55,"พะเยา":56,"เชียงราย":57,"แม่ฮ่องสอน":58,"นครสวรรค์":60,"อุทัยธานี":61,"กำแพงเพชร":62,"ตาก":63,"สุโขทัย":64,"พิษณุโลก":65,"พิจิตร":66,"เพชรบูรณ์":67,"ราชบุรี":70,"กาญจนบุรี":71,"สุพรรณบุรี":72,"สมุทรสงคราม":73,"เพชรบุรี":76,"ประจวบคีรีขันธ์":77,"นครปฐม":73,"สมุทรสาคร":74,"สุราษฎร์ธานี":84,"ระนอง":85,"ชุมพร":86,"สงขลา":90,"สตูล":91,"ตรัง":92,"พัทลุง":93,"ปัตตานี":94,"ยะลา":95,"นราธิวาส":96,"ภูเก็ต":83,"กระบี่":81,"พังงา":82,"นครศรีธรรมราช":80
}
# Correct duplicate/overlap for western codes where needed.
PROVINCE_CODES.update({"นครปฐม":73,"สมุทรสาคร":74,"สมุทรสงคราม":75,"เพชรบุรี":76,"ประจวบคีรีขันธ์":77})

HEADERS={"Accept":"application/json","User-Agent":"KKU-Smart-Flood-AI/3.0","Referer":"https://www.thaiwater.net/"}

def _get_json(path, params=None):
    r=requests.get(f"{THAIWATER_BASE}{path}",params=params,headers=HEADERS,timeout=25)
    r.raise_for_status()
    return r.json()

def _rows(payload):
    if isinstance(payload,dict):
        for key in ("data","rainfall_data","waterlevel_data","result"):
            v=payload.get(key)
            if isinstance(v,list): return v
            if isinstance(v,dict) and isinstance(v.get("data"),list): return v["data"]
    return []

def _province_name(row):
    g=row.get("geocode") or {}
    p=g.get("province_name") or row.get("province_name") or {}
    if isinstance(p,dict): return p.get("th") or p.get("en") or ""
    return str(p)

def _num(v):
    try: return float(v)
    except (TypeError,ValueError): return None

def fetch_thaiwater(province):
    code=PROVINCE_CODES.get(province)
    if not code: raise ValueError(f"ไม่มีรหัส ThaiWater สำหรับ {province}")
    rain_rows=_rows(_get_json("/public/rain_24h", {"province_code":code}))
    rain_rows=[r for r in rain_rows if _province_name(r)==province or not _province_name(r)]
    r24=[_num(r.get("rain_24h")) for r in rain_rows]
    r1=[_num(r.get("rain_1h")) for r in rain_rows]
    r24=[x for x in r24 if x is not None]; r1=[x for x in r1 if x is not None]
    # 3d/7d endpoints are currently documented by ThaiWater but can temporarily return empty.
    rain3_rows=_rows(_get_json("/provinces/rain3d"))
    rain7_rows=_rows(_get_json("/provinces/rain7d"))
    def acc(rows,key):
        vals=[_num(r.get(key)) for r in rows if (_province_name(r)==province or not _province_name(r))]
        vals=[x for x in vals if x is not None]
        return max(vals) if vals else None
    r3=acc(rain3_rows,"rain_3d"); r7=acc(rain7_rows,"rain_7d")

    wl_rows=_rows(_get_json("/public/waterlevel_load"))
    wl_rows=[r for r in wl_rows if _province_name(r)==province]
    levels=[]; trends=[]; overbank=0; warning=0; critical=0; stations=[]
    for r in wl_rows:
        st=r.get("station") or {}
        name=st.get("tele_station_name") or {}
        name=name.get("th") if isinstance(name,dict) else str(name)
        level=_num(r.get("waterlevel_msl")); prev=_num(r.get("waterlevel_msl_previous"))
        if level is not None: levels.append(level)
        if level is not None and prev is not None: trends.append(level-prev)
        diff_text=str(r.get("diff_wl_bank_text") or "")
        sit=_num(r.get("situation_level")) or 0
        if "ล้นตลิ่ง" in diff_text: overbank += 1
        if sit >= 3: warning += 1
        if sit >= 4: critical += 1
        if level is not None:
            stations.append({"station":name or "ไม่ระบุชื่อสถานี","level_msl":level,"trend_m":(level-prev if level is not None and prev is not None else None),"situation_level":int(sit) if sit else None,"bank_status":diff_text or "ไม่ระบุ"})
    max_level=max(levels) if levels else None
    avg_level=sum(levels)/len(levels) if levels else None
    max_trend=max(trends) if trends else 0.0
    max_sit=max([s["situation_level"] or 0 for s in stations], default=0)
    # Choose a representative level: highest latest MSL station in the province.
    return {
      "province":province,"province_code":code,"rainfall_1h":max(r1) if r1 else 0.0,"rainfall_24h":max(r24) if r24 else 0.0,
      "rainfall_3d":r3,"rainfall_7d":r7,"rain_station_count":len(rain_rows),
      "water_level_m":max_level,"water_level_avg_m":avg_level,"water_trend_m":max_trend,"water_station_count":len(stations),
      "overbank_count":overbank,"warning_station_count":warning,"critical_station_count":critical,"max_situation_level":max_sit,
      "water_stations":sorted(stations,key=lambda x:x["level_msl"],reverse=True)[:20],
      "updated_at":datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %z")
    }

def fetch_weather(province):
    if province not in PROVINCES: raise ValueError("ไม่พบจังหวัดที่เลือก")
    lat,lon=PROVINCES[province]
    params={"latitude":lat,"longitude":lon,"current":"temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m","timezone":"Asia/Bangkok"}
    r=requests.get(OPEN_METEO_URL,params=params,timeout=15); r.raise_for_status(); d=r.json(); c=d.get("current",{})
    return {"province":province,"latitude":lat,"longitude":lon,"temperature":float(c.get("temperature_2m",0)),"humidity":float(c.get("relative_humidity_2m",0)),"current_precipitation":float(c.get("precipitation",0)),"wind_speed":float(c.get("wind_speed_10m",0)),"updated_at":c.get("time",datetime.now().isoformat())}


def weather_code_thai(code):
    """Translate WMO weather codes to Thai labels/icons."""
    try:
        code=int(code)
    except (TypeError, ValueError):
        return "สภาพอากาศไม่ทราบ", "🌤️"
    mapping={
        0:("ท้องฟ้าแจ่มใส","☀️"),1:("แจ่มใสเป็นส่วนใหญ่","🌤️"),2:("มีเมฆบางส่วน","⛅"),3:("มีเมฆมาก","☁️"),
        45:("มีหมอก","🌫️"),48:("มีหมอกเกาะตัว","🌫️"),51:("ฝนปรอยเล็กน้อย","🌦️"),53:("ฝนปรอยปานกลาง","🌦️"),55:("ฝนปรอยหนาแน่น","🌧️"),
        56:("ฝนเยือกแข็งเล็กน้อย","🌧️"),57:("ฝนเยือกแข็งหนาแน่น","🌧️"),61:("ฝนตกเล็กน้อย","🌧️"),63:("ฝนตกปานกลาง","🌧️"),65:("ฝนตกหนัก","🌧️"),
        66:("ฝนเยือกแข็งเล็กน้อย","🌧️"),67:("ฝนเยือกแข็งหนัก","🌧️"),71:("หิมะตกเล็กน้อย","🌨️"),73:("หิมะตกปานกลาง","🌨️"),75:("หิมะตกหนัก","❄️"),
        77:("เกล็ดหิมะ","❄️"),80:("ฝนซู่เล็กน้อย","🌦️"),81:("ฝนซู่ปานกลาง","🌧️"),82:("ฝนซู่หนัก","⛈️"),85:("หิมะซู่เล็กน้อย","🌨️"),
        86:("หิมะซู่หนัก","❄️"),95:("พายุฝนฟ้าคะนอง","⛈️"),96:("พายุฝนฟ้าคะนอง มีลูกเห็บ","⛈️"),99:("พายุฝนฟ้าคะนองรุนแรง","⛈️")
    }
    return mapping.get(code,("สภาพอากาศไม่ทราบ","🌤️"))


def fetch_weather_forecast_7days(province):
    """Fetch today plus the next 6 days for the selected Thai province."""
    if province not in PROVINCES:
        raise ValueError("ไม่พบจังหวัดที่เลือก")
    lat,lon=PROVINCES[province]
    params={
        "latitude":lat,"longitude":lon,
        "daily":"weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,rain_sum,precipitation_probability_max,wind_speed_10m_max",
        "forecast_days":7,"timezone":"Asia/Bangkok"
    }
    r=requests.get(OPEN_METEO_URL,params=params,timeout=20); r.raise_for_status()
    daily=r.json().get("daily") or {}
    dates=daily.get("time") or []
    n=min(7,len(dates))
    if n==0: raise RuntimeError("Open-Meteo ไม่ส่งข้อมูลพยากรณ์ 7 วัน")
    thai_days=["จันทร์","อังคาร","พุธ","พฤหัสบดี","ศุกร์","เสาร์","อาทิตย์"]
    def arr(k): return daily.get(k) or []
    out=[]
    for i in range(n):
        code=(arr("weather_code")[i] if i<len(arr("weather_code")) else None)
        desc,icon=weather_code_thai(code)
        try:
            from datetime import date as _date
            day_name=thai_days[_date.fromisoformat(str(dates[i])).weekday()]
        except Exception: day_name=""
        def val(key,default=None):
            a=arr(key); return a[i] if i<len(a) else default
        out.append({
            "date":str(dates[i]),"day_name":day_name,"label":"วันนี้" if i==0 else day_name,
            "icon":icon,"description":desc,"weather_code":code,
            "temp_max":float(val("temperature_2m_max",0)) if val("temperature_2m_max") is not None else None,
            "temp_min":float(val("temperature_2m_min",0)) if val("temperature_2m_min") is not None else None,
            "precipitation_mm":float(val("precipitation_sum",0) or 0),
            "rain_mm":float(val("rain_sum",0) or 0),
            "rain_probability":float(val("precipitation_probability_max",0)) if val("precipitation_probability_max") is not None else None,
            "wind_max_kmh":float(val("wind_speed_10m_max",0)) if val("wind_speed_10m_max") is not None else None
        })
    return {"province":province,"latitude":lat,"longitude":lon,"forecast":out,"updated_at":datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %z"),"source":"Open-Meteo"}

def fetch_province_data(province):
    rain=fetch_thaiwater(province)
    weather=fetch_weather(province)
    rain.update(weather)
    return rain

def _coords_from_row(row):
    """Read ThaiWater coordinates from common field-name variants."""
    station = row.get("station") or {}
    station_info = row.get("station_info") or row.get("stationInfo") or {}
    candidates = [row, station, station_info]

    lat_keys = ("lat", "latitude", "Latitude", "LAT")
    lon_keys = ("lon", "long", "longitude", "Longitude", "LONG")

    lat = lon = None
    for obj in candidates:
        if not isinstance(obj, dict):
            continue
        if lat is None:
            for k in lat_keys:
                lat = _num(obj.get(k))
                if lat is not None:
                    break
        if lon is None:
            for k in lon_keys:
                lon = _num(obj.get(k))
                if lon is not None:
                    break
        if lat is not None and lon is not None:
            break

    # Some ThaiWater payloads place coordinates under geocode/station metadata.
    if lat is None or lon is None:
        geo = row.get("geocode") or {}
        for obj in (geo,):
            if isinstance(obj, dict):
                if lat is None:
                    for k in lat_keys:
                        lat = _num(obj.get(k))
                        if lat is not None:
                            break
                if lon is None:
                    for k in lon_keys:
                        lon = _num(obj.get(k))
                        if lon is not None:
                            break
    return lat, lon

def _extract_rid_rows(payload):
    """Normalize RID SWOC rainfall-24h payloads from common response shapes."""
    if isinstance(payload, list):
        return payload
    if not isinstance(payload, dict):
        return []
    for key in ("data", "result", "items", "results", "records"):
        value = payload.get(key)
        if isinstance(value, list):
            return value
        if isinstance(value, dict):
            nested = _extract_rid_rows(value)
            if nested:
                return nested
    return []

def _first_value(obj, keys):
    if not isinstance(obj, dict):
        return None
    for k in keys:
        v = obj.get(k)
        if v is not None and v != "":
            return v
    return None

def _rid_rain_point(row):
    """Map common RID/HII station field names into our map format."""
    if not isinstance(row, dict):
        return None
    # Coordinates may be directly on the row or nested in station/location metadata.
    candidates = [row, row.get("station") or {}, row.get("station_info") or {}, row.get("location") or {}, row.get("stationLocation") or {}]
    lat = lon = None
    for obj in candidates:
        if lat is None:
            lat = _num(_first_value(obj, ("lat", "latitude", "Latitude", "LAT")))
        if lon is None:
            lon = _num(_first_value(obj, ("lon", "long", "longitude", "Longitude", "LONG")))
        if lat is not None and lon is not None:
            break
    if lat is None or lon is None:
        return None

    value = _num(_first_value(row, ("rain_24h", "rain24h", "rainfall_24h", "rainfall24h", "rainfall", "value", "rain")))
    if value is None:
        return None

    station = row.get("station") or {}
    name = _first_value(row, ("station_name", "stationName", "name", "stationname"))
    if name is None and isinstance(station, dict):
        name = _first_value(station, ("station_name", "stationName", "name", "tele_station_name"))
    province = _first_value(row, ("province", "province_name", "provinceName"))
    if isinstance(province, dict):
        province = _first_value(province, ("th", "name", "province_name"))
    if province is None:
        province = _province_name(row)
    tm = _first_value(row, ("datetime", "date_time", "rainfall_datetime", "rainfallDateTime", "timestamp", "time")) or ""
    if isinstance(tm, dict):
        tm = _first_value(tm, ("value", "datetime", "date_time")) or ""

    if not (5.0 <= lat <= 21.5 and 97.0 <= lon <= 106.5):
        return None
    return {"lat": lat, "lon": lon, "rain_24h": value, "station": str(name or "สถานีไม่ระบุ"), "province": str(province or "ไม่ระบุ"), "time": str(tm)}

def _fetch_rain_map_rid():
    """Primary map source: RID SWOC/HII proxy, rainfall accumulated over 24h."""
    url = "https://swoc-api-service.rid.go.th/api/rainfall-hii-24hr/"
    r = requests.get(url, timeout=20, headers={"User-Agent": "KKU-Smart-Flood-AI/3.2"})
    r.raise_for_status()
    rows = _extract_rid_rows(r.json())
    points = []
    for row in rows:
        p = _rid_rain_point(row)
        if p:
            points.append(p)
    if not points:
        raise RuntimeError("RID SWOC API ตอบกลับสำเร็จ แต่ไม่พบข้อมูลสถานี/พิกัดฝน 24 ชั่วโมง")
    return points

def _fetch_rain_map_open_meteo():
    """Reliable fallback map: 24h accumulated precipitation at 77 provincial points."""
    names=list(PROVINCES.keys())
    lats=[PROVINCES[n][0] for n in names]
    lons=[PROVINCES[n][1] for n in names]
    params={
        "latitude": ",".join(str(x) for x in lats),
        "longitude": ",".join(str(x) for x in lons),
        "hourly": "precipitation",
        "past_days": 1,
        "forecast_days": 0,
        "timezone": "Asia/Bangkok"
    }
    r=requests.get(OPEN_METEO_URL, params=params, timeout=30)
    r.raise_for_status()
    payload=r.json()
    if not isinstance(payload,list):
        payload=[payload]
    points=[]
    for i, item in enumerate(payload[:len(names)]):
        hourly=item.get("hourly",{}) if isinstance(item,dict) else {}
        times=hourly.get("time",[]) or []
        vals=hourly.get("precipitation",[]) or []
        pairs=[]
        for t,v in zip(times,vals):
            x=_num(v)
            if x is not None:
                pairs.append((t,x))
        if not pairs:
            continue
        # Use the latest 24 hourly observations returned by Open-Meteo.
        last24=pairs[-24:]
        total=sum(v for _,v in last24)
        name=names[i]
        lat,lon=PROVINCES[name]
        points.append({
            "lat":lat,"lon":lon,"rain_24h":total,
            "station":f"จุดตัวแทนจังหวัด {name}","province":name,
            "time":last24[-1][0],"source":"Open-Meteo (จังหวัดตัวแทน)"
        })
    if not points:
        raise RuntimeError("Open-Meteo ไม่พบข้อมูลฝนย้อนหลัง 24 ชั่วโมง")
    return points


def fetch_rain_map():
    """Fetch a 24h rain map using multiple public sources, with a guaranteed weather fallback."""
    errors=[]
    try:
        points=_fetch_rain_map_rid()
        for p in points: p["source"]="RID SWOC / HII"
        return points
    except Exception as e:
        errors.append("RID SWOC: "+str(e))

    try:
        rows=_rows(_get_json("/public/rain_24h"))
        points=[]
        for r in rows:
            lat,lon=_coords_from_row(r); val=_num(r.get("rain_24h"))
            if lat is None or lon is None or val is None: continue
            st=r.get("station") or {}
            nm=st.get("tele_station_name") or r.get("station_name") or ""
            nm=nm.get("th") if isinstance(nm,dict) else str(nm)
            if not (5.0<=lat<=21.5 and 97.0<=lon<=106.5): continue
            points.append({"lat":lat,"lon":lon,"rain_24h":val,"station":nm or "สถานีไม่ระบุ","province":_province_name(r),"time":r.get("rainfall_datetime") or r.get("rainfall_time") or r.get("timestamp") or "","source":"ThaiWater"})
        if points: return points
        raise RuntimeError("ThaiWater ไม่พบข้อมูลพิกัดสถานี")
    except Exception as e:
        errors.append("ThaiWater: "+str(e))

    try:
        return _fetch_rain_map_open_meteo()
    except Exception as e:
        errors.append("Open-Meteo: "+str(e))
        raise RuntimeError("ไม่สามารถโหลดแผนที่ฝนได้ | " + " | ".join(errors))
