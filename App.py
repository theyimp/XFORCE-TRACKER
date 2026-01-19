import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

# --- Configuration ---
DB_CONS = "data_consumption.csv"
DB_REFILL = "data_refill.csv"

st.set_page_config(page_title="Xforce Ultimate Tracker", layout="wide")

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
st.title("🚗 XFORCE ULTIMATE - GRAY EDITION V3")
st.write(f"📅 พุธกลางวันมงคล | 🟢 สีเขียวเสริมดวง | **บันทึกละเอียด & แก้ไขได้ทุกจุด**")

tab1, tab2, tab3 = st.tabs(["📊 บันทึกหน้าจอ (km/L)", "⛽ บันทึกการเติมน้ำมัน", "🛠 แก้ไขประวัติ & สรุปผล"])

# --- หน้า 1: บันทึกหน้าจอรถ ---
with tab1:
    st.subheader("📝 บันทึกอัตราสิ้นเปลืองจาก Dashboard")
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

# --- หน้า 2: บันทึกน้ำมัน (เพิ่มราคาต่อลิตร) ---
with tab2:
    st.subheader("⛽ บันทึกการเติมน้ำมัน")
    with st.form("refill_form"):
        col1, col2 = st.columns(2)
        with col1:
            r_date = st.date_input("วันที่เติม", datetime.now())
            r_station = st.selectbox("ปั๊มน้ำมัน", ["PTT", "PTG", "Caltex", "Shell", "Bangchak", "ETC"])
            r_type = st.selectbox("ชนิดน้ำมัน", ["Gasohol 95", "Gasohol 91", "E20", "Gasoline 95"])
        with col2:
            r_price_per_liter = st.number_input("ราคาต่อลิตร (บาท)", step=0.01, format="%.2f")
            r_liter = st.number_input("จำนวนลิตรที่เติม", step=0.01, format="%.2f")
            r_odo = st.number_input("เลขไมล์ขณะเติม (km)", step=1)
        
        # คำนวณราคารวมให้อัตโนมัติ (โชว์เพื่อความสะดวก)
        total_calc = r_price_per_liter * r_liter
        st.write(f"💰 ราคารวมโดยประมาณ: **{total_calc:,.2f} บาท**")

        if st.form_submit_button("บันทึกข้อมูลการเติมน้ำมัน"):
            append_data({
                "Date": str(r_date), 
                "Station": r_station, 
                "FuelType": r_type, 
                "PricePerLiter": r_price_per_liter,
                "Liters": r_liter, 
                "TotalPrice": total_calc,
                "Odometer": r_odo
            }, DB_REFILL)
            st.success(f"บันทึกข้อมูล {r_station} สำเร็จ!")

# --- หน้า 3: แก้ไขประวัติ & สรุปผล ---
with tab3:
    df_c = load_data(DB_CONS)
    df_r = load_data(DB_REFILL)
    
    # --- ส่วนที่ 1: แก้ไขประวัติการเติมน้ำมัน (Full Edit) ---
    st.subheader("⛽ แก้ไขประวัติการเติมน้ำมัน (แก้ไขได้ทุกช่อง)")
    if not df_r.empty:
        for i, row in df_r.iterrows():
            with st.expander(f"แก้ไขรายการ: {row['Date']} | {row['Station']} | {row['TotalPrice']:.2f} บาท"):
                with st.form(f"edit_refill_{i}"):
                    e_col1, e_col2 = st.columns(2)
                    with e_col1:
                        new_date = st.date_input("วันที่", value=datetime.strptime(row['Date'], '%Y-%m-%d'), key=f"date_{i}")
                        new_station = st.selectbox("ปั๊ม", ["PTT", "PTG", "Caltex", "Shell", "Bangchak", "ETC"], 
                                                 index=["PTT", "PTG", "Caltex", "Shell", "Bangchak", "ETC"].index(row['Station']), key=f"st_{i}")
                        new_fuel = st.selectbox("น้ำมัน", ["Gasohol 95", "Gasohol 91", "E20", "Gasoline 95"],
                                               index=["Gasohol 95", "Gasohol 91", "E20", "Gasoline 95"].index(row['FuelType']), key=f"ft_{i}")
                    with e_col2:
                        new_ppl = st.number_input("ราคา/ลิตร", value=float(row['PricePerLiter']), format="%.2f", key=f"ppl_{i}")
                        new_lit = st.number_input("จำนวนลิตร", value=float(row['Liters']), format="%.2f", key=f"lit_{i}")
                        new_odo = st.number_input("เลขไมล์", value=int(row['Odometer']), key=f"odo_{i}")
                    
                    if st.form_submit_button("บันทึกการแก้ไขรายการนี้"):
                        df_r.at[i, 'Date'] = str(new_date)
                        df_r.at[i, 'Station'] = new_station
                        df_r.at[i, 'FuelType'] = new_fuel
                        df_r.at[i, 'PricePerLiter'] = new_ppl
                        df_r.at[i, 'Liters'] = new_lit
                        df_r.at[i, 'TotalPrice'] = new_ppl * new_lit
                        df_r.at[i, 'Odometer'] = new_odo
                        save_all_data(df_r, DB_REFILL)
                        st.success("อัปเดตข้อมูลแล้ว!")
                        st.rerun()
    else:
        st.info("ยังไม่มีข้อมูลการเติมน้ำมัน")

    st.divider()

    # --- ส่วนที่ 2: แก้ไขประวัติ km/L ---
    st.subheader("📋 แก้ไขประวัติ km/L (หน้าจอ)")
    if not df_c.empty:
        for i, row in df_c.iterrows():
            with st.expander(f"แก้ไขรายการ: {row['Date']} | {row['Mode']} | {row['Consumption']} km/L"):
                with st.form(f"edit_cons_{i}"):
                    ec1, ec2 = st.columns(2)
                    with ec1:
                        nc_date = st.date_input("วันที่", value=datetime.strptime(row['Date'], '%Y-%m-%d'), key=f"cdate_{i}")
                        nc_mode = st.selectbox("Mode", ["Normal", "Wet", "Gravel", "Mud", "Tarmac"], 
                                             index=["Normal", "Wet", "Gravel", "Mud", "Tarmac"].index(row['Mode']), key=f"cm_{i}")
                    with ec2:
                        nc_cons = st.number_input("km/L", value=float(row['Consumption']), format="%.1f", key=f"cc_{i}")
                        nc_route = st.text_input("เส้นทาง", value=row['Route'], key=f"cr_{i}")
                    
                    if st.form_submit_button("บันทึกการแก้ไข km/L"):
                        df_c.at[i, 'Date'] = str(nc_date)
                        df_c.at[i, 'Mode'] = nc_mode
                        df_c.at[i, 'Consumption'] = nc_cons
                        df_c.at[i, 'Route'] = nc_route
                        save_all_data(df_c, DB_CONS)
                        st.success("อัปเดตเรียบร้อย!")
                        st.rerun()
