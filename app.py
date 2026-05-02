import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- 1. การตั้งค่าหน้าจอ ---
st.set_page_config(page_title="Smart Farm Dashboard", layout="wide")

# --- 2. CSS สำหรับจัดระเบียบตัวเลข ---
st.markdown("""
<style>
    [data-testid="stMetric"] { padding-left: 20px !important; border-left: 3px solid #4E4E4E; }
    div[data-testid="stMetricValue"] { text-align: left !important; justify-content: flex-start !important; font-size: 32px !important; }
    div[data-testid="stMetricLabel"] { text-align: left !important; margin-bottom: -10px !important; }
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
    
    # คำนวณค่า Min/Max เพื่อกำหนดขอบเขตแกนให้ "เลย" เส้นกราฟ
    t_min, t_max = data['temp'].min(), data['temp'].max()
    h_min, h_max = data['hum'].min(), data['hum'].max()

    # --- 4. แสดงเวลาและ Metrics ---
    ts = latest['timestamp']
    thai_year = ts.year + 543
    st.info(f"🕒 อัปเดตล่าสุด: {ts.strftime(f'%d/%m/{thai_year} %H:%M:%S')}")

    col1, col2, col3 = st.columns(3)
    with col1: st.metric("🌡️ อุณหภูมิ", f"{latest['temp']} °C")
    with col2: st.metric("💧 ความชื้น", f"{latest['hum']} %")
    with col3: st.metric("☀️ แสง (Lux)", f"{latest['lux']}")

    st.divider()

    # --- 5. กราฟ 2 แกน (ปรับให้ตารางเลยเส้นกราฟ) ---
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
        template="plotly_dark", hovermode="x unified",
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    # ปรับแกนซ้าย (อุณหภูมิ): ให้ขอบเขต (range) ต่ำกว่า min และสูงกว่า max อย่างละ 2 หน่วย
    fig.update_yaxes(
        title_text="อุณหภูมิ (°C)", 
        title_font=dict(color="#FF4B4B"), tickfont=dict(color="#FF4B4B"),
        range=[round(t_min - 2), round(t_max + 2)], 
        dtick=1, showgrid=True, gridcolor='rgba(255, 255, 255, 0.1)',
        secondary_y=False
    )

    # ปรับแกนขวา (ความชื้น): ให้ขอบเขต (range) ต่ำกว่า min และสูงกว่า max อย่างละ 5 หน่วย
    fig.update_yaxes(
        title_text="ความชื้น (%)", 
        title_font=dict(color="#00D2FF"), tickfont=dict(color="#00D2FF"),
        range=[round(h_min - 5), round(h_max + 5)], 
        dtick=2, showgrid=False,
        secondary_y=True
    )

    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"⚠️ เกิดข้อผิดพลาด: {e}")
