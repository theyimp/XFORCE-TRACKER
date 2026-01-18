import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image
import datetime
import os

# ตั้งค่าหน้าเว็บ (ธีมสีเขียวเหนี่ยวทรัพย์ วันพุธ)
st.set_page_config(page_title="Xforce Fuel Tracker", layout="wide")

# ไฟล์เก็บข้อมูล
DATA_FILE = 'fuel_data.csv'

# ฟังก์ชันโหลดและบันทึก
def load_data():
    if not os.path.exists(DATA_FILE):
        return pd.DataFrame(columns=['Date', 'Km_per_Liter', 'Odometer', 'Note'])
    return pd.read_csv(DATA_FILE)

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

st.title("🚗 Mitsubishi Xforce: บันทึกเลขไมล์มงคล")

# --- ส่วนที่ 1: กรอกข้อมูลใหม่ (พร้อมที่อัปโหลดรูป) ---
with st.expander("📸 เพิ่มข้อมูลใหม่ (กดที่นี่เพื่อใส่รูป)", expanded=True):
    
    # [จุดที่ใส่รูปอยู่ตรงนี้ครับ]
    uploaded_file = st.file_uploader("1. อัปโหลดรูปหน้าจอ Dashboard ที่นี่", type=['jpg', 'jpeg', 'png'])
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        # แสดงรูปเพื่อให้ดูตัวเลขง่ายๆ ตอนกรอก
        st.image(image, caption='รูปหน้าจอที่อัปโหลด', width=400)
        st.info("💡 ดูตัวเลขจากรูปด้านบน แล้วกรอกลงช่องข้างล่างได้เลยครับ")

    st.divider()
    
    # ช่องกรอกข้อมูล
    col1, col2 = st.columns(2)
    with col1:
        date_input = st.date_input("2. วันที่", datetime.date.today())
        fuel_input = st.number_input("3. อัตราสิ้นเปลือง (km/L)", value=22.0, step=0.1)
    with col2:
        odo_input = st.number_input("4. เลขไมล์ (km)", value=0, step=1)
        note_input = st.text_input("5. บันทึกช่วยจำ", "ขับไปทำงาน")

    if st.button("💾 บันทึกข้อมูล"):
        df = load_data()
        new_row = pd.DataFrame({
            'Date': [date_input],
            'Km_per_Liter': [fuel_input],
            'Odometer': [odo_input],
            'Note': [note_input]
        })
        df = pd.concat([df, new_row], ignore_index=True)
        save_data(df)
        st.success("บันทึกเรียบร้อย! ขอให้รวยๆ ครับ")
        st.rerun()

# --- ส่วนที่ 2: ตารางแก้ไขข้อมูล ---
st.subheader("📋 ประวัติการบันทึก (แก้ไข/ลบ ได้ที่นี่)")
df = load_data()
edited_df = st.data_editor(df, num_rows="dynamic", key="editor", use_container_width=True)

if st.button("ยืนยันการแก้ไขตาราง"):
    save_data(edited_df)
    st.success("แก้ไขข้อมูลเรียบร้อย!")
    st.rerun()

# --- ส่วนที่ 3: กราฟ ---
if not df.empty:
    st.divider()
    st.subheader("📈 กราฟความประหยัด")
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date')
    fig = px.line(df, x='Date', y='Km_per_Liter', markers=True, title="สถิติ km/L")
    fig.update_traces(line_color='#166534')
    st.plotly_chart(fig, use_container_width=True)
