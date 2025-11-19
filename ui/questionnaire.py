# ui/questionnaire.py
"""Sidebar questionnaire for user preferences."""

import streamlit as st
from typing import Dict, Any, List, Optional, Literal

from config.constants import (
    CRITERIA, CRITERIA_ICONS, CRITERIA_LABELS,
    CAR_FREQ_LABELS, CAR_FREQ_TO_WCAR,
    SPORT_FREQ_LABELS, SPORT_FREQ_TO_W,
    HOSPITAL_USE_LABELS, HOSPITAL_USE_TO_W,
    EDU_LEVEL_OPTIONS,
)


def render_questionnaire(df_raw) -> Dict[str, Any]:
    """Render sidebar questionnaire and return user preferences.
    
    Args:
        df_raw: Raw municipality dataset for population bounds
        
    Returns:
        Dictionary with user preferences:
            - w_car, w_sport, w_hospital: float weights
            - edu_has_kids: bool
            - edu_variant: Optional['public'|'pubpriv']
            - edu_levels: List[str]
            - edu_trade: float
            - pop_min, pop_max: int
            - ranks: List[float]
    """
    with st.sidebar:
        st.header(":material/account_box: | Tu perfil y prioridades")

        # Mobility
        st.subheader(":material/directions_car: | Movilidad - Coche")
        car_use = st.selectbox(
            "¿Con qué frecuencia usarías el coche?",
            options=CAR_FREQ_LABELS,
            index=2,
        )
        w_car = CAR_FREQ_TO_WCAR[car_use]

        # Family - Education
        st.subheader(":material/school: | Familia - Educación")
        has_kids_ans = st.radio(
            "¿Tienes hij@s pequeñ@s?",
            options=["No", "Sí"],
            horizontal=True,
        )
        edu_has_kids = has_kids_ans == "Sí"

        edu_variant: Optional[Literal["public", "pubpriv"]] = None
        edu_levels: List[str] = []
        edu_trade: float = 0.0

        if edu_has_kids:
            school_type = st.radio(
                "¿Van a colegio público o privado?",
                options=["Solo público", "Privado o mixto"],
                horizontal=True,
            )
            edu_variant = "public" if school_type == "Solo público" else "pubpriv"

            edu_levels = st.multiselect(
                "¿En qué etapas tienes hij@s?",
                options=EDU_LEVEL_OPTIONS,
                help="Si eliges varias, las ponderamos igual.",
            )

            edu_trade = st.slider(
                "¿Qué priorizas en educación?",
                min_value=0.0,
                max_value=1.0,
                value=0.5,
                step=0.05,
                help="(0) ← Calidad del centro educativo | Cercanía al hogar → (1)",
            )

        # Lifestyle - Sports
        st.subheader(":material/sports_and_outdoors: | Estilo de vida - Deporte")
        sport_use = st.selectbox(
            "¿Con qué frecuencia harías deporte?",
            options=SPORT_FREQ_LABELS,
            index=1,
        )
        w_sport = SPORT_FREQ_TO_W[sport_use]

        # Health
        st.subheader(":material/local_hospital: | Salud - Hospitales y farmacias")
        hosp_use = st.selectbox(
            "¿Qué uso haces de hospitales/centros de salud?",
            options=HOSPITAL_USE_LABELS,
            index=1,
        )
        w_hospital = HOSPITAL_USE_TO_W[hosp_use]

        # Population
        st.subheader(":material/location_city: | Tamaño del municipio")
        if "IDE_PoblacionTotal" in df_raw.columns:
            min_pop_data = int(df_raw["IDE_PoblacionTotal"].min())
            max_pop_data = int(df_raw["IDE_PoblacionTotal"].max())
        else:
            min_pop_data, max_pop_data = 0, 50000

        pop_min, pop_max = st.slider(
            "Rango de población del municipio:",
            min_value=min_pop_data,
            max_value=max_pop_data,
            value=(min_pop_data, min(50000, max_pop_data)),
            step=1000,
        )

        # Criteria ranking
        st.subheader(":material/stack_star: | Prioriza estas características (10 = más importante)") # Change ((10 = más importante)) to a help icon
        st.caption("Puedes dar la misma puntuación a varios criterios.")
        ranks: List[float] = []
        for crit in CRITERIA:
            label = f"{CRITERIA_ICONS[crit]}  |  {CRITERIA_LABELS[crit]}"
            rank = st.number_input(
                label,
                min_value=1,
                max_value=10,
                value=5,
                step=1,
                key=f"rank_{crit}",
                help="10 = muy importante, 1 = poco importante"
            )
            ranks.append(float(rank))

    return {
        "w_car": w_car,
        "w_sport": w_sport,
        "w_hospital": w_hospital,
        "edu_has_kids": edu_has_kids,
        "edu_variant": edu_variant,
        "edu_levels": edu_levels,
        "edu_trade": edu_trade,
        "pop_min": pop_min,
        "pop_max": pop_max,
        "ranks": ranks,
    }
