import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ตั้งค่าเบื้องต้น
st.set_page_config(page_title="Smart Farm", layout="wide")

# ลิงก์ Google Sheets ของคุณ
sheet_url = "https://docs.google.com/spreadsheets/d/1mFHJgSss6ofUTghbaEgy6Po2032DMZ3cd_gzPd04Cf4/edit?usp=sharing"
csv_url = sheet_url.replace('/edit?usp=sharing', '/export?format=csv')

@st.cache_data(ttl=5) # บังคับให้โหลดใหม่ทุก 5 วินาทีเพื่อเช็กบัก
def load_data():
    try:
        df = pd.read_csv(csv_url)
        # ล้างชื่อคอลัมน์เพื่อป้องกันช่องว่าง
        df.columns = [str(col).strip().lower() for col in df.columns]
        return df
    except Exception as e:
        return e

st.title("🌱 Smart Farm Live Dashboard")

data = load_data()

if isinstance(data, Exception):
    st.error(f"เชื่อมต่อ Google Sheets ไม่ได้: {data}")
else:
    try:
        # ดึงข้อมูลแถวสุดท้าย
        latest = data.iloc[-1]
        
        # แสดง Metric แบบง่ายก่อนเพื่อเช็กว่าค่ามาไหม
        c1, c2, c3 = st.columns(3)
        c1.metric("อุณหภูมิ", f"{latest.iloc[1]} °C")
        c2.metric("ความชื้น", f"{latest.iloc[2]} %")
        c3.metric("แสง", f"{latest.iloc[3]} Lux")
        
        st.success("ดึงข้อมูลสำเร็จ!")
        st.write("ข้อมูล 5 แถวล่าสุด:", data.tail())
        
    except Exception as e:
        st.warning(f"ดึงข้อมูลสำเร็จแต่แสดงผลไม่ได้: {e}")
        st.write("โครงสร้างตารางของคุณ:", data.columns.tolist())
