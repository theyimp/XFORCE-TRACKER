import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

# --- ตั้งค่าโฟลเดอร์เก็บรูป ---
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# --- ฟังก์ชันจัดการข้อมูล ---
DB_CONS = "data_consumption.csv"
DB_REFILL = "data_refill.csv"

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

# --- UI Setup ---
st.set_page_config(page_title="Xforce Pro Tracker", layout="wide")
st.markdown("<style>h1, h2, h3 { color: #2E7D32; }</style>", unsafe_allow_html=True)

st.title("🚗 Xforce Energy & Photo Tracker")

tab1, tab2, tab3 = st.tabs(["📊 บันทึกอัตราสิ้นเปลือง", "⛽ บันทึกการเติมน้ำมัน", "📈 สรุปและประวัติ"])

# --- หน้า 1: บันทึกหน้าจอรถ ---
with tab1:
    st.header("📸 บันทึกหน้าจอ Dashboard")
    with st.form("form_cons"):
        col1, col2 = st.columns(2)
        with col1:
            img_file = st.file_uploader("อัปโหลดรูปหน้าจอรถ", type=['jpg', 'png'])
            d_date = st.date_input("วันที่", datetime.now())
        with col2:
            d_cons = st.number_input("อัตราสิ้นเปลือง (km/L)", step=0.1)
            d_odo = st.number_input("เลขไมล์ (km)", step=1)
        
        if st.form_submit_button("✅ บันทึกข้อมูลและรูปภาพ"):
            path = save_image(img_file, "dash")
            save_data({"Date": d_date, "Consumption": d_cons, "Odometer": d_odo, "Image": path}, DB_CONS)
            st.success(f"บันทึกสำเร็จ! เก็บรูปไว้ที่ {path}")

# --- หน้า 2: บันทึกน้ำมัน ---
with tab2:
    st.header("⛽ บันทึกการเติมน้ำมัน & สลิป")
    with st.form("form_refill"):
        col1, col2 = st.columns(2)
        with col1:
            slip_file = st.file_uploader("อัปโหลดรูปสลิปน้ำมัน", type=['jpg', 'png'])
            r_date = st.date_input("วันที่เติม", datetime.now())
        with col2:
            r_price = st.number_input("ยอดเงิน (บาท)", step=1.0)
            r_liter = st.number_input("จำนวนลิตร", step=0.01)
            r_odo = st.number_input("เลขไมล์ขณะเติม", step=1)
        
        if st.form_submit_button("⛽ บันทึกข้อมูลและสลิป"):
            path = save_image(slip_file, "refill")
            save_data({"Date": r_date, "Price": r_price, "Liters": r_liter, "Odometer": r_odo, "Image": path}, DB_REFILL)
            st.success("บันทึกข้อมูลและสลิปเรียบร้อย!")

# --- หน้า 3: สรุปและแสดงรูปย้อนหลัง ---
with tab3:
    st.header("📈 สรุปผลและประวัติการเดินทาง")
    
    df_c = pd.read_csv(DB_CONS) if os.path.exists(DB_CONS) else pd.DataFrame()
    df_r = pd.read_csv(DB_REFILL) if os.path.exists(DB_REFILL) else pd.DataFrame()

    if not df_c.empty:
        st.subheader("📋 ประวัติอัตราสิ้นเปลือง")
        # แสดงตารางพร้อมปุ่มดูรูป
        for i, row in df_c.iterrows():
            with st.expander(f"บันทึกวันที่ {row['Date']} | {row['Consumption']} km/L"):
                c1, c2 = st.columns([1, 2])
                with c1:
                    if pd.notnull(row['Image']) and os.path.exists(row['Image']):
                        st.image(row['Image'], caption="รูปหน้าจอรถ", use_container_width=True)
                    else:
                        st.write("ไม่มีรูปภาพ")
                with c2:
                    st.write(f"**เลขไมล์:** {row['Odometer']:,} km")
                    st.write(f"**อัตราสิ้นเปลือง:** {row['Consumption']} km/L")

    st.divider()
    
    if not df_r.empty:
        st.subheader("⛽ ประวัติการเติมน้ำมัน")
        for i, row in df_r.iterrows():
            with st.expander(f"เติมวันที่ {row['Date']} | {row['Price']} บาท"):
                c1, c2 = st.columns([1, 2])
                with c1:
                    if pd.notnull(row['Image']) and os.path.exists(row['Image']):
                        st.image(row['Image'], caption="รูปสลิป", use_container_width=True)
                    else:
                        st.write("ไม่มีรูปภาพ")
                with c2:
                    st.write(f"**จำนวนเงิน:** {row['Price']} บาท")
                    st.write(f"**จำนวนลิตร:** {row['Liters']} L")
                    st.write(f"**เลขไมล์:** {row['Odometer']:,} km")

# --- เคล็ดมงคล (Sidebar) ---
st.sidebar.title("🔮 พุธกลางวันมงคล")
st.sidebar.info("อย่าลืมเก็บสลิปน้ำมันไว้ในที่ร่ม เพื่อเคล็ดลับด้านการเงินที่ไหลลื่นครับ!")
