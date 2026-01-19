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
    .stButton>button { background-color: #2ECC71; color: black; font-weight: bold; border-radius: 5px; width: 100%; }
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

tab1, tab2, tab3 = st.tabs(["➕ บันทึก km/L (หน้าจอ)", "⛽ บันทึกการเติมน้ำมัน", "🛠 แก้ไข & สรุปผล"])

# --- หน้า 1: บันทึกหน้าจอรถ ---
with tab1:
    st.subheader("📊 บันทึกอัตราสิ้นเปลืองจาก Dashboard")
    with st.form("add_form"):
        c1, c2 = st.columns(2)
        with c1:
            d_date = st.date_input("วันที่บันทึก", datetime.now())
            d_mode = st.selectbox("Drive Mode", ["Normal", "Wet", "Gravel", "Mud", "Tarmac"])
        with c2:
            d_cons = st.number_input("Consumption (km/L)", format="%.1f")
            d_odo = st.number_input("เลขไมล์หน้าจอ (km)", step=1)
            d_route = st.text_input("เส้นทาง/หมายเหตุ")
        if st.form_submit_button("บันทึกข้อมูลหน้าจอ"):
            append_data({"Date": str(d_date), "Consumption": d_cons, "Odometer": d_odo, "Mode": d_mode, "Route": d_route}, DB_CONS)
            st.success("บันทึกสำเร็จ!")

# --- หน้า 2: บันทึกน้ำมัน (อัปเดต ปั๊ม และ ชนิดน้ำมัน) ---
with tab2:
    st.subheader("⛽ รายละเอียดการเข้าสถานีบริการน้ำมัน")
    with st.form("refill_form"):
        c1, c2 = st.columns(2)
        with c1:
            r_date = st.date_input("วันที่เติม", datetime.now())
            r_station = st.selectbox("ปั๊มน้ำมัน", ["PTT", "PTG", "Caltex", "Shell", "Bangchak", "ETC"])
            r_type = st.selectbox("ชนิดน้ำมัน", ["Gasohol 95", "Gasohol 91", "E20", "Gasoline 95"])
        with c2:
            r_price = st.number_input("ยอดเงินรวม (บาท)", step=1.0)
            r_liter = st.number_input("จำนวนลิตร", step=0.01)
            r_odo = st.number_input("เลขไมล์ขณะเติม (km)", step=1)
        
        if st.form_submit_button("บันทึกข้อมูลการเติมน้ำมัน"):
            append_data({
                "Date": str(r_date), 
                "Station": r_station, 
                "FuelType": r_type, 
                "Price": r_price, 
                "Liters": r_liter, 
                "Odometer": r_odo
            }, DB_REFILL)
            st.success(f"บันทึกข้อมูล {r_station} เรียบร้อย!")

# --- หน้า 3: แก้ไขและสรุปผล ---
with tab3:
    df_c = load_data(DB_CONS)
    df_r = load_data(DB_REFILL)
    
    st.subheader("📉 กราฟแนวโน้มสมรรถนะ")
    if not df_c.empty:
        fig = px.line(df_c, x='Date', y='Consumption', markers=True, template="plotly_dark")
        fig.update_traces(line_color='#2ECC71')
        st.plotly_chart(fig, use_container_width=True)

    # ส่วนแก้ไขข้อมูลหน้าจอ
    if not df_c.empty:
        st.subheader("📝 แก้ไขประวัติ km/L")
        for i, row in df_c.iterrows():
            with st.expander(f"แก้ไข: {row['Date']} | {row['Mode']} | {row['Route']}"):
                with st.form(f"edit_cons_{i}"):
                    new_cons = st.number_input("Consumption", value=float(row['Consumption']), key=f"ec_{i}")
                    new_route = st.text_input("Route", value=row['Route'], key=f"er_{i}")
                    if st.form_submit_button("อัปเดต"):
                        df_c.at[i, 'Consumption'] = new_cons
                        df_c.at[i, 'Route'] = new_route
                        save_all_data(df_c, DB_CONS)
                        st.rerun()

    # ส่วนแก้ไขข้อมูลเติมน้ำมัน
    if not df_r.empty:
        st.subheader("⛽ แก้ไขประวัติการเติมน้ำมัน")
        for i, row in df_r.iterrows():
            with st.expander(f"แก้ไข: {row['Date']} | {row['Station']} | {row['Price']} บาท"):
                with st.form(f"edit_refill_{i}"):
                    new_station = st.selectbox("ปั๊ม", ["PTT", "PTG", "Caltex", "Shell", "Bangchak", "ETC"], index=["PTT", "PTG", "Caltex", "Shell", "Bangchak", "ETC"].index(row['Station']), key=f"es_{i}")
                    new_price = st.number_input("ราคา", value=float(row['Price']), key=f"ep_{i}")
                    if st.form_submit_button("อัปเดต"):
                        df_r.at[i, 'Station'] = new_station
                        df_r.at[i, 'Price'] = new_price
                        save_all_data(df_r, DB_REFILL)
                        st.rerun()
