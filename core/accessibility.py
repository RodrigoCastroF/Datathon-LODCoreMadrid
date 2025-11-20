# core/accessibility.py
"""Accessibility computation: weekly commute hours from user preferences."""

import numpy as np
import pandas as pd
import streamlit as st
from typing import Dict, List, Optional, Literal

from config.constants import ACC_COLUMNS, edu_level_to_key


@st.cache_data
def compute_accessibility_hours(
    df: pd.DataFrame,
    freq_car: float,
    freq_supermarket: float,
    freq_sport: float,
    freq_hospital: float,
    edu_has_kids: bool,
    edu_variant: Optional[Literal["public", "pubpriv"]],
    edu_levels: List[str],
) -> pd.DataFrame:
    """Compute weekly accessibility hours per municipality.
    
    Aggregates round-trip travel time across essential services based on
    user-specified visit frequencies.
    
    Args:
        df: Municipality dataset
        freq_car: Car usage frequency (days per week) for mode choice weighting
        freq_supermarket: Supermarket visit frequency (times per week)
        freq_sport: Sports facility visit frequency (times per week)
        freq_hospital: Hospital/health center visit frequency (times per week)
        edu_has_kids: Whether to include education travel
        edu_variant: School type ('public' or 'pubpriv')
        edu_levels: Education stages to include
        
    Returns:
        DataFrame with AccessibilityHoursWeekly column (actually weekly hours)
    """
    out = df[["codigo", "Nombre"]].copy()
    total = np.zeros(len(df), dtype=float)

    # Compute car usage weight for transportation mode blending
    w_car = freq_car / 7.0  # Convert days per week to proportion

    def blend_minutes(col_car: str, col_pt: str) -> np.ndarray:
        """Blend car and public transport times based on car usage."""
        mc = df[col_car].astype(float)
        mp = df[col_pt].astype(float) if col_pt in df.columns else mc
        return w_car * mc + (1.0 - w_car) * mp

    def add_hours(key: str, minutes_one_way: np.ndarray, visits_per_week: float) -> None:
        """Add weekly commute hours for a service."""
        nonlocal total
        hours = visits_per_week * (2.0 * minutes_one_way) / 60.0
        out[f"hrs_{key}"] = hours
        total += hours

    # Supermarkets (user-specified frequency)
    mins_super = blend_minutes(
        ACC_COLUMNS["supermarket"]["coche"],
        ACC_COLUMNS["supermarket"]["TransportePublico"],
    )
    add_hours("supermarket", mins_super, freq_supermarket)

    # Gas stations (scale with car usage: ~0.5 visits/week for frequent drivers)
    if freq_car > 0:
        mins_gas = df[ACC_COLUMNS["gas"]["coche"]].astype(float)
        gas_visits_per_week = min(freq_car / 10.0, 1.0)  # Scale with car use
        add_hours("gas", mins_gas, gas_visits_per_week)

    # Sports facilities (user-specified frequency)
    if freq_sport > 0:
        mins_sport = blend_minutes(
            ACC_COLUMNS["sport"]["coche"],
            ACC_COLUMNS["sport"]["TransportePublico"],
        )
        add_hours("sport", mins_sport, freq_sport)

    # Healthcare: split frequency between GP (20%) and Pharmacy (80%)
    if freq_hospital > 0:
        mins_gp = blend_minutes(
            ACC_COLUMNS["gp"]["coche"],
            ACC_COLUMNS["gp"]["TransportePublico"],
        )
        add_hours("gp", mins_gp, freq_hospital * 0.2)

        mins_pharm = blend_minutes(
            ACC_COLUMNS["pharmacy"]["coche"],
            ACC_COLUMNS["pharmacy"]["TransportePublico"],
        )
        add_hours("pharmacy", mins_pharm, freq_hospital * 0.8)

    # Education (5 visits/week for school-age children on weekdays)
    if edu_has_kids and edu_variant in ("public", "pubpriv") and edu_levels:
        per_level = 1.0 / len(edu_levels)
        for level in edu_levels:
            svc_key = edu_level_to_key(level, edu_variant)
            cols = ACC_COLUMNS[svc_key]
            mins = blend_minutes(cols["coche"], cols["TransportePublico"])
            add_hours(
                f"edu_{level.lower()}",
                mins,
                5.0 * per_level,  # 5 school days per week, split evenly across levels
            )

    out["AccessibilityHoursWeekly"] = total
    return out
