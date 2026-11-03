"""Tests d'intégration HTTP pour l'API de caisse, via TestClient FastAPI."""

import pytest
from fastapi.testclient import TestClient

from supermarket_receipt_api.main import app

client = TestClient(app)


def test_checkout_accepted_three_for_two() -> None:
    """Vérifier un panier accepté avec la promotion 3 pour 2 sur les brosses à dents.

    Aucun effet de bord ; le calcul attendu est fait indépendamment du code, à partir
    du contrat : 3 brosses à 99 centimes = 297 centimes de brut, une offerte donc
    99 centimes de réduction, soit 198 centimes net.

    Returns:
        None: Le test réussit si le ticket JSON correspond exactement à l'attendu.

    Raises:
        AssertionError: Si le statut ou le contenu du ticket diffère de l'attendu.
    """
    response = client.post(
        "/checkout",
        json={"items": [{"product_id": "toothbrush", "quantity": 3}]},
    )

    assert response.status_code == 200
    body = response.json()
    assert body == {
        "lines": [
            {
                "product_id": "toothbrush",
                "name": "Brosse à dents",
                "quantity": 3,
                "unit": "piece",
                "unit_price_cents": 99,
                "subtotal_cents": 297,
                "discount_cents": 99,
                "total_cents": 198,
            }
        ],
        "subtotal_cents": 297,
        "discount_cents": 99,
        "total_cents": 198,
    }


@pytest.mark.parametrize(
    "payload",
    [
        {"items": [{"product_id": "toothbrush"}]},
        {"items": [{"product_id": "toothbrush", "quantity": 1, "gift_wrap": True}]},
        {"items": [{"product_id": "toothbrush", "quantity": "trois"}]},
    ],
)
def test_checkout_rejected_invalid_payload(payload: dict[str, object]) -> None:
    """Vérifier qu'une requête invalide est refusée.

    La validation est faite par FastAPI/Pydantic avant le moteur métier.

    Args:
        payload: Corps JSON invalide fourni par pytest.

    Raises:
        AssertionError: Si le statut diffère de 422.
    """
    response = client.post("/checkout", json=payload)

    assert response.status_code == 422
