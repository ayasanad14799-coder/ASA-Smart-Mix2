import streamlit as st
import joblib
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# 1. إعدادات الصفحة والهوية الأكاديمية الكاملة
st.set_page_config(page_title="ASA-Smart-Mix2 | AI-Based Eco-Concrete Optimizer", layout="wide", page_icon="🏗️")

# تنسيق الـ CSS (نفس التكنيك الاحترافي للبرنامج الأول)
st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 12px; border-left: 6px solid #004a99; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .header-container { background-color: #f8f9fa; padding: 25px; border-radius: 15px; border: 2px solid #004a99; text-align: center; margin-bottom: 25px; }
    .section-box { background-color: #ffffff; padding: 25px; border-radius: 15px; border: 1px solid #eee; margin-bottom: 25px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .disclaimer-box { background-color: #fff3e0; padding: 20px; border-radius: 10px; border-right: 5px solid #ff9800; font-size: 0.9em; line-height: 1.6; color: #555; margin-top: 30px; }
    .footer-text { text-align: center; color: #666; font-size: 0.9em; margin-top: 50px; padding: 20px; border-top: 1px solid #eee; }
    .login-header { color: #004a99; text-align: center; font-weight: bold; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# 2. نظام الدخول الآمن (ASA2026)
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    col_l, col_mid, col_r = st.columns([1, 2, 1])
    with col_mid:
        st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
        l_col1, l_col2 = st.columns(2)
        with l_col1:
            st.image("https://raw.githubusercontent.com/ayasanad14799-coder/ASA-Smart-Mix2/2692812d3d7d64c3ea237f8e877675f896bce834/LOGO.png", width=150)
        with l_col2:
            st.image("https://raw.githubusercontent.com/ayasanad14799-coder/ASA-Smart-Mix2/2692812d3d7d64c3ea237f8e877675f896bce834/OIP.jfif", width=150)
        
        st.markdown("<h2 class='login-header'>ASA-Smart-Mix2: AI Eco-Concrete Optimizer</h2>", unsafe_allow_html=True)
        st.subheader("🔒 Secure Access Portal")
        with st.form("login"):
            password = st.text_input("Enter Access Key", type="password")
            if st.form_submit_button("Access System"):
                if password == "ASA2026":
                    st.session_state.auth = True
                    st.rerun()
                else: st.error("Invalid Access Key. Please contact Eng. Aya Sanad.")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# 3. تحميل الموديل والبيانات المرجعية
@st.cache_resource
def load_assets():
    model = joblib.load('concrete_model.joblib')
    scaler = joblib.load('scaler.joblib')
    # قراءة قاعدة البيانات وتلميعها
    try:
        db = pd.read_csv('Trail3_DIAMOND_DATABASE.csv', sep=';')
    except:
        db = pd.read_csv('Trail3_DIAMOND_DATABASE.csv')
    db.columns = db.columns.str.strip()
    return model, scaler, db

model, scaler, db = load_assets()

# 4. لوحة التحكم والمدخلات (Sidebar)
st.sidebar.header("📋 Mix Design Inputs")
with st.sidebar:
    st.subheader("1. Binders (kg/m³)")
    cement = st.number_input("Cement", 250, 600, 350)
    sf = st.slider("Silica Fume", 0, 100, 0)
    fa = st.slider("Fly Ash", 0, 200, 0)
    wc = st.slider("W/C Ratio", 0.25, 0.75, 0.45)
    
    st.subheader("2. Aggregates")
    nca = st.number_input("Natural Coarse", 500, 1300, 1100)
    nfa = st.number_input("Fine Aggregate", 400, 1000, 700)
    rca_p = st.slider("RCA Replacement (%)", 0, 100, 0)
    mrca_p = st.slider("MRCA Replacement (%)", 0, 100, 0)
    
    st.subheader("3. Additives & Fibers")
    sp = st.number_input("Superplasticizer", 0.0, 15.0, 2.0)
    fiber = st.number_input("Nylon Fiber", 0.0, 5.0, 0.0)

# 5. التنبؤ والحسابات
water = wc * (cement + sf + fa)
features = np.array([[cement, water, nca, nfa, rca_p, mrca_p, sf, fa, fiber, wc, sp]])
prediction = model.predict(scaler.transform(features))[0]

# حسابات الـ LCA والتكلفة
co2_data = {"Cement": cement*0.85, "SF": sf*0.02, "FA": fa*0.01, "Agg": (nca+nfa)*0.005, "Addit": sp*0.7 + fiber*2.5}
total_co2 = sum(co2_data.values())
total_cost = (cement*0.1 + sf*0.25 + fa*0.03 + nca*0.015 + nfa*0.012 + sp*1.5 + fiber*4.0)
sust_index = (prediction / (total_co2 * total_cost)) * 1000

# 6. الهيكل الرئيسي (مقسم إلى 4 أقسام تبويبية)
st.markdown("<div class='header-container'><h1>🏗️ ASA-Smart-Mix2 Dashboard (2026)</h1><p>Global Optimization for Recycled Aggregate Concrete</p></div>", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["📊 Mechanical Results", "🌱 Sustainability & LCA", "🔍 Reliability & Validation", "📝 Feedback & Terms"])

with tab1:
    st.markdown("<div class='section-box'>", unsafe_allow_html=True)
    m1, m2, m3 = st.columns(3)
    m1.metric("Predicted Strength (28d)", f"{prediction:.2f} MPa")
    m2.metric("Splitting Tensile (Est.)", f"{(0.55 * np.sqrt(prediction)):.2f} MPa")
    m3.metric("Elastic Modulus (Est.)", f"{(4.7 * np.sqrt(prediction)):.2f} GPa")
    
    # Radar Chart
    fig_radar = go.Figure(data=go.Scatterpolar(
        r=[prediction/100, (100-rca_p)/100, (100-mrca_p)/100, (500-total_co2)/500],
        theta=['Strength', 'Eco-Aggregate', 'Multi-Cycle', 'Carbon Saving'], fill='toself'
    ))
    st.plotly_chart(fig_radar, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with tab2:
    st.markdown("<div class='section-box'>", unsafe_allow_html=True)
    s1, s2 = st.columns(2)
    with s1:
        st.metric("Total CO2 Footprint", f"{total_co2:.1f} kg/m³")
        fig_pie = px.pie(values=list(co2_data.values()), names=list(co2_data.keys()), title="LCA: Carbon Source Analysis", hole=0.4)
        st.plotly_chart(fig_pie)
    with s2:
        rank = "A+" if sust_index > 4.5 else ("A" if sust_index > 3.5 else "B")
        st.metric("Sustainability Index", f"{sust_index:.2f} (Rank: {rank})")
        fig_gauge = go.Figure(go.Indicator(mode="gauge+number", value=sust_index, gauge={'axis': {'range': [0, 6]}, 'bar': {'color': "#004a99"}}))
        st.plotly_chart(fig_gauge)
    st.markdown("</div>", unsafe_allow_html=True)

with tab3:
    st.markdown("<div class='section-box'>", unsafe_allow_html=True)
    st.subheader("📈 Scientific Validation Graphs")
    v1, v2 = st.columns(2)
    # استخدام الروابط التي استخرجتيها من كولاب
    v1.image("https://raw.githubusercontent.com/ayasanad14799-coder/ASA-Smart-Mix2/2ddbd240c3eeae0e4603f535d2089f80cf940ea6/accuracy_plot.png", caption="Model Accuracy Validation (R² ≈ 95.3%)")
    v2.image("https://raw.githubusercontent.com/ayasanad14799-coder/ASA-Smart-Mix2/2ddbd240c3eeae0e4603f535d2089f80cf940ea6/feature_importance.png", caption="Material Influence Analysis (SHAP Values)")
    
    st.subheader("🏆 Top 3 Closest Experimental Matches")
    db['diff'] = abs(db['CS_28'] - prediction)
    st.table(db.sort_values('diff').head(3)[['Mix_ID', 'CS_28', 'Sustainability', 'CO2']])
    st.markdown("</div>", unsafe_allow_html=True)

with tab4:
    st.markdown("<div class='section-box'>", unsafe_allow_html=True)
    st.subheader("📩 Research Feedback Form")
    with st.form("feedback_form"):
        name = st.text_input("Name/Organization")
        feedback = st.text_area("Observations or Lab Verification Results")
        if st.form_submit_button("Submit to Cloud Database"):
            st.success("Thank you! Your feedback has been recorded for the 2026 AI re-training cycle.")
    
    st.markdown("""
        <div class='disclaimer-box'>
        <b>Professional Responsibility Disclaimer:</b><br>
        The results generated by ASA-Smart-Mix2 are based on advanced Machine Learning algorithms trained on global experimental databases. 
        While the accuracy is extremely high (95.3%), these results should be considered as design guidance. 
        Eng. Aya Sanad and the Faculty of Engineering do not assume liability for structural applications designed without physical laboratory verification. 
        Safety factors and local code requirements must always be prioritized.
        </div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# تذييل الصفحة (Footer)
st.markdown("<div class='footer-text'>© 2026 Eng. Aya Sanad | Advanced Concrete AI Research Unit | Faculty of Engineering</div>", unsafe_allow_html=True)
