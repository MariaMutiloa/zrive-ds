import requests
import pandas as pd
import matplotlib.pyplot as plt
import jsonschema
from jsonschema import validate
from typing import Dict, Any, Optional

# Esquema para validar que lo devuelve la API está bien
validation_schema = {
    "type": "object",
    "properties": {
        "daily": {
            "type": "object",
            "properties": {
                "time": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 1, 
                },  
                "temperature_2m_mean": {
                    "type": "array",
                    "items": {"type": "number"},
                    "minItems": 1,  
                },
                "precipitation_sum": {
                    "type": "array",
                    "items": {"type": "number"},
                    "minItems": 1,  
                },
                "wind_speed_10m_max": {
                    "type": "array",
                    "items": {"type": "number"},
                    "minItems": 1,
                },
            },
            "required": [
                "time",  
                "temperature_2m_mean",
                "precipitation_sum",
                "wind_speed_10m_max",
            ],
        }
    },
}



# Función genérica para llamadas a APIs
def api_request(url: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Lanza un error para respuestas no exitosas
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error in the API request: {e}")
        return None


# Función para obtener datos meteorológicos de la API Meteo
def get_data_meteo_api(
    city: Dict[str, float], start_date: str, end_date: str
) -> Optional[Dict[str, Any]]:
    API_URL = "https://archive-api.open-meteo.com/v1/archive?"
    VARIABLES = ["temperature_2m_mean", "precipitation_sum", "wind_speed_10m_max"]

    params = {
        "latitude": city["latitude"],
        "longitude": city["longitude"],
        "start_date": start_date,
        "end_date": end_date,
        "daily": ",".join(VARIABLES),
        "timezone": "Europe/Madrid",
    }

    data = api_request(API_URL, params)

    if data and "daily" in data:
        # Validar la respuesta contra el esquema de arriba
        try:
            validate(instance=data, schema=validation_schema)
            return data["daily"]
        except jsonschema.exceptions.ValidationError as e:
            print(f"Error in the schema validation: {e.message}")
            return None
    else:
        print(
            "No daily data found in the response or no response obtained from the API."
        )
        return None


# Función para procesar los datos
def data_process(daily_data: Dict[str, Any]) -> pd.DataFrame:
    df = pd.DataFrame(
        {
            "Date": pd.to_datetime(daily_data["time"]),
            "Temperature (°C)": daily_data["temperature_2m_mean"],
            "Precipitation (mm)": daily_data["precipitation_sum"],
            "Wind Speed (m/s)": daily_data["wind_speed_10m_max"],
        }
    )

    df.set_index("Date", inplace=True)

    return df


# Función para graficar los datos
def data_plot(daily_data: Dict[str, Any], city_name: str, ax: plt.Axes) -> None:
    df = data_process(daily_data)  # Procesar datos para cada ciudad
    df_monthly = df.resample("ME").mean()  # Agrupar por mes 
    # Asegúrate de que df_monthly no esté vacío
    if df_monthly.empty:
        print(f"No hay datos mensuales para graficar {city_name}.")
        return

    df_monthly["Temperature (°C)"].plot(
        ax=ax, label="Temperature (°C)", color="red", linewidth=2, marker="o"
    )
    df_monthly["Wind Speed (m/s)"].plot(
        ax=ax,
        label="Wind Speed (m/s)",
        color="green",
        linewidth=2,
        linestyle="--",
        marker="s",
    )
    ax2 = ax.twinx()  # Crear un eje secundario para la precipitación
    df_monthly["Precipitation (mm)"].plot(
        ax=ax2, label="Precipitation (mm)", color="blue", linewidth=2, marker="x"
    )

    ax.set_title(f"Monthly Weather Data for {city_name} (2010-2020)", fontsize=16)
    ax.set_xlabel("Date", fontsize=14)
    ax.set_ylabel("Temperature (°C)", fontsize=14)
    ax2.set_ylabel("Precipitation (mm)", fontsize=14)
    ax.legend(loc="upper left")
    ax2.legend(loc="upper right")
    ax.grid(True)



COORDINATES: Dict[str, Dict[str, float]] = {
    "Madrid": {"latitude": 40.416775, "longitude": -3.703790},
    "London": {"latitude": 51.507351, "longitude": -0.127758},
    "Rio": {"latitude": -22.906847, "longitude": -43.172896},
}


def main() -> None:
    start_date = "2010-01-01"
    end_date = "2020-12-31"

    # Crear la figura y los ejes para los subgráficos
    figures, axs = plt.subplots(
        len(COORDINATES), 1, figsize=(12, 5 * len(COORDINATES)), sharex=True
    )
    for ax, (city_name, city_coords) in zip(axs, COORDINATES.items()):
        print(f"Obteniendo datos de {city_name}...")
        daily_data = get_data_meteo_api(city_coords, start_date, end_date)

        if daily_data:
            data_plot(daily_data, city_name, ax)
        else:
            print(f"Error al obtener los datos de {city_name}")

    plt.subplots_adjust(hspace=0.4)  # Ajustar el espacio entre subgráficas
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
