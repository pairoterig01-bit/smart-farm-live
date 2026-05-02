import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# 1. ตั้งค่าหน้าจอ
st.set_page_config(page_title="Smart Farm Dashboard", layout="wide")

# 2. ปรับแต่งสไตล์ (Dark Mode)
st.markdown("""
    <style>
    .main { background-color: #121212; color: #e0e0e0; }
    div[data-testid="stMetric"] {
        background-color: #1e1e1e;
        border: 1px solid #333;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
    }
    </style>
    """, unsafe_allow_index=True)

st.title("🌱 ระบบติดตามฟาร์มอัจฉริยะ (Live Dashboard)")

# 3. ลิงก์ข้อมูล (ตรวจสอบลิงก์นี้อีกทีนะครับ)
sheet_url = "https://docs.google.com/spreadsheets/d/1mFHJgSss6ofUTghbaEgy6Po2032DMZ3cd_gzPd04Cf4/edit?usp=sharing"
csv_url = sheet_url.replace('/edit?usp=sharing', '/export?format=csv')

@st.cache_data(ttl=10) # ลดเวลาเหลือ 10 วินาทีให้เห็นผลเร็วขึ้น
def load_data():
    df = pd.read_csv(csv_url)
    # ล้างช่องว่างและแปลงเป็นตัวเล็กเพื่อป้องกันบักชื่อคอลัมน์ไม่ตรง
    df.columns = [str(col).strip().lower() for col in df.columns]
    
    # พยายามหาคอลัมน์เวลา (ถ้าชื่อไม่ตรงให้ใช้คอลัมน์แรก)
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    else:
        df['timestamp'] = pd.to_datetime(df.iloc[:, 0])
        
    return df

try:
    df = load_data()
    latest = df.iloc[-1]

    # แสดงค่า Metric
    col1, col2, col3 = st.columns(3)
    # ใช้การดึงข้อมูลแบบระบุลำดับคอลัมน์แทนชื่อ เพื่อลดโอกาสเกิดบัก
    with col1:
        st.metric("🌡️ อุณหภูมิ", f"{float(latest.get('temp', latest.iloc[1])):.2f} °C")
    with col2:
        st.metric("💧 ความชื้น", f"{float(latest.get('hum', latest.iloc[2])):.2f} %")
    with col3:
        st.metric("☀️ ความเข้มแสง", f"{float(latest.get('lux', latest.iloc[3])):.1f} Lux")

    st.divider()

    # กราฟแยกสีแดง-ฟ้า
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df.get('temp', df.iloc[:, 1]), name='อุณหภูมิ', line=dict(color='#ff4b4b')))
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df.get('hum', df.iloc[:, 2]), name='ความชื้น', line=dict(color='#00a2ff'), yaxis="y2"))
    
    fig.update_layout(
        template="plotly_dark",
        yaxis=dict(title="อุณหภูมิ (°C)", titlefont=dict(color="#ff4b4b"), tickfont=dict(color="#ff4b4b")),
        yaxis2=dict(title="ความชื้น (%)", titlefont=dict(color="#00a2ff"), tickfont=dict(color="#00a2ff"), overlaying="y", side="right")
    )
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"⚠️ ตรวจพบปัญหา: {e}")
    # โชว์ข้อมูลที่ดึงมาได้จริงๆ เพื่อให้รู้ว่าบักตรงไหน
    st.write("ชื่อคอลัมน์ที่พบในไฟล์คุณ:", list(df.columns) if 'df' in locals() else "หาไฟล์ไม่เจอ")
