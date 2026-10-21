"""Electricity in France after the 2022 energy crisis – a simple Streamlit data story.
Run:  streamlit run app.py
"""
import json
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Electricity in France", page_icon="⚡", layout="wide")

SOURCE = "Source: Agence ORE – electricity and gas consumption by department (data.gouv.fr, Licence Ouverte)."
SECTORS = {"RESIDENTIEL": "Residential", "TERTIAIRE": "Services", "INDUSTRIE": "Industry", "AGRICULTURE": "Agriculture"}


# ---------- 1. Load and clean the data (only once, thanks to the cache) ----------
@st.cache_data
def load_data():
    raw = pd.read_csv("data/conso_elec_gaz_departement.csv", dtype={"Code Département": str},
                      low_memory=False)
    n_rows, n_dup = len(raw), raw.duplicated().sum()     # quality checks on the raw file
    raw = raw.drop_duplicates()                          # remove exact duplicates
    df = raw[["FILIERE", "Année", "Code Département", "Nom Département",
              "Nom Région", "CODE GRAND SECTEUR", "Conso totale (MWh)"]].copy()
    df.columns = ["energy", "year", "dep_code", "department", "region", "sector", "mwh"]

    quality = {"rows": n_rows, "duplicates": n_dup, "missing": df.isna().sum(), "rows_per_year": df.groupby("year").size()}

    df = df[df["energy"].str.startswith("Electr")]       # keep electricity only
    df = df[df["year"] >= 2018]                          # same sector classification from 2018
    df = df.dropna(subset=["mwh"])                       # hidden values (confidentiality)
    df["sector"] = df["sector"].map(SECTORS)             # readable names
    df = df.dropna(subset=["sector"])                    # drop "unknown" sector
    df["dep_code"] = df["dep_code"].str.zfill(2)         # "1" -> "01"
    return df, quality


@st.cache_data
def load_map():
    with open("data/departements.geojson", encoding="utf-8") as f:
        return json.load(f)


df, quality = load_data()
geo = load_map()

# ---------- 2. Sidebar filters ----------
st.sidebar.header("Filters")
years = st.sidebar.slider("Years", 2018, int(df["year"].max()), (2018, int(df["year"].max())))
regions = st.sidebar.multiselect("Regions (empty = all)", sorted(df["region"].dropna().unique()))
sectors = st.sidebar.multiselect("Sectors", list(SECTORS.values()), default=list(SECTORS.values()))
st.sidebar.caption(SOURCE)

y0, y1 = years
data = df[df["year"].between(y0, y1) & df["sector"].isin(sectors)]
if regions:
    data = data[data["region"].isin(regions)]
if data.empty:
    st.warning("No data for this selection.")
    st.stop()

# ---------- 3. Title and KPI header ----------
st.title("⚡ Did France really save electricity after the 2022 energy crisis?")
by_year = data.groupby("year")["mwh"].sum() / 1e6          # MWh -> TWh
change = (by_year[y1] - by_year[y0]) / by_year[y0] * 100

c1, c2, c3 = st.columns(3)
c1.metric(f"Consumption in {y1}", f"{by_year[y1]:.1f} TWh")
c2.metric(f"Change {y0} → {y1}", f"{change:+.1f} %")
c3.metric("Departments", data["dep_code"].nunique())

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Context", "Trend", "Map", "Data quality", "Conclusion"])

# ---------- 4. Story ----------
with tab1:
    st.markdown("""
In 2022, energy prices exploded in Europe and France launched an **energy sobriety plan** (−10 % target).
**Question:** did electricity consumption really go down, in which sectors and in which departments?
**Audience:** local energy planners and students. Use the filters on the left: every chart follows them.
""")

with tab2:
    trend = data.groupby(["year", "sector"], as_index=False)["mwh"].sum()
    trend["TWh"] = trend["mwh"] / 1e6
    fig = px.line(trend, x="year", y="TWh", color="sector", markers=True,
                  labels={"year": "Year", "TWh": "Consumption (TWh)", "sector": "Sector"})
    fig.add_vline(x=2022, line_dash="dash", annotation_text="2022 crisis")
    st.plotly_chart(fig, width="stretch")
    st.caption("Line chart: electricity consumption per sector and per year. The dashed line marks 2022.")

with tab3:
    dep = data[data["year"].isin([y0, y1])].pivot_table(
        index=["dep_code", "department"], columns="year", values="mwh", aggfunc="sum").reset_index()
    if y0 == y1:
        st.info("Choose at least two years to see the change.")
    else:
        dep["change_%"] = (dep[y1] - dep[y0]) / dep[y0] * 100
        fig = px.choropleth(dep, geojson=geo, locations="dep_code", featureidkey="properties.code",
                            color="change_%", color_continuous_scale="RdYlGn_r", hover_name="department",
                            labels={"change_%": f"Change {y0}→{y1} (%)"})
        fig.update_geos(fitbounds="locations", visible=False)
        st.plotly_chart(fig, width="stretch")
        st.caption("Map of mainland departments: green = consumption went down, red = it went up.")

        top = dep.nsmallest(10, "change_%")
        fig = px.bar(top, x="change_%", y="department", orientation="h",
                     labels={"change_%": f"Change {y0}→{y1} (%)", "department": "Department"})
        st.plotly_chart(fig, width="stretch")
        st.caption("Bar chart: the 10 departments with the biggest drop.")

with tab4:
    q1, q2 = st.columns(2)
    q1.metric("Rows in the raw file", f"{quality['rows']:,}")
    q2.metric("Exact duplicates", int(quality["duplicates"]))
    st.bar_chart(quality["rows_per_year"], x_label="Year", y_label="Number of rows")
    st.caption("Rows per year: the file is much more detailed from 2018, so the story starts in 2018.")
    st.write("Missing values per column (raw file):")
    st.dataframe(quality["missing"].rename("missing values"))
    st.markdown("""
**Cleaning steps:** keep electricity only, remove duplicates, keep years ≥ 2018,
remove hidden (confidential) values, give readable sector names.
**Limits:** totals are slightly underestimated (hidden values); weather is not corrected
(a cold winter raises consumption); data is yearly, not monthly.
""")

with tab5:
    st.markdown(f"""
- For the selected scope, consumption changed by **{change:+.1f} %** between {y0} and {y1}.
- The drop is clearest after **2022**, the year of the crisis and of the sobriety plan.
- **Next step:** use monthly data (RTE) and weather-corrected values to separate behaviour from temperature.
""")

st.caption(SOURCE)
