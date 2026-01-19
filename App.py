import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

# --- Configuration & Dark Mode Styling ---
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

DB_CONS = "data_consumption.csv"
DB_REFILL = "data_refill.csv"

st.set_page_config(page_title="Xforce Dark Tracker", layout="wide")

# ปรับแต่ง CSS ให้เป็น Dark Mode และโทนสีเขียวมงคล
st.markdown("""
    <style>
    /* พื้นหลังหลักสีดำ */
    .stApp {
        background-color: #0E1117;
        color: #FFFFFF;
    }
    /* ปรับแต่ง Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #161B22;
        border-radius: 10px 10px 0 0;
        padding: 5px;
    }
    .stTabs [data-baseweb="tab"] {
        color: #8B949E;
    }
    .stTabs [data-baseweb="tab--active"] {
        color: #2ECC71 !important;
        border-bottom-color: #2ECC71 !important;
    }
    /* ปรับแต่ง Input Box */
    input, select, textarea {
        background-color: #0D1117 !important;
        color: white !important;
        border: 1px solid #30363D !important;
    }
    /* หัวข้อสีเขียว */
    h1, h2, h3 {
        color: #2ECC71 !important;
    }
    /* ปุ่มมงคล */
    .stButton>button {
        width: 100%;
        background-color: #2ECC71;
        color: black;
        font-weight: bold;
        border: none;
    }
    .stButton>button:hover {
        background-color: #27AE60;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Helper Functions ---
def save_image(uploaded_file, prefix):
    if uploaded_file is not None:
        filename = f"{prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        save_path = os.path.join(UPLOAD_DIR, filename)
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return save_path
    return ""

def save_data(data, filename):
    df_new = pd.DataFrame([data])
    if os.path.exists(filename):
        df_old = pd.read_csv(filename)
        df_final = pd.concat([df_old, df_new], ignore_index=True)
    else:
        df_final = df_new
    df_final.to_csv(filename, index=False)

def load_data(filename):
    if os.path.exists(filename):
        df = pd.read_csv(filename)
        if not df.empty:
            df['Date'] = pd.to_datetime(df['Date'])
            return df
    return pd.DataFrame()

# --- Header Section (ข้อมูลมงคลย้ายมาไว้ที่นี่) ---
st.title("🚗 XFORCE ULTIMATE ENERGY PRO")
c_top1, c_top2 = st.columns([2, 1])
with c_top1:
    st.write(f"📅 วันนี้: วัน{datetime.now().strftime('%A')} (พุธกลางวันมงคล)")
with c_top2:
    st.markdown("🟢 **สีมงคล:** เขียวเหนี่ยวทรัพย์ | **เลขนำโชค:** 4, 6")

# --- Main Interface ---
tab1, tab2, tab3 = st.tabs(["📊 บันทึกอัตราสิ้นเปลือง", "⛽ บันทึกการเติมน้ำมัน", "📈 สรุปผลและประวัติ"])

# --- หน้า 1: บันทึกหน้าจอรถ ---
with tab1:
    st.subheader("📸 บันทึกข้อมูล Dashboard")
    with st.form("form_cons"):
        col1, col2 = st.columns(2)
        with col1:
            img_file = st.file_uploader("อัปโหลดรูปหน้าจอรถ", type=['jpg', 'png'])
            d_date = st.date_input("วันที่บันทึก", datetime.now())
            d_mode = st.selectbox("โหมดการขับขี่", ["Normal", "Wet", "Gravel", "Mud", "Tarmac"])
        with col2:
            d_cons = st.number_input("อัตราสิ้นเปลือง (km/L)", step=0.1, format="%.1f")
            d_odo = st.number_input("เลขไมล์ปัจจุบัน (km)", step=1)
            d_route = st.text_input("เส้นทาง (เช่น บ้าน-ที่ทำงาน)")
        
        if st.form_submit_button("SAVE DATA"):
            path = save_image(img_file, "dash")
            save_data({"Date": d_date, "Consumption": d_cons, "Odometer": d_odo, "Mode": d_mode, "Route": d_route, "Image": path}, DB_CONS)
            st.success("บันทึกข้อมูลสำเร็จ")

# --- หน้า 2: บันทึกน้ำมัน ---
with tab2:
    st.subheader("⛽ บันทึกการเติมน้ำมัน")
    with st.form("form_refill"):
        col1, col2 = st.columns(2)
        with col1:
            slip_file = st.file_uploader("อัปโหลดสลิปน้ำมัน", type=['jpg', 'png'])
            r_date = st.date_input("วันที่เติม", datetime.now())
        with col2:
            r_price = st.number_input("ยอดเงินรวม (บาท)", step=1.0)
            r_liter = st.number_input("จำนวนลิตร (L)", step=0.01)
            r_odo = st.number_input("เลขไมล์ขณะเติม (km)", step=1)
        
        if st.form_submit_button("SAVE REFILL"):
            path = save_image(slip_file, "refill")
            save_data({"Date": r_date, "Price": r_price, "Liters": r_liter, "Odometer": r_odo, "Image": path}, DB_REFILL)
            st.success("บันทึกการเติมน้ำมันสำเร็จ")

# --- หน้า 3: สรุปผลและวิเคราะห์ ---
with tab3:
    df_c = load_data(DB_CONS)
    df_r = load_data(DB_REFILL)

    if not df_c.empty:
        # Metric Cards
        avg_v = df_c['Consumption'].mean()
        m1, m2 = st.columns(2)
        m1.metric("AVG CONSUMPTION", f"{avg_v:.2f} km/L")
        m2.metric("LATEST ODO", f"{df_c['Odometer'].max():,} km")

        # กราฟ Dark Theme
        color_map = {"Normal": "#2ECC71", "Wet": "#3498DB", "Gravel": "#F1C40F", "Mud": "#E67E22", "Tarmac": "#E74C3C"}
        fig = px.bar(df_c, x='Date', y='Consumption', color='Mode', 
                     title="Energy Efficiency by Mode",
                     template="plotly_dark", color_discrete_map=color_map)
        st.plotly_chart(fig, use_container_width=True)

        # ประวัติย้อนหลัง (Expander)
        st.subheader("📜 HISTORY")
        for i, row in df_c.iloc[::-1].iterrows():
            with st.expander(f"{row['Date'].date()} | {row['Mode']} | {row['Consumption']} km/L"):
                c1, c2 = st.columns([1, 2])
                with c1:
                    if pd.notnull(row['Image']) and os.path.exists(row['Image']):
                        st.image(row['Image'], use_container_width=True)
                with c2:
                    st.write(f"**เส้นทาง:** {row['Route']}")
                    st.write(f"**เลขไมล์:** {row['Odometer']:,} km")
    else:
        st.info("กรุณาเพิ่มข้อมูลเพื่อแสดงผลวิเคราะห์")
