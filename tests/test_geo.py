"""Tests for geolocation utilities."""
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
