import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
from PIL import Image
# หมายเหตุ: ในการใช้งานจริงต้องติดตั้ง easyocr: pip install easyocr

st.set_page_config(page_title="Xforce Fuel Tracker", layout="wide")

# ส่วนหัวแอปและเคล็ดมงคล
st.title("🚗 Mitsubishi Xforce Energy Tracker")
st.write(f"สวัสดีครับ วันนี้วัน{datetime.datetime.now().strftime('%A')} ขอให้เป็นวันที่ขับขี่ปลอดภัยและประหยัดพลังงานนะครับ")

# 1. ส่วนอัปโหลดรูปภาพ
uploaded_file = st.file_uploader("อัปโหลดรูปหน้าจอ Dashboard", type=['jpg', 'png', 'jpeg'])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption='รูปที่อัปโหลด', width=300)
    
    # ส่วนนี้คือ Logic การดึงข้อมูล (Simulated OCR)
    # ในแอปจริงจะใช้ easyocr.Reader(['en']).readtext(image)
    st.info("ระบบกำลังดึงข้อมูลจากหน้าจอ Ultimate Display...")
    
    # สมมติค่าที่ดึงได้จาก OCR
    avg_consumption = st.number_input("อัตราสิ้นเปลือง (km/L)", value=15.5)
    distance = st.number_input("ระยะทางสะสม (km)", value=1250)
    date = st.date_input("วันที่บันทึก", datetime.date.today())

    if st.button("บันทึกข้อมูล"):
        # บันทึกลง CSV
        new_data = {"Date": [date], "Consumption": [avg_consumption], "Odometer": [distance]}
        df_new = pd.DataFrame(new_data)
        # (Logic การ append ไฟล์ CSV)
        st.success("บันทึกข้อมูลเรียบร้อยแล้ว!")

---

# 2. กราฟแสดงผล
st.subheader("📊 แนวโน้มอัตราสิ้นเปลือง")
# สมมติข้อมูลย้อนหลัง
data = {
    'Date': pd.to_datetime(['2026-01-10', '2026-01-12', '2026-01-15', '2026-01-18']),
    'Consumption': [14.2, 15.8, 13.5, 16.2]
}
df = pd.DataFrame(data)
fig = px.line(df, x='Date', y='Consumption', title='ประวัติการสิ้นเปลือง (km/L)', markers=True)
st.plotly_chart(fig)
