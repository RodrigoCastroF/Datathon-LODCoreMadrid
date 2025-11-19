# Living on the Edge 🏘️

A Streamlit-based decision support application for finding your ideal municipality in the Community of Madrid based on accessibility, quality of life, and personal priorities.

## Overview

This app helps residents choose municipalities (<50k population) by ranking them according to:
- **Accessibility**: Monthly commute time to essential services (supermarkets, healthcare, sports, education)
- **Quality of Life**: Air quality, education quality, building attractiveness, transport infrastructure, economic dynamism
- **Affordability**: Housing prices per m²

## Key Features

### 1. Personalized Questionnaire
- Car usage frequency
- Family situation (children, education preferences)
- Sports and healthcare needs
- Population size preferences
- Priority ranking for 7 criteria (1-10 scale)

### 2. Smart Weighting (AHP)
- Analytic Hierarchy Process converts user priorities into normalized weights
- Consistency ratio (CR) validation with automatic correction
- Transparent weight display in sidebar

### 3. Interactive Visualizations
- **Map View**: Choropleth heatmap with click-to-select municipalities
- **List View**: Paginated cards with key metrics
- **Details Panel**: Full breakdown by criterion with progress bars
- **Comparison Mode**: Side-by-side municipality comparison

### 4. Sensitivity Analysis
- Tests ranking stability by varying top-3 criteria weights ±10%
- Shows overlap in top-5 municipalities
- Stability metrics (stable/variable)

### 5. Export
- Download full results as CSV with all scores and contributions

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
streamlit run app.py
```

## Project Structure

```md
App_v2/
├── app.py                 # Main application entry point
├── config/
│   ├── constants.py       # Criteria, labels, column mappings
│   └── styles.py          # CSS styling and page config
├── core/
│   ├── accessibility.py   # Monthly commute time computation
│   ├── ahp.py             # AHP weight calculation algorithms
│   ├── data_loader.py     # Data loading and image handling
│   └── scoring.py         # Normalization and ranking
├── ui/
│   ├── questionnaire.py   # Sidebar user input form
│   ├── map_view.py        # Interactive choropleth map
│   ├── list_view.py       # Municipality cards with pagination
│   ├── details_view.py    # Detailed breakdown and comparison
│   └── sensitivity.py     # Weight perturbation analysis
├── data/
│   └── merged_dataset.csv
├── boundaries/
│   └── recintos_municipales_inspire_peninbal_etrs89.shp    # Boundary data
└── assets/
    └── municipalities/    # Municipality images
```

## Methodology

### Accessibility Calculation

Monthly commute hours = $Σ (service visits/month × round-trip minutes / 60) × user weight$

#### Services included:

* Supermarkets (8 visits/month)

* Gas stations (2 visits/month, car-dependent)

* Sports facilities (4 visits/month)

* Healthcare: GP (0.25/month) + Pharmacy (1/month)

* Education (2 visits/month per level, if applicable)

### Criteria Normalization
* **Benefit criteria** (higher is better): (x - min) / (max - min)

* **Cost criteria** (lower is better): 1 - (x - min) / (max - min)

### Final Score

* Score = $Σ (normalized_criterion × AHP_weight)$

* Weighted score = (Score / max_score) × 100

## Data Sources

* Geographic boundaries: INSPIRE municipal boundaries (ETRS89)

* Indicators: Community of Madrid open data

* IDEALISTA

    * Demographics (`IDE_PoblacionTotal`)

    * Housing prices (`IDE_PrecioPorMetroCuadrado`)

* Accessibility times (ACC_* columns)

* Quality attributes (ATR_* columns)

## License
Educational/research use. Data sources retain their original licenses.

## Authors
_MiniEdgers_ - UC3M Datathon 2025