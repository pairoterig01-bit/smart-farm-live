import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- 1. การตั้งค่าหน้าจอ ---
st.set_page_config(page_title="Smart Farm Dashboard", layout="wide")

# --- 2. CSS ปรับจูนระดับและรองรับมือถือ ---
st.markdown("""
<style>
    /* ปรับแต่ง Metrics ให้ดูดีในมือถือ */
    [data-testid="stMetric"] { 
        padding-left: 15px !important; 
        border-left: 3px solid #4E4E4E; 
        margin-bottom: 10px;
    }
    div[data-testid="stMetricValue"] { font-size: 28px !important; }
    
    /* ปรับระดับ Date Input และ Info Box */
    .stDateInput { padding-top: 0px !important; }
    div.stAlert {
        margin-top: -1px !important; 
        padding: 8px !important;
        line-height: 1.2 !important;
        min-height: 44px !important;
        display: flex;
        align-items: center;
    }
    
    /* ซ่อนแถบเมนูกราฟถาวรเพื่อป้องกันการกดพลาดบนมือถือ */
    .modebar { display: none !important; }
</style>
""", unsafe_allow_html=True)

st.title("🌱 Smart Farm") # ลดความยาวชื่อเพื่อพื้นที่หน้าจอ

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
    max_date = all_data['timestamp'].max().date()

    # --- 4. ส่วนหัว Dashboard (ปรับช่องไฟให้กระชับ) ---
    c1, c2 = st.columns([1.2, 2.8], gap="small")
    with c1:
        selected_date = st.date_input("เลือกวันที่", value=max_date, label_visibility="collapsed")
    
    data = all_data[all_data['timestamp'].dt.date == selected_date]
    
    with c2:
        if not data.empty:
            latest = data.iloc[-1]
            st.info(f"🕒 {latest['timestamp'].strftime('%H:%M:%S')} (พ.ศ. {latest['timestamp'].year + 543})")
        else:
            st.warning("ไม่มีข้อมูล")

    if not data.empty:
        # --- 5. Metrics (ในมือถือจะเรียงแนวตั้งให้อัตโนมัติ) ---
        m1, m2, m3 = st.columns(3)
        m1.metric("🌡️ Temp", f"{latest['temp']}°C")
        m2.metric("💧 Hum", f"{latest['hum']}%")
        m3.metric("☀️ Lux", f"{latest['lux']}")

        st.divider()

        # --- 6. กราฟอุณหภูมิและความชื้น (ล็อคและปรับขนาด) ---
        st.write("📊 **Temp & Humidity**")
        fig1 = make_subplots(specs=[[{"secondary_y": True}]])
        fig1.add_trace(go.Scatter(x=data['timestamp'], y=data['temp'], name="T", line=dict(color="#FF4B4B", width=2)), secondary_y=False)
        fig1.add_trace(go.Scatter(x=data['timestamp'], y=data['hum'], name="H", line=dict(color="#00D2FF", width=2)), secondary_y=True)

        fig1.update_layout(
            template="plotly_dark", 
            hovermode="x unified",
            height=300, # ลดความสูงเพื่อให้ดูในมือถือง่ายขึ้น
            margin=dict(l=10, r=10, t=10, b=10),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, font=dict(size=10)),
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)',
            dragmode=False
        )
        fig1.update_xaxes(showgrid=True, gridcolor='rgba(255, 255, 255, 0.1)', fixedrange=True, tickfont=dict(size=10))
        fig1.update_yaxes(showgrid=True, gridcolor='rgba(255, 255, 255, 0.1)', fixedrange=True, tickfont=dict(size=10))
        fig1.update_yaxes(showgrid=False, secondary_y=True, fixedrange=True, tickfont=dict(size=10))
        
        st.plotly_chart(fig1, use_container_width=True, config={'displayModeBar': False})

        # --- 7. กราฟ Lux ---
        st.write("☀️ **Light Intensity**")
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=data['timestamp'], y=data['lux'], fill='tozeroy', line=dict(color="#FFCC00", width=1.5), fillcolor='rgba(255, 204, 0, 0.1)'))
        fig2.update_layout(
            template="plotly_dark", height=200, margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', dragmode=False
        )
        fig2.update_xaxes(showgrid=True, gridcolor='rgba(255, 255, 255, 0.1)', fixedrange=True, tickfont=dict(size=10))
        fig2.update_yaxes(showgrid=True, gridcolor='rgba(255, 255, 255, 0.1)', fixedrange=True, tickfont=dict(size=10))
        
        st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})

except Exception as e:
    st.error(f"Error: {e}")
