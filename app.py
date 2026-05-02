import streamlit as st
import pandas as pd

# --- 1. ตั้งค่าหน้าจอ ---
st.set_page_config(page_title="Smart Farm Dashboard", layout="wide")

# --- 2. ฟังก์ชันตกแต่ง CSS (แยกเขียนเพื่อป้องกัน Error) ---
css_style = """
<style>
    div[data-testid="stMetricValue"] {
        text-align: left !important;
        justify-content: flex-start !important;
    }
    div[data-testid="stMetricLabel"] {
        text-align: left !important;
    }
    .main {
        background-color: #0e1117;
    }
</style>
"""
st.markdown(css_style, unsafe_allow_index=True)

st.title("🌱 Smart Farm Dashboard")

# --- 3. ลิงก์ข้อมูล Google Sheets ---
sheet_url = "https://docs.google.com/spreadsheets/d/1mFHJgSss6ofUTghbaEgy6Po2032DMZ3cd_gzPd04Cf4/edit?usp=sharing"
csv_url = sheet_url.replace('/edit?usp=sharing', '/export?format=csv')

def load_data():
    df = pd.read_csv(csv_url)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

try:
    data = load_data()
    latest = df_row = data.iloc[-1]
    
    # --- 4. ปรับเวลาเป็นมาตรฐานไทย (พ.ศ. และ 24 ชม.) ---
    current_time = df_row['timestamp']
    thai_year = current_time.year + 543
    # รูปแบบ: วัน/เดือน/พ.ศ. เวลา (เช่น 02/05/2569 18:30:00)
    thai_time_str = current_time.strftime(f"%d/%m/{thai_year} %H:%M:%S")

    st.info(f"🕒 อัปเดตล่าสุดเมื่อ: {thai_time_str}")

    # --- 5. แสดงค่า Metrics (ชิดซ้าย) ---
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🌡️ อุณหภูมิ", f"{df_row['temp']} °C")
    with col2:
        st.metric("💧 ความชื้น", f"{df_row['hum']} %")
    with col3:
        st.metric("☀️ แสง (Lux)", f"{df_row['lux']}")

    st.divider()

    # --- 6. กราฟ (แสดงเวลาแบบ 24 ชม.) ---
    st.subheader("📊 กราฟอุณหภูมิและความชื้น")
    chart_data = data.copy()
    # ปรับแกน X ของกราฟให้แสดงเวลา 24 ชม.
    chart_data['time_label'] = chart_data['timestamp'].dt.strftime('%H:%M')
    
    st.line_chart(chart_data.set_index('time_label')[['temp', 'hum']])

    st.subheader("☀️ กราฟความเข้มแสง (Lux)")
    st.area_chart(chart_data.set_index('time_label')['lux'])

except Exception as e:
    st.error(f"⚠️ เกิดข้อผิดพลาด: {e}")
