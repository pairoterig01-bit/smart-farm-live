import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- 1. การตั้งค่าหน้าจอ ---
st.set_page_config(page_title="Smart Farm Dashboard", layout="wide")

# --- 2. ปรับแต่ง CSS: ตัวเลขชิดซ้าย จัดช่องไฟให้เท่ากัน และดูเป็นระเบียบ ---
st.markdown("""
<style>
    /* จัดระยะห่างของ Metric ทุกตัวให้เท่ากันและชิดซ้าย */
    [data-testid="stMetric"] {
        padding-left: 20px !important;
        border-left: 3px solid #4E4E4E; 
    }
    /* บังคับตัวเลขและหน่วยให้ชิดซ้าย */
    div[data-testid="stMetricValue"] {
        text-align: left !important;
        justify-content: flex-start !important;
        font-size: 32px !important;
    }
    /* บังคับป้ายชื่อให้ชิดซ้าย */
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
    # ล้างชื่อคอลัมน์ให้เป็นตัวเล็กและไม่มีช่องว่าง
    df.columns = [str(col).strip().lower() for col in df.columns]
    # แปลง Timestamp เป็นรูปแบบเวลา
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

try:
    data = load_data()
    latest = data.iloc[-1]
    
    # --- 4. แสดงเวลามาตรฐานไทย (พ.ศ. และ 24 ชม.) ---
    ts = latest['timestamp']
    thai_year = ts.year + 543
    thai_time_str = ts.strftime(f"%d/%m/{thai_year} %H:%M:%S")
    st.info(f"🕒 อัปเดตข้อมูลล่าสุดเมื่อ: {thai_time_str}")

    # --- 5. ส่วนแสดงผลค่าปัจจุบัน (Metrics) ---
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🌡️ อุณหภูมิ", f"{latest['temp']} °C")
    with col2:
        st.metric("💧 ความชื้น", f"{latest['hum']} %")
    with col3:
        st.metric("☀️ แสง (Lux)", f"{latest['lux']}")

    st.divider()

    # --- 6. กราฟ 2 แกน พร้อมปรับจูนเส้นตาราง (Grid) ให้สวยงามตามภาพตัวอย่าง ---
    st.subheader("📊 กราฟอุณหภูมิและความชื้น (แยกแกนซ้าย-ขวา)")
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # เพิ่มเส้นอุณหภูมิ (แกนซ้าย - สีแดง)
    fig.add_trace(
        go.Scatter(
            x=data['timestamp'], 
            y=data['temp'], 
            name="อุณหภูมิ (°C)", 
            line=dict(color="#FF4B4B", width=3)
        ),
        secondary_y=False,
    )

    # เพิ่มเส้นความชื้น (แกนขวา - สีฟ้า)
    fig.add_trace(
        go.Scatter(
            x=data['timestamp'], 
            y=data['hum'], 
            name="ความชื้น (%)", 
            line=dict(color="#00D2FF", width=3)
        ),
        secondary_y=True,
    )

    # ปรับแต่งหน้าตากราฟและระยะห่าง
    fig.update_layout(
        template="plotly_dark", 
        hovermode="x unified", 
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=50, r=50, t=50, b=50)
    )

    # ตั้งค่าแกน Y ซ้าย (อุณหภูมิ) - เส้นตารางห่างกันทีละ 1 หน่วย
    fig.update_yaxes(
        title_text="อุณหภูมิ (°C)", 
        title_font=dict(color="#FF4B4B"), 
        tickfont=dict(color="#FF4B4B"),
        showgrid=True, 
        gridcolor='rgba(255, 255, 255, 0.1)',
        dtick=1, 
        secondary_y=False
    )

    # ตั้งค่าแกน Y ขวา (ความชื้น) - ตัวเลขห่างกันทีละ 2 หน่วย
    fig.update_yaxes(
        title_text="ความชื้น (%)", 
        title_font=dict(color="#00D2FF"), 
        tickfont=dict(color="#00D2FF"),
        showgrid=False, # ปิดเส้นตารางฝั่งนี้เพื่อไม่ให้ลายตา
        dtick=2, 
        secondary_y=True
    )

    # ปรับแกน X ให้แสดงเส้นตารางแนวตั้งจางๆ
    fig.update_xaxes(showgrid=True, gridcolor='rgba(255, 255, 255, 0.1)')

    st.plotly_chart(fig, use_container_width=True)

    # --- 7. กราฟแสง Lux และตารางข้อมูล ---
    st.subheader("☀️ กราฟความเข้มแสง (Lux)")
    st.area_chart(data.set_index('timestamp')['lux'])

    with st.expander("ดูตารางข้อมูลย้อนหลัง"):
        st.write(data.sort_values(by='timestamp', ascending=False))

except Exception as e:
    st.error(f"⚠️ เกิดข้อผิดพลาด: {e}")
