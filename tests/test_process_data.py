import pytest
import pandas as pd
import json
from unittest.mock import patch, MagicMock
import sys
import os
import setuptools
import warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.process_data import *


@pytest.mark.parametrize("input_value, expected_output", [
    ("2PT Field Goal", 2),
    ("3PT Field Goal", 3),
    ("", 0),
    (None, 0),
])
def test_encode_shot_type(input_value, expected_output):
    assert encode_shot_type(input_value) == expected_output


@patch("src.process_data.connect_to_mongo")
@patch("src.process_data.ensure_collection_exists")
@patch("src.process_data.pymongo.MongoClient")
@patch("src.process_data.json_util.dumps")
def test_get_raw_json_from_mongo_success(mock_dumps, mock_mongo_client, mock_ensure_collection, mock_connect):
    # Simuler connect_to_mongo avec succès
    mock_connect.return_value = (True, MagicMock())

    # Simuler que la collection existe
    mock_ensure_collection.return_value = True

    # Simuler les documents retournés par MongoDB
    mock_collection = MagicMock()
    mock_collection.find.return_value = [{"_id": 1, "name": "test"}]

    # Simuler le client MongoDB et sa structure
    mock_db = MagicMock()
    mock_db.__getitem__.return_value = mock_collection
    mock_mongo_client.return_value.__getitem__.return_value = mock_db

    # Simuler json_util.dumps
    mock_dumps.return_value = '[{"_id": 1, "name": "test"}]'

    # Appel de la fonction
    df = get_raw_json_from_mongo("fake_uri", "fake_db", "fake_collection")

    # Vérification du résultat
    assert isinstance(df, pd.DataFrame)
    assert "name" in df.columns
    assert df.iloc[0]["name"] == "test"

@patch("src.process_data.connect_to_mongo")
@patch("src.process_data.ensure_collection_exists")
def test_inject_processed_json_to_mongo_success(mock_ensure_collection, mock_connect):
    # Simuler connect_to_mongo avec succès
    mock_client = MagicMock()
    mock_connect.return_value = (True, mock_client)

    # Simuler que la collection existe
    mock_ensure_collection.return_value = True

    # Mock la collection MongoDB
    mock_collection = MagicMock()
    mock_db = MagicMock()
    mock_db.__getitem__.return_value = mock_collection
    mock_client.__getitem__.return_value = mock_db

    # Données JSON valides (liste)
    processed_data = json.dumps([
        {"name": "Alice"},
        {"name": "Bob"}
    ])

    # Appel de la fonction
    result = inject_processed_json_to_mongo(
        mongo_uri="fake_uri",
        db_name="fake_db",
        collection_name="fake_collection",
        processed_data=processed_data
    )

    # Vérifier que les documents ont bien été insérés
    mock_collection.delete_many.assert_called_once()
    mock_collection.insert_many.assert_called_once()
    assert result is True