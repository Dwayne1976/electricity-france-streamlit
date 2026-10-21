"""Download the open data into data/ (only needed if the data folder is empty)."""
import urllib.request

DATA = "https://opendata.agenceore.fr/data-fair/api/v1/datasets/consommation-annuelle-d-electricite-et-gaz-par-departement/raw"
MAP = "https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/departements-version-simplifiee.geojson"

urllib.request.urlretrieve(DATA, "data/conso_elec_gaz_departement.csv")
urllib.request.urlretrieve(MAP, "data/departements.geojson")
print("Data downloaded in the data/ folder.")
