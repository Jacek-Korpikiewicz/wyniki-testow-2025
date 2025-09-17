import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Page configuration
st.set_page_config(
    page_title="Wyniki Testów 2025 - Warszawa",
    page_icon="📊",
    layout="wide"
)

# Load data
@st.cache_data
def load_data():
    """Load and cache the test results data"""
    try:
        df = pd.read_csv('wyniki_testow_fixed.csv')
        # Filter for Warsaw only
        warsaw_df = df[df['powiat - nazwa'] == 'Warszawa'].copy()
        return warsaw_df
    except FileNotFoundError:
        st.error("❌ File 'wyniki_testow_fixed.csv' not found. Please make sure the file is in the same directory as this app.")
        return None

def create_histogram(data, selected_value, title, x_label, y_label="Liczba szkół"):
    """Create histogram with selected school highlighted in red"""
    if data.empty or pd.isna(selected_value):
        return None
    
    # Create histogram
    fig = px.histogram(
        data, 
        x=title.lower().replace(' ', '_'),
        nbins=int(data[title.lower().replace(' ', '_')].max() - data[title.lower().replace(' ', '_')].min() + 1),
        title=f"Rozkład {title} - wszystkie szkoły w Warszawie",
        labels={title.lower().replace(' ', '_'): x_label, 'count': y_label},
        color_discrete_sequence=['lightblue']
    )
    
    # Add red line for selected school
    if not pd.isna(selected_value):
        fig.add_vline(
            x=selected_value, 
            line_dash="dash", 
            line_color="red", 
            line_width=3,
            annotation_text=f"Wybrana szkoła: {selected_value:.2f}",
            annotation_position="top"
        )
    
    fig.update_layout(
        showlegend=False,
        height=400,
        margin=dict(l=0, r=0, t=40, b=0)
    )
    
    return fig

