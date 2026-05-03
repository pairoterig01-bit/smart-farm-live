import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime
import pytz

# --- 1. การตั้งค่าหน้าจอ ---
st.set_page_config(page_title="Smart Farm", layout="wide")

# กำหนดเขตเวลาประเทศไทย
tz_thai = pytz.timezone('Asia/Bangkok')

# --- 2. CSS ปรับแต่ง (คงเดิม) ---
st.markdown("""
<style>
    .block-container { padding-top: 2rem !important; padding-bottom: 1rem !important; }
    [data-testid="stMetric"] { 
        padding: 8px 12px !important; 
        border-left: 20px solid #4E4E4E; 
        background: rgba(255,255,255,0.03);
    }
    div[data-testid="stMetricValue"] { font-size: 20px !important; }
    div.stAlert { padding: 0px 20px !important; min-height: auto !important; margin-top: 0px !important; }
    div.stAlert p { font-size: 20px !important; margin: 0 !important; }
</style>
""", unsafe_allow_html=True)

# --- 3. การเชื่อมต่อและจัดการข้อมูล ---
sheet_url = "https://docs.google.com/spreadsheets/d/1mFHJgSss6ofUTghbaEgy6Po2032DMZ3cd_gzPd04Cf4/edit?usp=sharing"
csv_url = sheet_url.replace('/edit?usp=sharing', '/export?format=csv')

@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv(csv_url)
    df.columns = [str(col).strip().lower() for col in df.columns]
    
    # อ่านวันที่แบบ mixed เพื่อรองรับทุกรูปแบบ
    df['timestamp'] = pd.to_datetime(df['timestamp'], format='mixed')
    
    # ฟังก์ชันจัดการ Timezone ให้เป็นประเทศไทยทั้งหมดโดยไม่บวกเวลาซ้ำซ้อน
    def standardize_tz(dt):
        if dt.tzinfo is not None:
            # ถ้ามีโซนเวลา (เช่น ISO ที่มี Z) ให้แปลงเป็นเวลาไทย
            return dt.astimezone(tz_thai)
        # ถ้าไม่มีโซนเวลา (เช่น 9:30:54 ที่บันทึกใหม่) ให้กำหนดเป็นเวลาไทยทันที
        return tz_thai.localize(dt)

    df['timestamp'] = df['timestamp'].apply(standardize_tz)
    
    # เรียงลำดับข้อมูลจากเก่าไปใหม่
    df = df.sort_values('timestamp').reset_index(drop=True)
    return df

try:
    all_data = load_data()
    # ดึงวันที่ล่าสุดที่มีข้อมูลจริง
    latest_date_in_data = all_data['timestamp'].max().date()

    st.subheader("🌱 Smart Farm")
    
    head_c1, head_c2 = st.columns([1, 2], gap="small")
    with head_c1:
        selected_date = st.date_input("Date", value=latest_date_in_data, label_visibility="collapsed")
    
    # กรองข้อมูลตามวันที่เลือก
    data = all_data[all_data['timestamp'].dt.date == selected_date]

    with head_c2:
        if not data.empty:
            latest = data.iloc[-1]
            # แสดงเวลาให้ตรงกับใน Sheet
            st.info(f"🕒 {latest['timestamp'].strftime('%H:%M:%S')} (พ.ศ. {latest['timestamp'].year + 543})")
        else:
            st.warning(f"ไม่มีข้อมูลของวันที่ {selected_date.strftime('%d/%m/%Y')}")

    if not data.empty:
        # --- Metrics ---
        m1, m2, m3 = st.columns(3)
        m1.metric("🌡️ Temp", f"{float(latest['temp']):.2f}°C")
        m2.metric("💧 Hum", f"{float(latest['hum']):.2f}%")
        m3.metric("☀️ Lux", f"{float(latest['lux']):.2f}")

        # --- กราฟรวม ---
        fig1 = make_subplots(specs=[[{"secondary_y": True}]])
        fig1.add_trace(go.Scatter(x=data['timestamp'], y=data['temp'], name="Temp", line=dict(color="#FF4B4B", width=2)), secondary_y=False)
        fig1.add_trace(go.Scatter(x=data['timestamp'], y=data['hum'], name="Hum", line=dict(color="#00D2FF", width=2)), secondary_y=True)

        fig1.update_layout(
            template="plotly_dark", height=280, 
            margin=dict(l=10, r=10, t=10, b=10),
            hovermode="x unified", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            showlegend=True, dragmode=False,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig1, use_container_width=True, config={'displayModeBar': False})

        # --- กราฟ Lux ---
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=data['timestamp'], y=data['lux'], fill='tozeroy', line=dict(color="#FFCC00", width=1.5), fillcolor='rgba(255, 204, 0, 0.1)'))
        fig2.update_layout(template="plotly_dark", height=160, margin=dict(l=10, r=10, t=10, b=10), dragmode=False)
        st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})

except Exception as e:
    st.error(f"Error: {e}")
