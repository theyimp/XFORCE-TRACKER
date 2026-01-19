import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

# --- Configuration ---
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

DB_CONS = "data_consumption.csv"
DB_REFILL = "data_refill.csv"

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
        df['Date'] = pd.to_datetime(df['Date'])
        return df
    return pd.DataFrame()

# --- UI Setup ---
st.set_page_config(page_title="Xforce Pro Tracker", layout="wide")
# ธีมสีเขียวมงคลสำหรับคนเกิดวันพุธกลางวัน
st.markdown("""
    <style>
    .stApp { background-color: #f0f7f0; }
    h1, h2, h3 { color: #1B5E20; font-family: 'Tahoma'; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; background-color: #e8f5e9; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

st.title("♻️ Xforce : Energy Tracker")

tab1, tab2, tab3 = st.tabs(["📊 บันทึกอัตราสิ้นเปลือง", "⛽ บันทึกการเติมน้ำมัน", "📈 สรุปผลและวิเคราะห์"])

# --- หน้า 1: บันทึกหน้าจอรถ (เพิ่ม Tarmac) ---
with tab1:
    st.header("📸 บันทึกข้อมูลจาก Dashboard")
    with st.form("form_cons"):
        col1, col2 = st.columns(2)
        with col1:
            img_file = st.file_uploader("อัปโหลดรูป Dashboard", type=['jpg', 'png'])
            d_date = st.date_input("วันที่บันทึก", datetime.now())
            # เพิ่มโหมด Tarmac เข้าไปในรายการ
            d_mode = st.selectbox("โหมดการขับขี่ที่ใช้", ["Normal", "Wet", "Gravel", "Mud", "Tarmac"])
        with col2:
            d_cons = st.number_input("อัตราสิ้นเปลือง (km/L)", min_value=0.0, step=0.1, format="%.1f")
            d_odo = st.number_input("เลขไมล์ปัจจุบัน (km)", min_value=0, step=1)
            d_route = st.text_input("เส้นทาง (เช่น ไปทำงาน, ออกทริป)")
        
        if st.form_submit_button("✅ บันทึกข้อมูล"):
            path = save_image(img_file, "dash")
            save_data({
                "Date": d_date, "Consumption": d_cons, "Odometer": d_odo, 
                "Mode": d_mode, "Route": d_route, "Image": path
            }, DB_CONS)
            st.success(f"บันทึกข้อมูลโหมด {d_mode} เรียบร้อย!")

# --- หน้า 2: บันทึกน้ำมัน ---
with tab2:
    st.header("⛽ บันทึกการเติมน้ำมัน")
    with st.form("form_refill"):
        col1, col2 = st.columns(2)
        with col1:
            slip_file = st.file_uploader("อัปโหลดสลิปน้ำมัน", type=['jpg', 'png'])
            r_date = st.date_input("วันที่เติม", datetime.now())
        with col2:
            r_price = st.number_input("ยอดเงินรวม (บาท)", min_value=0.0)
            r_liter = st.number_input("จำนวนลิตร (L)", min_value=0.0, step=0.01)
            r_odo = st.number_input("เลขไมล์ขณะเติม (km)", min_value=0)
        
        if st.form_submit_button("⛽ บันทึกการเติมน้ำมัน"):
            path = save_image(slip_file, "refill")
            save_data({
                "Date": r_date, "Price": r_price, "Liters": r_liter, 
                "Odometer": r_odo, "Image": path
            }, DB_REFILL)
            st.success("บันทึกประวัติการเติมน้ำมันเรียบร้อย!")

# --- หน้า 3: สรุปผลและกราฟ (เพิ่มการวิเคราะห์โหมด) ---
with tab3:
    df_c = load_data(DB_CONS)
    df_r = load_data(DB_REFILL)

    if not df_c.empty:
        st.header("📊 บทสรุปสมรรถนะ Xforce")
        
        # กราฟแท่งแยกตามโหมด (เพิ่มสีสำหรับ Tarmac)
        color_map = {
            "Normal": "#2E7D32", # เขียว
            "Wet": "#1976D2",    # ฟ้า
            "Gravel": "#FFA000", # ส้ม
            "Mud": "#795548",    # น้ำตาล
            "Tarmac": "#B71C1C"  # แดง (Performance)
        }
        
        fig = px.bar(df_c, x='Date', y='Consumption', color='Mode', 
                     title="อัตราสิ้นเปลืองแยกตามโหมด (km/L)",
                     color_discrete_map=color_map,
                     hover_data=['Route', 'Odometer'])
        st.plotly_chart(fig, use_container_width=True)

        # ตารางประวัติ
        st.subheader("📋 ประวัติการขับขี่ล่าสุด")
        st.dataframe(df_c.sort_values(by='Date', ascending=False), use_container_width=True)
    else:
        st.warning("กรุณาบันทึกข้อมูลในหน้าแรกก่อนเพื่อแสดงกราฟ")
