import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image
import datetime

# ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="Xforce Fuel Tracker", layout="wide")

# ส่วนหัวแอป
st.title("🚗 Mitsubishi Xforce Tracker")
st.write(f"สวัสดีครับ วันนี้วัน{datetime.datetime.now().strftime('%A')} ขอให้เดินทางปลอดภัยครับ")

# 1. ระบุวันที่
date_record = st.date_input("เลือกวันที่บันทึก", datetime.date.today())

# 2. อัปโหลดรูปภาพ
uploaded_file = st.file_uploader("📷 อัปโหลดรูปหน้าจอ Dashboard", type=['jpg', 'jpeg', 'png'])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption='รูปหน้าจอที่อัปโหลด', width=400)
    
    # ส่วนกรอกข้อมูล (ดึงค่าจากรูปมาใส่ตามรูปที่คุณส่งมา)
    st.subheader("📝 ยืนยันข้อมูลจากหน้าจอ")
    col1, col2 = st.columns(2)
    with col1:
        fuel = st.number_input("อัตราสิ้นเปลือง (km/L)", value=22.0, step=0.1)
    with col2:
        odo = st.number_input("เลขไมล์รวม (km)", value=342, step=1)

    if st.button("💾 บันทึกข้อมูล"):
        st.success(f"บันทึกค่า {fuel} km/L ของวันที่ {date_record} สำเร็จ!")
        st.balloons()

# 3. กราฟแสดงผล
st.divider()
st.subheader("📊 แนวโน้มการประหยัดพลังงาน")

# ข้อมูลตัวอย่าง (ในอนาคตสามารถเขียนให้อ่านจากไฟล์ CSV ได้ครับ)
chart_data = pd.DataFrame({
    'วันที่': pd.to_datetime(['2026-01-15', '2026-01-17', str(date_record)]),
    'km_L': [18.5, 19.8, 22.0]
})

fig = px.line(chart_data, x='วันที่', y='km_L', markers=True, title="ประวัติ km/L")
fig.update_traces(line_color='#166534') # สีเขียวมงคล
st.plotly_chart(fig, use_container_width=True)
