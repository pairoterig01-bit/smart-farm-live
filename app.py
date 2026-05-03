import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pytz

# --- 1. การตั้งค่าหน้าจอ ---
st.set_page_config(page_title="Smart Farm Dashboard", layout="wide")
tz_thai = pytz.timezone('Asia/Bangkok')

# --- 2. CSS ปรับแต่ง UI ---
st.markdown("""
<style>
    .block-container { padding-top: 2rem !important; padding-bottom: 1rem !important; }
    [data-testid="stMetric"] { 
        padding: 8px 12px !important; 
        border-left: 20px solid #4E4E4E; 
        background: rgba(255,255,255,0.03);
    }
    div[data-testid="stMetricValue"] { font-size: 20px !important; }
    .stVerticalBlock { gap: 0.8rem !important; }
</style>
""", unsafe_allow_html=True)

# --- 3. การเชื่อมต่อข้อมูลแบบ Dynamic Sheet ---
sheet_id = "1mFHJgSss6ofUTghbaEgy6Po2032DMZ3cd_gzPd04Cf4"

@st.cache_data(ttl=60)
def load_data():
    # สร้างชื่อ Sheet ตามเดือนปัจจุบัน (เช่น MAY_2026)
    now = pd.Timestamp.now(tz=tz_thai)
    month_names = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
    current_sheet_name = f"{month_names[now.month - 1]}_{now.year}"
    
    # URL สำหรับดึง CSV โดยระบุชื่อ Sheet
    csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={current_sheet_name}"
    
    try:
        df = pd.read_csv(csv_url)
        df.columns = [str(col).strip().lower() for col in df.columns]
        
        if 'timestamp' not in df.columns:
            return pd.DataFrame()

        df['timestamp'] = pd.to_datetime(df['timestamp'], format='mixed')
        df['timestamp'] = df['timestamp'].apply(lambda dt: tz_thai.localize(dt) if dt.tzinfo is None else dt.astimezone(tz_thai))
        df = df.sort_values('timestamp').reset_index(drop=True)
        return df
    except:
        return pd.DataFrame()

try:
    all_data = load_data()
    
    # --- 4. ส่วนหัวและการเลือกวันที่ ---
    st.subheader("🌱 Smart Farm Monitoring")
    
    if not all_data.empty:
        latest_date_val = all_data['timestamp'].max().date()
        col_date, col_time = st.columns([1, 2])
        
        with col_date:
            selected_date = st.date_input("เลือกวันที่", value=latest_date_val, label_visibility="collapsed")
        
        data = all_data[all_data['timestamp'].dt.date == selected_date]
        
        with col_time:
            if not data.empty:
                latest = data.iloc[-1]
                st.info(f"🕒 ข้อมูลล่าสุด: {latest['timestamp'].strftime('%H:%M:%S')} (พ.ศ. {latest['timestamp'].year + 543})")
            else:
                st.warning(f"ไม่มีข้อมูลของวันที่ {selected_date.strftime('%d/%m/%Y')}")

        if not data.empty:
            # --- 5. Metrics ---
            m1, m2, m3 = st.columns(3)
            m1.metric("🌡️ อุณหภูมิ", f"{float(latest['temp']):.2f}°C")
            m2.metric("💧 ความชื้น", f"{float(latest['hum']):.2f}%")
            m3.metric("☀️ แสงสว่าง", f"{float(latest['lux']):.2f} Lux")

            # --- 6. กราฟ Temp & Hum ---
            fig1 = make_subplots(specs=[[{"secondary_y": True}]])
            fig1.add_trace(go.Scatter(x=data['timestamp'], y=data['temp'], name="Temp", line=dict(color="#FF4B4B", width=2)), secondary_y=False)
            fig1.add_trace(go.Scatter(x=data['timestamp'], y=data['hum'], name="Hum", line=dict(color="#00D2FF", width=2)), secondary_y=True)
            
            fig1.update_layout(
                template="plotly_dark", height=280, margin=dict(l=10, r=10, t=10, b=10),
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', hovermode="x unified"
            )
            fig1.update_xaxes(tickformat="%H:%M", showgrid=True, gridcolor='rgba(255,255,255,0.1)')
            st.plotly_chart(fig1, use_container_width=True)

            # --- 7. กราฟ Lux ---
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(x=data['timestamp'], y=data['lux'], fill='tozeroy', name="Lux", line=dict(color="#FFCC00")))
            fig2.update_layout(template="plotly_dark", height=160, margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            fig2.update_xaxes(tickformat="%H:%M", showgrid=True, gridcolor='rgba(255,255,255,0.1)')
            st.plotly_chart(fig2, use_container_width=True)
    else:
        st.error("ไม่พบข้อมูลในระบบ โปรดตรวจสอบการเชื่อมต่อกับ Google Sheets")

except Exception as e:
    st.error(f"เกิดข้อผิดพลาด: {e}")
