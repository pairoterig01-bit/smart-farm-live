import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- 1. การตั้งค่าหน้าจอ ---
st.set_page_config(page_title="Smart Farm Dashboard", layout="wide")

# --- 2. CSS สำหรับจัดระเบียบตัวเลขและช่องไฟให้สมดุล ---
st.markdown("""
<style>
    [data-testid="stMetric"] {
        padding-left: 20px !important;
        border-left: 3px solid #4E4E4E;
    }
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

# --- 3. การเชื่อมต่อข้อมูลจาก Google Sheets ---
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
    
    # คำนวณค่า Min/Max เพื่อกำหนดขอบเขตแกนให้ "เลย" เส้นกราฟออกมา
    t_min, t_max = data['temp'].min(), data['temp'].max()
    h_min, h_max = data['hum'].min(), data['hum'].max()

    # --- 4. แสดงเวลามาตรฐานไทย ---
    ts = latest['timestamp']
    thai_year = ts.year + 543
    st.info(f"🕒 อัปเดตล่าสุด: {ts.strftime(f'%d/%m/{thai_year} %H:%M:%S')}")

    # --- 5. ส่วนแสดงผล Metrics ---
    col1, col2, col3 = st.columns(3)
    with col1: st.metric("🌡️ อุณหภูมิ", f"{latest['temp']} °C")
    with col2: st.metric("💧 ความชื้น", f"{latest['hum']} %")
    with col3: st.metric("☀️ แสง (Lux)", f"{latest['lux']}")

    st.divider()

    # --- 6. กราฟ 2 แกน (ขยายเส้นตาราง Grid ให้เลยเส้นกราฟ) ---
    st.subheader("📊 กราฟอุณหภูมิและความชื้น (แยกแกนซ้าย-ขวา)")
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # เส้นอุณหภูมิ (สีแดง)
    fig.add_trace(
        go.Scatter(x=data['timestamp'], y=data['temp'], name="อุณหภูมิ (°C)", line=dict(color="#FF4B4B", width=3)),
        secondary_y=False,
    )

    # เส้นความชื้น (สีฟ้า)
    fig.add_trace(
        go.Scatter(x=data['timestamp'], y=data['hum'], name="ความชื้น (%)", line=dict(color="#00D2FF", width=3)),
        secondary_y=True,
    )

    fig.update_layout(
        template="plotly_dark", 
        hovermode="x unified",
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=50, r=50, t=50, b=50)
    )

    # ปรับแกน Y ซ้าย (อุณหภูมิ): ขยาย range ให้เลยกราฟ และตั้งระยะช่องตาราง
    fig.update_yaxes(
        title_text="อุณหภูมิ (°C)", 
        title_font=dict(color="#FF4B4B"), 
        tickfont=dict(color="#FF4B4B"),
        range=[round(t_min - 2), round(t_max + 2)], # เผื่อพื้นที่บน-ล่าง อย่างละ 2 หน่วย
        dtick=1, 
        showgrid=True, 
        gridcolor='rgba(255, 255, 255, 0.1)',
        secondary_y=False
    )

    # ปรับแกน Y ขวา (ความชื้น): ขยาย range ให้เลยกราฟ และตั้งระยะตัวเลข
    fig.update_yaxes(
        title_text="ความชื้น (%)", 
        title_font=dict(color="#00D2FF"), 
        tickfont=dict(color="#00D2FF"),
        range=[round(h_min - 4), round(h_max + 4)], # เผื่อพื้นที่บน-ล่าง อย่างละ 4 หน่วย
        dtick=2, 
        showgrid=False,
        secondary_y=True
    )

    # เพิ่มเส้นตารางแกนตั้ง (แกน X)
    fig.update_xaxes(showgrid=True, gridcolor='rgba(255, 255, 255, 0.1)')

    st.plotly_chart(fig, use_container_width=True)

    # --- 7. กราฟแสงและตารางข้อมูล ---
    st.subheader("☀️ กราฟความเข้มแสง (Lux)")
    st.area_chart(data.set_index('timestamp')['lux'])

    with st.expander("ดูตารางข้อมูลย้อนหลัง"):
        st.write(data.sort_values(by='timestamp', ascending=False))

except Exception as e:
    st.error(f"⚠️ เกิดข้อผิดพลาด: {e}")
