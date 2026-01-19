import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

# --- ตั้งค่าพื้นฐาน ---
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

DB_CONS = "data_consumption.csv"
DB_REFILL = "data_refill.csv"

# --- ฟังก์ชันจัดการข้อมูล ---
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
        return pd.read_csv(filename)
    return pd.DataFrame()

# --- UI Setup ---
st.set_page_config(page_title="Xforce Pro Tracker", layout="wide")
st.markdown("<style>h1, h2, h3 { color: #2E7D32; } .stApp { background-color: #fdfdfd; }</style>", unsafe_allow_html=True)

# ส่วนหัวแอปพร้อมเคล็ดมงคล
st.title("🚗 Xforce Ultimate Energy Tracker")
st.sidebar.title("🔮 มงคลพุธกลางวัน")
st.sidebar.success("🟢 วันนี้เน้นสีเขียว เสริมความราบรื่น")
st.sidebar.info("Tips: การบันทึกข้อมูลหลังขับขี่ ช่วยให้เราเห็นพฤติกรรมเพื่อการประหยัดที่มากขึ้นครับ")

tab1, tab2, tab3 = st.tabs(["📊 บันทึกอัตราสิ้นเปลือง", "⛽ บันทึกการเติมน้ำมัน", "📈 สรุปผลและประวัติ"])

# --- หน้า 1: บันทึกหน้าจอรถ ---
with tab1:
    st.header("📸 บันทึกข้อมูล Dashboard")
    with st.form("form_cons"):
        col1, col2 = st.columns(2)
        with col1:
            img_file = st.file_uploader("อัปโหลดรูปหน้าจอรถ", type=['jpg', 'png'])
            d_date = st.date_input("วันที่", datetime.now())
            # เพิ่มโหมดการขับขี่ของ Xforce
            d_mode = st.selectbox("โหมดการขับขี่", ["Normal", "Wet", "Gravel", "Mud"])
        with col2:
            d_cons = st.number_input("อัตราสิ้นเปลือง (km/L)", step=0.1, format="%.1f")
            d_odo = st.number_input("เลขไมล์ปัจจุบัน (km)", step=1)
            d_route = st.text_input("เส้นทาง/หมายเหตุ (เช่น บ้าน-อโศก, ไปห้าง)")
        
        if st.form_submit_button("✅ บันทึกข้อมูล"):
            path = save_image(img_file, "dash")
            save_data({
                "Date": d_date, "Consumption": d_cons, "Odometer": d_odo, 
                "Mode": d_mode, "Route": d_route, "Image": path
            }, DB_CONS)
            st.success(f"บันทึกข้อมูลโหมด {d_mode} เรียบร้อยแล้ว!")

# --- หน้า 2: บันทึกน้ำมัน ---
with tab2:
    st.header("⛽ บันทึกการเติมน้ำมัน")
    with st.form("form_refill"):
        col1, col2 = st.columns(2)
        with col1:
            slip_file = st.file_uploader("อัปโหลดสลิปน้ำมัน", type=['jpg', 'png'])
            r_date = st.date_input("วันที่เติม", datetime.now())
            r_type = st.selectbox("ประเภทน้ำมัน", ["Gasohol 95", "Gasohol 91", "E20", "Power 95"])
        with col2:
            r_price = st.number_input("ยอดเงินรวม (บาท)", step=1.0)
            r_liter = st.number_input("จำนวนลิตร", step=0.01)
            r_odo = st.number_input("เลขไมล์ขณะเติม (km)", step=1)
            r_note = st.text_input("หมายเหตุ (เช่น ชื่อปั๊ม, เส้นทางหลักก่อนเติม)")
        
        if st.form_submit_button("⛽ บันทึกการเติมน้ำมัน"):
            path = save_image(slip_file, "refill")
            save_data({
                "Date": r_date, "Price": r_price, "Liters": r_liter, 
                "Odometer": r_odo, "Type": r_type, "Route": r_note, "Image": path
            }, DB_REFILL)
            st.success("บันทึกประวัติการเติมน้ำมันแล้ว!")

# --- หน้า 3: สรุปและประวัติ ---
with tab3:
    st.header("📈 วิเคราะห์และประวัติย้อนหลัง")
    df_c = load_data(DB_CONS)
    df_r = load_data(DB_REFILL)

    if not df_c.empty:
        # ส่วน Metric สรุป
        avg_val = df_c['Consumption'].mean()
        st.metric("ค่าเฉลี่ยความประหยัดรวม", f"{avg_val:.2f} km/L")
        
        # กราฟแยกตามโหมด
        fig = px.bar(df_c, x='Date', y='Consumption', color='Mode', 
                     title="อัตราสิ้นเปลืองแยกตามโหมดและวันที่",
                     hover_data=['Route', 'Odometer'],
                     color_discrete_map={"Normal": "#2E7D32", "Wet": "#1976D2", "Gravel": "#FFA000", "Mud": "#795548"})
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("📋 รายละเอียดประวัติการขับขี่")
        for i, row in df_c.iloc[::-1].iterrows(): # แสดงจากใหม่ไปเก่า
            with st.expander(f"📅 {row['Date']} | {row['Mode']} | {row['Consumption']} km/L | {row['Route']}"):
                c1, c2 = st.columns([1, 2])
                with c1:
                    if pd.notnull(row['Image']) and os.path.exists(row['Image']):
                        st.image(row['Image'], use_container_width=True)
                with c2:
                    st.write(f"**โหมดที่ใช้:** {row['Mode']}")
                    st.write(f"**เส้นทาง:** {row['Route']}")
                    st.write(f"**เลขไมล์:** {row['Odometer']:,} km")
                    st.write(f"**อัตราสิ้นเปลือง:** {row['Consumption']} km/L")
    else:
        st.warning("ยังไม่มีข้อมูลเพื่อแสดงผล")