def main():
    st.title("📊 Wyniki Testów 2025 - Warszawa")
    
    # Load data
    df = load_data()
    if df is None:
        return
    
    st.info(f"📊 Dane dla {len(df)} szkół w Warszawie")
    
    # Metric selection
    metric_choice = st.radio(
        "Wybierz metrykę:",
        options=["Średnia", "Mediana"],
        index=0,
        horizontal=True,
        help="Wybierz czy chcesz analizować średnie czy mediany wyników"
    )
    
    # School selection
    df['school_display'] = df['Nazwa szkoły'] + " - " + df['Miejscowość']
    
    # Find the index of the target school
    target_school = "SZKOŁA PODSTAWOWA NR 398 - Warszawa"
    school_options = df['school_display'].unique()
    
    try:
        default_index = list(school_options).index(target_school)
    except ValueError:
        # If school not found, use first school as default
        default_index = 0
        st.warning(f"⚠️ Szkoła '{target_school}' nie została znaleziona. Używam pierwszej dostępnej szkoły.")
    
    selected_school = st.selectbox(
        "Wybierz szkołę:",
        options=school_options,
        index=default_index,
        help="Wybierz szkołę z listy rozwijanej"
    )
    
    # Filter data for selected school
    school_data = df[df['school_display'] == selected_school].iloc[0]
    
    st.subheader(f"🏫 {school_data['Nazwa szkoły']} - {school_data['Miejscowość']}")
    
    # Calculate artificial score for selected school
    if metric_choice == "Średnia":
        score_polski = school_data['mean_polski'] if pd.notna(school_data['mean_polski']) else 0
        score_matematyka = school_data['mean_matematyka'] if pd.notna(school_data['mean_matematyka']) else 0
        score_angielski = school_data['mean_angielski'] if pd.notna(school_data['mean_angielski']) else 0
    else:
        score_polski = school_data['median_polski'] if pd.notna(school_data['median_polski']) else 0
        score_matematyka = school_data['median_matematyka'] if pd.notna(school_data['median_matematyka']) else 0
        score_angielski = school_data['median_angielski'] if pd.notna(school_data['median_angielski']) else 0
    
    selected_school_score = score_polski + score_matematyka + score_angielski
    
    # Calculate artificial scores for all schools
    if metric_choice == "Średnia":
        df['artificial_score'] = (
            df['mean_polski'].fillna(0) + 
            df['mean_matematyka'].fillna(0) + 
            df['mean_angielski'].fillna(0)
        )
    else:
        df['artificial_score'] = (
            df['median_polski'].fillna(0) + 
            df['median_matematyka'].fillna(0) + 
            df['median_angielski'].fillna(0)
        )
    
    # Display artificial score
    st.metric(f"🎯 Wynik łączny ({metric_choice.lower()})", f"{selected_school_score:.2f}")
    
    # Create three sections for each subject
    col1, col2, col3 = st.columns(3)
    
    # Polish section
    with col1:
        st.markdown("### 🇵🇱 Język Polski")
        
        # Get the selected metric value
        if metric_choice == "Średnia":
            metric_value = school_data['mean_polski']
            metric_col = 'mean_polski'
            metric_label = "Średnia"
        else:
            metric_value = school_data['median_polski']
            metric_col = 'median_polski'
            metric_label = "Mediana"
        
        # Display metric
        if pd.notna(metric_value):
            st.metric(metric_label, f"{metric_value:.2f}")
        else:
            st.metric(metric_label, "Brak danych")
        
        # Comparison information
        if pd.notna(metric_value):
            # Filter out schools without data for this metric
            polish_data = df[df[metric_col].notna()].copy()
            higher_count = len(polish_data[polish_data[metric_col] > metric_value])
            total_count = len(polish_data)
            percentage = (higher_count / total_count) * 100
            
            st.info(f"📊 {higher_count} z {total_count} szkół ({percentage:.1f}%) ma wyższe wyniki")
        else:
            st.info("Brak danych do porównania")
        
        # Histogram
        if pd.notna(metric_value):
            polish_data['polski'] = polish_data[metric_col]
            
            fig = create_histogram(
                polish_data, 
                metric_value, 
                "polski", 
                f"{metric_label} wyników"
            )
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Brak danych do wyświetlenia histogramu")
    
    # Math section
    with col2:
        st.markdown("### 🔢 Matematyka")
        
        # Get the selected metric value
        if metric_choice == "Średnia":
            metric_value = school_data['mean_matematyka']
            metric_col = 'mean_matematyka'
            metric_label = "Średnia"
        else:
            metric_value = school_data['median_matematyka']
            metric_col = 'median_matematyka'
            metric_label = "Mediana"
        
        # Display metric
        if pd.notna(metric_value):
            st.metric(metric_label, f"{metric_value:.2f}")
        else:
            st.metric(metric_label, "Brak danych")
        
        # Comparison information
        if pd.notna(metric_value):
            # Filter out schools without data for this metric
            math_data = df[df[metric_col].notna()].copy()
            higher_count = len(math_data[math_data[metric_col] > metric_value])
            total_count = len(math_data)
            percentage = (higher_count / total_count) * 100
            
            st.info(f"📊 {higher_count} z {total_count} szkół ({percentage:.1f}%) ma wyższe wyniki")
        else:
            st.info("Brak danych do porównania")
        
        # Histogram
        if pd.notna(metric_value):
            math_data['matematyka'] = math_data[metric_col]
            
            fig = create_histogram(
                math_data, 
                metric_value, 
                "matematyka", 
                f"{metric_label} wyników"
            )
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Brak danych do wyświetlenia histogramu")
    
    # English section
    with col3:
        st.markdown("### 🇬🇧 Język Angielski")
        
        # Get the selected metric value
        if metric_choice == "Średnia":
            metric_value = school_data['mean_angielski']
            metric_col = 'mean_angielski'
            metric_label = "Średnia"
        else:
            metric_value = school_data['median_angielski']
            metric_col = 'median_angielski'
            metric_label = "Mediana"
        
        # Display metric
        if pd.notna(metric_value):
            st.metric(metric_label, f"{metric_value:.2f}")
        else:
            st.metric(metric_label, "Brak danych")
        
        # Comparison information
        if pd.notna(metric_value):
            # Filter out schools without data for this metric
            english_data = df[df[metric_col].notna()].copy()
            higher_count = len(english_data[english_data[metric_col] > metric_value])
            total_count = len(english_data)
            percentage = (higher_count / total_count) * 100
            
            st.info(f"📊 {higher_count} z {total_count} szkół ({percentage:.1f}%) ma wyższe wyniki")
        else:
            st.info("Brak danych do porównania")
        
        # Histogram
        if pd.notna(metric_value):
            english_data['angielski'] = english_data[metric_col]
            
            fig = create_histogram(
                english_data, 
                metric_value, 
                "angielski", 
                f"{metric_label} wyników"
            )
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Brak danych do wyświetlenia histogramu")
    
    # Final artificial score section
    st.markdown("---")
    st.subheader("🎯 Wynik łączny - wszystkie przedmioty")
    
    # Comparison information for artificial score
    higher_score_count = len(df[df['artificial_score'] > selected_school_score])
    total_schools = len(df)
    percentage = (higher_score_count / total_schools) * 100
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.info(f"📊 {higher_score_count} z {total_schools} szkół ({percentage:.1f}%) ma wyższy wynik łączny")
    
    with col2:
        # Create final histogram for artificial score
        fig = px.histogram(
            df, 
            x='artificial_score',
            nbins=int(df['artificial_score'].max() - df['artificial_score'].min() + 1),
            title=f"Rozkład wyniku łącznego ({metric_choice.lower()}) - wszystkie szkoły w Warszawie",
            labels={'artificial_score': 'Wynik łączny', 'count': 'Liczba szkół'},
            color_discrete_sequence=['lightgreen']
        )
        
        # Add red line for selected school
        fig.add_vline(
            x=selected_school_score, 
            line_dash="dash", 
            line_color="red", 
            line_width=3,
            annotation_text=f"Wybrana szkoła: {selected_school_score:.2f}",
            annotation_position="top"
        )
        
        fig.update_layout(
            showlegend=False,
            height=400,
            margin=dict(l=0, r=0, t=40, b=0)
        )
        
        st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()

