import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- 1. การตั้งค่าหน้าจอ ---
st.set_page_config(page_title="Smart Farm Dashboard", layout="wide")

# --- 2. ตกแต่งให้ตัวเลข Metric ชิดซ้าย ---
st.markdown("""
<style>
    div[data-testid="stMetricValue"] { text-align: left !important; justify-content: flex-start !important; }
    div[data-testid="stMetricLabel"] { text-align: left !important; }
</style>
""", unsafe_allow_html=True)

st.title("🌱 Smart Farm Dashboard")

# --- 3. ดึงข้อมูลจาก Google Sheets ---
sheet_url = "https://docs.google.com/spreadsheets/d/1mFHJgSss6ofUTghbaEgy6Po2032DMZ3cd_gzPd04Cf4/edit?usp=sharing"
csv_url = sheet_url.replace('/edit?usp=sharing', '/export?format=csv')

@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv(csv_url)
    df.columns = [str(col).strip().lower() for col in df.columns]
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

try:
    data = load_data()
    latest = data.iloc[-1]
    
    # --- 4. แสดงเวลามาตรฐานไทย (พ.ศ.) ---
    ts = latest['timestamp']
    thai_year = ts.year + 543
    thai_time = ts.strftime(f"%d/%m/{thai_year} %H:%M:%S")
    st.info(f"🕒 อัปเดตล่าสุด: {thai_time}")

    # --- 5. แสดง Metrics (ชิดซ้าย) ---
    col1, col2, col3 = st.columns(3)
    with col1: st.metric("🌡️ อุณหภูมิ", f"{latest['temp']} °C")
    with col2: st.metric("💧 ความชื้น", f"{latest['hum']} %")
    with col3: st.metric("☀️ แสง (Lux)", f"{latest['lux']}")

    st.divider()

    # --- 6. สร้างกราฟ 2 แกน (แก้ปัญหา Error titlefont) ---
    st.subheader("📊 กราฟอุณหภูมิและความชื้น (แยกแกนซ้าย-ขวา)")
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # เพิ่มเส้นอุณหภูมิ (แกนซ้าย - สีแดง)
    fig.add_trace(
        go.Scatter(x=data['timestamp'], y=data['temp'], name="อุณหภูมิ (°C)", line=dict(color="#FF4B4B", width=3)),
        secondary_y=False,
    )

    # เพิ่มเส้นความชื้น (แกนขวา - สีฟ้า)
    fig.add_trace(
        go.Scatter(x=data['timestamp'], y=data['hum'], name="ความชื้น (%)", line=dict(color="#00D2FF", width=3)),
        secondary_y=True,
    )

    # ปรับแต่ง Layout และแก้บักชื่อแกน
    fig.update_layout(
        template="plotly_dark", 
        hovermode="x unified", 
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    # ตั้งค่าแกน Y ซ้าย (ใช้ title_font แทน titlefont)
    fig.update_yaxes(
        title_text="อุณหภูมิ (°C)", 
        title_font=dict(color="#FF4B4B"), 
        tickfont=dict(color="#FF4B4B"), 
        secondary_y=False
    )

    # ตั้งค่าแกน Y ขวา (ใช้ title_font แทน titlefont)
    fig.update_yaxes(
        title_text="ความชื้น (%)", 
        title_font=dict(color="#00D2FF"), 
        tickfont=dict(color="#00D2FF"), 
        secondary_y=True
    )

    st.plotly_chart(fig, use_container_width=True)

    # --- 7. กราฟแสง Lux ---
    st.subheader("☀️ กราฟความเข้มแสง (Lux)")
    st.area_chart(data.set_index('timestamp')['lux'])

except Exception as e:
    st.error(f"⚠️ เกิดข้อผิดพลาด: {e}")
