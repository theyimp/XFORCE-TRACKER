import streamlit as st
import pandas as pd
import os
import plotly.express as px
from datetime import datetime

# --- Configuration ---
DB_CONS = "data_consumption.csv"
DB_REFILL = "data_refill.csv"

# ชื่อคอลัมน์มาตรฐาน
COLS_CONS = ["Date", "Consumption", "Odometer", "Mode", "Route"]
COLS_REFILL = ["Date", "Station", "FuelType", "PricePerLiter", "Liters", "TotalPrice", "Odometer"]

st.set_page_config(page_title="Xforce Energy Tracker", layout="wide", page_icon="♻️")

# --- UI Styling (Dark Theme & Green) ---
st.markdown("""
    <style>
    /* พื้นหลังหลัก */
    .stApp { background-color: #1E1E1E; color: #E0E0E0; }
    
    /* Title */
    h1 { 
        color: #2ECC71 !important; 
        font-family: 'Arial Black', sans-serif;
        text-transform: uppercase;
        font-size: 3.5rem !important;
        margin-bottom: 0px;
        padding-top: 10px;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { 
        gap: 8px; 
        background-color: transparent;
        margin-top: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #2D2D2D;
        border-radius: 8px;
        color: #B0B0B0;
        font-size: 1.1rem;
        padding: 10px 20px;
    }
    .stTabs [data-baseweb="tab--active"] {
        background-color: #2ECC71 !important;
        color: black !important;
        font-weight: bold;
    }
    
    /* Input Fields */
    input, select, textarea { 
        background-color: #333 !important; 
        color: white !important; 
        border: 1px solid #444 !important; 
        border-radius: 5px;
    }
    
    /* Buttons */
    .stButton>button { 
        background-color: #2ECC71; 
        color: black; 
        font-weight: bold; 
        width: 100%; 
        border-radius: 8px;
        border: none;
        height: 45px;
        font-size: 1rem;
        margin-top: 10px;
    }
    .stButton>button:hover { 
        background-color: #27AE60; 
        color: white; 
    }
    
    /* Download Button (สีทอง/เหลือง เพื่อความเด่น) */
    .stDownloadButton>button {
        background-color: #F1C40F !important;
        color: black !important;
        border: none;
    }
    .stDownloadButton>button:hover {
        background-color: #F39C12 !important;
    }
    
    /* Metrics & Expanders */
    div[data-testid="metric-container"] {
        background-color: #262626;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #2ECC71;
        color: white;
    }
    div[data-testid="stExpander"] { 
        background-color: #262626; 
        border: 1px solid #444; 
        border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Functions ---
def load_data(filename, columns):
    if os.path.exists(filename):
        try:
            df = pd.read_csv(filename)
            for col in columns:
                if col not in df.columns:
                    if col in ['PricePerLiter', 'Liters', 'TotalPrice', 'Odometer', 'Consumption']:
                        df[col] = 0.0
                    else:
                        df[col] = ""
            return df
        except Exception:
            return pd.DataFrame(columns=columns)
    return pd.DataFrame(columns=columns)

# --- Header ---
st.markdown("# ♻️ XFORCE : ENERGY TRACKER")

# --- Tabs ---
tab1, tab2, tab3, tab4 = st.tabs(["📊 อัตราสิ้นเปลือง", "⛽ บันทึกน้ำมัน", "🛠 แก้ไขประวัติ", "📈 สรุปผล & Export"])

# ------------------------------------------------------------------
# TAB 1: อัตราสิ้นเปลือง
# ------------------------------------------------------------------
with tab1:
    with st.form("add_cons_form"):
        c1, c2 = st.columns(2)
        d_date = c1.date_input("วันที่บันทึก", datetime.now())
        d_cons = c2.number_input("อัตราสิ้นเปลืองพลังงาน (km/L)", format="%.1f")

        c3, c4 = st.columns(2)
        d_mode = c3.selectbox("โหมดการขับขี่", ["Normal", "Wet", "Gravel", "Mud", "Tarmac"])
        d_odo = c4.number_input("เลขไมล์ (km)", step=1)
        
        d_route = st.text_input("เส้นทาง/หมายเหตุ")
        
        if st.form_submit_button("บันทึกข้อมูลหน้าจอ"):
            df = load_data(DB_CONS, COLS_CONS)
            new_data = pd.DataFrame([{"Date": str(d_date), "Consumption": d_cons, "Odometer": d_odo, "Mode": d_mode, "Route": d_route}])
            pd.concat([df, new_data], ignore_index=True).to_csv(DB_CONS, index=False)
            st.success("✅ บันทึกข้อมูลเรียบร้อย!")

# ------------------------------------------------------------------
# TAB 2: บันทึกน้ำมัน
# ------------------------------------------------------------------
with tab2:
    with st.form("add_refill_form"):
        c1, c2 = st.columns(2)
        r_date = c1.date_input("วันที่เติม", datetime.now())
        r_station = c2.selectbox("ปั๊มน้ำมัน", ["PTT", "PTG", "Caltex", "Shell", "Bangchak", "ETC"])
        
        c3, c4 = st.columns(2)
        r_type = c3.selectbox("ชนิดน้ำมัน", ["Gasohol 95", "Gasohol 91", "E20", "Gasoline 95"])
        r_odo = c4.number_input("เลขไมล์", step=1)
        
        c5, c6 = st.columns(2)
        r_ppl = c5.number_input("ราคา/ลิตร", format="%.2f")
        r_lit = c6.number_input("จำนวนลิตร", format="%.2f")
        
        total_calc = r_ppl * r_lit
        st.caption(f"💰 ราคารวมโดยประมาณ: {total_calc:,.2f} บาท")
        
        if st.form_submit_button("บันทึกการเติมน้ำมัน"):
            df = load_data(DB_REFILL, COLS_REFILL)
            new_data = pd.DataFrame([{"Date": str(r_date), "Station": r_station, "FuelType": r_type, 
                                      "PricePerLiter": r_ppl, "Liters": r_lit, "TotalPrice": total_calc, "Odometer": r_odo}])
            pd.concat([df, new_data], ignore_index=True).to_csv(DB_REFILL, index=False)
            st.success("✅ บันทึกข้อมูลน้ำมันเรียบร้อย!")

# ------------------------------------------------------------------
# TAB 3: แก้ไขประวัติ
# ------------------------------------------------------------------
with tab3:
    st.subheader("⛽ ประวัติการเติมน้ำมัน (แก้ไข)")
    df_refill = load_data(DB_REFILL, COLS_REFILL)
    
    if not df_refill.empty:
        for i in reversed(range(len(df_refill))):
            row = df_refill.iloc[i]
            disp_price = row.get('TotalPrice', 0.0)
            if pd.isna(disp_price): disp_price = 0.0
            
            with st.expander(f"📝 {row['Date']} | {row['Station']} | {float(disp_price):.2f} บาท"):
                c_e1, c_e2 = st.columns(2)
                try: val_date = pd.to_datetime(row['Date']).date()
                except: val_date = datetime.now().date()
                curr_st = row['Station'] if row['Station'] in ["PTT", "PTG", "Caltex", "Shell", "Bangchak", "ETC"] else "ETC"
                
                new_date = c_e1.date_input("วันที่", value=val_date, key=f"rd_{i}")
                new_st = c_e2.selectbox("ปั๊ม", ["PTT", "PTG", "Caltex", "Shell", "Bangchak", "ETC"], index=["PTT", "PTG", "Caltex", "Shell", "Bangchak", "ETC"].index(curr_st), key=f"rs_{i}")
                
                c_e3, c_e4, c_e5 = st.columns(3)
                new_ppl = c_e3.number_input("ราคา/ลิตร", value=float(row.get('PricePerLiter', 0)), key=f"rp_{i}")
                new_lit = c_e4.number_input("จำนวนลิตร", value=float(row.get('Liters', 0)), key=f"rl_{i}")
                new_odo = c_e5.number_input("เลขไมล์", value=int(row.get('Odometer', 0)), key=f"ro_{i}")

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

    st.divider()

    st.subheader("📊 ประวัติอัตราสิ้นเปลือง (แก้ไข)")
    df_cons = load_data(DB_CONS, COLS_CONS)
    
    if not df_cons.empty:
        for i in reversed(range(len(df_cons))):
            row = df_cons.iloc[i]
            with st.expander(f"📝 {row['Date']} | {row['Mode']} | {row.get('Consumption', 0)} km/L"):
                try: val_c_date = pd.to_datetime(row['Date']).date()
                except: val_c_date = datetime.now().date()
                curr_mode = row['Mode'] if row['Mode'] in ["Normal", "Wet", "Gravel", "Mud", "Tarmac"] else "Normal"

                ce_1, ce_2 = st.columns(2)
                new_c_date = ce_1.date_input("วันที่", value=val_c_date, key=f"cd_{i}")
                new_c_cons = ce_2.number_input("Consumption", value=float(row.get('Consumption', 0)), key=f"cc_{i}")

                ce_3, ce_4 = st.columns(2)
                new_c_mode = ce_3.selectbox("Mode", ["Normal", "Wet", "Gravel", "Mud", "Tarmac"], index=["Normal", "Wet", "Gravel", "Mud", "Tarmac"].index(curr_mode), key=f"cm_{i}")
                new_c_odo = ce_4.number_input("เลขไมล์", value=int(row.get('Odometer', 0)), key=f"co_{i}")
                
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

# ------------------------------------------------------------------
# TAB 4: สรุปผล & Export
# ------------------------------------------------------------------
with tab4:
    st.markdown("### 📈 Dashboard & Export")
    
    df_cons = load_data(DB_CONS, COLS_CONS)
    df_refill = load_data(DB_REFILL, COLS_REFILL)
    
    # --- Metrics & Charts ---
    if not df_cons.empty:
        avg_cons = df_cons['Consumption'].mean()
        max_cons = df_cons['Consumption'].max()
        best_mode = df_cons.loc[df_cons['Consumption'].idxmax()]['Mode']
        
        m1, m2, m3 = st.columns(3)
        m1.metric("อัตราสิ้นเปลืองเฉลี่ย", f"{avg_cons:.2f} km/L")
        m2.metric("ประหยัดที่สุด (Best)", f"{max_cons:.2f} km/L")
        m3.metric("โหมดที่ประหยัดสุด", f"{best_mode}")
        
        st.divider()

        df_cons_sorted = df_cons.sort_values(by="Date")
        fig_line = px.line(df_cons_sorted, x='Date', y='Consumption', 
                           markers=True, text='Consumption',
                           title='Timeline อัตราสิ้นเปลืองน้ำมัน',
                           color_discrete_sequence=['#2ECC71'])
        fig_line.update_traces(textposition="top center", line_width=3)
        fig_line.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#E0E0E0')
        st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.info("ยังไม่มีข้อมูลกราฟ")

    st.divider()
    
    # --- Export Section (ส่วนที่เพิ่มใหม่) ---
    st.subheader("📥 Export Data (ดาวน์โหลดไฟล์)")
    
    col_dl1, col_dl2 = st.columns(2)
    
    with col_dl1:
        st.write("📄 **ข้อมูลอัตราสิ้นเปลือง (km/L)**")
        if not df_cons.empty:
            csv_cons = df_cons.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="⬇️ Download Consumption CSV",
                data=csv_cons,
                file_name="xforce_consumption.csv",
                mime="text/csv",
                key='dl-cons'
            )
        else:
            st.write("(ไม่มีข้อมูล)")
            
    with col_dl2:
        st.write("🛢️ **ข้อมูลการเติมน้ำมัน**")
        if not df_refill.empty:
            csv_refill = df_refill.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="⬇️ Download Refill CSV",
                data=csv_refill,
                file_name="xforce_refill.csv",
                mime="text/csv",
                key='dl-refill'
            )
        else:
            st.write("(ไม่มีข้อมูล)")
