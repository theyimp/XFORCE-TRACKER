import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- Configuration ---
DB_CONS = "data_consumption.csv"
DB_REFILL = "data_refill.csv"

# กำหนดชื่อคอลัมน์ให้ครบถ้วนป้องกัน Error
COLS_CONS = ["Date", "Consumption", "Odometer", "Mode", "Route"]
COLS_REFILL = ["Date", "Station", "FuelType", "PricePerLiter", "Liters", "TotalPrice", "Odometer"]

st.set_page_config(page_title="Xforce Energy Tracker", layout="wide", page_icon="♻️")

# --- UI Styling (Dark Theme & Green) ---
st.markdown("""
    <style>
    /* พื้นหลังและสีหลัก */
    .stApp { background-color: #1E1E1E; color: #E0E0E0; }
    
    /* ปรับแต่ง Title ให้เหมือนรูป */
    h1 { 
        color: #2ECC71 !important; 
        font-family: 'Arial Black', sans-serif;
        text-transform: uppercase;
        font-size: 3rem;
    }
    
    /* ปรับแต่ง Tabs */
    .stTabs [data-baseweb="tab-list"] { 
        gap: 10px; 
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #2D2D2D;
        border-radius: 5px;
        color: #E0E0E0;
        font-weight: bold;
    }
    .stTabs [data-baseweb="tab--active"] {
        background-color: #2ECC71 !important;
        color: black !important;
    }
    
    /* Input Fields */
    input, select, textarea { 
        background-color: #333 !important; 
        color: white !important; 
        border: 1px solid #444 !important; 
    }
    
    /* Buttons */
    .stButton>button { 
        background-color: #2ECC71; 
        color: black; 
        font-weight: bold; 
        width: 100%; 
        border-radius: 8px;
        border: none;
    }
    .stButton>button:hover { 
        background-color: #27AE60; 
        color: white; 
    }
    
    /* Expander */
    div[data-testid="stExpander"] { 
        background-color: #262626; 
        border: 1px solid #444; 
    }
    </style>
    """, unsafe_allow_html=True)

# --- Functions ---
def load_data(filename, columns):
    if os.path.exists(filename):
        try:
            df = pd.read_csv(filename)
            # *** Auto-Fix: ตรวจสอบและเติมคอลัมน์ที่ขาดหายไปป้องกัน KeyError ***
            for col in columns:
                if col not in df.columns:
                    df[col] = 0.0 if 'Price' in col or 'Liter' in col or 'Odo' in col else ""
            return df
        except Exception as e:
            st.error(f"Error loading data: {e}")
            return pd.DataFrame(columns=columns)
    return pd.DataFrame(columns=columns)

# --- Header Design ตามรูป ---
col_h1, col_h2 = st.columns([1, 8])
with col_h1:
    st.image("https://img.icons8.com/color/96/recycling-symbol.png", width=70) # ใช้ไอคอนรีไซเคิลสีเขียว
with col_h2:
    st.markdown("♻️ XFORCE : ENERGY TRACKER")

# --- Tabs (เปลี่ยนชื่อตามรูป) ---
tab1, tab2, tab3 = st.tabs(["📊 อัตราสิ้นเปลืองพลังงาน", "⛽ บันทึกน้ำมัน", "🛠 แก้ไขประวัติ"])

# ------------------------------------------------------------------
# TAB 1: อัตราสิ้นเปลืองพลังงาน
# ------------------------------------------------------------------
with tab1:
    with st.form("add_cons_form"):
        c1, c2 = st.columns(2)
        d_mode = c1.selectbox("โหมดการขับขี่", ["Normal", "Wet", "Gravel", "Mud", "Tarmac"])
        d_odo = c2.number_input("เลขไมล์ (km)", step=1)
        
        # ปรับ Layout ให้เหมือนรูป (Route ยาวเต็มบรรทัด)
        d_route = st.text_input("เส้นทาง/หมายเหตุ")
        
        c3, c4 = st.columns(2)
        d_date = c3.date_input("วันที่บันทึก", datetime.now())
        d_cons = c4.number_input("อัตราสิ้นเปลืองพลังงาน (km/L)", format="%.1f")
        
        if st.form_submit_button("บันทึกอัตราสิ้นเปลืองพลังงาน"):
            df = load_data(DB_CONS, COLS_CONS)
            new_data = pd.DataFrame([{"Date": str(d_date), "Consumption": d_cons, "Odometer": d_odo, "Mode": d_mode, "Route": d_route}])
            pd.concat([df, new_data], ignore_index=True).to_csv(DB_CONS, index=False)
            st.success("บันทึกข้อมูลเรียบร้อย!")

# ------------------------------------------------------------------
# TAB 2: บันทึกน้ำมัน
# ------------------------------------------------------------------
with tab2:
    with st.form("add_refill_form"):
        c1, c2 = st.columns(2)
        r_station = c1.selectbox("ปั๊มน้ำมัน", ["PTT", "PTG", "Caltex", "Shell", "Bangchak", "ETC"])
        r_type = c2.selectbox("ชนิดน้ำมัน", ["Gasohol 95", "Gasohol 91", "E20", "Gasoline 95"])
        
        c3, c4, c5 = st.columns(3)
        r_ppl = c3.number_input("ราคา/ลิตร", format="%.2f")
        r_lit = c4.number_input("จำนวนลิตร", format="%.2f")
        r_odo = c5.number_input("เลขไมล์", step=1)
        
        r_date = st.date_input("วันที่เติม", datetime.now())
        
        # คำนวณราคารวมอัตโนมัติ
        total_calc = r_ppl * r_lit
        st.write(f"💰 ราคารวม: **{total_calc:,.2f} บาท**")
        
        if st.form_submit_button("บันทึกการเติมน้ำมัน"):
            df = load_data(DB_REFILL, COLS_REFILL)
            new_data = pd.DataFrame([{"Date": str(r_date), "Station": r_station, "FuelType": r_type, 
                                      "PricePerLiter": r_ppl, "Liters": r_lit, "TotalPrice": total_calc, "Odometer": r_odo}])
            pd.concat([df, new_data], ignore_index=True).to_csv(DB_REFILL, index=False)
            st.success("บันทึกข้อมูลน้ำมันเรียบร้อย!")

