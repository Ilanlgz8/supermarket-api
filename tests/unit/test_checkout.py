"""Tests unitaires de départ pour les calculs de sous-total et de réduction."""

import pytest

from supermarket_receipt_api.checkout import (
    line_subtotal_cents,
    percentage_discount_cents,
    validate_quantity,
)


@pytest.mark.parametrize(
    "unit_price_cents, quantity, unit, expected",
    [(100, 2, "piece", 200), (199, 1000, "gram", 199), (199, 2000, "gram", 398)],
)
def test_line_subtotal_nominal(
    unit_price_cents: int, quantity: int, unit: str, expected: int
) -> None:
    """Vérifier des calculs de sous-total.

    Aucun effet de bord ni application HTTP.

    Args:
        unit_price_cents (int): Prix unitaire en centimes fourni par pytest.
        quantity (int): Quantité de pièces ou de grammes fournie par pytest.
        unit (str): Unité de vente du cas paramétré.
        expected (int): Montant brut attendu en centimes.

    Returns:
        None: Le test réussit si le montant calculé correspond à l'attendu.

    Raises:
        AssertionError: Si le montant calculé diffère de expected.
    """
    assert line_subtotal_cents(unit_price_cents, quantity, unit) == expected


@pytest.mark.parametrize(
    "subtotal_cents, discount_percent, expected",
    [(1000, 20, 200), (1200, 10, 120), (800, 25, 200)]
    + [(100 * amount_euros, 10, 10 * amount_euros) for amount_euros in range(20, 114)],
)
def test_percentage_discount_nominal(
    subtotal_cents: int, discount_percent: int, expected: int
) -> None:
    """Vérifier des calculs de réduction en pourcentage.

    Aucun effet de bord ni application HTTP.

    Args:
        subtotal_cents (int): Montant brut en centimes fourni par pytest.
        discount_percent (int): Pourcentage de réduction fourni par pytest.
        expected (int): Réduction attendue en centimes.

    Returns:
        None: Le test réussit si la réduction calculée correspond à l'attendu.

    Raises:
        AssertionError: Si la réduction calculée diffère de expected.
    """
    assert percentage_discount_cents(subtotal_cents, discount_percent) == expected


def test_validate_quantity_valeur_normale():
    assert validate_quantity(5) == 5


def test_validate_quantity_valeur_negative():
    with pytest.raises(ValueError):
        validate_quantity(-5)


def test_validate_quantity_valeur_true():
    with pytest.raises(TypeError):
        validate_quantity(True)


def test_three_for_two_discount_cents():
    quantity = 3
    unit_price_cents = 100
    expected_discount = 100
    assert test_three_for_two_discount_cents(unit_price_cents, quantity) == expected_discount
