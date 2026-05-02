import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- 1. การตั้งค่าหน้าจอ ---
st.set_page_config(page_title="Smart Farm Dashboard", layout="wide")

# --- 2. แก้ไข CSS เพื่อจัดระยะช่องไฟให้เท่ากันและชิดซ้ายอย่างเป็นระเบียบ ---
st.markdown("""
<style>
    /* จัดการช่องว่างของ Metric ทุกตัวให้เท่ากัน */
    [data-testid="stMetric"] {
        padding-left: 20px !important;
        border-left: 3px solid #4E4E4E; /* เพิ่มเส้นคั่นซ้ายเบาๆ ให้ดูมีระเบียบ */
    }
    /* บังคับตัวเลขและป้ายชื่อชิดซ้าย */
    div[data-testid="stMetricValue"] {
        text-align: left !important;
        justify-content: flex-start !important;
        font-size: 32px !important;
    }
    div[data-testid="stMetricLabel"] {
        text-align: left !important;
        margin-bottom: -10px !important;
    }
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
    
    # --- 4. แสดงเวลามาตรฐานไทย ---
    ts = latest['timestamp']
    thai_year = ts.year + 543
    thai_time = ts.strftime(f"%d/%m/{thai_year} %H:%M:%S")
    st.info(f"🕒 อัปเดตล่าสุด: {thai_time}")

    # --- 5. แสดง Metrics (ปรับช่องไฟให้เท่ากันแล้ว) ---
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🌡️ อุณหภูมิ", f"{latest['temp']} °C")
    with col2:
        st.metric("💧 ความชื้น", f"{latest['hum']} %")
    with col3:
        st.metric("☀️ แสง (Lux)", f"{latest['lux']}")

    st.divider()

    # --- 6. กราฟ 2 แกน (เวอร์ชันแก้ไข Title Font แล้ว) ---
    st.subheader("📊 กราฟอุณหภูมิและความชื้น (แยกแกนซ้าย-ขวา)")
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Scatter(x=data['timestamp'], y=data['temp'], name="อุณหภูมิ (°C)", line=dict(color="#FF4B4B", width=3)),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(x=data['timestamp'], y=data['hum'], name="ความชื้น (%)", line=dict(color="#00D2FF", width=3)),
        secondary_y=True,
    )

    fig.update_layout(
        template="plotly_dark", 
        hovermode="x unified", 
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    fig.update_yaxes(title_text="อุณหภูมิ (°C)", title_font=dict(color="#FF4B4B"), tickfont=dict(color="#FF4B4B"), secondary_y=False)
    fig.update_yaxes(title_text="ความชื้น (%)", title_font=dict(color="#00D2FF"), tickfont=dict(color="#00D2FF"), secondary_y=True)

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("☀️ กราฟความเข้มแสง (Lux)")
    st.area_chart(data.set_index('timestamp')['lux'])

except Exception as e:
    st.error(f"⚠️ เกิดข้อผิดพลาด: {e}")
