import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- 1. การตั้งค่าหน้าจอ ---
st.set_page_config(page_title="Smart Farm Dashboard", layout="wide")

# --- 2. CSS ปรับจูนระดับให้เท่ากันเป๊ะ (Pixel Perfect) ---
st.markdown("""
<style>
    [data-testid="stMetric"] { padding-left: 20px !important; border-left: 3px solid #4E4E4E; }
    div[data-testid="stMetricValue"] { text-align: left !important; justify-content: flex-start !important; font-size: 32px !important; }
    div[data-testid="stMetricLabel"] { text-align: left !important; margin-bottom: -10px !important; }
    
    /* ปรับระดับ Date Input และ Info Box ให้ขนานกันพอดี */
    .stDateInput { padding-top: 0px !important; }
    div.stAlert {
        margin-top: -2px !important;      /* ดันขึ้นเล็กน้อยเพื่อให้ขอบล่างเสมอพิกเซล */
        padding-top: 8px !important;      /* ปรับความหนาภายในให้เท่าช่อง Input */
        padding-bottom: 8px !important;
        line-height: 1.2 !important;
        min-height: 42px !important;
        display: flex;
        align-items: center;
    }
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

    # --- 4. ส่วนหัว Dashboard ---
    with st.container():
        c1, c2 = st.columns([1, 4], gap="small", vertical_alignment="center")
        
        with c1:
            selected_date = st.date_input(
                "📅 เลือกวันที่",
                value=max_date,
                min_value=min_date,
                max_value=max_date,
                label_visibility="collapsed"
            )

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

        # --- 6. กราฟอุณหภูมิและความชื้น ---
        st.subheader("📊 กราฟอุณหภูมิและความชื้น (แยกแกนซ้าย-ขวา)")
        fig1 = make_subplots(specs=[[{"secondary_y": True}]])
        fig1.add_trace(go.Scatter(x=data['timestamp'], y=data['temp'], name="อุณหภูมิ (°C)", line=dict(color="#FF4B4B", width=3)), secondary_y=False)
        fig1.add_trace(go.Scatter(x=data['timestamp'], y=data['hum'], name="ความชื้น (%)", line=dict(color="#00D2FF", width=3)), secondary_y=True)

        fig1.update_layout(
            template="plotly_dark", 
            hovermode="x unified", 
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=0, t=30, b=0),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        fig1.update_yaxes(title_text="อุณหภูมิ (°C)", showgrid=True, gridcolor='rgba(255, 255, 255, 0.1)', secondary_y=False)
        fig1.update_yaxes(title_text="ความชื้น (%)", showgrid=False, secondary_y=True)
        st.plotly_chart(fig1, use_container_width=True)

        # --- 7. กราฟความเข้มแสง (Lux) แบบใหม่ให้สอดคล้องกัน ---
        st.subheader("☀️ กราฟความเข้มแสง (Lux)")
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=data['timestamp'], 
            y=data['lux'], 
            name="แสง (Lux)",
            fill='tozeroy', # ทำเป็น Area Chart
            line=dict(color="#FFCC00", width=2),
            fillcolor='rgba(255, 204, 0, 0.2)'
        ))

        fig2.update_layout(
            template="plotly_dark",
            hovermode="x unified",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=0, t=30, b=0),
            showlegend=False
        )
        fig2.update_xaxes(showgrid=True, gridcolor='rgba(255, 255, 255, 0.1)')
        fig2.update_yaxes(title_text="Lux", showgrid=True, gridcolor='rgba(255, 255, 255, 0.1)')
        
        st.plotly_chart(fig2, use_container_width=True)

except Exception as e:
    st.error(f"⚠️ เกิดข้อผิดพลาด: {e}")
