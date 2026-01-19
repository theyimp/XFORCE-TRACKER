import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date
import os

# --- Configuration ---
DB_CONS = "data_consumption.csv"
DB_REFILL = "data_refill.csv"

st.set_page_config(page_title="Xforce Ultimate Tracker", layout="wide")

# --- UI Styling ---
st.markdown("""
    <style>
    .stApp { background-color: #1E1E1E; color: #E0E0E0; }
    h1, h2, h3 { color: #2ECC71 !important; }
    div[data-testid="stExpander"] { background-color: #2D2D2D; border: 1px solid #444; margin-bottom: 10px; }
    input, select, textarea { background-color: #333 !important; color: white !important; }
    .stButton>button { background-color: #2ECC71; color: black; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- Functions ---
def load_data(filename, columns):
    if os.path.exists(filename):
        df = pd.read_csv(filename)
        for col in columns:
            if col not in df.columns: df[col] = None
        return df
    return pd.DataFrame(columns=columns)

COLS_CONS = ["Date", "Consumption", "Odometer", "Mode", "Route"]
COLS_REFILL = ["Date", "Station", "FuelType", "PricePerLiter", "Liters", "TotalPrice", "Odometer"]

# --- Header ---
st.title("♻️ XFORCE : ENERGY TRACKER")

tab1, tab2, tab3 = st.tabs(["📊 อัตราสิ้นเปลืองพลังงาน", "⛽ บันทึกน้ำมัน", "🛠 แก้ไขประวัติ"])

# --- หน้า 1 & 2 (บันทึกข้อมูลปกติ) ---
with tab1:
    with st.form("add_c"):
        c1, c2 = st.columns(2)
        d_date = c1.date_input("วันที่", date.today())
        d_mode = c1.selectbox("Mode", ["Normal", "Wet", "Gravel", "Mud", "Tarmac"])
        d_cons = c2.number_input("km/L", format="%.1f")
        d_odo = c2.number_input("เลขไมล์", step=1)
        d_route = st.text_input("เส้นทาง")
        if st.form_submit_button("บันทึก"):
            df = load_data(DB_CONS, COLS_CONS)
            new_row = pd.DataFrame([{"Date": str(d_date), "Consumption": d_cons, "Odometer": d_odo, "Mode": d_mode, "Route": d_route}])
            pd.concat([df, new_row], ignore_index=True).to_csv(DB_CONS, index=False)
            st.success("บันทึกแล้ว")

with tab2:
    with st.form("add_r"):
        c1, c2 = st.columns(2)
        r_date = c1.date_input("วันที่เติม", date.today())
        r_st = c1.selectbox("ปั๊ม", ["PTT", "PTG", "Caltex", "Shell", "Bangchak", "ETC"])
        r_ppl = c2.number_input("ราคาต่อลิตร", format="%.2f")
        r_lit = c2.number_input("ลิตร", format="%.2f")
        if st.form_submit_button("บันทึกการเติมน้ำมัน"):
            df = load_data(DB_REFILL, COLS_REFILL)
            new_row = pd.DataFrame([{"Date": str(r_date), "Station": r_st, "PricePerLiter": r_ppl, "Liters": r_lit, "TotalPrice": r_ppl*r_lit}])
            pd.concat([df, new_row], ignore_index=True).to_csv(DB_REFILL, index=False)
            st.success("บันทึกแล้ว")

# --- หน้า 3: แก้ไขประวัติ (แก้ไขให้ทำงานได้จริง) ---
with tab3:
    st.subheader("🛠 รายการที่สามารถแก้ไขได้")
    
    # ดึงข้อมูลมาแสดง (ใช้ .copy() เพื่อป้องกัน Error เวลาแก้ไข)
    df_r = load_data(DB_REFILL, COLS_REFILL).copy()
    
    if not df_r.empty:
        # แสดงจากล่างขึ้นบน (ล่าสุดอยู่บน)
        for i in reversed(range(len(df_r))):
            row = df_r.iloc[i]
            # สร้าง Key เฉพาะตัวสำหรับแต่ละรายการ
            with st.expander(f"📝 รายการวันที่ {row['Date']} | {row['Station']} | {row.get('TotalPrice', 0):.2f} บาท"):
                # *** สำคัญ: ไม่ใช้ st.form ในหน้าแก้ไขแบบ Loop เพื่อลดปัญหาปุ่มไม่ทำงาน ***
                e_col1, e_col2 = st.columns(2)
                
                # แสดงค่าปัจจุบันและรับค่าใหม่
                new_date = e_col1.date_input("วันที่", value=pd.to_datetime(row['Date']).date(), key=f"d_{i}")
                new_st = e_col1.selectbox("ปั๊ม", ["PTT", "PTG", "Caltex", "Shell", "Bangchak", "ETC"], 
                                         index=["PTT", "PTG", "Caltex", "Shell", "Bangchak", "ETC"].index(row['Station']) if row['Station'] in ["PTT", "PTG", "Caltex", "Shell", "Bangchak", "ETC"] else 0,
                                         key=f"s_{i}")
                
                new_ppl = e_col2.number_input("ราคา/ลิตร", value=float(row['PricePerLiter'] or 0), key=f"p_{i}")
                new_lit = e_col2.number_input("จำนวนลิตร", value=float(row['Liters'] or 0), key=f"l_{i}")
                
                # ปุ่มบันทึกแยกรายรายการ
                if st.button(f"ยืนยันการแก้ไขรายการที่ {i+1}", key=f"btn_{i}"):
                    df_r.at[i, 'Date'] = str(new_date)
                    df_r.at[i, 'Station'] = new_st
                    df_r.at[i, 'PricePerLiter'] = new_ppl
                    df_r.at[i, 'Liters'] = new_lit
                    df_r.at[i, 'TotalPrice'] = new_ppl * new_lit
                    
                    df_r.to_csv(DB_REFILL, index=False)
                    st.success(f"อัปเดตรายการที่ {i+1} สำเร็จ!")
                    st.rerun() # รีเฟรชหน้าจอเพื่อแสดงค่าใหม่
    else:
        st.info("ยังไม่มีข้อมูลการเติมน้ำมันให้แก้ไข")
