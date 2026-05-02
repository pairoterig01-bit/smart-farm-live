import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- 1. การตั้งค่าหน้าจอและสไตล์ (Dark Mode เหมือน index.html เดิม) ---
st.set_page_config(page_title="Smart Farm Dashboard", layout="wide")

st.markdown("""
    <style>
    /* พื้นหลังหลัก */
    .main { background-color: #121212; color: #e0e0e0; }
    
    /* สไตล์กล่อง Metric */
    div[data-testid="stMetric"] {
        background-color: #1e1e1e;
        border: 1px solid #333;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.5);
    }
    
    /* ปรับสีตัวอักษรใน Metric */
    label[data-testid="stMetricLabel"] { color: #aaaaaa !important; font-size: 1.1rem !important; }
    div[data-testid="stMetricValue"] { color: #ffffff !important; font-weight: bold !important; }
    
    /* ปรับแต่งส่วนหัว */
    h1 { color: #4CAF50; text-align: center; font-weight: bold; }
    </style>
    """, unsafe_allow_index=True)

st.title("🌱 ระบบติดตามฟาร์มอัจฉริยะ (Live Dashboard)")

# --- 2. การเชื่อมต่อข้อมูลจาก Google Sheets ---
# ลิงก์จาก Google Sheets ของคุณ (แชร์แบบ Anyone with link can view)
sheet_url = "https://docs.google.com/spreadsheets/d/1mFHJgSss6ofUTghbaEgy6Po2032DMZ3cd_gzPd04Cf4/edit?usp=sharing"
csv_url = sheet_url.replace('/edit?usp=sharing', '/export?format=csv')

@st.cache_data(ttl=30) # รีเฟรชข้อมูลทุกๆ 30 วินาที
def load_data():
    df = pd.read_csv(csv_url)
    # ล้างช่องว่างในชื่อคอลัมน์และทำให้เป็นตัวเล็ก
    df.columns = [col.strip().lower() for col in df.columns]
    # แปลงคอลัมน์เวลา
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

try:
    df = load_data()
    latest = df.iloc[-1] # ข้อมูลแถวล่าสุด

    # --- 3. ส่วนแสดงค่าปัจจุบัน (Metrics) ---
    st.markdown(f"### 📍 อัปเดตล่าสุด: {latest['timestamp'].strftime('%d/%m/%Y %H:%M:%S')}")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🌡️ อุณหภูมิ", f"{float(latest['temp']):.2f} °C")
    with col2:
        st.metric("💧 ความชื้น", f"{float(latest['hum']):.2f} %")
    with col3:
        st.metric("☀️ ความเข้มแสง", f"{float(latest['lux']):.1f} Lux")

    st.divider()

    # --- 4. กราฟอุณหภูมิและความชื้น (แยกแกนซ้าย-ขวา เพื่อไม่ให้เส้นทับกันมาก) ---
    st.subheader("📊 กราฟอุณหภูมิและความชื้นย้อนหลัง")
    
    fig_temp_hum = go.Figure()

    # เส้นอุณหภูมิ (แกนซ้าย)
    fig_temp_hum.add_trace(go.Scatter(
        x=df['timestamp'], y=df['temp'], 
        name='อุณหภูมิ (°C)',
        line=dict(color='#ff4b4b', width=3)
    ))

    # เส้นความชื้น (แกนขวา)
    fig_temp_hum.add_trace(go.Scatter(
        x=df['timestamp'], y=df['hum'], 
        name='ความชื้น (%)',
        line=dict(color='#00a2ff', width=3),
        yaxis="y2"
    ))

    fig_temp_hum.update_layout(
        template="plotly_dark",
        hovermode="x unified",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        yaxis=dict(title="อุณหภูมิ (°C)", titlefont=dict(color="#ff4b4b"), tickfont=dict(color="#ff4b4b")),
        yaxis2=dict(title="ความชื้น (%)", titlefont=dict(color="#00a2ff"), tickfont=dict(color="#00a2ff"), 
                    overlaying="y", side="right")
    )
    st.plotly_chart(fig_temp_hum, use_container_width=True)

    # --- 5. กราฟความเข้มแสง (สีเหลืองแบบ Area Chart) ---
    st.subheader("☀️ กราฟความเข้มแสง (Lux)")
    
    fig_lux = go.Figure()
    fig_lux.add_trace(go.Scatter(
        x=df['timestamp'], y=df['lux'], 
        name='ความเข้มแสง',
        fill='tozeroy', 
        line=dict(color='#ffcc00', width=2),
        fillcolor='rgba(255, 204, 0, 0.2)'
    ))
    
    fig_lux.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        yaxis=dict(title="Lux", titlefont=dict(color="#ffcc00"), tickfont=dict(color="#ffcc00"))
    )
    st.plotly_chart(fig_lux, use_container_width=True)

    # ส่วนตารางข้อมูล (ซ่อนไว้ใน Expander)
    with st.expander("ดูตารางข้อมูลย้อนหลัง"):
        st.dataframe(df.sort_values(by='timestamp', ascending=False), use_container_width=True)

except Exception as e:
    st.error(f"⚠️ ตรวจพบข้อผิดพลาด: {e}")
    st.info("คำแนะนำ: ตรวจสอบว่าชื่อคอลัมน์ใน Google Sheets คือ timestamp, temp, hum, lux และมีการแชร์ลิงก์ถูกต้อง")
