import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
import numpy as np
from datetime import datetime, timedelta

# Configuración de página
st.set_page_config(
    page_title="Sales Analytics Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado para mejorar el diseño
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    
    .kpi-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .kpi-value {
        font-size: 2rem;
        font-weight: bold;
        margin: 0;
    }
    
    .kpi-label {
        font-size: 0.9rem;
        margin: 0;
        opacity: 0.9;
    }
    
    .insight-box {
        background: #f8f9fa;
        padding: 1rem;
        border-left: 4px solid #1f77b4;
        border-radius: 5px;
        margin: 1rem 0;
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border: 1px solid #e0e0e0;
    }
</style>
""", unsafe_allow_html=True)

# Configuración global de estilo para seaborn
sns.set_style("whitegrid")
plt.style.use('seaborn-v0_8')

@st.cache_data
def load_data(uploaded_file):
    """Carga y procesa los datos del archivo CSV"""
    try:
        df = pd.read_csv(uploaded_file)
        
        # Limpieza y procesamiento de datos
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df['Sales Amount'] = pd.to_numeric(df['Sales Amount'], errors='coerce')
        df['Sales Order'] = pd.to_numeric(df['Sales Order'], errors='coerce')
        
        # Crear columnas adicionales útiles
        df['Year'] = df['Date'].dt.year
        df['Month'] = df['Date'].dt.month
        df['Month_Name'] = df['Date'].dt.strftime('%B')
        df['Quarter'] = df['Date'].dt.quarter
        df['Day_of_Week'] = df['Date'].dt.day_name()
        
        return df
    except Exception as e:
        st.error(f"Error al cargar los datos: {str(e)}")
        return None

def show_data_overview(df):
    """Muestra una vista general del dataset con estadísticas y estructura"""
    with st.expander("🔍 Ver Detalles del Dataset"):
        tab1, tab2, tab3 = st.tabs(["Muestra de Datos", "Estadísticas", "Información de Columnas"])
        
        with tab1:
            st.dataframe(df.head(10), use_container_width=True)
        
        with tab2:
            st.write("**Estadísticas de Sales Amount:**")
            st.dataframe(df['Sales Amount'].describe(), use_container_width=True)
        
        with tab3:
            info_df = pd.DataFrame({
                'Columna': df.columns,
                'Tipo': df.dtypes,
                'Valores Únicos': [df[col].nunique() for col in df.columns],
                'Valores Nulos': [df[col].isnull().sum() for col in df.columns],
                'Porcentaje Nulos': [f"{(df[col].isnull().sum()/len(df)*100):.1f}%" for col in df.columns]
            })
            st.dataframe(info_df, use_container_width=True)
        
        with tab3:
            info_df = pd.DataFrame({
                'Columna': df.columns,
                'Tipo': df.dtypes,
                'Valores Únicos': [df[col].nunique() for col in df.columns],
                'Valores Nulos': [df[col].isnull().sum() for col in df.columns],
                'Porcentaje Nulos': [f"{(df[col].isnull().sum()/len(df)*100):.1f}%" for col in df.columns]
            })
            st.dataframe(info_df, use_container_width=True)

def show_kpis(df, filtered_df):
    """Muestra KPIs principales en tarjetas atractivas"""
    st.header("KPIs Principales")
    
    # Calcular métricas
    total_sales = filtered_df['Sales Amount'].sum()
    avg_order = filtered_df['Sales Amount'].mean()
    total_orders = len(filtered_df)
    top_category = filtered_df.groupby('Category')['Sales Amount'].sum().idxmax()
    top_region = filtered_df.groupby('Country-Region')['Sales Amount'].sum().idxmax()
    
    # Mostrar KPIs en columnas
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(f"""
        <div class="kpi-container">
            <p class="kpi-value">${total_sales:,.0f}</p>
            <p class="kpi-label">Ventas Totales</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="kpi-container">
            <p class="kpi-value">${avg_order:,.0f}</p>
            <p class="kpi-label">Venta Promedio</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="kpi-container">
            <p class="kpi-value">{total_orders:,}</p>
            <p class="kpi-label">Total Órdenes</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="kpi-container">
            <p class="kpi-value">{top_category}</p>
            <p class="kpi-label">Top Categoría</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown(f"""
        <div class="kpi-container">
            <p class="kpi-value">{top_region}</p>
            <p class="kpi-label">Top Región</p>
        </div>
        """, unsafe_allow_html=True)

def create_sidebar_filters(df):
    """Crea filtros interactivos en la barra lateral"""
    st.sidebar.header("Filtros")
    
    # Filtro por año
    years = sorted(df['Year'].dropna().unique())
    selected_years = st.sidebar.multiselect(
        "Seleccionar Años:",
        options=years,
        default=years
    )
    
    # Filtro por categoría
    categories = sorted(df['Category'].dropna().unique())
    selected_categories = st.sidebar.multiselect(
        "Seleccionar Categorías:",
        options=categories,
        default=categories
    )
    
    # Filtro por canal
    channels = sorted(df['Channel'].dropna().unique())
    selected_channels = st.sidebar.multiselect(
        "Seleccionar Canales:",
        options=channels,
        default=channels
    )
    
    # Filtro por región
    regions = sorted(df['Country-Region'].dropna().unique())
    selected_regions = st.sidebar.multiselect(
        "🌍 Seleccionar Regiones:",
        options=regions,
        default=regions
    )
    
    # Aplicar filtros
    filtered_df = df[
        (df['Year'].isin(selected_years)) &
        (df['Category'].isin(selected_categories)) &
        (df['Channel'].isin(selected_channels)) &
        (df['Country-Region'].isin(selected_regions))
    ]
    
    st.sidebar.write(f"📊 Registros mostrados: {len(filtered_df):,} de {len(df):,}")
    
    return filtered_df

def plot_sales_evolution(df):
    """Gráfico de evolución de ventas en el tiempo"""
    st.subheader("Evolución de Ventas en el Tiempo")
    
    # Agregación temporal
    time_agg = st.selectbox("Agregación temporal:", ["Diaria", "Semanal", "Mensual"], key="time_agg")
    
    if time_agg == "Diaria":
        time_series = df.groupby('Date')['Sales Amount'].sum().reset_index()
        x_col, title_suffix = 'Date', 'Diaria'
    elif time_agg == "Semanal":
        df_temp = df.copy()
        df_temp['Week'] = df_temp['Date'].dt.to_period('W').dt.start_time
        time_series = df_temp.groupby('Week')['Sales Amount'].sum().reset_index()
        x_col, title_suffix = 'Week', 'Semanal'
    else:  # Mensual
        df_temp = df.copy()
        df_temp['Month_Year'] = df_temp['Date'].dt.to_period('M').dt.start_time
        time_series = df_temp.groupby('Month_Year')['Sales Amount'].sum().reset_index()
        x_col, title_suffix = 'Month_Year', 'Mensual'
    
    fig = px.line(
        time_series, 
        x=x_col, 
        y='Sales Amount',
        title=f"Evolución de Ventas {title_suffix}",
        template="plotly_white"
    )
    fig.update_traces(line_color="#1f77b4", line_width=3)
    fig.update_layout(
        xaxis_title="Fecha",
        yaxis_title="Ventas ($)",
        height=400,
        hovermode="x unified"
    )
    st.plotly_chart(fig, use_container_width=True)

def plot_category_analysis(df):
    """Análisis por categorías y subcategorías"""
    st.subheader("🏷️ Análisis por Categorías")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Ventas por categoría
        category_sales = df.groupby('Category')['Sales Amount'].sum().sort_values(ascending=True)
        fig = px.bar(
            y=category_sales.index,
            x=category_sales.values,
            orientation='h',
            title="Ventas Totales por Categoría",
            template="plotly_white",
            color=category_sales.values,
            color_continuous_scale="viridis"
        )
        fig.update_layout(
            xaxis_title="Ventas ($)",
            yaxis_title="Categoría",
            height=400,
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Top subcategorías
        subcat_sales = df.groupby('Subcategory')['Sales Amount'].sum().sort_values(ascending=False).head(10)
        fig = px.bar(
            x=subcat_sales.index,
            y=subcat_sales.values,
            title="Top 10 Subcategorías",
            template="plotly_white",
            color=subcat_sales.values,
            color_continuous_scale="plasma"
        )
        fig.update_layout(
            xaxis_title="Subcategoría",
            yaxis_title="Ventas ($)",
            height=400,
            showlegend=False
        )
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)

def plot_channel_region_analysis(df):
    """Análisis por canal y región"""
    st.subheader("🌍 Análisis por Canal y Región")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Boxplot por canal
        fig = px.box(
            df, 
            x='Channel', 
            y='Sales Amount',
            title="Distribución de Ventas por Canal",
            template="plotly_white",
            color='Channel'
        )
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Ventas por región
        region_sales = df.groupby('Country-Region')['Sales Amount'].sum().sort_values(ascending=True)
        fig = px.bar(
            y=region_sales.index,
            x=region_sales.values,
            orientation='h',
            title="Ventas por Región",
            template="plotly_white",
            color=region_sales.values,
            color_continuous_scale="sunset"
        )
        fig.update_layout(
            xaxis_title="Ventas ($)",
            yaxis_title="Región",
            height=400,
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)

def plot_geographic_analysis(df):
    """Análisis geográfico por ciudades"""
    st.subheader("🗺️ Análisis Geográfico")
    
    city_data = df.groupby(['Country-Region', 'City']).agg({
        'Sales Amount': ['sum', 'count', 'mean']
    }).round(2)
    city_data.columns = ['Total_Sales', 'Orders', 'Avg_Sale']
    city_data = city_data.reset_index().sort_values('Total_Sales', ascending=False)
    
    # Gráfico de dispersión
    fig = px.scatter(
        city_data.head(20),
        x='Orders',
        y='Avg_Sale',
        size='Total_Sales',
        color='Country-Region',
        hover_name='City',
        title="Top 20 Ciudades: Órdenes vs Venta Promedio (Tamaño = Ventas Totales)",
        template="plotly_white"
    )
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)

