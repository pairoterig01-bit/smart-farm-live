import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- 1. การตั้งค่าหน้าจอ ---
st.set_page_config(page_title="Smart Farm", layout="wide")

# --- 2. CSS ปรับแต่งระยะห่างให้สมดุล ---
st.markdown("""
<style>
    .block-container { 
        padding-top: 2rem !important; 
        padding-bottom: 1rem !important; 
    }
    
    /* ปรับแต่ง Metrics ให้สวยงามและประหยัดพื้นที่ */
    [data-testid="stMetric"] { 
        padding: 8px 12px !important; 
        border-left: 10px solid #4E4E4E; 
        background: rgba(255,255,255,0.03);
    }
    div[data-testid="stMetricValue"] { font-size: 20px !important; }

    /* ปรับแต่งแถบ Info ให้เล็กลงเพื่อวางในคอลัมน์ */
    div.stAlert {
        padding: 0px 20px !important;
        min-height: auto !important;
        margin-top: 0px !important;
    }
    div.stAlert p { font-size: 20px !important; margin: 0 !important; }

    .stVerticalBlock { gap: 0.8rem !important; }
    .modebar { display: none !important; }
</style>
""", unsafe_allow_html=True)

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

    # --- 4. ส่วนหัว (ย้ายอัปเดตล่าสุดไปไว้ด้านบนขวา) ---
    st.subheader("🌱 Smart Farm")
    
    # แบ่งคอลัมน์สำหรับ วันที่ และ แถบอัปเดตล่าสุด
    head_c1, head_c2 = st.columns([1, 2], gap="small")
    
    with head_c1:
        selected_date = st.date_input("Date", value=max_date, label_visibility="collapsed")
    
    data = all_data[all_data['timestamp'].dt.date == selected_date]

    with head_c2:
        if not data.empty:
            latest = data.iloc[-1]
            # ย้ายมาไว้ในกรอบขวามือตามที่ระบุ
            st.info(f"🕒 {latest['timestamp'].strftime('%H:%M:%S')} (พ.ศ. {latest['timestamp'].year + 543})")
        else:
            st.warning("ไม่มีข้อมูล")

    if not data.empty:
        # --- 5. Metrics ---
        m1, m2, m3 = st.columns(3)
        m1.metric("🌡️ Temp", f"{latest['temp']}°C")
        m2.metric("💧 Hum", f"{latest['hum']}%")
        m3.metric("☀️ Lux", f"{latest['lux']}")

        # --- 6. กราฟรวม (ล็อคการปรับ และตั้งความสูงให้พอดีมือถือ) ---
        fig1 = make_subplots(specs=[[{"secondary_y": True}]])
        fig1.add_trace(go.Scatter(x=data['timestamp'], y=data['temp'], name="T", line=dict(color="#FF4B4B", width=2)), secondary_y=False)
        fig1.add_trace(go.Scatter(x=data['timestamp'], y=data['hum'], name="H", line=dict(color="#00D2FF", width=2)), secondary_y=True)

        fig1.update_layout(
            template="plotly_dark", height=280, 
            margin=dict(l=10, r=10, t=10, b=10),
            hovermode="x unified", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            showlegend=False, dragmode=False
        )
        fig1.update_xaxes(showgrid=True, gridcolor='rgba(255, 255, 255, 0.1)', fixedrange=True)
        fig1.update_yaxes(showgrid=True, gridcolor='rgba(255, 255, 255, 0.1)', fixedrange=True)
        fig1.update_yaxes(secondary_y=True, showgrid=False, fixedrange=True)
        
        st.plotly_chart(fig1, use_container_width=True, config={'displayModeBar': False})

        # --- 7. กราฟ Lux ---
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=data['timestamp'], y=data['lux'], fill='tozeroy', line=dict(color="#FFCC00", width=1.5), fillcolor='rgba(255, 204, 0, 0.1)'))
        fig2.update_layout(
            template="plotly_dark", height=160, 
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', dragmode=False
        )
        fig2.update_xaxes(showgrid=True, gridcolor='rgba(255, 255, 255, 0.1)', fixedrange=True)
        fig2.update_yaxes(showgrid=True, gridcolor='rgba(255, 255, 255, 0.1)', fixedrange=True)
        
        st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})

except Exception as e:
    st.error(f"Error: {e}")
