import streamlit as st
import pandas as pd

# ลิงก์จาก Google Sheets ของคุณ
sheet_url = "https://docs.google.com/spreadsheets/d/1mFHJgSss6ofUTghbaEgy6Po2032DMZ3cd_gzPd04Cf4/edit?usp=sharing"
# แปลงลิงก์ให้เป็นรูปแบบที่ pandas อ่านได้ (CSV)
csv_url = sheet_url.replace('/edit?usp=sharing', '/export?format=csv')

st.set_page_config(page_title="Smart Farm Dashboard", layout="wide")
st.title("🌱 Smart Farm Dashboard")

def load_data():
    df = pd.read_csv(csv_url)
    # แปลง Timestamp เป็นรูปแบบเวลาเพื่อให้กราฟแสดงผลถูกต้อง
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

try:
    data = load_data()
    
    # 1. แสดงค่าล่าสุด (Current Status)
    latest = data.iloc[-1]
    col1, col2, col3 = st.columns(3)
    col1.metric("อุณหภูมิ", f"{latest['temp']} °C")
    col2.metric("ความชื้น", f"{latest['hum']} %")
    col3.metric("แสง (Lux)", f"{latest['lux']}")

    # 2. กราฟอุณหภูมิและความชื้น (เหมือน index.html เดิม)
    st.subheader("📊 กราฟอุณหภูมิและความชื้น")
    st.line_chart(data.set_index('timestamp')[['temp', 'hum']])

    # 3. กราฟแสง Lux
    st.subheader("☀️ กราฟความเข้มแสง (Lux)")
    st.area_chart(data.set_index('timestamp')['lux'])

    # 4. ตารางข้อมูลย้อนหลัง
    with st.expander("ดูตารางข้อมูลทั้งหมด"):
        st.write(data.sort_values(by='timestamp', ascending=False))

except Exception as e:
    st.error(f"เกิดข้อผิดพลาดในการดึงข้อมูล: {e}")
