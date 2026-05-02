import streamlit as st
import pandas as pd

# --- 1. การตั้งค่าหน้าจอ ---
st.set_page_config(page_title="Smart Farm Dashboard", layout="wide")

# --- 2. ฟังก์ชันตกแต่ง CSS เพื่อให้ตัวเลขชิดซ้าย ---
st.markdown("""
<style>
    /* บังคับให้ Metric ชิดซ้าย */
    div[data-testid="stMetricValue"] {
        text-align: left !important;
        justify-content: flex-start !important;
    }
    div[data-testid="stMetricLabel"] {
        text-align: left !important;
    }
</style>
""", unsafe_allow_html=True) # แก้ไขพารามิเตอร์เป็น unsafe_allow_html

st.title("🌱 Smart Farm Dashboard")

# --- 3. การดึงข้อมูลจาก Google Sheets ---
sheet_url = "https://docs.google.com/spreadsheets/d/1mFHJgSss6ofUTghbaEgy6Po2032DMZ3cd_gzPd04Cf4/edit?usp=sharing"
csv_url = sheet_url.replace('/edit?usp=sharing', '/export?format=csv')

def load_data():
    df = pd.read_csv(csv_url)
    # ล้างชื่อคอลัมน์เพื่อป้องกันช่องว่าง
    df.columns = [str(col).strip().lower() for col in df.columns]
    # แปลงคอลัมน์เวลา
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

try:
    data = load_data()
    latest = data.iloc[-1]
    
    # --- 4. ปรับเวลาเป็นมาตรฐานไทย (พ.ศ. และ 24 ชม.) ---
    ts = latest['timestamp']
    thai_year = ts.year + 543
    thai_time_str = ts.strftime(f"%d/%m/{thai_year} %H:%M:%S")

    st.info(f"🕒 อัปเดตล่าสุดเมื่อ: {thai_time_str}")

    # --- 5. แสดงค่า Metrics (ชิดซ้าย) ---
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🌡️ อุณหภูมิ", f"{latest['temp']} °C")
    with col2:
        st.metric("💧 ความชื้น", f"{latest['hum']} %")
    with col3:
        st.metric("☀️ แสง (Lux)", f"{latest['lux']}")

    st.divider()

    # --- 6. กราฟแนวโน้ม (เวลา 24 ชม.) ---
    chart_data = data.copy()
    chart_data['เวลา'] = chart_data['timestamp'].dt.strftime('%H:%M')
    
    st.subheader("📊 กราฟอุณหภูมิและความชื้น")
    st.line_chart(chart_data.set_index('เวลา')[['temp', 'hum']])

    st.subheader("☀️ กราฟความเข้มแสง (Lux)")
    st.area_chart(chart_data.set_index('เวลา')['lux'])

except Exception as e:
    st.error(f"⚠️ เกิดข้อผิดพลาด: {e}")
