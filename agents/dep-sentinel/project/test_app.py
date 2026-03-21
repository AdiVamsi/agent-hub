"""Tests that verify all dependencies can be imported.

The harness runs these tests to check compatibility after policy changes.
"""


def test_imports():
    """All required packages must be importable."""
    import flask
    import requests
    import yaml
    import cryptography
    import PIL
    import sqlalchemy
    import jinja2
    import numpy
    import pandas
    import click
    import markupsafe
    import werkzeug
    assert True


def test_app_creates():
    """The Flask app must instantiate."""
    from app import app
    assert app is not None


def test_health_endpoint():
    """Health endpoint must respond."""
    from app import app
    client = app.test_client()
    response = client.get("/health")
    assert response.status_code == 200
