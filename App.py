import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os
from PIL import Image
import numpy as np

# --- การตั้งค่าเบื้องต้น ---
st.set_page_config(page_title="Xforce Fuel Tracker", layout="wide", page_icon="♻️")

# ฟังก์ชันบันทึกข้อมูลลง CSV
DB_FILE = "fuel_logs.csv"
def save_data(date, consumption, odometer, note):
    new_entry = pd.DataFrame([[date, consumption, odometer, note]], 
                             columns=["Date", "Consumption", "Odometer", "Note"])
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        df = pd.concat([df, new_entry], ignore_index=True)
    else:
        df = new_entry
    df.to_csv(DB_FILE, index=False)

# ฟังก์ชันโหลดข้อมูล
def load_data():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        df['Date'] = pd.to_datetime(df['Date'])
        return df.sort_values(by="Date")
    return pd.DataFrame(columns=["Date", "Consumption", "Odometer", "Note"])

# --- ส่วนการปรับแต่ง UI (Custom Styling) ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

# --- Sidebar: เคล็ดมงคลคนวันพุธกลางวัน ---
with st.sidebar:
    st.header("🔮 เคล็ดมงคลวันนี้")
    today_name = datetime.now().strftime('%A')
    st.write(f"สวัสดีวัน{today_name} ครับ")
    
    if today_name == "Wednesday":
        st.success("✨ วันพุธ: สีเขียวเหนี่ยวทรัพย์")
        st.write("วันนี้เหมาะกับการเจรจาและการเดินทางที่ราบรื่น")
    
    st.info("💡 **Tips สำหรับ Xforce:** ลองใช้ Eco Mode เมื่อขับในเมืองที่มีการจราจรหนาแน่น เพื่อปรับค่าเฉลี่ยให้ดีขึ้นครับ")

# --- ส่วนหน้าหลัก ---
st.title("🚗 Mitsubishi Xforce Ultimate Energy Tracker")
st.write("บันทึกและวิเคราะห์อัตราสิ้นเปลืองน้ำมันของคุณ")

# 1. ส่วนการรับข้อมูล (Input Zone)
col_in1, col_in2 = st.columns([1, 1])

with col_in1:
    st.subheader("📸 อัปโหลดรูปหน้าจอรถ")
    uploaded_file = st.file_uploader("เลือกรูปภาพ Dashboard...", type=['jpg', 'jpeg', 'png'])
    
    # ตัวแปรเริ่มต้น
    input_cons = 0.0
    input_odo = 0

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption='Dashboard Preview', use_container_width=True)
        st.info("🔍 ระบบตรวจพบข้อมูลอัตโนมัติ (Simulated OCR)")
        # ในระบบจริงจะใช้ easyocr ดึงค่า km/L จากรูปภาพ
        input_cons = 15.2 # ค่าสมมติที่ดึงได้
        input_odo = 2450  # ค่าสมมติที่ดึงได้

with col_in2:
    st.subheader("📝 ตรวจสอบและบันทึกข้อมูล")
    final_date = st.date_input("วันที่", datetime.now())
    final_cons = st.number_input("อัตราสิ้นเปลือง (km/L)", value=input_cons, step=0.1)
    final_odo = st.number_input("ระยะทางสะสม (Odometer - km)", value=input_odo)
    final_note = st.text_input("หมายเหตุ (เช่น เส้นทาง, โหมดการขับขี่)")

    if st.button("💾 บันทึกข้อมูลลงสมุดมงคล"):
        save_data(final_date, final_cons, final_odo, final_note)
        st.balloons()
        st.success("บันทึกข้อมูลเรียบร้อยแล้ว!")

st.divider()

# 2. ส่วนแสดงผล (Data Visualization)
df = load_data()

if not df.empty:
    # --- ส่วน Metric (ค่าเฉลี่ย) ---
    avg_total = df['Consumption'].mean()
    max_eff = df['Consumption'].max()
    last_odo = df['Odometer'].max()

    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric("ค่าเฉลี่ยรวมทั้งหมด", f"{avg_total:.2f} km/L")
    col_m2.metric("ประหยัดที่สุดที่เคยทำ", f"{max_eff:.1f} km/L")
    col_m3.metric("ระยะทางสะสมล่าสุด", f"{last_odo:,} km")

    # --- ส่วนกราฟ ---
    st.subheader("📈 แนวโน้มอัตราสิ้นเปลือง")
    fig = px.line(df, x='Date', y='Consumption', 
                  title='กราฟแสดงอัตราสิ้นเปลืองพลังงาน (km/L)',
                  markers=True, 
                  color_discrete_sequence=['#2E7D32']) # สีเขียวมงคล
    fig.update_layout(hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

    # --- ส่วนตารางข้อมูล ---
    with st.expander("📄 ดูประวัติการบันทึกทั้งหมด"):
        st.dataframe(df.sort_values(by="Date", ascending=False), use_container_width=True)
else:
    st.warning("ยังไม่มีข้อมูลในระบบ เริ่มบันทึกข้อมูลแรกของคุณได้เลย!")

# ฟุตเตอร์
st.caption(f"App Version 1.0 | พัฒนาเพื่อ Mitsubishi Xforce Ultimate | อัปเดตล่าสุด: {datetime.now().strftime('%d/%m/%Y')}")
