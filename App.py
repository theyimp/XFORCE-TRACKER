import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image
import datetime
import os

# ตั้งค่าธีมสีทองมงคล
st.set_page_config(page_title="Xforce Gold Tracker", layout="wide")

DATA_FILE = 'fuel_data.csv'

def load_data():
    if not os.path.exists(DATA_FILE):
        return pd.DataFrame(columns=['Date', 'Km_per_Liter', 'Odometer', 'Note'])
    df = pd.read_csv(DATA_FILE)
    return df

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# ส่วนหัว: รูปรถสีทองมงคล
st.title("Mitsubishi Xforce Ultimate X")
st.write(f"📅 วันนี้วัน{datetime.datetime.now().strftime('%A')} | Victor ")

# --- ส่วนที่ 1: อัปโหลดรูปเพื่อดูและกรอก ---
with st.expander("📸 บันทึกข้อมูลใหม่ (อัปโหลดรูปหน้าจอ)", expanded=True):
    uploaded_file = st.file_uploader("เลือกรูป Dashboard", type=['jpg', 'jpeg', 'png'])
    
    if uploaded_file:
        img = Image.open(uploaded_file)
        st.image(img, caption='ดูตัวเลขจากรูปนี้แล้วกรอกด้านล่างครับ', width=400)
    
    col1, col2 = st.columns(2)
    with col1:
        date_in = st.date_input("วันที่", datetime.date.today())
        fuel_in = st.number_input("อัตราสิ้นเปลือง (km/L)", value=22.0, step=0.1)
    with col2:
        odo_in = st.number_input("เลขไมล์รวม (km)", value=0, step=1)
        note_in = st.text_input("หมายเหตุ", "ขับขี่ปกติ")

    if st.button("💾 บันทึกข้อมูล"):
        df = load_data()
        new_row = pd.DataFrame({'Date': [str(date_in)], 'Km_per_Liter': [fuel_in], 'Odometer': [odo_in], 'Note': [note_in]})
        df = pd.concat([df, new_row], ignore_index=True)
        save_data(df)
        st.success("บันทึกข้อมูลเรียบร้อยแล้ว!")
        st.rerun()

# --- ส่วนที่ 2: แก้ไขและลบข้อมูล ---
st.divider()
st.subheader("📋 ประวัติและแก้ไขข้อมูล")
df = load_data()

if not df.empty:
    # ตารางที่แก้ไขได้
    edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True, key="main_editor")
    
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("✅ ยืนยันการแก้ไข/ลบ"):
            save_data(edited_df)
            st.success("อัปเดตฐานข้อมูลสำเร็จ!")
            st.rerun()
    with col_b:
        st.info("💡 วิธีลบ: ติ๊กหน้าแถวในตารางแล้วกด Delete (บนคอม) หรือเลือกแถวแล้วลบในตารางได้เลย")

    # --- ส่วนที่ 3: กราฟแสดงผล ---
    st.divider()
    st.subheader("📈 แนวโน้มความประหยัด")
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date')
    fig = px.line(df, x='Date', y='Km_per_Liter', markers=True, title="สถิติ km/L")
    fig.update_traces(line_color='#D4AF37') # เส้นกราฟสีทอง
    st.plotly_chart(fig, use_container_width=True)
else:
    st.write("ยังไม่มีข้อมูลในระบบ เริ่มบันทึกรายการแรกได้เลยครับ!")
