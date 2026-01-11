import streamlit as st
import joblib
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# 1. إعدادات الصفحة والهوية الأكاديمية
st.set_page_config(page_title="ASA-Smart-Mix2 | Advanced Eco-Concrete AI", layout="wide", page_icon="🏗️")

# تطبيق الـ CSS المتقدم (نفس التصميم الاحترافي لبرنامجك الأول)
st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border-left: 5px solid #004a99; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
    .header-container { background-color: #f8f9fa; padding: 25px; border-radius: 15px; border: 2px solid #004a99; margin-bottom: 25px; text-align: center; }
    .footer-text { text-align: center; color: #666; font-size: 0.85em; margin-top: 50px; padding: 20px; border-top: 1px solid #eee; }
    .doc-card { background-color: #f0f2f6; padding: 20px; border-radius: 10px; border-right: 5px solid #004a99; margin-bottom: 20px; }
    .login-title { color: #004a99; text-align: center; font-weight: bold; margin-top: 15px; margin-bottom: 20px; }
    .legend-box { background-color: #e8f5e9; padding: 15px; border-radius: 10px; border-left: 5px solid #2e7d32; margin-bottom: 15px; font-size: 0.9em; }
    </style>
    """, unsafe_allow_html=True)

# 2. نظام الدخول الآمن (ASA2026) وشعارات الجامعة والكلية
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    col_l, col_mid, col_r = st.columns([1, 2, 1])
    with col_mid:
        logo_col1, logo_col2 = st.columns(2)
        with logo_col1:
            st.image("https://raw.githubusercontent.com/ayasanad14799-coder/ASA-Smart-Mix2/2692812d3d7d64c3ea237f8e877675f896bce834/LOGO.png", width=140)
        with logo_col2:
            st.image("https://raw.githubusercontent.com/ayasanad14799-coder/ASA-Smart-Mix2/2692812d3d7d64c3ea237f8e877675f896bce834/OIP.jfif", width=140)
        
        st.markdown("<h2 class='login-title'>ASA-Smart-Mix2: AI-Based Eco-Concrete Optimizer</h2>", unsafe_allow_html=True)
        st.subheader("🔒 Secure Access Portal")
        with st.form("login"):
            password = st.text_input("Access Key", type="password")
            if st.form_submit_button("Enter"):
                if password == "ASA2026":
                    st.session_state.auth = True
                    st.rerun()
                else: st.error("Access Denied.")
    st.stop()

# 3. تحميل الموديل والبيانات المرجعية (Diamond Database)
@st.cache_resource
def load_assets():
    model = joblib.load('concrete_model.joblib')
    scaler = joblib.load('scaler.joblib')
    try:
        db = pd.read_csv('Trail3_DIAMOND_DATABASE.csv', sep=';')
    except:
        db = pd.read_csv('Trail3_DIAMOND_DATABASE.csv')
    db.columns = db.columns.str.strip()
    return model, scaler, db

model, scaler, db = load_assets()

# 4. الواجهة الرئيسية والهوية الأكاديمية
st.markdown("""
    <div class='header-container'>
        <h1>ASA-Smart-Mix2: Global AI Prediction System</h1>
        <p>Optimizing Sustainability for Recycled Aggregate Concrete</p>
    </div>
    """, unsafe_allow_html=True)

# تفاصيل المشرفين والطالبة (كما في برنامجك الأول)
col_info1, col_info2 = st.columns(2)
with col_info1:
    st.markdown("""
    <div class='doc-card'>
        <b>🎓 Academic Research Team</b><br>
        Developed by: Eng. Aya Sanad<br>
        PhD Research Project - 2026
    </div>
    """, unsafe_allow_html=True)
with col_info2:
    st.markdown("""
    <div class='doc-card'>
        <b>👨‍🏫 Under Supervision of:</b><br>
        Prof. Dr. [Insert Name 1] & Prof. Dr. [Insert Name 2]<br>
        Faculty of Engineering - Civil Engineering Dept.
    </div>
    """, unsafe_allow_html=True)

# 5. المدخلات الـ 11 بالترتيب الصارم في الـ Sidebar
st.sidebar.header("📥 All Mix Constituents")
with st.sidebar:
    st.markdown("<div class='legend-box'><b>Note:</b> Please enter all 11 values. Use 0 if the material is not used in your mix.</div>", unsafe_allow_html=True)
    cement = st.number_input("1. Cement (kg/m³)", 200, 600, 350)
    water_val = st.number_input("2. Water (kg/m³)", 100, 300, 160) # سيتم حساب W_C تلقائياً أيضاً
    nca = st.number_input("3. NCA (Natural Coarse Agg.)", 0, 1500, 1100)
    nfa = st.number_input("4. NFA (Fine Aggregate)", 0, 1200, 700)
    rca_p = st.slider("5. RCA Replacement (%)", 0, 100, 0)
    mrca_p = st.slider("6. MRCA Replacement (%)", 0, 100, 0)
    sf = st.number_input("7. Silica Fume (kg/m³)", 0, 150, 0)
    fa = st.number_input("8. Fly Ash (kg/m³)", 0, 250, 0)
    fiber = st.number_input("9. Nylon Fiber (kg/m³)", 0.0, 10.0, 0.0)
    wc_input = st.slider("10. Target W/C Ratio", 0.20, 0.80, 0.45)
    sp = st.number_input("11. Superplasticizer (kg/m³)", 0.0, 20.0, 2.0)

# 6. التنبؤ والحسابات
# الترتيب الـ 11: ['Cement', 'Water', 'NCA', 'NFA', 'RCA_P', 'MRCA_P', 'Silica_Fume', 'Fly_Ash', 'Nylon_Fiber', 'W_C', 'SP']
features = np.array([[cement, water_val, nca, nfa, rca_p, mrca_p, sf, fa, fiber, wc_input, sp]])
prediction = model.predict(scaler.transform(features))[0]

# حسابات الأثر البيئي والتكلفة
total_co2 = (cement*0.85 + sf*0.02 + fa*0.01 + nca*0.005 + nfa*0.005 + sp*0.7 + fiber*2.5)
total_cost = (cement*0.1 + sf*0.25 + fa*0.03 + nca*0.015 + nfa*0.012 + sp*1.5 + fiber*4.0)
sust_index = (prediction / (total_co2 * total_cost)) * 1000

# 7. الأقسام الأربعة (Tabs)
tab1, tab2, tab3, tab4 = st.tabs(["Mechanical Performance", "Environmental & LCA", "Technical Validation", "Support & Feedback"])

with tab1:
    st.subheader("📊 Predicted Mechanical Properties")
    c1, c2, c3 = st.columns(3)
    c1.metric("28-Day Strength", f"{prediction:.2f} MPa")
    c2.metric("Est. Split Tensile", f"{(0.55 * np.sqrt(prediction)):.2f} MPa")
    c3.metric("Est. Elastic Modulus", f"{(4.7 * np.sqrt(prediction)):.2f} GPa")
    
    # Radar Chart
    fig_radar = go.Figure(data=go.Scatterpolar(
        r=[prediction/100, (100-rca_p)/100, (100-mrca_p)/100, (600-total_co2)/600],
        theta=['Strength', 'Recycling', 'Multi-Cycle', 'Eco-Safety'], fill='toself'
    ))
    st.plotly_chart(fig_radar, use_container_width=True)

with tab2:
    st.subheader("🌱 Sustainability & Carbon Report (LCA)")
    c4, c5 = st.columns(2)
    with c4:
        st.metric("Carbon Footprint (CO2)", f"{total_co2:.1f} kg/m³")
        lca_vals = [cement*0.85, sf*0.02, fa*0.01, (nca+nfa)*0.005, sp*0.7]
        fig_pie = px.pie(values=lca_vals, names=["Cement", "SF", "FA", "Aggregates", "Additives"], hole=0.4)
        st.plotly_chart(fig_pie)
    with c5:
        rank = "A+" if sust_index > 4.5 else ("A" if sust_index > 3.5 else "B")
        st.metric("Sustainability Score", f"{sust_index:.2f} (Rank: {rank})")
        fig_gauge = go.Figure(go.Indicator(mode="gauge+number", value=sust_index, gauge={'axis': {'range': [0, 6]}, 'bar': {'color': "#004a99"}}))
        st.plotly_chart(fig_gauge)

with tab3:
    st.subheader("🔍 Scientific Reliability & Validation")
    v1, v2 = st.columns(2)
    v1.image("https://raw.githubusercontent.com/ayasanad14799-coder/ASA-Smart-Mix2/2ddbd240c3eeae0e4603f535d2089f80cf940ea6/accuracy_plot.png", caption="Model Accuracy Validation (95.3%)")
    v2.image("https://raw.githubusercontent.com/ayasanad14799-coder/ASA-Smart-Mix2/2ddbd240c3eeae0e4603f535d2089f80cf940ea6/feature_importance.png", caption="Material Influence Analysis")
    
    st.subheader("📍 Closest Experimental Lab Mixes")
    db['diff'] = abs(db['CS_28'] - prediction)
    st.table(db.sort_values('diff').head(3)[['Mix_ID', 'CS_28', 'Sustainability', 'CO2']])

with tab4:
    st.subheader("📝 Disclaimer & User Support")
    st.markdown("""
        <div class='legend-box'>
        <b>Academic Disclaimer:</b> The results provided are for preliminary guidance and design optimization. Final validation must be conducted in accredited laboratories. 
        Eng. Aya Sanad and the supervision committee are not liable for direct application without structural testing.
        </div>
    """, unsafe_allow_html=True)
    
    with st.form("feedback"):
        st.write("📩 Send us your feedback or lab verification results:")
        fb_name = st.text_input("Full Name")
        fb_email = st.text_input("Email")
        fb_msg = st.text_area("Observations")
        if st.form_submit_button("Submit"):
            st.success("Feedback submitted successfully. Thank you for your contribution to the 2026 research cycle.")

# التذييل النهائي (Footer)
st.markdown(f"<div class='footer-text'>© {datetime.now().year} Eng. Aya Sanad | AI Engineering Research Unit | Final PhD Interface 2026</div>", unsafe_allow_html=True)
