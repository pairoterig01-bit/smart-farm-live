import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# 1. การตั้งค่าหน้าจอและสไตล์ (Dark Mode เหมือน index.html)
st.set_page_config(page_title="Smart Farm Dashboard", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #121212; color: #e0e0e0; }
    div[data-testid="stMetric"] {
        background-color: #1e1e1e;
        border: 1px solid #333;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
    }
    label[data-testid="stMetricLabel"] { color: #e0e0e0 !important; font-size: 1.2rem !important; }
    div[data-testid="stMetricValue"] { color: #ffffff !important; }
    </style>
    """, unsafe_allow_index=True)

st.title("🌱 ระบบติดตามฟาร์มอัจฉริยะ (Live Dashboard)")

# 2. เชื่อมต่อข้อมูลจาก Google Sheets (อ้างอิงจากไฟล์เดิมของคุณ)
sheet_url = "https://docs.google.com/spreadsheets/d/1mFHJgSss6ofUTghbaEgy6Po2032DMZ3cd_gzPd04Cf4/edit?usp=sharing"
csv_url = sheet_url.replace('/edit?usp=sharing', '/export?format=csv')

@st.cache_data(ttl=30) # อัปเดตทุก 30 วินาที
def load_data():
    df = pd.read_csv(csv_url)
    df.columns = [col.strip().lower() for col in df.columns] # ล้างชื่อคอลัมน์
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

try:
    df = load_data()
    latest = df.iloc[-1]

    # 3. ส่วนแสดงค่าปัจจุบัน (Metrics)
    st.subheader(f"📍 ข้อมูลล่าสุดเมื่อ: {latest['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("🌡️ อุณหภูมิ", f"{float(latest['temp']):.2f} °C")
    with col2:
        st.metric("💧 ความชื้น", f"{float(latest['hum']):.2f} %")
    with col3:
        st.metric("☀️ ความเข้มแสง", f"{float(latest['lux']):.1f} Lux")

    st.divider()

    # 4. กราฟอุณหภูมิและความชื้น (แยกสีตาม index.html เดิม)
    st.subheader("📊 กราฟอุณหภูมิและความชื้น")
    fig_temp_hum = go.Figure()
    fig_temp_hum.add_trace(go.Scatter(x=df['timestamp'], y=df['temp'], name='อุณหภูมิ (°C)',
                         line=dict(color='#ff4b4b', width=2)))
    fig_temp_hum.add_trace(go.Scatter(x=df['timestamp'], y=df['hum'], name='ความชื้น (%)',
                         line=dict(color='#00a2ff', width=2)))
    
    fig_temp_hum.update_layout(
        template="plotly_dark",
        margin=dict(l=20, r=20, t=20, b=20),
        hovermode="x unified",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig_temp_hum, use_container_width=True)

    # 5. กราฟความเข้มแสง (สีเหลืองแบบ Area Chart ตามรูป)
    st.subheader("☀️ กราฟความเข้มแสง (Lux)")
    fig_lux = go.Figure()
    fig_lux.add_trace(go.Scatter(x=df['timestamp'], y=df['lux'], name='Lux',
                         fill='tozeroy', line=dict(color='#ffcc00', width=1),
                         fillcolor='rgba(255, 204, 0, 0.1)'))
    
    fig_lux.update_layout(
        template="plotly_dark",
        margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig_lux, use_container_width=True)

except Exception as e:
    st.error(f"⚠️ เกิดข้อผิดพลาดในการโหลดข้อมูล: {e}")
