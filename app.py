import streamlit as st
import pandas as pd

# ลิงก์ Google Sheets ของคุณที่ตั้งค่าแชร์ไว้แล้ว
sheet_url = "https://docs.google.com/spreadsheets/d/1mFHJgSss6ofUTghbaEgy6Po2032DMZ3cd_gzPd04Cf4/edit?usp=sharing"
csv_url = sheet_url.replace('/edit?usp=sharing', '/export?format=csv')

st.set_page_config(page_title="Smart Farm Dashboard", layout="wide")
st.title("🌱 ระบบติดตามฟาร์มอัจฉริยะ (Live)")

def load_data():
    df = pd.read_csv(csv_url)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

try:
    data = load_data()
    latest = data.iloc[-1] # ดึงข้อมูลแถวล่าสุด
    
    col1, col2, col3 = st.columns(3)
    col1.metric("🌡️ อุณหภูมิ", f"{latest['temp']} °C")
    col2.metric("💧 ความชื้น", f"{latest['hum']} %")
    col3.metric("☀️ แสง (Lux)", f"{latest['lux']}")

    st.subheader("📊 กราฟข้อมูลย้อนหลัง")
    st.line_chart(data.set_index('timestamp')[['temp', 'hum']])

except Exception as e:
    st.error(f"รอข้อมูลจาก Google Sheets... ({e})")
