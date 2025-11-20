# config/constants.py
"""Configuration constants for LodCORE Madrid municipality finder."""

from typing import Dict, List, Literal

# Criteria definitions
CRITERIA: List[str] = [
    "AccessibilityHoursWeekly",
    "EducationQuality",
    "AirQuality",
    "BuildingQuality",
    "TransportInfraQuality",
    "EconomicDynamism",
    "HousePriceSqm",
]

CRITERIA_LABELS: Dict[str, str] = {
    "AccessibilityHoursWeekly": "Ahorro de tiempo en desplazamientos",
    "EducationQuality": "Calidad de la educación",
    "AirQuality": "Calidad del aire y del entorno",
    "BuildingQuality": "Atractividad de las viviendas",
    "TransportInfraQuality": "Calidad de las infraestructuras de transporte",
    "EconomicDynamism": "Dinamismo económico",
    "HousePriceSqm": "Precio de la vivienda (€/m²)",
}

CRITERIA_ICONS: Dict[str, str] = {
    "AccessibilityHoursWeekly": ":material/schedule:",
    "EducationQuality": ":material/school:",
    "AirQuality": ":material/air:",
    "BuildingQuality": ":material/home:",
    "TransportInfraQuality": ":material/train:",
    "EconomicDynamism": ":material/work:",
    "HousePriceSqm": ":material/payments:",
}

CRITERIA_TOOLTIPS: Dict[str, str] = {
    "AccessibilityHoursWeekly": "Tiempo semanal estimado en desplazamientos a servicios esenciales (supermercados, salud, educación, etc.).",
    "EducationQuality": "Calidad de los centros educativos basada en indicadores estadísticos de la Comunidad de Madrid.",
    "AirQuality": "Calidad del aire y entorno natural medida por estaciones de monitoreo ambiental.",
    "BuildingQuality": "Atractividad y estado de conservación del parque inmobiliario del municipio.",
    "TransportInfraQuality": "Disponibilidad y calidad de infraestructuras de transporte público y carreteras.",
    "EconomicDynamism": "Actividad económica, empleo y tejido empresarial del municipio.",
    "HousePriceSqm": "Precio medio de vivienda por metro cuadrado según datos de Idealista. Menor es mejor.",
}

# Dataset column mappings
BENEFIT_COLUMNS: Dict[str, str] = {
    "EducationQuality": "ATR_ServiciosDeEducacion_ClusterEstadistica",
    "AirQuality": "ATR_CalidadDelAire_ClusterEstadistica",
    "BuildingQuality": "ATR_AtractividadDeLosInmuebles_ClusterEstadistica",
    "TransportInfraQuality": "ATR_AtractividadDeLasInfraestructurasDeTransporte_ClusterEstadistica",
    "EconomicDynamism": "ATR_DinamismosEconomico_ClusterEstadistica",
}

COST_COLUMNS: Dict[str, str] = {
    "HousePriceSqm": "IDE_PrecioPorMetroCuadrado",
}

ACC_COLUMNS: Dict[str, Dict[str, str]] = {
    "sport": {
        "coche": "ACC_deporte_tiempo_coche",
        "TransportePublico": "ACC_deporte_tiempo_TransportePublico",
    },
    "gp": {
        "coche": "ACC_sanidad_tiempo_coche_OfertaAsistencial_MedicinaGeneralDeFamilia",
        "TransportePublico": "ACC_sanidad_tiempo_TransportePublico_OfertaAsistencial_MedicinaGeneralDeFamilia",
    },
    "pharmacy": {
        "coche": "ACC_farmacias_tiempo_coche",
        "TransportePublico": "ACC_farmacias_tiempo_TransportePublico",
    },
    "gas": {
        "coche": "ACC_gasolineras_tiempo_coche",
        "TransportePublico": "ACC_gasolineras_tiempo_coche",
    },
    "supermarket": {
        "coche": "OSM_supermercados_tiempo_coche",
        "TransportePublico": "OSM_supermercados_tiempo_TransportePublico",
    },
    "edu_preinf_public": {
        "coche": "ACC_educacion_tiempo_coche_Preinfantil_Publicos",
        "TransportePublico": "ACC_educacion_tiempo_TransportePublico_Preinfantil_Publicos",
    },
    "edu_preinf_pubpriv": {
        "coche": "ACC_educacion_tiempo_coche_Preinfantil_Publicos",
        "TransportePublico": "ACC_educacion_tiempo_TransportePublico_Preinfantil_PublicosPrivados",
    },
    "edu_inf_public": {
        "coche": "ACC_educacion_tiempo_coche_Infantil_Publicos",
        "TransportePublico": "ACC_educacion_tiempo_TransportePublico_Infantil_Publicos",
    },
    "edu_inf_pubpriv": {
        "coche": "ACC_educacion_tiempo_coche_Infantil_PublicosPrivados",
        "TransportePublico": "ACC_educacion_tiempo_TransportePublico_Infantil_PublicosPrivados",
    },
    "edu_prim_public": {
        "coche": "ACC_educacion_tiempo_coche_Primaria_Publicos",
        "TransportePublico": "ACC_educacion_tiempo_TransportePublico_Primaria_Publicos",
    },
    "edu_prim_pubpriv": {
        "coche": "ACC_educacion_tiempo_coche_Primaria_PublicosPrivados",
        "TransportePublico": "ACC_educacion_tiempo_TransportePublico_Primaria_PublicosPrivados",
    },
    "edu_sec_public": {
        "coche": "ACC_educacion_tiempo_coche_Secundaria_Publicos",
        "TransportePublico": "ACC_educacion_tiempo_TransportePublico_Secundaria_Publicos",
    },
    "edu_sec_pubpriv": {
        "coche": "ACC_educacion_tiempo_coche_Secundaria_PublicosPrivados",
        "TransportePublico": "ACC_educacion_tiempo_TransportePublico_Secundaria_PublicosPrivados",
    },
}

