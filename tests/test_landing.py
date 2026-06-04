"""test_landing.py — Landing page tests."""

import pytest


@pytest.fixture
def client(app):
    from app import create_app

    return create_app("testing").test_client()


@pytest.fixture
def app():
    from app import create_app

    return create_app("testing")


def test_landing_sections(client):
    response = client.get("/")
    html = response.data
    assert response.status_code == 200
    for section_id in (
        b'id="hero"',
        b'id="about"',
        b'id="services"',
        b'id="ia"',
        b'id="gallery"',
        b'id="contact"',
    ):
        assert section_id in html


def test_contact_form_post(client):
    response = client.post(
        "/contact",
        data={
            "name": "Jean Dupont",
            "email": "jean@example.com",
            "message": "Demande de démo",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Jean Dupont" in response.data
