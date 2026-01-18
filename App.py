import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image
import datetime
import os

# ตั้งค่าหน้าเว็บ (ธีมสีเขียวเหนี่ยวทรัพย์)
st.set_page_config(page_title="Xforce Fuel Tracker", layout="wide")

# ไฟล์สำหรับเก็บข้อมูล (เปรียบเสมือนสมุดบัญชี)
DATA_FILE = 'fuel_data.csv'

# ฟังก์ชันโหลดข้อมูล
def load_data():
    if not os.path.exists(DATA_FILE):
        return pd.DataFrame(columns=['Date', 'Km_per_Liter', 'Odometer', 'Note'])
    return pd.read_csv(DATA_FILE)

# ฟังก์ชันบันทึกข้อมูล
def save_data(df):
    df.to_csv(DATA_FILE, index=False)

st.title("🚗 Mitsubishi Xforce: บันทึกและแก้ไขข้อมูล")
st.write(f"วัน{datetime.datetime.now().strftime('%A')} สดใส ขับขี่ปลอดภัยครับ")

# --- ส่วนที่ 1: บันทึกข้อมูลใหม่ ---
with st.expander("📝 เพิ่มข้อมูลใหม่ (คลิกเพื่อเปิด)", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        date_input = st.date_input("วันที่", datetime.date.today())
        fuel_input = st.number_input("อัตราสิ้นเปลือง (km/L)", value=22.0, step=0.1)
    with col2:
        odo_input = st.number_input("เลขไมล์ (km)", value=0, step=1)
        note_input = st.text_input("บันทึกช่วยจำ", "ขับไปทำงาน")

    if st.button("💾 บันทึกรายการใหม่"):
        # โหลดข้อมูลเก่ามา
        df = load_data()
        # สร้างรายการใหม่
        new_row = pd.DataFrame({
            'Date': [date_input],
            'Km_per_Liter': [fuel_input],
            'Odometer': [odo_input],
            'Note': [note_input]
        })
        # รวมร่างและบันทึก
        df = pd.concat([df, new_row], ignore_index=True)
        save_data(df)
        st.success("บันทึกเรียบร้อย!")
        st.rerun() # รีเฟรชหน้าจอทันที

# --- ส่วนที่ 2: ตารางประวัติ (แก้ไข/ลบได้) ---
st.divider()
st.subheader("📋 ประวัติการบันทึก (แก้ไขได้ที่นี่)")

df = load_data()

# แสดงตารางแบบแก้ไขได้ (Data Editor)
edited_df = st.data_editor(
    df,
    num_rows="dynamic",    # อนุญาตให้เพิ่ม/ลบแถวได้
    key="editor",
    use_container_width=True
)

# ปุ่มกดเพื่อยืนยันการแก้ไข
if st.button("บันทึกการแก้ไขตาราง"):
    save_data(edited_df)
    st.success("อัปเดตข้อมูลในตารางเรียบร้อย!")
    st.rerun()

# --- ส่วนที่ 3: กราฟแสดงผล ---
if not df.empty:
    st.divider()
    st.subheader("📈 แนวโน้มความประหยัด")
    # แปลงข้อมูลวันที่ให้กราฟอ่านรู้เรื่อง
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date')
    
    fig = px.line(df, x='Date', y='Km_per_Liter', markers=True, title="สถิติ km/L ของ Xforce")
    fig.update_traces(line_color='#166534') # สีเขียวมงคล
    st.plotly_chart(fig, use_container_width=True)
