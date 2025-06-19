import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from accounts.models import User
from products.models import (
    Product,
    Language,
    Version,
    Condition,
    Grade,
    Variant,
    Listing,
)
from searches.models import SearchHistory


@pytest.mark.django_db
def test_search_with_filters():
    client = APIClient()
    seller = User.objects.create_user(username="seller", password="pass")
    lang = Language.objects.create(code="EN", name="English")
    ver = Version.objects.create(code="v1", name="First")
    cond = Condition.objects.create(code="NM", label="Near Mint")
    grade = Grade.objects.create(value=9.0, grader="PSA")
    product = Product.objects.create(name="Pikachu", tcg_type="pokemon", block="Base", series="1st")
    variant = Variant.objects.create(product=product, language=lang, version=ver, condition=cond, grade=grade)
    listing = Listing.objects.create(product=product, variant=variant, seller=seller, price=10, stock=5)

    other_lang = Language.objects.create(code="FR", name="French")
    other_ver = Version.objects.create(code="v2", name="Second")
    other_cond = Condition.objects.create(code="HP", label="HP")
    other_variant = Variant.objects.create(product=product, language=other_lang, version=other_ver, condition=other_cond)
    Listing.objects.create(product=product, variant=other_variant, seller=seller, price=30, stock=0)

    url = reverse("search")
    resp = client.get(url, {
        "q": "pika",
        "language": "EN",
        "tcg_type": "pokemon",
        "min_price": 5,
        "max_price": 15,
        "availability": "in_stock",
    })
    assert resp.status_code == 200
    assert resp.data["count"] == 1
    assert resp.data["results"][0]["id"] == listing.id


@pytest.mark.django_db
def test_search_history_created():
    client = APIClient()
    user = User.objects.create_user(username="user", password="pass")
    lang = Language.objects.create(code="EN", name="English")
    ver = Version.objects.create(code="v1", name="First")
    cond = Condition.objects.create(code="NM", label="Near Mint")
    product = Product.objects.create(name="Charizard", tcg_type="pokemon")
    variant = Variant.objects.create(product=product, language=lang, version=ver, condition=cond)
    Listing.objects.create(product=product, variant=variant, seller=user, price=5, stock=1)

    client.force_authenticate(user=user)
    url = reverse("search")
    client.get(url, {"q": "char"})
    assert SearchHistory.objects.filter(user=user).count() == 1


@pytest.mark.django_db
def test_search_pagination():
    client = APIClient()
    seller = User.objects.create_user(username="s", password="pass")
    lang = Language.objects.create(code="EN", name="English")
    ver = Version.objects.create(code="v1", name="First")
    cond = Condition.objects.create(code="NM", label="Near Mint")
    product = Product.objects.create(name="Bulkmon", tcg_type="pokemon")
    variant = Variant.objects.create(product=product, language=lang, version=ver, condition=cond)

    for i in range(25):
        Listing.objects.create(product=product, variant=variant, seller=seller, price=i + 1, stock=1)

    url = reverse("search")
    resp = client.get(url)
    assert resp.status_code == 200
    assert resp.data["count"] == 25
    assert len(resp.data["results"]) == 20
    assert resp.data["next"] is not None

