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
    /* ปรับแต่งส่วน Date Input ให้ดูกลืนกับแถบข้อมูล */
    .stDateInput { padding-top: 0px !important; }
</style>
""", unsafe_allow_html=True)

st.title("🌱 Smart Farm Dashboard")

# --- 3. การเชื่อมต่อข้อมูล ---
sheet_url = "https://docs.google.com/spreadsheets/d/1mFHJgSss6ofUTghbaEgy6Po2032DMZ3cd_gzPd04Cf4/edit?usp=sharing"
csv_url = sheet_url.replace('/edit?usp=sharing', '/export?format=csv')

@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv(csv_url)
    df.columns = [str(col).strip().lower() for col in df.columns]
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

try:
    all_data = load_data()
    min_date = all_data['timestamp'].min().date()
    max_date = all_data['timestamp'].max().date()

    # --- 4. ส่วนเลือกปฏิทินตรงบริเวณวงสีแดง (Container ด้านบน) ---
    with st.container():
        # สร้างคอลัมน์เพื่อจัดวาง ปฏิทิน และ ข้อความแจ้งเวลา ให้อยู่แถวเดียวกัน
        c1, c2 = st.columns([1, 3])
        
        with c1:
            selected_date = st.date_input(
                "📅 เลือกวันที่",
                value=max_date,
                min_value=min_date,
                max_value=max_date,
                label_visibility="collapsed" # ซ่อน label เพื่อให้ประหยัดพื้นที่
            )

        # กรองข้อมูลตามวันที่เลือก
        data = all_data[all_data['timestamp'].dt.date == selected_date]

        with c2:
            if not data.empty:
                latest = data.iloc[-1]
                ts = latest['timestamp']
                thai_year = ts.year + 543
                st.info(f"📅 ข้อมูลวันที่: {selected_date.strftime('%d/%m/')}{thai_year} | อัปเดตล่าสุด: {ts.strftime('%H:%M:%S')}")
            else:
                st.warning(f"⚠️ ไม่พบข้อมูลของวันที่ {selected_date.strftime('%d/%m/%Y')}")

    if not data.empty:
        # --- 5. แสดงผล Metrics ---
        col1, col2, col3 = st.columns(3)
        with col1: st.metric("🌡️ อุณหภูมิ", f"{latest['temp']} °C")
        with col2: st.metric("💧 ความชื้น", f"{latest['hum']} %")
        with col3: st.metric("☀️ แสง (Lux)", f"{latest['lux']}")

        st.divider()

        # --- 6. กราฟ 2 แกน ---
        st.subheader("📊 กราฟอุณหภูมิและความชื้น (แยกแกนซ้าย-ขวา)")
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Scatter(x=data['timestamp'], y=data['temp'], name="อุณหภูมิ (°C)", line=dict(color="#FF4B4B", width=3)), secondary_y=False)
        fig.add_trace(go.Scatter(x=data['timestamp'], y=data['hum'], name="ความชื้น (%)", line=dict(color="#00D2FF", width=3)), secondary_y=True)

        t_min, t_max = data['temp'].min(), data['temp'].max()
        h_min, h_max = data['hum'].min(), data['hum'].max()

        fig.update_layout(template="plotly_dark", hovermode="x unified", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        fig.update_yaxes(title_text="อุณหภูมิ (°C)", range=[round(t_min - 2), round(t_max + 2)], dtick=1, showgrid=True, gridcolor='rgba(255, 255, 255, 0.1)', secondary_y=False)
        fig.update_yaxes(title_text="ความชื้น (%)", range=[round(h_min - 4), round(h_max + 4)], dtick=2, showgrid=False, secondary_y=True)
        fig.update_xaxes(showgrid=True, gridcolor='rgba(255, 255, 255, 0.1)')

        st.plotly_chart(fig, use_container_width=True)

        st.subheader("☀️ กราฟความเข้มแสง (Lux)")
        st.area_chart(data.set_index('timestamp')['lux'])

        with st.expander("ดูตารางข้อมูลย้อนหลัง"):
            st.write(data.sort_values(by='timestamp', ascending=False))

except Exception as e:
    st.error(f"⚠️ เกิดข้อผิดพลาด: {e}")
