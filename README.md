# Proyecto_Tecno

Se debe instalar miniconda con los paquetes que se muestran en requirements.txt

`pip install python-dotenv folium geopandas`

## Descarga de datos

Geojson Poblasción https://ideocuc-ocuc.hub.arcgis.com/datasets/1f7b3056b4b149b0ab84b5f603afb0b8_0/explore?location=-33.456630%2C-70.625522%2C16.15

Geojson flujo vehicular stgo: https://ideocuc-ocuc.hub.arcgis.com/datasets/1e8ef7a4422741f6b626fb86a2c359f8_0/explore?location=-33.450723%2C-70.638065%2C14.27



## .env
Se debe crear un archivo .env en `/app-testinf` del siguiente estilo con los path de lo geojson descargados anteriormente:

```
GEOJSON_PATH_POBLACION=""
GEOJSON_PATH_FLUJOS=""
```