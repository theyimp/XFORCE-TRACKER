import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image
import datetime
import os
import easyocr
import numpy as np

# ตั้งค่าหน้าเว็บธีมสีเขียวทองมงคล
st.set_page_config(page_title="Xforce Gold Tracker", layout="wide")

# ฟังก์ชันโหลด AI สำหรับอ่านรูป
@st.cache_resource
def load_ocr():
    return easyocr.Reader(['en'])

# ไฟล์เก็บข้อมูล
DATA_FILE = 'fuel_data.csv'

def load_data():
    if not os.path.exists(DATA_FILE):
        return pd.DataFrame(columns=['Date', 'Km_per_Liter', 'Odometer', 'Note'])
    df = pd.read_csv(DATA_FILE)
    df['Date'] = pd.to_datetime(df['Date']).dt.date # จัดรูปแบบวันที่
    return df

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

st.title("🚗 Mitsubishi Xforce Ultimate (Gold Edition)")
st.write(f"สวัสดีวัน{datetime.datetime.now().strftime('%A')} ขอให้เดินทางปลอดภัยและประหยัดน้ำมันครับ")

# --- ส่วนที่ 1: บันทึกข้อมูลใหม่พร้อม AI อ่านรูป ---
with st.expander("📸 ขั้นตอนที่ 1: อัปโหลดรูปหน้าจอเพื่ออ่านข้อมูล", expanded=True):
    uploaded_file = st.file_uploader("เลือกภาพถ่าย Dashboard", type=['jpg', 'jpeg', 'png'])
    
    fuel_val = 22.0
    odo_val = 0
    
    if uploaded_file:
        img = Image.open(uploaded_file)
        st.image(img, caption='รูปที่ส่งมา', width=300)
        
        if st.button("🤖 กดเพื่อให้ AI ช่วยอ่านตัวเลข"):
            reader = load_ocr()
            img_np = np.array(img)
            with st.spinner('กำลังประมวลผล...'):
                results = reader.readtext(img_np)
                for (bbox, text, prob) in results:
                    text_clean = ''.join(c for c in text if c.isdigit() or c == '.')
                    if '.' in text_clean:
                        try: fuel_val = float(text_clean)
                        except: pass
                    elif len(text_clean) >= 3:
                        try: odo_val = int(text_clean)
                        except: pass
            st.success(f"AI อ่านค่าได้ประมาณ: {fuel_val} km/L และไมล์ {odo_val} km")

    st.divider()
    st.subheader("📝 ขั้นตอนที่ 2: ตรวจสอบและบันทึก")
    c1, c2 = st.columns(2)
    with c1:
        date_rec = st.date_input("วันที่", datetime.date.today())
        fuel_in = st.number_input("อัตราสิ้นเปลือง (km/L)", value=float(fuel_val))
    with c2:
        odo_in = st.number_input("เลขไมล์รวม (km)", value=int(odo_val))
        note_in = st.text_input("หมายเหตุ", "บันทึกจากรูป")

    if st.button("💾 ยืนยันบันทึกข้อมูล"):
        df = load_data()
        new_data = pd.DataFrame({'Date': [date_rec], 'Km_per_Liter': [fuel_in], 'Odometer': [odo_in], 'Note': [note_input]})
        df = pd.concat([df, new_data], ignore_index=True)
        save_data(df)
        st.balloons()
        st.rerun()

# --- ส่วนที่ 2: การจัดการข้อมูล (แก้ไข/ลบ) ---
st.divider()
st.subheader("⚙️ การจัดการข้อมูลประวัติ")

df_history = load_data()

if not df_history.empty:
    # 1. แก้ไขข้อมูลผ่านตาราง
    st.write("💡 คลิกที่ช่องเพื่อแก้ไขเลข แล้วกด 'บันทึกการแก้ไข' ด้านล่าง")
    edited_df = st.data_editor(df_history, num_rows="dynamic", use_container_width=True, key="data_edit")
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("✅ บันทึกการแก้ไขทั้งหมด"):
            save_data(edited_df)
            st.success("อัปเดตข้อมูลสำเร็จ!")
            st.rerun()
            
    # 2. ลบข้อมูล (เลือกตามวันที่หรือแถว)
    with col_btn2:
        if st.button("🗑️ ลบข้อมูลแถวที่เลือก"):
            # ในโหมด data_editor การลบทำได้โดยเลือกแถวแล้วกด Delete ที่คีย์บอร์ด 
            # หรือใช้ผลลัพธ์จาก edited_df บันทึกทับได้เลย
            save_data(edited_df)
            st.warning("แถวที่ถูกลบออกไปจะหายไปจากระบบเมื่อกดปุ่มบันทึก")
            st.rerun()

    # --- ส่วนที่ 3: กราฟ ---
    st.divider()
    st.subheader("📈 แนวโน้มความประหยัด")
    df_chart = df_history.sort_values('Date')
    fig = px.line(df_chart, x='Date', y='Km_per_Liter', markers=True, 
                  title="สถิติการใช้พลังงาน Xforce", color_discrete_sequence=['#D4AF37']) # สีทอง
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("ยังไม่มีข้อมูลบันทึกในระบบ")
