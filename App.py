import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image
import datetime
import os
import easyocr
import numpy as np

# ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="Xforce Auto-Reader", layout="wide")

# โหลด Reader (เก็บไว้ใน Cache เพื่อไม่ให้โหลดใหม่ทุกครั้ง)
@st.cache_resource
def load_ocr():
    return easyocr.Reader(['en'])

reader = load_ocr()
DATA_FILE = 'fuel_data.csv'

def load_data():
    if not os.path.exists(DATA_FILE):
        return pd.DataFrame(columns=['Date', 'Km_per_Liter', 'Odometer', 'Note'])
    return pd.read_csv(DATA_FILE)

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# แสดงรูปรถสีทองนำโชค
st.title("Xforce Ultimate X: Fuel Tracker")
st.image("https://img.imageboss.me/autoverse/width/1200/20230811105934_Mitsubishi-Xforce-18.jpg", width=500) 

# --- ส่วนอัปโหลดและอ่านรูป ---
with st.expander("📸 ถ่ายรูปหน้าจอเพื่ออ่านข้อมูลอัตโนมัติ", expanded=True):
    uploaded_file = st.file_uploader("เลือกรูป Dashboard", type=['jpg', 'jpeg', 'png'])
    
    # ค่าเริ่มต้น
    fuel_val = 22.0
    odo_val = 0
    
    if uploaded_file:
        img = Image.open(uploaded_file)
        st.image(img, caption='กำลังวิเคราะห์ข้อมูล...', width=400)
        
        # แปลงรูปเป็นรูปแบบที่ OCR อ่านได้
        img_np = np.array(img)
        
        with st.spinner('ระบบกำลังเพ่งมองตัวเลขมงคล...'):
            results = reader.readtext(img_np)
            
            # Logic ค้นหาตัวเลข km/L และ km
            for (bbox, text, prob) in results:
                text = text.lower()
                if 'km/l' in text or '.' in text:
                    try:
                        # พยายามดึงตัวเลขที่มีจุดทศนิยม
                        num = float(''.join(c for c in text if c.isdigit() or c == '.'))
                        if num < 50: fuel_val = num
                    except: pass
                if 'km' in text and 'l' not in text:
                    try:
                        # พยายามดึงตัวเลขระยะทางสะสม
                        num = int(''.join(c for c in text if c.isdigit()))
                        if num > 100: odo_val = num
                    except: pass

        st.success(f"🤖 อ่านเสร็จแล้ว! ตรวจพบค่าประมาณ: {fuel_val} km/L และเลขไมล์ {odo_val} km")

    # ช่องยืนยันข้อมูล (จะเปลี่ยนตามที่ OCR อ่านได้)
    col1, col2 = st.columns(2)
    with col1:
        date_record = st.date_input("วันที่", datetime.date.today())
        fuel_input = st.number_input("ยืนยัน km/L", value=fuel_val)
    with col2:
        odo_input = st.number_input("ยืนยันเลขไมล์ (km)", value=odo_val)
        note_input = st.text_input("บันทึก", "บันทึกอัตโนมัติ")

    if st.button("💾 บันทึกข้อมูลลงสมุด"):
        df = load_data()
        new_row = pd.DataFrame({'Date': [date_record], 'Km_per_Liter': [fuel_input], 'Odometer': [odo_input], 'Note': [note_input]})
        df = pd.concat([df, new_row], ignore_index=True)
        save_data(df)
        st.balloons()
        st.rerun()

# --- ตารางและกราฟแสดงผล ---
df = load_data()
st.subheader("📋 ประวัติข้อมูล")
st.data_editor(df, num_rows="dynamic", use_container_width=True)
