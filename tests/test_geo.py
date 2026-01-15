"""Tests for geolocation utilities."""
import pytest
from etl_utils.geo import extract_coords

def test_extract_coords_mapstate_obergurgl():
    """Test extraction from mapstate param (standard format)."""
    url = "https://www.bergfex.at/obergurgl-hochgurgl/schneebericht/#?mapstate=46.894161,11.064692,13,o,430,46.894161,11.064692"
    coords = extract_coords(url)
    assert coords == (46.894161, 11.064692)


def test_extract_coords_mapstate_sixt():
    """Test extraction from mapstate with different format."""
    url = "https://www.bergfex.at/sixt-fer-a-cheval/schneebericht/#?mapstate=46.043011,6.767044,13,o,430,46.043011,6.767044"
    coords = extract_coords(url)
    assert coords == (46.043011, 6.043011) if 6.043011 == 6.767044 else coords == (46.043011, 6.767044)


def test_extract_coords_html_destination():
    """Test extraction from HTML content with destination param."""
    url = "https://www.bergfex.at/dummy/"
    html = '... <a href="https://maps.google.com/?destination=46.043011%2C6.767044">Route</a> ...'
    coords = extract_coords(url, html)
    assert coords == (46.043011, 6.767044)

    # Test with comma instead of %2C
    html_comma = '... destination=46.043011,6.767044 ...'
    coords = extract_coords(url, html_comma)
    assert coords == (46.043011, 6.767044)


def test_extract_coords_none():
    """Test that None is returned when no coords are found."""
    url = "https://www.bergfex.at/dummy/schneebericht/"
    html = "<html><body>Just some text</body></html>"
    coords = extract_coords(url, html)
    assert coords is None


def test_extract_coords_raw_pattern():
    """Test extraction of raw lat,lon pattern from HTML."""
    url = "https://www.bergfex.at/dummy/"
    html = 'some text 46.894161,11.064692 more text'
    coords = extract_coords(url, html)
    assert coords == (46.894161, 11.064692)
    
    # With space after comma
    html_space = 'some text 47.420654, 13.128600 more text'
    coords = extract_coords(url, html_space)
    assert coords == (47.420654, 13.128600)


def test_extract_coords_salamandra_lon_check():
    """Test that coordinates with longitude > 17 are accepted (e.g. Salamandra)."""
    url = "https://www.bergfex.at/dummy/"
    # Salamandra coords: 48.45394, 18.858719
    html = 'some text 48.45394, 18.858719 more text'
    coords = extract_coords(url, html)
    assert coords == (48.45394, 18.858719)


def test_extract_coords_arrach_lat_check():
    """Test that coordinates with latitude > 49 are accepted (e.g. Arrach)."""
    url = "https://www.bergfex.de/arrach-eck-riedelstein/"
    # Arrach coords: 49.164897, 12.98172
    html = 'some text 49.164897,12.98172 more text'
    coords = extract_coords(url, html)
    assert coords == (49.164897, 12.98172)


def test_extract_coords_mapstate_query_param():
    """Test extraction from mapstate in query parameter (not just fragment)."""
    # User provided link: https://www.bergfex.de/arrach-eck-riedelstein/?mapstate=49.164897,12.98172,13,o,430,49.164897,12.98172
    url = "https://www.bergfex.de/arrach-eck-riedelstein/?mapstate=49.164897,12.98172,13,o,430,49.164897,12.98172"
    coords = extract_coords(url)
    assert coords == (49.164897, 12.98172)


@pytest.mark.integration
def test_extract_coords_integration_real_page():
    """Integration test: fetch real Bergfex page and extract coords."""
    import requests
    
    url = "https://www.bergfex.at/obergurgl-hochgurgl/"
    resp = requests.get(url, timeout=30)
    assert resp.status_code == 200
    
    coords = extract_coords(url, resp.text)
    assert coords is not None, "Should find coords in real Obergurgl page"
    
    lat, lon = coords
    # Obergurgl is approximately at 46.89°N, 11.06°E
    assert 46.8 < lat < 47.0, f"Latitude {lat} should be near 46.89"
    assert 10.9 < lon < 11.2, f"Longitude {lon} should be near 11.06"


@pytest.mark.integration
def test_extract_coords_integration_arrach():
    """Integration test: fetch real Arrach-Eck-Riedelstein page and extract coords."""
    import requests
    
    # Use the base URL, assuming the scraper hits this
    url = "https://www.bergfex.de/arrach-eck-riedelstein/"
    resp = requests.get(url, timeout=30)
    assert resp.status_code == 200
    
    # If standard extraction works via raw patterns in HTML
    coords = extract_coords(url, resp.text)
    
    # If that fails, maybe try the direct map link if we can find it in the HTML?
    # But for now let's assert that the updated regex finds it in the main page HTML
    assert coords is not None, "Should find coords in real Arrach page"
    
    lat, lon = coords
    # Arrach: 49.164897, 12.98172
    assert 49.0 < lat < 49.3, f"Latitude {lat} should be near 49.16"
    assert 12.8 < lon < 13.1, f"Longitude {lon} should be near 12.98"


@pytest.mark.integration
def test_extract_coords_integration_alpspitz():
    """Integration test: fetch real Alpspitz-Edelsberg page and extract coords."""
    import requests
    
    url = "https://www.bergfex.de/alpspitz-edelsberg-ostallgaeu/"
    resp = requests.get(url, timeout=30)
    assert resp.status_code == 200
    
    coords = extract_coords(url, resp.text)
    assert coords is not None, "Should find coords in real Alpspitz page"
    
    lat, lon = coords
    # Alpspitz: 47.603617, 10.49881
    assert 47.5 < lat < 47.7, f"Latitude {lat} should be near 47.60"
    assert 10.4 < lon < 10.6, f"Longitude {lon} should be near 10.50"
