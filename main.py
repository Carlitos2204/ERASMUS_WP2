# -*- coding: utf-8 -*-
"""
Created on Thu Jun 20 11:06:29 2024

@author: Carlos Arroyo
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
import streamlit.components.v1 as components

# Cargar archivo CSS
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css("style.css")

# Mostrar el logo del proyecto
st.image("ELA4ATTRACT ALT LOGO.png", width=200)

# Título del Dashboard
st.title("Proyecto Erasmus - Dashboard de Respuestas de Encuestas LATAM")

# Cargar datos
file_path = 'LATAM - Proyecto ELA4ATTRACT(Respuestas).xlsx'
data = pd.read_excel(file_path)

# Filtrar datos relevantes
data = data[data.iloc[:, 1] == 'Sí, estoy de acuerdo']

# Columnas que se intentarán eliminar si existen
columns_to_drop = [
    'Antes de comenzar la encuesta, es importante informarle que los datos proporcionados serán tratados de forma confidencial y utilizados únicamente para los fines del proyecto ELA4ATTRACT ¿Está de acuerdo con el tratamiento de sus datos para este propósito?',
    'Nombre completo de quién coordina el diligenciamiento de la encuesta',
    'Correo electrónico institucional'
]

# Eliminar columnas no deseadas solo si existen
data.drop(columns=[col for col in columns_to_drop if col in data.columns], inplace=True)

# Limpiar datos de universidades
data['Universidad'] = data['Universidad'].str.replace(r'\\n', ' ', regex=True)

# Función para crear enlaces
def create_hyperlink(url):
    return f'<a href="{url}" target="_blank">Documento</a>'

# Convertir la columna de enlaces a hipervínculos
if 'Enlace a los documentos' in data.columns:
    data['Documentos'] = data['Enlace a los documentos'].apply(lambda x: create_hyperlink(x) if pd.notnull(x) else 'No disponible')

# Barra lateral para filtros y búsqueda de palabras clave
st.sidebar.header("Filtros")

# Botón para restablecer filtros
if st.sidebar.button("Restablecer Filtros"):
    st.experimental_rerun()

# Filtro de países
paises = st.sidebar.multiselect(
    "Seleccione el país",
    options=data['País'].unique(),
    default=data['País'].unique()
)

# Filtro de universidades
universidades = st.sidebar.multiselect(
    "Seleccione la universidad",
    options=data['Universidad'].unique(),
    default=data['Universidad'].unique()
)

# Búsqueda de palabras clave
keyword = st.sidebar.text_input("Buscar por palabra clave")

# Sección de filtros
st.sidebar.header("Filtre por sección de preguntas")
sections = st.sidebar.selectbox(
    "Seleccione la Sección",
    ["Todas las preguntas",
     "SECCIÓN I: Caracterización de la Población",
     "Parte I.I: Caracterización de estudiantes en educación media, a nivel nacional",
     "Parte I.II: Caracterización de estudiantes de pregrado de su universidad",
     "SECCIÓN II: Actividades de Promoción de Carreras STEM",
     "SECCIÓN III: Actividades de Apoyo Financiero",
     "SECCIÓN IV: Actividades para Evaluar la Permanencia Estudiantil",
     "SECCIÓN V: Actividades con Perspectiva de Género",
     "SECCIÓN VI: Caracterización del Staff encargado de la promoción de carreras STEM",
     "SECCIÓN VII: Preguntas de Cierre"]
)

# Mapear secciones a preguntas
sections_questions = {
    "Todas las preguntas": data.columns.tolist(),  # Incluye todas las columnas
    "SECCIÓN I: Caracterización de la Población": list(range(1, 12)),
    "Parte I.I: Caracterización de estudiantes en educación media, a nivel nacional": list(range(1, 5)),
    "Parte I.II: Caracterización de estudiantes de pregrado de su universidad": list(range(5, 12)),
    "SECCIÓN II: Actividades de Promoción de Carreras STEM": list(range(12, 22)),
    "SECCIÓN III: Actividades de Apoyo Financiero": list(range(22, 26)),
    "SECCIÓN IV: Actividades para Evaluar la Permanencia Estudiantil": list(range(26, 29)),
    "SECCIÓN V: Actividades con Perspectiva de Género": list(range(29, 33)),
    "SECCIÓN VI: Caracterización del Staff encargado de la promoción de carreras STEM": list(range(33, 40)),
    "SECCIÓN VII: Preguntas de Cierre": list(range(40, 42))
}

# Filtrar datos según la sección seleccionada
if sections == "Todas las preguntas":
    data_filtered = data.copy()
else:
    questions_range = sections_questions[sections]
    questions_columns = [f"{i}-" for i in questions_range]
    filtered_columns = [col for col in data.columns if any(col.startswith(q) for q in questions_columns)]
    data_filtered = data[filtered_columns + ['Universidad', 'País']]

# Aplicar filtros de país y universidad
data_filtered = data_filtered[data_filtered['País'].isin(paises)]
data_filtered = data_filtered[data_filtered['Universidad'].isin(universidades)]

# Filtrar columnas por palabra clave
if keyword:
    matching_columns = [col for col in data_filtered.columns if keyword.lower() in col.lower()]
    data_filtered = data_filtered[matching_columns + ['Universidad']]

# Reducir el tamaño de la letra en la visualización de los datos filtrados
st.markdown('<style> .filtered-data { font-size: 12px; } </style>', unsafe_allow_html=True)

# Mostrar datos filtrados con opción de expandir cada respuesta

st.write(data_filtered.to_html(escape=False, index=False), unsafe_allow_html=True)

# Gráficos y visualizaciones
st.subheader("Visualizaciones")

# Número de respuestas por universidad
universidades_count = data_filtered['Universidad'].value_counts().reset_index()
universidades_count.columns = ['Universidad', 'Número de Respuestas']

fig = px.bar(universidades_count, x='Universidad', y='Número de Respuestas', title="Número de Respuestas por Universidad")
st.plotly_chart(fig)

# Ejemplo de gráfico circular
agree_count = data_filtered.iloc[:, 1].value_counts().reset_index()
agree_count.columns = ['Respuesta', 'Count']
fig2 = px.pie(agree_count, values='Count', names='Respuesta', title="Distribución de Respuestas Aceptadas")
st.plotly_chart(fig2)

# Gráficos interactivos para preguntas específicas con gráfico de torta
questions_pie = [
    '34- ¿Cuál es el promedio de años de experiencia del personal dedicado a las actividades de promoción de carreras STEM en su universidad?',
    '35- ¿Cuál es la edad promedio del personal dedicado a actividades de promoción de carreras STEM en su universidad?',
    '36- ¿Cuántas personas conforman el equipo dedicado a actividades de promoción de carreras STEM en su universidad?',
    '37- ¿Cuál es el porcentaje de mujeres dedicadas a actividades de promoción de carreras STEM en su universidad?'
]

for question in questions_pie:
    if question in data_filtered.columns:
        st.subheader(f"Distribución de respuestas para: {question}")
        fig = px.pie(data_filtered, names=question, title=question, hover_data=['Universidad'], labels={question: 'Respuestas'})
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig)

# Guardar datos filtrados como archivo xlsx
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    processed_data = output.getvalue()
    return processed_data

# Descarga del archivo filtrado
st.sidebar.download_button(
    label="Descargar datos filtrados",
    data=to_excel(data_filtered),
    file_name='datos_filtrados.xlsx',
    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
)

# Iniciar la aplicación
if __name__ == "__main__":
    st.set_page_config(page_title="Proyecto Erasmus", layout="wide")
    st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Erasmus%2B_Logo.jpg/220px-Erasmus%2B_Logo.jpg", width=200)
