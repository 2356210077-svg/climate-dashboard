import streamlit as st
import pandas as pd
import joblib
import plotly.express as px
import plotly.graph_objects as go 
import streamlit.components.v1 as components

# ==========================================
# 1. CẤU HÌNH TRANG
# ==========================================
st.set_page_config(
    layout="wide", 
    page_title="Climate Analytics Hub",
    page_icon=None,
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. CSS "SIÊU CẤP" (FIX TRIỆT ĐỂ LỖI & GIAO DIỆN DARK MODE)
# ==========================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@300;400;500;600;700;900&display=swap');

    /* --- 1. NỀN TRÁI ĐẤT BAN ĐÊM --- */
    [data-testid="stAppViewContainer"] {
        background-image: url("https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=2072&auto=format&fit=crop");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }
    /* Lớp phủ tối (90%) để chữ nổi bật */
    [data-testid="stAppViewContainer"]::before {
        content: "";
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(2, 6, 15, 0.92); 
        z-index: -1;
    }

    /* --- 2. TYPOGRAPHY (FONT & MÀU) --- */
    * { font-family: 'Be Vietnam Pro', sans-serif !important; }

    /* Gradient Text cho Tiêu đề */
    h1, h2, h3, strong, .gradient-text {
        background: linear-gradient(90deg, #33FFBB 0%, #00B4FF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 900 !important;
        letter-spacing: 0.5px;
    }
    
    /* Màu chữ thường: Trắng sáng */
    p, span, div, label, li, .stCaption, .stMarkdown {
        color: #F1F5F9 !important; /* Trắng hơi xám nhẹ cho đỡ mỏi mắt */
    }

    /* --- 3. KHẮC PHỤC LỖI "KEYBOARD..." (KỸ THUẬT ZERO SIZE) --- */
    /* Bước 1: Thu nhỏ font của nút về 0 để giấu chữ lỗi */
    [data-testid="stSidebarCollapsedControl"] {
        font-size: 0 !important;
        width: 40px;
        height: 40px;
    }
    
    /* Bước 2: Vẽ mũi tên mới đè lên bằng pseudo-element */
    [data-testid="stSidebarCollapsedControl"]::after {
        content: "➤"; /* Ký tự mũi tên an toàn */
        font-size: 24px !important; /* Kích thước mũi tên */
        color: #33FFBB !important; /* Màu xanh Gradient */
        display: block;
        text-align: center;
        line-height: 40px;
        cursor: pointer;
    }

    /* Ẩn icon lỗi trong Expander */
    .streamlit-expanderHeader svg { display: none !important; }
    .streamlit-expanderHeader { padding-left: 1rem !important; }

    /* --- 4. GIAO DIỆN BẢNG DỮ LIỆU (DATAFRAME) --- */
    /* Làm trong suốt nền bảng và chỉnh màu chữ trắng */
    [data-testid="stDataFrame"], [data-testid="stTable"] {
        background-color: transparent !important;
    }
    /* Chỉnh màu chữ trong bảng thành trắng */
    div[data-testid="stDataFrame"] div {
        color: white !important;
        background-color: rgba(255, 255, 255, 0.02) !important; /* Nền dòng cực mờ */
    }
    /* Header của bảng */
    div[data-testid="stDataFrame"] div[role="columnheader"] {
        color: #33FFBB !important; /* Màu xanh cho tiêu đề cột */
        background-color: rgba(0, 0, 0, 0.5) !important;
        font-weight: bold;
    }

    /* --- 5. CARD KPI (METRIC) --- */
    div[data-testid="stMetric"] {
        background: linear-gradient(180deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.02) 100%);
        border: 1px solid rgba(51, 255, 187, 0.3);
        border-radius: 15px;
        padding: 15px;
        box-shadow: 0 0 20px rgba(0,0,0,0.6);
        backdrop-filter: blur(10px);
    }
    div[data-testid="stMetricLabel"] { 
        color: #94A3B8 !important; 
        font-size: 13px !important; 
        text-transform: uppercase;
        letter-spacing: 1px;
        -webkit-text-fill-color: #94A3B8 !important; /* Label không gradient */
    }
    div[data-testid="stMetricValue"] { 
        font-size: 40px !important; 
        font-weight: 800;
        /* Value dùng Gradient */
        background: linear-gradient(90deg, #FFFFFF 0%, #D1D5DB 100%); 
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* --- 6. SIDEBAR --- */
    [data-testid="stSidebar"] { 
        background-color: #020617 !important; 
        border-right: 1px solid rgba(255, 255, 255, 0.05); 
    }
    
    /* --- 7. KHUNG BẢN ĐỒ & BIỂU ĐỒ --- */
    iframe {
        border-radius: 15px;
        border: 1px solid rgba(51, 255, 187, 0.3);
        box-shadow: 0 0 20px rgba(0,0,0,0.5);
    }
    .streamlit-expanderHeader {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: #33FFBB !important; /* Chữ tiêu đề expander màu xanh */
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. HÀM XỬ LÝ DỮ LIỆU
# ==========================================
@st.cache_data
def load_data(filepath='city_temperatures_clean.zip'): 
    try:
        df = pd.read_csv(filepath)
    except FileNotFoundError:
        st.error(f"❌ Lỗi: Không tìm thấy file '{filepath}'.")
        return pd.DataFrame() 
    
    if 'AvgTemperature' in df.columns:
        if not pd.api.types.is_datetime64_any_dtype(df['Date']):
             df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df = df.dropna(subset=['AvgTemperature', 'Date', 'City'])
        
        if df['AvgTemperature'].mean() > 60:
            df['Temperature_C'] = (df['AvgTemperature'] - 32) * 5/9
        else:
            df['Temperature_C'] = df['AvgTemperature']
            
        # Việt hóa tên cột để hiển thị đẹp trong bảng
        df = df.rename(columns={
            'Date': 'Ngày',
            'Temperature_C': 'Nhiệt độ (°C)',
            'City': 'Thành phố',
            'Country': 'Quốc gia'
        })
    return df

@st.cache_resource
def load_model(model_path='model_Global.pkl'): 
    try: return joblib.load(model_path)
    except: return None

@st.cache_data
def load_global_data(path='global_temp_series.pkl'):
    try:
        data = joblib.load(path)
        if not isinstance(data.index, pd.DatetimeIndex):
            data.index = pd.to_datetime(data.index)
        return data.resample('ME').mean()
    except: return None

# KHỞI TẠO
df = load_data()
model_global = load_model()
global_data = load_global_data()
if df.empty: st.stop()

unique_cities = sorted(df['Thành phố'].unique())

# ==========================================
# 4. UI: SIDEBAR (SẠCH SẼ, KHÔNG ICON)
# ==========================================
with st.sidebar:
    st.markdown("### ĐIỀU KHIỂN")
    selected_city = st.selectbox("Chọn thành phố:", unique_cities)
    st.caption("Thao tác: Di chuột vào biểu đồ để xem chi tiết.")
    
    st.markdown("---")
    # Tên nhóm Gradient
    st.markdown("""
        <div class='gradient-text' style='font-size: 20px;'>
        USSH.3CE TEAM
        </div>
    """, unsafe_allow_html=True)
    st.caption("Dự án Phân tích Dữ liệu Quản lý 2025")

# ==========================================
# 5. UI: HEADER CHÍNH (GRADIENT)
# ==========================================
st.markdown(f"""
    <h1>CLIMATE ANALYTICS <span class='gradient-text'>HUB</span></h1>
    <p style='font-size: 18px; color: #CBD5E1; margin-top: 5px;'>
        Báo cáo phân tích dữ liệu chuyên sâu cho <strong class='gradient-text'>{selected_city}</strong>
    </p>
    <br>
""", unsafe_allow_html=True)

# ==========================================
# 6. DASHBOARD THÀNH PHỐ
# ==========================================
city_data = df[df['Thành phố'] == selected_city].copy()

if not city_data.empty:
    stats = city_data['Nhiệt độ (°C)'].describe()
    chart_data = city_data.set_index('Ngày')['Nhiệt độ (°C)'].resample('Y').mean().reset_index()
    current_temp = chart_data.iloc[-1]['Nhiệt độ (°C)']
    delta = 0
    if len(chart_data) > 1:
        delta = current_temp - chart_data.iloc[-2]['Nhiệt độ (°C)']

    # KPI Row
    kpi1, kpi2, kpi3 = st.columns(3)
    with kpi1:
        st.metric("Nhiệt độ TB (2020)", f"{current_temp:.1f}°C", f"{delta:.1f}°C vs năm trước")
    with kpi2:
        st.metric("Cao nhất lịch sử", f"{stats['max']:.1f}°C")
    with kpi3:
        st.metric("Thấp nhất lịch sử", f"{stats['min']:.1f}°C")

    st.markdown("<br>", unsafe_allow_html=True)

    # --- BẢN ĐỒ VỆ TINH ---
    st.markdown("### 🗺️ Vị trí Địa lý")
    map_url = f"https://maps.google.com/maps?q={selected_city}&t=k&z=11&ie=UTF8&iwloc=&output=embed"
    components.iframe(map_url, height=350, scrolling=False)
    st.markdown("<br>", unsafe_allow_html=True)

    # --- BIỂU ĐỒ XU HƯỚNG ---
    st.markdown("### 📈 Xu hướng Nhiệt độ")
    
    fig = px.area(
        chart_data, x='Ngày', y='Nhiệt độ (°C)',
        template='plotly_dark',
        color_discrete_sequence=['#33FFBB'] # Xanh Sáng
    )
    
    fig.update_layout(
        paper_bgcolor='rgba(15, 23, 42, 0.8)', # Nền đen mờ 80% để tách biệt
        plot_bgcolor='rgba(0,0,0,0)',
        font_family="Be Vietnam Pro",
        hovermode="x unified",
        xaxis=dict(showgrid=False, title="", showticklabels=True),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', title="Độ C", zeroline=False),
        margin=dict(l=20, r=20, t=20, b=20),
        height=450
    )
    fig.update_traces(fill='tozeroy', line=dict(width=3))
    st.plotly_chart(fig, use_container_width=True)

    # --- BẢNG DỮ LIỆU CHI TIẾT (ĐÃ TỐI ƯU CSS) ---
    with st.expander("Xem bảng dữ liệu chi tiết"):
        st.dataframe(
            city_data[['Ngày', 'Nhiệt độ (°C)']].style.format({"Nhiệt độ (°C)": "{:.2f}"}), 
            use_container_width=True
        )

# ==========================================
# 7. PHẦN DỰ BÁO
# ==========================================
st.markdown("---")
st.markdown("## 🔮 Phân tích & Dự báo AI")

tab1, tab2 = st.tabs(["Dữ liệu Lịch sử", "Mô hình Dự báo"])

with tab1:
    if global_data is not None:
        global_viz = global_data.copy()
        global_viz.name = "Nhiệt độ TB (°C)"
        fig_global = px.line(global_viz, template='plotly_dark')
        fig_global.update_traces(line_color='#00B4FF', line_width=3) # Xanh Dương Sáng
        fig_global.update_layout(
            paper_bgcolor='rgba(15, 23, 42, 0.8)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis_title="", yaxis_title="Độ C", margin=dict(t=20, l=20, r=20, b=20)
        )
        st.plotly_chart(fig_global, use_container_width=True)

with tab2:
    if model_global is not None and global_data is not None:
        col_opt, col_chart = st.columns([1, 3])
        with col_opt:
            st.markdown("#### Tham số")
            years = st.slider('Số năm dự báo:', 1, 10, 5)
            st.caption("Kéo thanh trượt để điều chỉnh thời gian.")
        
        with col_chart:
            steps = 12 * years
            last_date = global_data.index.max()
            idx = pd.date_range(start=last_date + pd.DateOffset(months=1), periods=steps, freq='ME')
            forecast = pd.DataFrame(model_global.forecast(steps), index=idx, columns=['Dự báo'])
            y_hist = global_data.iloc[:, 0] if isinstance(global_data, pd.DataFrame) else global_data

            fig_fc = go.Figure()
            fig_fc.add_trace(go.Scatter(
                x=global_data.index, y=y_hist, mode='lines', name='Lịch sử',
                line=dict(color='rgba(255, 255, 255, 0.3)', width=2)
            ))
            fig_fc.add_trace(go.Scatter(
                x=forecast.index, y=forecast['Dự báo'], mode='lines', name='Dự báo AI',
                line=dict(color='#FF006E', width=3) # Hồng Neon
            ))
            fig_fc.update_layout(
                template='plotly_dark',
                paper_bgcolor='rgba(15, 23, 42, 0.8)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_family="Be Vietnam Pro",
                legend=dict(orientation="h", y=1.1),
                xaxis_title="", yaxis_title="Độ C",
                margin=dict(t=20, l=20, r=20, b=20), height=450
            )
            st.plotly_chart(fig_fc, use_container_width=True)
    else:
        st.warning("⚠️ Chưa tải được dữ liệu dự báo.")