# Questionnaire options
CAR_FREQ_LABELS: List[str] = [
    "Casi nunca (0-1 días/semana)",
    "Ocasionalmente (2-3 días/semana)",
    "Frecuentemente (4-5 días/semana)",
    "Casi siempre (6-7 días/semana)",
]

CAR_FREQ_TO_WCAR: Dict[str, float] = {
    CAR_FREQ_LABELS[0]: 0.5,
    CAR_FREQ_LABELS[1]: 2.5,
    CAR_FREQ_LABELS[2]: 4.5,
    CAR_FREQ_LABELS[3]: 6.5,
}

SPORT_FREQ_LABELS: List[str] = CAR_FREQ_LABELS

SPORT_FREQ_TO_W: Dict[str, float] = {
    SPORT_FREQ_LABELS[0]: 0.5,
    SPORT_FREQ_LABELS[1]: 2.5,
    SPORT_FREQ_LABELS[2]: 4.5,
    SPORT_FREQ_LABELS[3]: 6.5,
}

HOSPITAL_USE_LABELS: List[str] = [
    "Solo para emergencias",
    "Revisiones regulares",
    "Acompañar personas de riesgo",
    "Enfermedad recurrente",
]

HOSPITAL_USE_TO_W: Dict[str, float] = {
    "Solo para emergencias": 0.05,
    "Revisiones regulares": 0.25,
    "Acompañar personas de riesgo": 1.0,
    "Enfermedad recurrente": 2.0,
}

EDU_LEVEL_OPTIONS: List[str] = ["Preinfantil", "Infantil", "Primaria", "Secundaria"]

# Demographic column mappings
DEMOGRAPHIC_COLUMNS: Dict[str, str] = {
    "0-19": "DEM_Edad_0_19_Total",
    "20-39": "DEM_Edad_20_39_Total",
    "40-59": "DEM_Edad_40_59_Total",
    "60-79": "DEM_Edad_60_79_Total",
    "80+": "DEM_Edad_80Plus_Total",
}

# Age group labels for display
AGE_GROUP_LABELS: Dict[str, str] = {
    "0-19": "0-19 años",
    "20-39": "20-39 años",
    "40-59": "40-59 años",
    "60+": "60+ años",
}

# Age groups to combine for 60+
AGE_60_PLUS_GROUPS: List[str] = ["60-79", "80+"]

def edu_level_to_key(level: str, variant: Literal["public", "pubpriv"]) -> str:
    """Map education level and variant to ACC column key.
    
    Args:
        level: Education level (Preinfantil, Infantil, Primaria, Secundaria)
        variant: School type (public or pubpriv)
        
    Returns:
        Key for ACC_COLUMNS dictionary
        
    Raises:
        ValueError: If level is unknown
    """
    lv = level.lower()
    if lv == "preinfantil":
        return "edu_preinf_public" if variant == "public" else "edu_preinf_pubpriv"
    if lv == "infantil":
        return "edu_inf_public" if variant == "public" else "edu_inf_pubpriv"
    if lv == "primaria":
        return "edu_prim_public" if variant == "public" else "edu_prim_pubpriv"
    if lv == "secundaria":
        return "edu_sec_public" if variant == "public" else "edu_sec_pubpriv"
    raise ValueError(f"Unknown education level: {level}")
