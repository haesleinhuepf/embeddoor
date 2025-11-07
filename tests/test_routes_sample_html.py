"""Tests for HTML sample route."""

from embeddoor.app import create_app
import pandas as pd


def test_sample_html_no_data():
    app = create_app()
    client = app.test_client()
    resp = client.get('/api/data/sample_html?n=5')
    assert resp.status_code == 404


def test_sample_html_with_data():
    app = create_app()
    # Inject a simple dataframe
    app.data_manager.df = pd.DataFrame({'a': [1, 2], 'b': [3, 4]})
    client = app.test_client()
    resp = client.get('/api/data/sample_html?n=5')
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    assert '<table' in html
    assert 'a' in html
    assert 'b' in html
