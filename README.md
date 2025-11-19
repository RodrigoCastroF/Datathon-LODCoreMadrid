# Living on the Edge 🏘️

A Streamlit-based decision support application for finding your ideal municipality in the Community of Madrid based on accessibility, quality of life, and personal priorities.

## Overview

This app helps residents choose municipalities (<50k population) by ranking them according to:
- **Accessibility**: Weekly commute time to essential services (supermarkets, healthcare, sports, education)
- **Quality of Life**: Air quality, education quality, building attractiveness, transport infrastructure, economic dynamism
- **Affordability**: Housing prices per m²

## Key Features

### 1. Personalized Questionnaire
- Car usage frequency (days per week)
- Sports facility usage frequency (visits per week)
- Healthcare facility usage frequency (visits per week)
- Family situation (children, education levels)
- Population size preferences
- Priority ranking for 7 criteria (0-10 scale, where 0 = not important)

### 2. Smart Weighting (AHP)
- Analytic Hierarchy Process converts user priorities into normalized weights
- Robust to user input inconsistencies with automatic mathematical correction
- Zero-weight support for criteria users consider unimportant

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
│   ├── accessibility.py   # Weekly commute time computation
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

Weekly commute time is calculated based on user-specified visit frequencies:

$$
\text{Weekly Hours} = \sum_{\text{service}} \left( \text{visits per week} \times \frac{2 \times \text{minutes one-way}}{60} \right)
$$

#### Services included:

- **Supermarkets**: 2 visits/week (fixed baseline)
- **Gas stations**: Scaled with car usage (~0.1 × days per week using car)
- **Sports facilities**: User-specified frequency (visits per week)
- **Healthcare**: User-specified frequency split between:
  - GP visits (20%)
  - Pharmacy visits (80%)
- **Education**: 5 visits/week (weekdays) per level, split evenly if multiple levels

#### Transportation mode blending:

Travel times blend car and public transport based on car usage frequency:

$$
\text{Minutes} = \left(\frac{\text{car days}}{\text{7}}\right) \times \text{minutes}_{\text{car}} + \left(1 - \frac{\text{car days}}{\text{7}}\right) \times \text{minutes}_{\text{PT}}
$$

### Criteria Normalization

**Benefit criteria** (higher is better):

$$
\text{Normalized} = \frac{x - x_{\min}}{x_{\max} - x_{\min}}
$$

**Cost criteria** (lower is better):

$$
\text{Normalized} = 1 - \frac{x - x_{\min}}{x_{\max} - x_{\min}}
$$

### Final Score

Raw score:

$$
\text{Score} = \sum_{i=1}^{7} \left( \text{Normalized}_i \times \text{Weight}_i \right)
$$

Weighted score (0-100 scale):

$$
\text{Weighted Score} = \frac{\text{Score}}{\max(\text{Score})} \times 100
$$

## Data Sources

- **Geographic boundaries**: INSPIRE municipal boundaries (ETRS89)
- **Community of Madrid open data**: 
  - Demographics (`IDE_PoblacionTotal`)
  - Housing prices (`IDE_PrecioPorMetroCuadrado`)
  - Accessibility travel times (`ACC_*` columns for car and public transport)
  - Quality attributes (`ATR_*` clusters for education, air quality, buildings, transport, economy)
- **OpenStreetMap**: Supermarket locations and accessibility

## License
Educational/research use. Data sources retain their original licenses.

## Authors
_MiniEdgers_ - UC3M Datathon 2025