def plot_seasonal_patterns(df):
    """Análisis de patrones estacionales"""
    st.subheader("📅 Patrones Estacionales")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Ventas por mes
        monthly_sales = df.groupby('Month_Name')['Sales Amount'].sum()
        month_order = ['January', 'February', 'March', 'April', 'May', 'June',
                      'July', 'August', 'September', 'October', 'November', 'December']
        monthly_sales = monthly_sales.reindex([m for m in month_order if m in monthly_sales.index])
        
        fig = px.bar(
            x=monthly_sales.index,
            y=monthly_sales.values,
            title="Ventas por Mes",
            template="plotly_white",
            color=monthly_sales.values,
            color_continuous_scale="blues"
        )
        fig.update_layout(height=400, showlegend=False)
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Ventas por día de la semana
        dow_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        dow_sales = df.groupby('Day_of_Week')['Sales Amount'].sum()
        dow_sales = dow_sales.reindex([d for d in dow_order if d in dow_sales.index])
        
        fig = px.bar(
            x=dow_sales.index,
            y=dow_sales.values,
            title="Ventas por Día de la Semana",
            template="plotly_white",
            color=dow_sales.values,
            color_continuous_scale="greens"
        )
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

def show_insights(df):
    """Muestra insights automáticos del análisis"""
    st.header("💡 Insights Principales")
    
    # Top performers
    top_category = df.groupby('Category')['Sales Amount'].sum().idxmax()
    top_region = df.groupby('Country-Region')['Sales Amount'].sum().idxmax()
    top_channel = df.groupby('Channel')['Sales Amount'].sum().idxmax()
    
    # Tendencias
    monthly_growth = df.groupby(df['Date'].dt.to_period('M'))['Sales Amount'].sum().pct_change().mean() * 100
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="insight-box">
            <h4>🏆 Top Performers</h4>
            <ul>
                <li><strong>Mejor Categoría:</strong> {top_category}</li>
                <li><strong>Mejor Región:</strong> {top_region}</li>
                <li><strong>Mejor Canal:</strong> {top_channel}</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="insight-box">
            <h4>📊 Tendencias</h4>
            <ul>
                <li><strong>Crecimiento Mensual Promedio:</strong> {monthly_growth:.1f}%</li>
                <li><strong>Ticket Promedio:</strong> ${df['Sales Amount'].mean():.2f}</li>
                <li><strong>Mediana de Ventas:</strong> ${df['Sales Amount'].median():.2f}</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