# ------------------------------------------------------------------
# TAB 3: แก้ไขประวัติ (Robust Version)
# ------------------------------------------------------------------
with tab3:
    # 3.1 แก้ไขน้ำมัน
    st.subheader("⛽ ประวัติการเติมน้ำมัน (แก้ไข)")
    df_refill = load_data(DB_REFILL, COLS_REFILL)
    
    if not df_refill.empty:
        for i in reversed(range(len(df_refill))):
            row = df_refill.iloc[i]
            # ตรวจสอบค่า TotalPrice ป้องกัน KeyError
            disp_price = row.get('TotalPrice', 0.0)
            if pd.isna(disp_price): disp_price = 0.0
            
            with st.expander(f"📝 {row['Date']} | {row['Station']} | {float(disp_price):.2f} บาท"):
                col_e1, col_e2 = st.columns(2)
                
                # Input Fields (Safe Check)
                try: val_date = pd.to_datetime(row['Date']).date()
                except: val_date = datetime.now().date()
                
                # ถ้า Station ไม่อยู่ใน List ให้ Default เป็น ETC
                curr_st = row['Station'] if row['Station'] in ["PTT", "PTG", "Caltex", "Shell", "Bangchak", "ETC"] else "ETC"
                
                new_date = col_e1.date_input("วันที่", value=val_date, key=f"rd_{i}")
                new_st = col_e1.selectbox("ปั๊ม", ["PTT", "PTG", "Caltex", "Shell", "Bangchak", "ETC"], index=["PTT", "PTG", "Caltex", "Shell", "Bangchak", "ETC"].index(curr_st), key=f"rs_{i}")
                
                new_ppl = col_e2.number_input("ราคา/ลิตร", value=float(row.get('PricePerLiter', 0)), key=f"rp_{i}")
                new_lit = col_e2.number_input("จำนวนลิตร", value=float(row.get('Liters', 0)), key=f"rl_{i}")
                new_odo = col_e2.number_input("เลขไมล์", value=int(row.get('Odometer', 0)), key=f"ro_{i}")

                if st.button(f"บันทึกแก้ไข (รายการที่ {i+1})", key=f"btn_r_{i}"):
                    df_refill.at[i, 'Date'] = str(new_date)
                    df_refill.at[i, 'Station'] = new_st
                    df_refill.at[i, 'PricePerLiter'] = new_ppl
                    df_refill.at[i, 'Liters'] = new_lit
                    df_refill.at[i, 'TotalPrice'] = new_ppl * new_lit
                    df_refill.at[i, 'Odometer'] = new_odo
                    df_refill.to_csv(DB_REFILL, index=False)
                    st.success("แก้ไขเสร็จสิ้น!")
                    st.rerun()
    else:
        st.info("ไม่มีข้อมูลน้ำมัน")

    st.divider()

    # 3.2 แก้ไข km/L
    st.subheader("📊 ประวัติอัตราสิ้นเปลือง (แก้ไข)")
    df_cons = load_data(DB_CONS, COLS_CONS)
    
    if not df_cons.empty:
        for i in reversed(range(len(df_cons))):
            row = df_cons.iloc[i]
            with st.expander(f"📝 {row['Date']} | {row['Mode']} | {row.get('Consumption', 0)} km/L"):
                col_c1, col_c2 = st.columns(2)
                
                try: val_c_date = pd.to_datetime(row['Date']).date()
                except: val_c_date = datetime.now().date()
                
                curr_mode = row['Mode'] if row['Mode'] in ["Normal", "Wet", "Gravel", "Mud", "Tarmac"] else "Normal"

                new_c_date = col_c1.date_input("วันที่", value=val_c_date, key=f"cd_{i}")
                new_c_mode = col_c1.selectbox("Mode", ["Normal", "Wet", "Gravel", "Mud", "Tarmac"], index=["Normal", "Wet", "Gravel", "Mud", "Tarmac"].index(curr_mode), key=f"cm_{i}")
                
                new_c_cons = col_c2.number_input("Consumption", value=float(row.get('Consumption', 0)), key=f"cc_{i}")
                new_c_odo = col_c2.number_input("เลขไมล์", value=int(row.get('Odometer', 0)), key=f"co_{i}")
                new_c_route = st.text_input("เส้นทาง", value=str(row.get('Route', '')), key=f"cr_{i}")

                if st.button(f"บันทึกแก้ไข (รายการที่ {i+1})", key=f"btn_c_{i}"):
                    df_cons.at[i, 'Date'] = str(new_c_date)
                    df_cons.at[i, 'Mode'] = new_c_mode
                    df_cons.at[i, 'Consumption'] = new_c_cons
                    df_cons.at[i, 'Odometer'] = new_c_odo
                    df_cons.at[i, 'Route'] = new_c_route
                    df_cons.to_csv(DB_CONS, index=False)
                    st.success("แก้ไขเสร็จสิ้น!")
                    st.rerun()
    else:
        st.info("ไม่มีข้อมูลอัตราสิ้นเปลือง")
