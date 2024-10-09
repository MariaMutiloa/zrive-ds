import pytest
import requests
import pandas as pd
from pandas.testing import assert_frame_equal
from unittest.mock import MagicMock 
from src.module_1.module_1_meteo_api import main, api_request, get_data_meteo_api, data_process, data_plot

def test_api_request_OK(requests_mock):
    url = "https://url.com" 
    params = {"param1": "value1"}
    requests_mock.get(url, json={"key": "value"}, status_code=200) #simulo una respuesta API con el codigo 200
    response = api_request(url, params)
    assert response == {"key": "value"}

def test_api_request_fail(requests_mock):
    url = "https://url.com"  
    params = {"param1": "value1"}
    requests_mock.get(url, status_code=404)
    response = api_request(url, params)
    assert response is None

@pytest.fixture
def city_coords():  # Pongo como ejemplo Madrid
    return {"latitude": 40.416775, "longitude": -3.703790}

def test_get_data_meteo_api_OK(requests_mock, city_coords):
    url = "https://archive-api.open-meteo.com/v1/archive?"
    mock_response = {
        "daily": {
            "time": ["2010-01-01", "2010-01-02"],
            "temperature_2m_mean": [10.0, 12.0],
            "precipitation_sum": [0.5, 1.0],
            "wind_speed_10m_max": [3.0, 5.0],
        }
    }

    requests_mock.get(url, json=mock_response, status_code=200)

    data = get_data_meteo_api(city_coords, "2010-01-01", "2020-12-31")
    assert data == mock_response["daily"] # verifica que los datos devueltos por get_data_meteo_api coinciden con los datos de la prueba

def test_get_data_meteo_api_wrong_schema(requests_mock, city_coords):
    url = "https://archive-api.open-meteo.com/v1/archive?"
    mock_response = {
        "daily": {
            "time": ["2010-01-01", "2010-01-02"],
            "temperature_2m_mean": [10.0],
            "precipitation_sum": [0.5],
            "wind_speed_10m_max": [],
        }
    }

    requests_mock.get(url, json=mock_response, status_code=200)

    data = get_data_meteo_api(city_coords, "2010-01-01", "2020-12-31")
    assert data is None  #verifica que el esquema no coincide

def test_data_process():
    daily_data = {
        "time": ["2010-01-01", "2010-01-02"],
        "temperature_2m_mean": [10.0, 12.0],
        "precipitation_sum": [0.5, 1.0],
        "wind_speed_10m_max": [3.0, 5.0],
    }

    expected_df = pd.DataFrame(
        {
            "Date": pd.to_datetime(["2010-01-01", "2010-01-02"]),
            "Temperature (°C)": [10.0, 12.0],
            "Precipitation (mm)": [0.5, 1.0],
            "Wind Speed (m/s)": [3.0, 5.0],
        }
    ).set_index("Date")

    result_df = data_process(daily_data)
    assert_frame_equal(result_df, expected_df)