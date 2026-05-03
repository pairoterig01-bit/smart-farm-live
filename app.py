import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pytz

# --- 1. การตั้งค่าหน้าจอ ---
st.set_page_config(page_title="Smart Farm Monitoring", layout="wide")
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

# --- 3. ฟังก์ชันโหลดข้อมูล (รองรับการเลือก Sheet ตามเดือน) ---
sheet_id = "1mFHJgSss6ofUTghbaEgy6Po2032DMZ3cd_gzPd04Cf4"

@st.cache_data(ttl=60)
def load_data_by_date(target_date):
    month_names = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
    sheet_name = f"{month_names[target_date.month - 1]}_{target_date.year}"
    
    csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    
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

# --- 4. ส่วนหัวและการเลือกวันที่ ---
st.subheader("🌱 Smart Farm Monitoring")

now_thai = pd.Timestamp.now(tz=tz_thai)
col_date, col_time = st.columns([1, 2])

with col_date:
    selected_date = st.date_input("เลือกวันที่", value=now_thai.date(), label_visibility="collapsed")

all_data = load_data_by_date(selected_date)

try:
    if not all_data.empty:
        data = all_data[all_data['timestamp'].dt.date == selected_date]
        
        if not data.empty:
            latest = data.iloc[-1]
            with col_time:
                st.info(f"🕒 ข้อมูลล่าสุด: {latest['timestamp'].strftime('%H:%M:%S')} (พ.ศ. {latest['timestamp'].year + 543})")

            # กำหนดช่วงเวลา Min/Max เพื่อล็อคแกน X
            min_x = data['timestamp'].min()
            max_x = data['timestamp'].max()

            # --- 5. Metrics ---
            m1, m2, m3 = st.columns(3)
            m1.metric("🌡️ อุณหภูมิ", f"{float(latest['temp']):.2f}°C")
            m2.metric("💧 ความชื้น", f"{float(latest['hum']):.2f}%")
            m3.metric("☀️ แสงสว่าง", f"{float(latest['lux']):.2f} Lux")

            # --- 6. กราฟรวม (Temp & Hum) ---
            fig1 = make_subplots(specs=[[{"secondary_y": True}]])
            fig1.add_trace(go.Scatter(x=data['timestamp'], y=data['temp'], name="Temp", line=dict(color="#FF4B4B", width=2)), secondary_y=False)
            fig1.add_trace(go.Scatter(x=data['timestamp'], y=data['hum'], name="Hum", line=dict(color="#00D2FF", width=2)), secondary_y=True)
            
            fig1.update_layout(
                template="plotly_dark", height=280, 
                margin=dict(l=10, r=50, t=10, b=10), # กำหนดระยะขอบขวา r=50 เผื่อแกนความชื้น
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', hovermode="x unified",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                dragmode=False
            )
            
            fig1.update_xaxes(
                tickformat="%H:%M", showgrid=True, gridcolor='rgba(255,255,255,0.1)', 
                fixedrange=True, range=[min_x, max_x]
            )
            fig1.update_yaxes(showgrid=True, gridcolor='rgba(255,255,255,0.1)', fixedrange=True, secondary_y=False, nticks=10)
            fig1.update_yaxes(showgrid=False, fixedrange=True, secondary_y=True) # ปิด Grid ของแกนขวา
            st.plotly_chart(fig1, use_container_width=True, config={'displayModeBar': False})

            # --- 7. กราฟ Lux (ปรับเพื่อให้พื้นที่เท่ากับกราฟบน) ---
            # ใช้ make_subplots และ secondary_y=True เพื่อจองพื้นที่ด้านขวาให้เท่ากัน
            fig2 = make_subplots(specs=[[{"secondary_y": True}]])
            fig2.add_trace(go.Scatter(x=data['timestamp'], y=data['lux'], fill='tozeroy', name="Lux", 
                                     line=dict(color="#FFCC00", width=1.5), 
                                     fillcolor='rgba(255, 204, 0, 0.1)'), secondary_y=False)
            
            fig2.update_layout(
                template="plotly_dark", height=160, 
                margin=dict(l=10, r=50, t=10, b=10), # r=50 ต้องเท่ากับกราฟบนเป๊ะ
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', dragmode=False,
                showlegend=False
            )
            
            fig2.update_xaxes(
                tickformat="%H:%M", showgrid=True, gridcolor='rgba(255,255,255,0.1)', 
                fixedrange=True, range=[min_x, max_x]
            )
            fig2.update_yaxes(showgrid=True, gridcolor='rgba(255,255,255,0.1)', fixedrange=True, secondary_y=False)
            # จองพื้นที่แกนขวาแต่ไม่แสดงตัวเลข (เพื่อให้ช่องวาดกราฟกว้างเท่ากราฟบน)
            fig2.update_yaxes(secondary_y=True, showticklabels=False, showgrid=False, fixedrange=True)
            
            st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})
        else:
            with col_time:
                st.warning(f"ยังไม่มีข้อมูลของวันที่ {selected_date.strftime('%d/%m/%Y')}")
    else:
        st.error(f"ไม่พบฐานข้อมูลของเดือน {selected_date.strftime('%m/%Y')}")

except Exception as e:
    st.error(f"เกิดข้อผิดพลาด: {e}")
