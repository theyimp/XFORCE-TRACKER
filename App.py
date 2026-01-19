import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

# --- Configuration ---
DB_CONS = "data_consumption.csv"
DB_REFILL = "data_refill.csv"
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR): os.makedirs(UPLOAD_DIR)

st.set_page_config(page_title="Xforce Edit Gray", layout="wide")

# --- UI Styling (Dark Gray & Green) ---
st.markdown("""
    <style>
    .stApp { background-color: #1E1E1E; color: #E0E0E0; }
    h1, h2, h3 { color: #2ECC71 !important; }
    .stTabs [data-baseweb="tab-list"] { background-color: #2D2D2D; border-radius: 8px; }
    .stTabs [data-baseweb="tab"] { color: #BBBBBB; }
    .stTabs [data-baseweb="tab--active"] { color: #2ECC71 !important; border-bottom-color: #2ECC71 !important; }
    div[data-testid="stExpander"] { background-color: #2D2D2D; border: 1px solid #444; }
    input, select, textarea { background-color: #333 !important; color: white !important; }
    .stButton>button { background-color: #2ECC71; color: black; font-weight: bold; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- Functions ---
def load_data(filename):
    if os.path.exists(filename):
        return pd.read_csv(filename)
    return pd.DataFrame()

def save_all_data(df, filename):
    df.to_csv(filename, index=False)

def append_data(data, filename):
    df_new = pd.DataFrame([data])
    df_old = load_data(filename)
    df_final = pd.concat([df_old, df_new], ignore_index=True)
    df_final.to_csv(filename, index=False)

# --- Header ---
st.title("🚗 XFORCE ULTIMATE - GRAY EDITION")
st.write(f"📅 พุธกลางวันมงคล | 🟢 สีเขียวเสริมดวง | โหมดปัจจุบัน: **Tarmac Supported**")

tab1, tab2, tab3 = st.tabs(["➕ เพิ่มข้อมูลใหม่", "⛽ เติมน้ำมัน", "แก้ไข & สรุปผล"])

# --- หน้า 1: เพิ่มข้อมูล ---
with tab1:
    with st.form("add_form"):
        c1, c2 = st.columns(2)
        with c1:
            d_date = st.date_input("วันที่", datetime.now())
            d_mode = st.selectbox("Drive Mode", ["Normal", "Wet", "Gravel", "Mud", "Tarmac"])
        with c2:
            d_cons = st.number_input("Consumption (km/L)", format="%.1f")
            d_odo = st.number_input("Odometer (km)", step=1)
            d_route = st.text_input("เส้นทาง/หมายเหตุ")
        if st.form_submit_button("บันทึกข้อมูล"):
            append_data({"Date": str(d_date), "Consumption": d_cons, "Odometer": d_odo, "Mode": d_mode, "Route": d_route}, DB_CONS)
            st.success("บันทึกสำเร็จ!")

# --- หน้า 2: เติมน้ำมัน ---
with tab2:
    with st.form("refill_form"):
        c1, c2 = st.columns(2)
        with c1:
            r_date = st.date_input("วันที่เติม", datetime.now())
            r_price = st.number_input("ยอดเงิน (บาท)")
        with c2:
            r_liter = st.number_input("จำนวนลิตร", step=0.01)
            r_odo = st.number_input("เลขไมล์ขณะเติม", step=1)
        if st.form_submit_button("บันทึกการเติมน้ำมัน"):
            append_data({"Date": str(r_date), "Price": r_price, "Liters": r_liter, "Odometer": r_odo}, DB_REFILL)
            st.success("บันทึกสำเร็จ!")

# --- หน้า 3: แก้ไขและสรุปผล ---
with tab3:
    df_c = load_data(DB_CONS)
    if not df_c.empty:
        st.subheader("📋 ประวัติการขับขี่ (สามารถแก้ไขได้)")
        
        # กราฟ
        fig = px.line(df_c, x='Date', y='Consumption', title="Performance Trend", markers=True, template="plotly_dark")
        fig.update_traces(line_color='#2ECC71')
        st.plotly_chart(fig, use_container_width=True)

        # ส่วนแก้ไขข้อมูล
        for i, row in df_c.iterrows():
            with st.expander(f"✏️ แก้ไขรายการวันที่: {row['Date']} | {row['Route']}"):
                with st.form(f"edit_form_{i}"):
                    ec1, ec2, ec3 = st.columns(3)
                    new_cons = ec1.number_input("Consumption", value=float(row['Consumption']), key=f"c_{i}")
                    new_odo = ec2.number_input("Odometer", value=int(row['Odometer']), key=f"o_{i}")
                    new_route = ec3.text_input("Route", value=row['Route'], key=f"r_{i}")
                    new_mode = st.selectbox("Mode", ["Normal", "Wet", "Gravel", "Mud", "Tarmac"], 
                                            index=["Normal", "Wet", "Gravel", "Mud", "Tarmac"].index(row['Mode']), key=f"m_{i}")
                    
                    if st.form_submit_button("อัปเดตข้อมูลรายการนี้"):
                        df_c.at[i, 'Consumption'] = new_cons
                        df_c.at[i, 'Odometer'] = new_odo
                        df_c.at[i, 'Route'] = new_route
                        df_c.at[i, 'Mode'] = new_mode
                        save_all_data(df_c, DB_CONS)
                        st.success("อัปเดตเรียบร้อย! กรุณารีเฟรชหน้าจอ")
                        st.rerun()
    else:
        st.info("ยังไม่มีข้อมูลให้แสดงผล")
