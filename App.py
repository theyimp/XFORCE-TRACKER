import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

# --- การตั้งค่าธีมและหน้าตาแอป ---
st.set_page_config(page_title="Xforce Pro Tracker", layout="wide", page_icon="♻️")

# สไตล์สีเขียวมงคล (พุธกลางวัน)
st.markdown("""
    <style>
    .stApp { background-color: #f8faf8; }
    h1, h2, h3 { color: #2E7D32; }
    .stButton>button { background-color: #2E7D32; color: white; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- ส่วนจัดการฐานข้อมูล ---
DB_CONS = "data_consumption.csv"
DB_REFILL = "data_refill.csv"

def save_data(data, filename):
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
        if not df.empty:
            df['Date'] = pd.to_datetime(df['Date'])
            return df.sort_values(by="Date")
    return pd.DataFrame()

# --- เมนูหลัก 3 หน้า (Tabs) ---
tab1, tab2, tab3 = st.tabs([
    "📊 บันทึกอัตราสิ้นเปลือง (หน้าจอรถ)", 
    "⛽ บันทึกการเติมน้ำมัน", 
    "📈 สรุปข้อมูลและกราฟ"
])

# ---------------------------------------------------------
# หน้าที่ 1: บันทึกอัตราสิ้นเปลือง (Dashboard Data)
# ---------------------------------------------------------
with tab1:
    st.header("📋 บันทึกข้อมูลจากหน้าจอ Digital Driver Display")
    st.info("แนะนำ: ถ่ายรูปหน้าจอ 'Fuel Economy' หรือ 'Driving Score' ของ Xforce มากรอกข้อมูลที่นี่")
    
    with st.form("form_consumption"):
        col1, col2 = st.columns(2)
        with col1:
            d_date = st.date_input("วันที่บันทึก", datetime.now())
            d_cons = st.number_input("อัตราสิ้นเปลืองบนหน้าจอ (km/L)", min_value=0.0, step=0.1, format="%.1f")
        with col2:
            d_odo = st.number_input("เลขไมล์ปัจจุบัน (km)", min_value=0, step=1)
            d_note = st.text_input("หมายเหตุ (เช่น โหมด Normal/Wet, สภาพจราจร)")
        
        btn_save_cons = st.form_submit_button("✅ บันทึกข้อมูลหน้าจอ")
        
        if btn_save_cons:
            save_data({"Date": d_date, "Consumption": d_cons, "Odometer": d_odo, "Note": d_note}, DB_CONS)
            st.success("บันทึกข้อมูลอัตราสิ้นเปลืองเรียบร้อย!")

# ---------------------------------------------------------
# หน้าที่ 2: บันทึกการเติมน้ำมัน (Refill Log)
# ---------------------------------------------------------
with tab2:
    st.header("⛽ บันทึกข้อมูลการเข้าสถานีบริการน้ำมัน")
    
    with st.form("form_refill"):
        col1, col2 = st.columns(2)
        with col1:
            r_date = st.date_input("วันที่เติมน้ำมัน", datetime.now())
            r_price = st.number_input("ยอดเงินรวม (บาท)", min_value=0.0, step=10.0)
            r_liter = st.number_input("จำนวนน้ำมัน (ลิตร)", min_value=0.0, step=0.01)
        with col2:
            r_odo = st.number_input("เลขไมล์ขณะเติม (km)", min_value=0, step=1)
            r_type = st.selectbox("ประเภทน้ำมัน", ["Gasoline 95", "Gasohol 95", "Gasohol E10", "Gasohol E20"])
        
        btn_save_refill = st.form_submit_button("⛽ บันทึกการเติมน้ำมัน")
        
        if btn_save_refill:
            save_data({"Date": r_date, "Price": r_price, "Liters": r_liter, "Odometer": r_odo, "Type": r_type}, DB_REFILL)
            st.balloons()
            st.success("บันทึกข้อมูลการเติมน้ำมันเรียบร้อย!")

# ---------------------------------------------------------
# หน้าที่ 3: สรุปข้อมูลและแสดงผล (Summary & Charts)
# ---------------------------------------------------------
with tab3:
    st.header("📊 บทสรุปและวิเคราะห์พลังงาน")
    
    df_c = load_data(DB_CONS)
    df_r = load_data(DB_REFILL)

    if df_c.empty and df_r.empty:
        st.warning("ยังไม่มีข้อมูลในระบบ กรุณาบันทึกข้อมูลในหน้า 1 หรือ 2 ก่อนครับ")
    else:
        # ส่วนแสดง Card สรุปผล
        m1, m2, m3, m4 = st.columns(4)
        
        with m1:
            avg_disp = df_c['Consumption'].mean() if not df_c.empty else 0
            st.metric("Avg หน้าจอรถ", f"{avg_disp:.2f} km/L")
        
        with m2:
            total_spent = df_r['Price'].sum() if not df_r.empty else 0
            st.metric("รวมค่าใช้จ่าย", f"{total_spent:,.0f} บาท")
            
        with m3:
            if len(df_r) > 1:
                dist = df_r['Odometer'].max() - df_r['Odometer'].min()
                liters = df_r['Liters'].iloc[1:].sum() # คำนวณถังถัดมา
                real_avg = dist / liters if liters > 0 else 0
                st.metric("Avg เติมจริง", f"{real_avg:.2f} km/L")
            else:
                st.metric("Avg เติมจริง", "รอเติมถังที่ 2")
        
        with m4:
            # เสริมดวง: เลขมงคลคนวันพุธคือ 4 และ 6
            st.write("🔮 **เคล็ดมงคลวันนี้**")
            st.caption("สีนำโชค: เขียว")
            st.caption("เลขเสริมดวง: 4, 6")

        st.divider()

        # ส่วนกราฟแสดงผล
        col_g1, col_g2 = st.columns(2)
        
        with col_g1:
            if not df_c.empty:
                fig1 = px.line(df_c, x='Date', y='Consumption', title="แนวโน้มอัตราสิ้นเปลือง (km/L)",
                              markers=True, color_discrete_sequence=['#2E7D32'])
                st.plotly_chart(fig1, use_container_width=True)
        
        with col_g2:
            if not df_r.empty:
                df_r['Month'] = df_r['Date'].dt.strftime('%b')
                fig2 = px.bar(df_r, x='Month', y='Price', title="ค่าใช้จ่ายรายเดือน (บาท)",
                             color_discrete_sequence=['#FFD600']) # สีเหลืองเสริมพุธกลางวัน
                st.plotly_chart(fig2, use_container_width=True)

        # ตารางข้อมูลดิบ
        with st.expander("🔍 ดูตารางข้อมูลทั้งหมด"):
            st.write("ประวัติหน้าจอรถ")
            st.table(df_c.tail(5))
            st.write("ประวัติการเติมน้ำมัน")
            st.table(df_r.tail(5))

# --- ฟุตเตอร์มงคล ---
st.sidebar.markdown("---")
st.sidebar.write(f"📅 วันนี้: วัน{datetime.now().strftime('%A')}")
st.sidebar.info("ขับ Mitsubishi Xforce อย่างมั่นใจ วันนี้สีมงคลของคุณคือ 'สีเขียว' ครับ")
