import streamlit as st
import joblib
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# 1. إعدادات الصفحة والهوية الأكاديمية
st.set_page_config(page_title="ASA-Smart-Mix2 | AI-Based Eco-Concrete Optimizer", layout="wide", page_icon="🏗️")

# تنسيق الـ CSS المتقدم (من البرنامج الأول + إضافات)
st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 12px; border-left: 6px solid #004a99; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .header-container { background-color: #f8f9fa; padding: 30px; border-radius: 15px; border: 2px solid #004a99; margin-bottom: 25px; text-align: center; }
    .footer-text { text-align: center; color: #666; font-size: 0.9em; margin-top: 50px; padding: 20px; border-top: 2px solid #eee; }
    .login-title { color: #004a99; text-align: center; font-weight: bold; margin-bottom: 20px; }
    .stButton>button { width: 100%; border-radius: 8px; background-color: #004a99; color: white; }
    .report-card { background-color: #e3f2fd; padding: 20px; border-radius: 15px; border-right: 8px solid #01579b; margin-top: 20px; }
    </style>
    """, unsafe_allow_html=True)

# 2. نظام الدخول الآمن (Authentication)
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    col_l, col_mid, col_r = st.columns([1, 2, 1])
    with col_mid:
        st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
        # الشعارات (استخدام روابط Raw لضمان الظهور)
        l_col1, l_col2 = st.columns(2)
        with l_col1:
            st.image("https://raw.githubusercontent.com/ayasanad14799-coder/ASA-Smart-Mix2/main/LOGO.png", width=150)
        with l_col2:
            st.image("https://raw.githubusercontent.com/ayasanad14799-coder/ASA-Smart-Mix2/main/OIP.jfif", width=150)
        
        st.markdown("<h2 class='login-title'>ASA-Smart-Mix2: AI Eco-Concrete Optimizer</h2>", unsafe_allow_html=True)
        st.subheader("🔒 Secure Access Portal")
        
        with st.form("login_form"):
            user_pass = st.text_input("Enter Access Key", type="password")
            submit_login = st.form_submit_button("Access System")
            
            if submit_login:
                if user_pass == "ASA2024": # يمكنك تغيير الباسورد هنا
                    st.session_state.auth = True
                    st.rerun()
                else:
                    st.error("Invalid Access Key. Please contact Eng. Aya Sanad.")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# 3. تحميل الموديل والبيانات (Caching)
@st.cache_resource
def load_assets():
    model = joblib.load('concrete_model.joblib')
    scaler = joblib.load('scaler.joblib')
    # حل مشكلة الـ KeyError: قراءة الملف وتنظيفه
    try:
        db = pd.read_csv('Trail3_DIAMOND_DATABASE.csv', sep=';')
    except:
        db = pd.read_csv('Trail3_DIAMOND_DATABASE.csv')
    db.columns = db.columns.str.strip() # حذف أي مسافات من أسماء الأعمدة
    return model, scaler, db

model, scaler, db = load_assets()

# 4. واجهة المستخدم الرئيسية
st.markdown("<div class='header-container'><h1>🏗️ ASA-Smart-Mix2 Dashboard</h1><p>Advanced AI System for Sustainable Concrete Design</p></div>", unsafe_allow_html=True)

# القائمة الجانبية للمدخلات
st.sidebar.header("📋 Mix Parameters")
with st.sidebar:
    st.subheader("Binders (kg/m³)")
    cement = st.number_input("Cement", 250, 600, 350)
    sf = st.slider("Silica Fume", 0, 100, 0)
    fa = st.slider("Fly Ash", 0, 200, 0)
    wc = st.slider("W/C Ratio", 0.25, 0.75, 0.45)
    
    st.subheader("Aggregates")
    nca = st.number_input("Natural Coarse (kg/m³)", 500, 1300, 1100)
    nfa = st.number_input("Fine Aggregate (kg/m³)", 400, 1000, 700)
    rca_p = st.slider("RCA Replacement (%)", 0, 100, 0)
    mrca_p = st.slider("MRCA Replacement (%)", 0, 100, 0)
    
    st.subheader("Additives")
    sp = st.slider("Superplasticizer", 0.0, 15.0, 2.0)
    fiber = st.slider("Nylon Fiber", 0.0, 5.0, 0.0)

# 5. التنبؤ والحسابات المتقدمة
water = wc * (cement + sf + fa)
# المتجه بالترتيب الـ 11
features = np.array([[cement, water, nca, nfa, rca_p, mrca_p, sf, fa, fiber, wc, sp]])
features_scaled = scaler.transform(features)
prediction = model.predict(features_scaled)[0]

# حسابات الـ LCA والتكلفة
co2_breakdown = {
    "Cement": cement * 0.85,
    "Silica Fume": sf * 0.02,
    "Fly Ash": fa * 0.01,
    "Aggregates": (nca + nfa) * 0.005,
    "Additives": sp * 0.7 + fiber * 2.5
}
total_co2 = sum(co2_breakdown.values())
total_cost = (cement*0.1 + sf*0.25 + fa*0.03 + nca*0.015 + nfa*0.012 + sp*1.5 + fiber*4.0)

# 6. عرض النتائج التفاعلية (Plotly)
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("<div class='stMetric'>", unsafe_allow_html=True)
    st.subheader("🎯 Strength & Sustainability Gauge")
    
    # 1. Gauge Chart (مقياس الاستدامة)
    sust_index = (prediction / (total_co2 * total_cost)) * 1000
    # تحديد الرتبة
    rank = "C"
    if sust_index > 4.5: rank = "A+"
    elif sust_index > 3.5: rank = "A"
    elif sust_index > 2.0: rank = "B"
    
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = sust_index,
        title = {'text': f"Rank: {rank}"},
        gauge = {'axis': {'range': [0, 6]},
                 'bar': {'color': "#004a99"},
                 'steps' : [
                     {'range': [0, 2], 'color': "#ffcdd2"},
                     {'range': [2, 4], 'color': "#fff9c4"},
                     {'range': [4, 6], 'color': "#c8e6c9"}]}))
    st.plotly_chart(fig_gauge, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='stMetric'>", unsafe_allow_html=True)
    st.subheader("📊 Performance Balance (Radar)")
    
    # 2. Radar Chart (الرادار الذكي)
    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=[prediction/100, (600-total_co2)/600, (100-total_cost)/100, (100-rca_p)/100],
        theta=['Strength', 'Eco-Score', 'Economy', 'Durability'],
        fill='toself', name='Current Mix'
    ))
    fig_radar.update_layout(polar=dict(radialaxis=dict(visible=False, range=[0, 1])), showlegend=False)
    st.plotly_chart(fig_radar, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

# 7. تقرير LCA و Benchmarking
col3, col4 = st.columns([1, 1])

with col3:
    st.subheader("🌱 Instant LCA Report")
    # 3. LCA Pie Chart (تقرير الكربون الفوري)
    fig_lca = px.pie(values=list(co2_breakdown.values()), names=list(co2_breakdown.keys()), 
                     title="CO2 Contribution by Material", hole=0.4, color_discrete_sequence=px.colors.sequential.Blues_r)
    st.plotly_chart(fig_lca, use_container_width=True)

with col4:
    st.subheader("🏆 Benchmarking (Closest Lab Mixes)")
    # 4. المقارنة المرجعية (Benchmarking)
    # حل مشكلة الـ KeyError بضمان وجود العمود
    if 'CS_28' in db.columns:
        db['diff'] = abs(db['CS_28'] - prediction)
        closest_mixes = db.sort_values('diff').head(3)
        st.dataframe(closest_mixes[['Mix_ID', 'CS_28', 'Sustainability', 'CO2']])
        st.info("💡 Pro-Tip: The closer your mix to lab results, the higher the reliability.")

# تذييل الصفحة
st.markdown(f"""
    <div class='footer-text'>
    <p>ASA-Smart-Mix2 | AI Optimization Engine | Accuracy: 95.3%</p>
    <p>Developed by: Eng. Aya Sanad | Faculty of Engineering | 2024</p>
    </div>
    """, unsafe_allow_html=True)
