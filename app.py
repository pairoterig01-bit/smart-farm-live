import streamlit as st
import pandas as pd

# --- 1. การตั้งค่าหน้าจอและสไตล์ (บังคับให้ Metric ชิดซ้าย) ---
st.set_page_config(page_title="Smart Farm Dashboard", layout="wide")

st.markdown("""
    <style>
    /* บังคับให้ตัวเลขและหน่วยใน Metric ชิดซ้าย */
    div[data-testid="stMetricValue"] {
        text-align: left !important;
        justify-content: flex-start !important;
    }
    div[data-testid="stMetricLabel"] {
        text-align: left !important;
    }
    /* ปรับสีพื้นหลังให้ดูสบายตาแบบ Dark Mode */
    .main {
        background-color: #0e1117;
    }
    </style>
    """, unsafe_allow_index=True)

st.title("🌱 Smart Farm Dashboard")

# --- 2. การดึงข้อมูลจาก Google Sheets ---
sheet_url = "https://docs.google.com/spreadsheets/d/1mFHJgSss6ofUTghbaEgy6Po2032DMZ3cd_gzPd04Cf4/edit?usp=sharing"
csv_url = sheet_url.replace('/edit?usp=sharing', '/export?format=csv')

def load_data():
    df = pd.read_csv(csv_url)
    # แปลงคอลัมน์ timestamp ให้เป็นรูปแบบเวลา
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

try:
    data = load_data()
    latest = data.iloc[-1]
    
    # --- 3. ปรับรูปแบบเวลาให้เป็นมาตรฐานไทย ---
    # วัน/เดือน/ปี (พ.ศ.) เวลา 24 ชม.
    thai_year = latest['timestamp'].year + 543
    thai_time_str = latest['timestamp'].strftime(f'%d/%m/{thai_year} %H:%M:%S')

    st.info(f"🕒 อัปเดตข้อมูลล่าสุดเมื่อ: {thai_time_str} (เวลาไทย พ.ศ.)")

    # --- 4. แสดงค่าปัจจุบัน (Metrics ชิดซ้ายตามที่ต้องการ) ---
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🌡️ อุณหภูมิ", f"{latest['temp']} °C")
    with col2:
        st.metric("💧 ความชื้น", f"{latest['hum']} %")
    with col3:
        st.metric("☀️ แสง (Lux)", f"{latest['lux']}")

    st.divider()

    # --- 5. กราฟการแสดงผล (ใช้ X-axis เป็นเวลาแบบ 24 ชม.) ---
    st.subheader("📊 กราฟอุณหภูมิและความชื้น (ย้อนหลัง)")
    # สร้างคอลัมน์ใหม่สำหรับแสดงผลเวลาในกราฟให้เป็นแบบไทย/24ชม.
    chart_data = data.copy()
    chart_data['เวลา'] = chart_data['timestamp'].dt.strftime('%H:%M')
    
    st.line_chart(chart_data.set_index('เวลา')[['temp', 'hum']])

    st.subheader("☀️ กราฟความเข้มแสง (Lux)")
    st.area_chart(chart_data.set_index('เวลา')['lux'])

    # --- 6. ตารางข้อมูลย้อนหลัง ---
    with st.expander("ดูตารางข้อมูลทั้งหมด"):
        # ปรับรูปแบบเวลาในตารางให้เป็นมาตรฐานไทยก่อนแสดงผล
        display_df = data.copy()
        display_df['timestamp'] = display_df['timestamp'].apply(lambda x: x.strftime(f'%d/%m/{x.year + 543} %H:%M:%S'))
        st.write(display_df.sort_values(by='timestamp', ascending=False))

except Exception as e:
    st.error(f"เกิดข้อผิดพลาดในการดึงข้อมูล: {e}")
