import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from accounts.models import User
from products.models import Product, Category, Collection, Language, Version, Condition, Variant


@pytest.mark.django_db
def test_create_collection():
    client = APIClient()
    user = User.objects.create_user(username="user1", password="pass", email="u1@example.com")
    cat = Category.objects.create(name="Cat1")
    product = Product.objects.create(name="Prod", tcg_type="pokemon")
    product.categories.add(cat)
    lang = Language.objects.create(code="EN", name="English")
    ver = Version.objects.create(code="v1", name="First")
    cond = Condition.objects.create(code="NM", label="Near Mint")
    variant = Variant.objects.create(product=product, language=lang, version=ver, condition=cond)
    client.force_authenticate(user=user)
    url = reverse('collection-list')
    response = client.post(url, {"name": "My Collection", "variants_ids": [variant.id]})
    assert response.status_code == 201
    coll = Collection.objects.get(user=user, name="My Collection")
    assert coll.variants.count() == 1
