import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime
import pytz

# --- 1. การตั้งค่าหน้าจอ ---
st.set_page_config(page_title="Smart Farm", layout="wide")

# ล็อคเขตเวลาสำหรับแสดงผลเป็นประเทศไทย
tz_thai = pytz.timezone('Asia/Bangkok')

# --- 2. การเชื่อมต่อและแปลงข้อมูล ---
sheet_url = "https://docs.google.com/spreadsheets/d/1mFHJgSss6ofUTghbaEgy6Po2032DMZ3cd_gzPd04Cf4/edit?usp=sharing"
csv_url = sheet_url.replace('/edit?usp=sharing', '/export?format=csv')

@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv(csv_url)
    df.columns = [str(col).strip().lower() for col in df.columns]
    
    # แก้ไขบรรทัดนี้: ใช้ format='mixed' เพื่อให้อ่านได้ทุกรูปแบบ
    df['timestamp'] = pd.to_datetime(df['timestamp'], format='mixed')
    
    # ตรวจสอบและแปลง Timezone
    if df['timestamp'].dt.tz is None:
        # ถ้าไม่มีโซนเวลา (แบบเก่า) ให้ถือว่าเป็น UTC ก่อน
        df['timestamp'] = df['timestamp'].dt.tz_localize('UTC')
    
    # แปลงเป็นเวลาไทยเสมอสำหรับการแสดงผล
    df['timestamp'] = df['timestamp'].dt.tz_convert('Asia/Bangkok')
        
    return df

try:
    all_data = load_data()
    
    # ดึงวันที่ปัจจุบันของไทยเพื่อเป็นค่าเริ่มต้นในปฏิทิน
    today_th = datetime.datetime.now(tz_thai).date()

    st.subheader("🌱 Smart Farm")
    
    head_c1, head_c2 = st.columns([1, 2], gap="small")
    with head_c1:
        # ปฏิทินจะแสดงวันที่ปัจจุบันของไทยเสมอ
        selected_date = st.date_input("Date", value=today_th, label_visibility="collapsed")
    
    # กรองข้อมูลตามวันที่เลือกในปฏิทิน
    data = all_data[all_data['timestamp'].dt.date == selected_date]

    with head_c2:
        if not data.empty:
            latest = data.iloc[-1]
            # แสดงเวลาไทยในแถบสถานะ
            st.info(f"🕒 {latest['timestamp'].strftime('%H:%M:%S')} (พ.ศ. {latest['timestamp'].year + 543})")
        else:
            st.warning(f"ไม่มีข้อมูลของวันที่ {selected_date.strftime('%d/%m/%Y')}")

    # ... (ส่วนการพล็อต Metric และ Graph ใช้โค้ดเดิมได้เลยครับ) ...
    if not data.empty:
        m1, m2, m3 = st.columns(3)
        m1.metric("🌡️ Temp", f"{latest['temp']:.2f}°C")
        m2.metric("💧 Hum", f"{latest['hum']:.2f}%")
        m3.metric("☀️ Lux", f"{latest['lux']:.2f}")
        
        # กราฟจะใช้แกน X เป็นเวลาไทยที่แปลงมาแล้วโดยอัตโนมัติ
        fig1 = make_subplots(specs=[[{"secondary_y": True}]])
        fig1.add_trace(go.Scatter(x=data['timestamp'], y=data['temp'], name="Temp"), secondary_y=False)
        fig1.add_trace(go.Scatter(x=data['timestamp'], y=data['hum'], name="Hum"), secondary_y=True)
        fig1.update_layout(template="plotly_dark", height=280, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig1, use_container_width=True)

except Exception as e:
    st.error(f"Error: {e}")
