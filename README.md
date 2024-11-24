# Proyecto_Tecno

Se debe instalar miniconda con los paquetes que se muestran en requirements.txt

`pip install python-dotenv folium geopandas`

## Descarga de datos

Geojson Poblasción https://ideocuc-ocuc.hub.arcgis.com/datasets/1f7b3056b4b149b0ab84b5f603afb0b8_0/explore?location=-33.456630%2C-70.625522%2C16.15

Geojson flujo vehicular stgo: https://ideocuc-ocuc.hub.arcgis.com/datasets/1e8ef7a4422741f6b626fb86a2c359f8_0/explore?location=-33.450723%2C-70.638065%2C14.27

Geojson EOD (con cantidad de viajes divididpos x tipo y macrozona): https://ideocuc-ocuc.hub.arcgis.com/datasets/65d6ea3ca38d4983a56297b986ddc697_0/explore?location=-33.451286%2C-70.658580%2C14.14


Se deben dejar estas descargas y otros gojson en una carpeta "data" en la raiz del repo

## .env
Se debe crear un archivo .env en `app-testing/test` del siguiente estilo con los path de lo geojson descargados anteriormente:

```
GEOJSON_PATH_POBLACION="C:\Users\pablo\Desktop\EL6101-Proyecto_Tecno\data\Poblacin_Total_Santiago_de_Chile_2012-cud.geojson"
GEOJSON_PATH_FLUJOS="C:\Users\pablo\Desktop\EL6101-Proyecto_Tecno\data\Calculo_de_flujo_vehicular_en_AMS.geojson"
GEOJSON_PATH_SALIDA="C:\Users\pablo\Desktop\EL6101-Proyecto_Tecno\app-testing\out\"
```