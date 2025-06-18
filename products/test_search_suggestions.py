import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from products.models import Product


@pytest.mark.django_db
def test_name_suggestions():
    Product.objects.create(name="Pikachu", tcg_type="pokemon")
    Product.objects.create(name="Pikaman", tcg_type="pokemon")
    Product.objects.create(name="Bulbasaur", tcg_type="pokemon")

    client = APIClient()
    url = reverse("search-suggestions")
    response = client.get(url, {"query": "Pika"})

    assert response.status_code == 200
    assert "Pikachu" in response.data
    assert "Pikaman" in response.data
    assert "Bulbasaur" not in response.data


@pytest.mark.django_db
def test_block_and_series_suggestions():
    Product.objects.create(name="Charizard", block="Fire Block", series="Alpha", tcg_type="pokemon")
    Product.objects.create(name="Mewtwo", block="Fire Tower", series="Beta", tcg_type="pokemon")

    client = APIClient()
    url = reverse("search-suggestions")
    response = client.get(url, {"query": "Fire"})

    assert response.status_code == 200
    assert "Fire Block" in response.data
    assert "Fire Tower" in response.data
    # series not matched by 'Fire'
    assert "Alpha" not in response.data


@pytest.mark.django_db
def test_empty_query_returns_empty():
    Product.objects.create(name="Test", tcg_type="pokemon")

    client = APIClient()
    url = reverse("search-suggestions")
    response = client.get(url, {"query": ""})

    assert response.status_code == 200
    assert response.data == []

