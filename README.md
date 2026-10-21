# ⚡ Did France really save electricity after the 2022 energy crisis?

Streamlit data story – Individual Student Project (EFREI, 2026).

**Question:** after the 2022 energy crisis and the sobriety plan, did electricity consumption go down, in which sectors and in which departments?
**Audience:** local energy planners and students.

## Data
- Agence ORE – *Consommation annuelle d'électricité et gaz par département*: https://www.data.gouv.fr/datasets/65f1185fbb16ea436d7ba548 (Licence Ouverte)
- Department boundaries: france-geojson (G. David)

Both files are in `data/`. To download them again: `python download_data.py`

## Run
```
pip install -r requirements.txt
streamlit run app.py
```

## Project structure
```
app.py            the whole app (loading, cleaning, filters, charts)
download_data.py  downloads the data
requirements.txt  libraries
data/             CSV + map of departments
```

## What the app contains
- Sidebar filters: years, regions, sectors
- KPI header: consumption, change, number of departments
- 3 interactive charts: trend by sector, map of departments, top 10 drops
- Data quality tab: duplicates, missing values, rows per year, cleaning steps, limits
- `st.cache_data` to load the data only once; a caption under each chart for accessibility

## Cleaning
Keep electricity only, remove duplicates, keep years ≥ 2018 (sector classification changes before), remove hidden values, readable sector names.

## Limits
Hidden values (slight underestimation), no weather correction, yearly data only.

## Deployment
Push to GitHub, then https://share.streamlit.io → New app → `app.py`.
Deployed app: _add link_ · Demo video: _add link_