def main():
    """Función principal de la aplicación"""
    
    # Título principal
    st.markdown('<h1 class="main-header">Sales Analytics Dashboard</h1>', unsafe_allow_html=True)
    st.markdown("### 📊 Análisis Completo de Datos de Ventas")
    
    # Carga de archivo
    uploaded_file = st.file_uploader(
        "📁 Cargar Dataset (CSV)",
        type=["csv"],
        help="Sube tu archivo dataset.csv para comenzar el análisis"
    )
    
    if uploaded_file is not None:
        # Cargar datos
        with st.spinner("Cargando y procesando datos..."):
            df = load_data(uploaded_file)
        
        if df is not None:
            # Crear filtros en sidebar
            filtered_df = create_sidebar_filters(df)
            
            # Mostrar información general
            show_data_overview(df)
            st.divider()
            
            # Mostrar KPIs
            show_kpis(df, filtered_df)
            st.divider()
            
            # Visualizaciones principales
            plot_sales_evolution(filtered_df)
            st.divider()
            
            plot_category_analysis(filtered_df)
            st.divider()
            
            plot_channel_region_analysis(filtered_df)
            st.divider()
            
            plot_geographic_analysis(filtered_df)
            st.divider()
            
            plot_seasonal_patterns(filtered_df)
            st.divider()
            
            # Insights finales
            show_insights(filtered_df)
            
            # Footer
            st.markdown("---")
            st.markdown(
                "<div style='text-align: center; color: #666;'>"
                "📊 Sales Analytics Dashboard | Desarrollado con Streamlit & Plotly"
                "</div>", 
                unsafe_allow_html=True
            )
    
    else:
        # Pantalla de bienvenida
        st.info("👆 Para comenzar, sube tu archivo CSV usando el botón de arriba")
        
        st.markdown("""
        ### 🚀 Características del Dashboard:
        
        - **📊 KPIs Interactivos**: Métricas clave en tiempo real
        - **🎛️ Filtros Avanzados**: Por año, categoría, canal y región
        - **📈 Visualizaciones Dinámicas**: Gráficos interactivos con Plotly
        - **🌍 Análisis Geográfico**: Mapeo de ventas por ciudades
        - **📅 Patrones Estacionales**: Tendencias por mes y día de la semana
        - **💡 Insights Automáticos**: Análisis inteligente de los datos
        
        ### 📋 Formato de Datos Esperado:
        El archivo CSV debe contener las siguientes columnas: `WeekDay`, `Day`, `Month`, `Year`, `Date`, `Sales Amount`, `Sales Order`, `Channel`, `Product`, `Model`, `Color`, `SKU`, `Category`, `Subcategory`, `Country-Region`, `City`
        """)

if __name__ == "__main__":
    main()