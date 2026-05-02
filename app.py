import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- 1. การตั้งค่าหน้าจอ ---
st.set_page_config(page_title="Smart Farm Dashboard", layout="wide")

# --- 2. ตกแต่งให้ตัวเลขชิดซ้าย ---
st.markdown("""
<style>
    div[data-testid="stMetricValue"] { text-align: left !important; justify-content: flex-start !important; }
    div[data-testid="stMetricLabel"] { text-align: left !important; }
</style>
""", unsafe_allow_html=True)

st.title("🌱 Smart Farm Dashboard")

# --- 3. ดึงข้อมูล ---
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
    
    # --- 4. แสดงเวลามาตรฐานไทย ---
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

    # --- 6. สร้างกราฟ 2 แกน (ตามที่คุณต้องการ) ---
    st.subheader("📊 กราฟอุณหภูมิและความชื้น (แยกแกนซ้าย-ขวา)")
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # เส้นอุณหภูมิ (แกนซ้าย - สีแดง)
    fig.add_trace(
        go.Scatter(x=data['timestamp'], y=data['temp'], name="อุณหภูมิ (°C)", line=dict(color="#FF4B4B", width=3)),
        secondary_y=False,
    )

    # เส้นความชื้น (แกนขวา - สีฟ้า)
    fig.add_trace(
        go.Scatter(x=data['timestamp'], y=data['hum'], name="ความชื้น (%)", line=dict(color="#00D2FF", width=3)),
        secondary_y=True,
    )

    # ปรับแต่งหน้าตาและชื่อแกน
    fig.update_layout(template="plotly_dark", hovermode="x unified", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    fig.update_yaxes(title_text="<b>อุณหภูมิ (°C)</b>", titlefont=dict(color="#FF4B4B"), secondary_y=False)
    fig.update_yaxes(title_text="<b>ความชื้น (%)</b>", titlefont=dict(color="#00D2FF"), secondary_y=True)

    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"⚠️ เกิดข้อผิดพลาด: {e}")
