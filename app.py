import streamlit as st
import pandas as pd
import joblib
import plotly.express as px
import plotly.graph_objects as go 

# ==========================================
# 1. CẤU HÌNH TRANG
# ==========================================
st.set_page_config(
    layout="wide", 
    page_title="Climate Analytics Hub",
    page_icon="🌏",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. CSS SỬA LỖI MẠNH TAY & GIAO DIỆN ĐÊM
# ==========================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@300;400;500;600;700;900&display=swap');

    /* --- NỀN TRÁI ĐẤT BAN ĐÊM --- */
    [data-testid="stAppViewContainer"] {
        background-image: url("https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=2072&auto=format&fit=crop");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }
    [data-testid="stAppViewContainer"]::before {
        content: "";
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(5, 10, 20, 0.9); 
        z-index: -1;
    }

    /* --- FONT CHỮ NỘI DUNG --- */
    /* Chỉ áp dụng font đẹp cho nội dung chính */
    h1, h2, h3, h4, h5, h6, p, label, .stMarkdown, .stMetricLabel, .stMetricValue, .stDataFrame {
        font-family: 'Be Vietnam Pro', sans-serif !important;
        color: #FFFFFF !important;
        text-shadow: 0 1px 2px rgba(0,0,0,0.8);
    }
    
    /* --- KHẮC PHỤC LỖI "KEYBOARD..." (GIẢI PHÁP MẠNH TAY) --- */
    
    /* 1. Làm chữ icon hệ thống trở nên trong suốt (không nhìn thấy) */
    button, [data-testid="stSidebarCollapsedControl"] {
        color: transparent !important; 
    }
    
    /* 2. Vẽ một mũi tên giả đè lên nút Sidebar để thay thế */
    [data-testid="stSidebarCollapsedControl"]::after {
        content: "➤"; /* Mũi tên đơn giản an toàn tuyệt đối */
        color: #00F4B0; /* Màu xanh neon */
        font-size: 20px;
        position: absolute;
        top: 50%; left: 50%;
        transform: translate(-50%, -50%);
        font-family: sans-serif; /* Dùng font mặc định của máy để không bao giờ lỗi */
    }
    
    /* 3. Ẩn icon lỗi trong Expander */
    .streamlit-expanderHeader svg { display: none !important; }
    .streamlit-expanderHeader { padding-left: 1rem !important; }

    /* --- GIAO DIỆN --- */
    /* Tiêu đề Xanh Neon */
    h1, h2, h3, strong { color: #00F4B0 !important; }
    
    /* Chữ thường */
    p, label, li, .stCaption { color: #E2E8F0 !important; }

    /* Metric Card */
    div[data-testid="stMetric"] {
        background-color: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(0, 244, 176, 0.3);
        border-radius: 12px;
        padding: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.5);
    }
    div[data-testid="stMetricValue"] { font-size: 38px !important; font-weight: 700; color: #FFFFFF !important; }
    div[data-testid="stMetricLabel"] { color: #94A3B8 !important; }

    /* Sidebar */
    [data-testid="stSidebar"] { 
        background-color: #020617 !important; 
        border-right: 1px solid rgba(255, 255, 255, 0.1); 
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: #00F4B0 !important;
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
unique_cities = sorted(df['City'].unique())

# ==========================================
# 4. UI: SIDEBAR
# ==========================================
with st.sidebar:
    st.markdown("### ĐIỀU KHIỂN")
    selected_city = st.selectbox("Chọn thành phố:", unique_cities)
    st.caption("Thao tác: Di chuột vào biểu đồ để xem chi tiết.")
    
    st.markdown("---")
    st.markdown("""
        <div style="color: #00F4B0; font-weight: bold; font-size: 18px;">
        USSH.3CE TEAM
        </div>
    """, unsafe_allow_html=True)
    st.caption("Dự án Phân tích Dữ liệu Quản lý 2025")

# ==========================================
# 5. UI: HEADER CHÍNH
# ==========================================
st.markdown(f"""
    <h1>CLIMATE ANALYTICS <span style='color:#FFFFFF'>HUB</span></h1>
    <p style='font-size: 18px; color: #CBD5E1; margin-top: 5px;'>
        Báo cáo phân tích dữ liệu chuyên sâu cho <strong style='color: #00F4B0'>{selected_city}</strong>
    </p>
    <br>
""", unsafe_allow_html=True)

# ==========================================
# 6. DASHBOARD THÀNH PHỐ
# ==========================================
city_data = df[df['City'] == selected_city].copy()

if not city_data.empty:
    stats = city_data['Temperature_C'].describe()
    chart_data = city_data.set_index('Date')['Temperature_C'].resample('Y').mean().reset_index()
    current_temp = chart_data.iloc[-1]['Temperature_C']
    delta = 0
    if len(chart_data) > 1:
        delta = current_temp - chart_data.iloc[-2]['Temperature_C']

    kpi1, kpi2, kpi3 = st.columns(3)
    with kpi1:
        st.metric("Nhiệt độ TB (2020)", f"{current_temp:.1f}°C", f"{delta:.1f}°C vs năm trước")
    with kpi2:
        st.metric("Cao nhất lịch sử", f"{stats['max']:.1f}°C")
    with kpi3:
        st.metric("Thấp nhất lịch sử", f"{stats['min']:.1f}°C")

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("### Xu hướng Nhiệt độ")
    
    fig = px.area(
        chart_data, x='Date', y='Temperature_C',
        template='plotly_dark',
        color_discrete_sequence=['#00F4B0']
    )
    
    fig.update_layout(
        paper_bgcolor='rgba(15, 23, 42, 0.6)', # Nền mờ nhẹ hơn
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

    with st.expander("Xem bảng dữ liệu chi tiết"):
        st.dataframe(
            city_data[['Date', 'Temperature_C']].style.format({"Temperature_C": "{:.2f}"}), 
            use_container_width=True
        )

# ==========================================
# 7. PHẦN DỰ BÁO
# ==========================================
st.markdown("---")
st.markdown("## Phân tích & Dự báo AI")

tab1, tab2 = st.tabs(["Dữ liệu Lịch sử", "Mô hình Dự báo"])

with tab1:
    if global_data is not None:
        fig_global = px.line(global_data, template='plotly_dark')
        fig_global.update_traces(line_color='#00A3FF', line_width=3)
        fig_global.update_layout(
            paper_bgcolor='rgba(15, 23, 42, 0.6)',
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
                line=dict(color='#FF0055', width=3)
            ))
            
            fig_fc.update_layout(
                template='plotly_dark',
                paper_bgcolor='rgba(15, 23, 42, 0.6)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_family="Be Vietnam Pro",
                legend=dict(orientation="h", y=1.1),
                xaxis_title="", yaxis_title="Độ C",
                margin=dict(t=20, l=20, r=20, b=20), height=450
            )
            st.plotly_chart(fig_fc, use_container_width=True)
    else:

        st.warning("⚠️ Chưa tải được dữ liệu dự báo.")
