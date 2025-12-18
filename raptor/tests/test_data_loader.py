import pytest
from raptor.src import data_loader


def test_cleaned_metadata_exists():
    df = data_loader.load_cleaned_metadata()
    assert not df.empty


def test_list_nav_files():
    schemes = data_loader.list_available_schemes()
    assert isinstance(schemes, list)
    assert len(schemes) > 0
