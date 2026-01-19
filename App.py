import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os
from PIL import Image

# --- Configuration & Styling ---
st.set_page_config(page_title="Xforce Energy Pro", layout="wide", page_icon="⛽")

# สีเขียวมงคลสำหรับคนวันพุธกลางวัน
STYLING = """
<style>
    .stApp { background-color: #f0f4f0; }
    .metric-card { background-color: #ffffff; padding: 20px; border-radius: 15px; border-left: 5px solid #2E7D32; }
    h1, h2, h3 { color: #1B5E20; }
</style>
"""
st.markdown(STYLING, unsafe_allow_html=True)

# --- Database Management ---
DB_CONSUMPTION = "consumption_logs.csv"
DB_REFILL = "refill_logs.csv"

def save_to_csv(data, filename):
    df_new = pd.DataFrame([data])
    if os.path.exists(filename):
        df_old = pd.read_csv(filename)
        df_final = pd.concat([df_old, df_new], ignore_index=True)
    else:
        df_final = df_new
    df_final.to_csv(filename, index=False)

def load_data(filename):
    if os.path.exists(filename):
        df = pd.read_csv(filename)
        df['Date'] = pd.to_datetime(df['Date'])
        return df.sort_values(by="Date")
    return pd.DataFrame()

# --- Sidebar: Lucky & Personal Info ---
with st.sidebar:
    st.image("https://www.mitsubishi-motors.co.th/content/dam/mitsubishi-motors-th/images/cars/xforce/2024/primary/mitsubishi-xforce-exterior-1.png", caption="Mitsubishi Xforce Ultimate")
    st.header("🔮 เคล็ดมงคลวันพุธ")
    st.success("🟢 สีนำโชค: สีเขียว / สีเหลือง")
    st.info("🕒 ฤกษ์มงคลวันนี้: 08:24 - 10:30 น. (เหมาะกับการออกรถ/บันทึกบัญชี)")
    st.divider()
    st.write("วันเกิด: พุธกลางวัน")
    st.write("รถที่ใช้: Xforce Ultimate")

# --- Main App Interface ---
st.title("⛽ Xforce Energy & Refill Tracker")

tab1, tab2, tab3 = st.tabs(["📝 บันทึกข้อมูล", "📊 วิเคราะห์ผล", "📜 ประวัติย้อนหลัง"])

# --- TAB 1: Input Data ---
with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📸 บันทึกจากหน้าจอรถ (Dashboard)")
        with st.form("dashboard_form"):
            up_file = st.file_uploader("อัปโหลดรูป Dashboard", type=['jpg','png'])
            d_date = st.date_input("วันที่", datetime.now(), key="d_date")
            d_cons = st.number_input("อัตราสิ้นเปลืองบนหน้าจอ (km/L)", min_value=0.0, step=0.1)
            d_odo = st.number_input("เลขไมล์ปัจจุบัน (km)", min_value=0)
            if st.form_submit_button("บันทึกข้อมูลหน้าจอ"):
                save_to_csv({"Date": d_date, "Consumption": d_cons, "Odometer": d_odo}, DB_CONSUMPTION)
                st.toast("บันทึกข้อมูลหน้าจอแล้ว!", icon="✅")

    with col2:
        st.subheader("⛽ บันทึกการเติมน้ำมัน (Refill)")
        with st.form("refill_form"):
            r_date = st.date_input("วันที่เติมน้ำมัน", datetime.now(), key="r_date")
            r_liter = st.number_input("จำนวนลิตร (L)", min_value=0.0, step=0.01)
            r_price = st.number_input("ราคารวม (บาท)", min_value=0.0, step=1.0)
            r_odo = st.number_input("เลขไมล์ขณะเติม (km)", min_value=0)
            if st.form_submit_button("บันทึกการเติมน้ำมัน"):
                save_to_csv({"Date": r_date, "Liters": r_liter, "Price": r_price, "Odometer": r_odo}, DB_REFILL)
                st.toast("บันทึกข้อมูลเติมน้ำมันแล้ว!", icon="⛽")

# --- TAB 2: Analysis & Graphs ---
with tab2:
    df_c = load_data(DB_CONSUMPTION)
    df_r = load_data(DB_REFILL)

    if not df_c.empty or not df_r.empty:
        # คำนวณค่าเฉลี่ย
        avg_dash = df_c['Consumption'].mean() if not df_c.empty else 0
        total_spent = df_r['Price'].sum() if not df_r.empty else 0
        
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("Avg (หน้าจอรถ)", f"{avg_dash:.2f} km/L")
        with m2:
            st.metric("ค่าใช้จ่ายรวม", f"{total_spent:,.2f} บาท")
        with m3:
            if len(df_r) > 1:
                dist = df_r['Odometer'].max() - df_r['Odometer'].min()
                total_l = df_r['Liters'].iloc[1:].sum()
                real_avg = dist / total_l if total_l > 0 else 0
                st.metric("Avg (เติมจริง)", f"{real_avg:.2f} km/L")
            else:
                st.metric("Avg (เติมจริง)", "รอข้อมูลเพิ่ม")

        st.divider()
        
        # กราฟ
        c1, c2 = st.columns(2)
        with c1:
            if not df_c.empty:
                fig_line = px.line(df_c, x='Date', y='Consumption', title='กราฟอัตราสิ้นเปลืองรายวัน (km/L)',
                                  markers=True, color_discrete_sequence=['#2E7D32'])
                st.plotly_chart(fig_line, use_container_width=True)
        
        with c2:
            if not df_r.empty:
                df_r['Month'] = df_r['Date'].dt.strftime('%b')
                fig_bar = px.bar(df_r, x='Month', y='Price', title='ค่าใช้จ่ายน้ำมันรายเดือน (บาท)',
                                color_discrete_sequence=['#FBC02D'])
                st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("ยังไม่มีข้อมูลเพื่อนำมาวิเคราะห์")

# --- TAB 3: History ---
with tab3:
    col_h1, col_h2 = st.columns(2)
    with col_h1:
        st.write("📋 ประวัติหน้าจอรถ")
        st.dataframe(df_c, use_container_width=True)
    with col_h2:
        st.write("📋 ประวัติการเติมน้ำมัน")
        st.dataframe(df_r, use_container_width=True)
