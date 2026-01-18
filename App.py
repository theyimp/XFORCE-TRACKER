import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image
import datetime
import os

# ตั้งค่าธีมและสีมงคล
st.set_page_config(page_title="Xforce Ultimate Tracker", layout="wide")

LOG_FILE = 'drive_log.csv'   
FUEL_FILE = 'fuel_log.csv'   

def load_data(file_path, columns):
    if not os.path.exists(file_path):
        return pd.DataFrame(columns=columns)
    df = pd.read_csv(file_path)
    return df

def save_data(df, file_path):
    df.to_csv(file_path, index=False)

st.title("Xforce Tracker")

tab1, tab2 = st.tabs(["📊 สถิติหน้าจอ (km/L)", "⛽ บันทึกเติมน้ำมัน & ระยะทาง"])

# --- หน้าที่ 1: บันทึกจาก Dashboard ---
with tab1:
    st.subheader("บันทึกจากหน้าจอ Dashboard")
    with st.expander("📸 อัปโหลดรูปและกรอกข้อมูล"):
        up_drive = st.file_uploader("รูปหน้าจอรถ", type=['jpg','png','jpeg'], key="up1")
        c1, c2 = st.columns(2)
        with c1:
            d_date = st.date_input("วันที่", datetime.date.today(), key="d_date")
            d_fuel = st.number_input("อัตราสิ้นเปลือง (km/L)", value=22.0, key="d_fuel")
        with c2:
            d_odo = st.number_input("เลขไมล์รวมปัจจุบัน (km)", value=0, key="d_odo")
            d_note = st.text_input("หมายเหตุ", "ขับปกติ", key="d_note")
        if st.button("💾 บันทึกสถิติ"):
            df = load_data(LOG_FILE, ['Date', 'Km_L', 'Odometer', 'Note'])
            new = pd.DataFrame({'Date':[str(d_date)], 'Km_L':[d_fuel], 'Odometer':[d_odo], 'Note':[d_note]})
            save_data(pd.concat([df, new], ignore_index=True), LOG_FILE)
            st.rerun()

    df_log = load_data(LOG_FILE, ['Date', 'Km_L', 'Odometer', 'Note'])
    if not df_log.empty:
        st.data_editor(df_log, num_rows="dynamic", use_container_width=True, key="ed1")

# --- หน้าที่ 2: บันทึกเติมน้ำมัน (เพิ่มชนิดน้ำมัน) ---
with tab2:
    st.subheader("บันทึกการเติมน้ำมัน")
    
    df_f_old = load_data(FUEL_FILE, ['Date', 'Fuel_Type', 'Price_Per_Liter', 'Liters', 'Total_Cost', 'Odometer', 'Trip_Dist'])
    last_odo = 0
    if not df_f_old.empty:
        last_odo = df_f_old['Odometer'].max()
        st.info(f"📍 เลขไมล์ล่าสุดที่บันทึกไว้: {last_odo:,} km")

    with st.expander("⛽ กรอกข้อมูลการเติมน้ำมัน", expanded=True):
        f1, f2 = st.columns(2)
        with f1:
            f_date = st.date_input("วันที่เติม", datetime.date.today(), key="f_date")
            # --- เพิ่มส่วนเลือกชนิดน้ำมัน ---
            f_type = st.selectbox("ชนิดน้ำมันที่เติม", 
                                ["Gasohol 95", "Gasohol 91", "E20", "Premium 95", "อื่น ๆ"])
            f_price = st.number_input("ราคาน้ำมัน (บาท/ลิตร)", value=0.0, step=0.1)
            f_liters = st.number_input("จำนวนลิตรที่เติม", value=0.0, step=0.1)
        with f2:
            f_odo = st.number_input("เลขไมล์ขณะเติม (km)", value=int(last_odo), step=1)
            trip_dist = f_odo - last_odo if last_odo > 0 else 0
            st.write(f"🛣️ ระยะทางที่วิ่งได้จากถังก่อน: **{trip_dist:,} km**")
            
            f_total = f_price * f_liters
            st.write(f"💰 ยอดรวม: **{f_total:,.2f} บาท**")

        if st.button("⛽ บันทึกการเติมน้ำมัน"):
            df = load_data(FUEL_FILE, ['Date', 'Fuel_Type', 'Price_Per_Liter', 'Liters', 'Total_Cost', 'Odometer', 'Trip_Dist'])
            new = pd.DataFrame({
                'Date':[str(f_date)], 
                'Fuel_Type':[f_type], # บันทึกชนิดน้ำมันลงไปด้วย
                'Price_Per_Liter':[f_price], 
                'Liters':[f_liters], 
                'Total_Cost':[f_total],
                'Odometer':[f_odo],
                'Trip_Dist':[trip_dist]
            })
            save_data(pd.concat([df, new], ignore_index=True), FUEL_FILE)
            st.success(f"บันทึก {f_type} เรียบร้อย! ขอให้เดินทางราบรื่นครับ")
            st.rerun()

    # ตารางสรุปผล
    df_fuel = load_data(FUEL_FILE, ['Date', 'Fuel_Type', 'Price_Per_Liter', 'Liters', 'Total_Cost', 'Odometer', 'Trip_Dist'])
    if not df_fuel.empty:
        st.divider()
        st.write("📋 ประวัติการเติมน้ำมัน (ชนิดน้ำมัน/ยอดเงิน/ระยะทาง)")
        edit_fuel = st.data_editor(df_fuel, num_rows="dynamic", use_container_width=True, key="ed2")
        if st.button("✅ ยืนยันการแก้ไข"):
            save_data(edit_fuel, FUEL_FILE)
            st.rerun()
            
        # กราฟแยกตามชนิดน้ำมัน
        st.write("📊 สรุปสัดส่วนชนิดน้ำมันที่เติม")
        fig_pie = px.pie(df_fuel, names='Fuel_Type', values='Liters', color_discrete_sequence=px.colors.sequential.Greens_r)
        st.plotly_chart(fig_pie, use_container_width=True)
