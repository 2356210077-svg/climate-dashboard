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
    page_icon="🌏",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. CSS TỐI ƯU (CHỈNH FONT CÓ CHỌN LỌC & MÀU SẮC PHẲNG)
# ==========================================
st.markdown("""
    <style>
    /* Import font Be Vietnam Pro */
    @import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@300;400;500;600;700;900&display=swap');

    /* --- 1. NỀN TRÁI ĐẤT BAN ĐÊM (Giao diện tối mặc định) --- */
    [data-testid="stAppViewContainer"] {
        background-image: url("https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=2072&auto=format&fit=crop");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }
    /* Lớp phủ tối (90%) */
    [data-testid="stAppViewContainer"]::before {
        content: "";
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(2, 6, 15, 0.92); 
        z-index: -1;
    }

    /* --- 2. TYPOGRAPHY (CHỈ ÁP DỤNG CHO VĂN BẢN CỤ THỂ) --- */
    /* Thay vì ép toàn bộ (*), ta chỉ ép font cho các thẻ văn bản chính */
    h1, h2, h3, h4, h5, h6, p, label, .stMarkdown, .stMetricLabel, .stMetricValue, .stDataFrame {
        font-family: 'Be Vietnam Pro', sans-serif !important;
        /* Xóa bỏ hoàn toàn hiệu ứng đổ bóng chữ */
        text-shadow: none !important;
    }
    
    /* --- 3. MÀU SẮC & GRADIENT --- */
    /* Gradient Xanh Ngọc cho các điểm nhấn và tiêu đề phụ */
    h1 span, strong, .gradient-text, h2, h3, h4, h5, h6 {
        background: linear-gradient(90deg, #33FFBB 0%, #00B4FF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 900 !important;
        letter-spacing: 0.5px;
        
        /* Xóa bỏ filter drop-shadow */
        filter: none !important; 
    }
    
    /* Chữ tiêu đề chính màu trắng (phần không gradient) */
    h1 { 
        color: white !important; 
        text-shadow: none !important;
    }
    
    /* Chữ thường màu trắng xám */
    p, span, div, label, li, .stCaption {
        color: #E0E6ED;
    }

    /* --- 4. GIAO DIỆN CÁC THÀNH PHẦN --- */
    
    /* Metric Card (KPI) */
    div[data-testid="stMetric"] {
        background: linear-gradient(180deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.02) 100%);
        border: 1px solid rgba(51, 255, 187, 0.3);
        border-radius: 15px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        backdrop-filter: blur(10px);
        transition: transform 0.2s;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-5px);
        border-color: #33FFBB;
        box-shadow: 0 10px 20px rgba(51, 255, 187, 0.2);
    }
    
    /* Màu chữ trong KPI */
    div[data-testid="stMetricLabel"] { color: #9CA3AF !important; }
    div[data-testid="stMetricValue"] { 
        font-size: 40px !important; 
        font-weight: 800; 
        color: #FFFFFF !important;
        text-shadow: none !important; /* Xóa bóng chữ số */
    }

    /* Sidebar */
    [data-testid="stSidebar"] { 
        background-color: #020617 !important; 
        border-right: 1px solid rgba(255, 255, 255, 0.05); 
    }
    
    /* Bảng dữ liệu trong suốt */
    [data-testid="stDataFrame"] { background: transparent !important; }
    div[data-testid="stDataFrame"] div {
        background-color: transparent !important;
        color: white !important;
    }
    
    /* Expander & Iframe */
    .streamlit-expanderHeader {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(51, 255, 187, 0.3);
        color: #33FFBB !important;
        border-radius: 8px;
    }
    iframe {
        border-radius: 15px;
        border: 1px solid rgba(51, 255, 187, 0.3);
    }
    
    /* --- QUAN TRỌNG: KHÔNG CÓ CODE "HACK" ICON Ở ĐÂY --- */
    /* Chúng ta để Streamlit tự quản lý icon, nó sẽ hiển thị đúng mũi tên mặc định */
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

# HÀM BẢN ĐỒ
@st.cache_data
def prepare_map_data(df):
    map_df = df.copy()
    map_df['Năm'] = map_df['Ngày'].dt.year
    map_data = map_df.groupby(['Quốc gia', 'Năm'])['Nhiệt độ (°C)'].mean().reset_index()
    return map_data.sort_values('Năm')

# KHỞI TẠO
df = load_data()
model_global = load_model()
global_data = load_global_data()
map_data = prepare_map_data(df) 

if df.empty: st.stop()

unique_cities = sorted(df['Thành phố'].unique())

# ==========================================
# 4. UI: SIDEBAR
# ==========================================
with st.sidebar:
    st.markdown("### ĐIỀU KHIỂN")
    selected_city = st.selectbox("Chọn thành phố:", unique_cities)
    st.caption("Thao tác: Di chuột vào biểu đồ để xem chi tiết.")
    
    st.markdown("---")
    st.markdown("""
        <div style='font-size: 20px; font-weight: 900; background: linear-gradient(135deg, #00F260 0%, #0575E6 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; display: inline-block;'>
        USSH.3CE TEAM
        </div>
    """, unsafe_allow_html=True)
    st.caption("Dự án Phân tích Dữ liệu Quản lý 2025")

# ==========================================
# 5. UI: HEADER CHÍNH
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
        st.metric("Nhiệt độ Trung bình (2020)", f"{current_temp:.1f}°C", f"{delta:.1f}°C vs năm trước")
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

    # --- BIỂU ĐỒ ---
    st.markdown("### 📈 Xu hướng Nhiệt độ")
    
    fig = px.area(
        chart_data, x='Ngày', y='Nhiệt độ (°C)',
        template='plotly_dark',
        color_discrete_sequence=['#33FFBB'] 
    )
    
    fig.update_layout(
        paper_bgcolor='rgba(15, 23, 42, 0.8)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_family="Be Vietnam Pro",
        hovermode="x unified",
        xaxis=dict(showgrid=False, title="", showticklabels=True),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', title="Độ C", zeroline=False),
        margin=dict(l=20, r=20, t=20, b=20),
        height=450
    )
    # Cập nhật hiển thị Tooltip chuyên nghiệp hơn
    fig.update_traces(
        fill='tozeroy', 
        line=dict(width=3),
        hovertemplate="<b>Năm:</b> %{x|%Y}<br><b>Nhiệt độ:</b> %{y:.2f}°C<extra></extra>"
    )
    st.plotly_chart(fig, use_container_width=True)

    # --- BẢNG DỮ LIỆU ---
    with st.expander("Xem bảng dữ liệu chi tiết"):
        st.dataframe(
            city_data[['Ngày', 'Nhiệt độ (°C)']].style.format({"Nhiệt độ (°C)": "{:.2f}"}), 
            use_container_width=True
        )

# ==========================================
# 7. PHẦN DỰ BÁO & BẢN ĐỒ TOÀN CẦU
# ==========================================
st.markdown("---")
st.markdown("## 🔮 Phân tích & Dự báo AI")

tab1, tab2 = st.tabs(["Dữ liệu Lịch sử & Bản đồ", "Mô hình Dự báo"])

with tab1:
    st.markdown("### 🌍 Bản đồ nhiệt Timelapse: Nhiệt độ Trung bình Toàn cầu")
    st.caption("Nhấn nút **Play (►)** bên dưới để xem sự thay đổi nhiệt độ qua các năm.")
    
    if not map_data.empty:
        fig_map = px.choropleth(
            map_data,
            locations="Quốc gia",
            locationmode="country names",
            color="Nhiệt độ (°C)",
            hover_name="Quốc gia",
            animation_frame="Năm", 
            color_continuous_scale=px.colors.sequential.YlOrRd, 
            range_color=[-10, 30], 
            template='plotly_dark'
        )
        
        fig_map.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            geo=dict(
                bgcolor='rgba(0,0,0,0)',
                showlakes=True, 
                lakecolor='rgba(0,0,0,0.2)',
                showocean=True,
                oceancolor='rgba(0, 20, 40, 0.5)',
                projection_type='natural earth' 
            ),
            font_family="Be Vietnam Pro",
            margin=dict(l=0, r=0, t=0, b=0),
            height=500
        )
        # Cập nhật tooltip cho bản đồ
        fig_map.update_traces(
            hovertemplate="<b>%{hovertext}</b><br>Nhiệt độ: %{z:.2f}°C<extra></extra>"
        )
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.info("Đang tải dữ liệu bản đồ...")
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    if global_data is not None:
        st.markdown("### 📉 Xu hướng Nhiệt độ Toàn cầu (1995-2020)")
        global_viz = global_data.copy()
        global_viz.name = "Nhiệt độ Trung bình (°C)"
        fig_global = px.line(global_viz, template='plotly_dark')
        fig_global.update_traces(
            line_color='#00B4FF', 
            line_width=3,
            hovertemplate="<b>Thời gian:</b> %{x|%m/%Y}<br><b>Nhiệt độ Trung bình:</b> %{y:.2f}°C<extra></extra>"
        )
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
                line=dict(color='rgba(255, 255, 255, 0.3)', width=2),
                hovertemplate="<b>Ngày:</b> %{x|%m/%Y}<br><b>Lịch sử:</b> %{y:.2f}°C<extra></extra>"
            ))
            fig_fc.add_trace(go.Scatter(
                x=forecast.index, y=forecast['Dự báo'], mode='lines', name='Dự báo AI',
                line=dict(color='#FF0055', width=3),
                hovertemplate="<b>Ngày:</b> %{x|%m/%Y}<br><b>Dự báo:</b> %{y:.2f}°C<extra></extra>"
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