"""Moteur de caisse pédagogique inspiré du Supermarket Receipt Kata d'Emily Bache.

Les contrats décrivent le comportement attendu, pas une garantie de correction du starter.
Voir docs/contrat.md et THIRD_PARTY_NOTICES.md. Aucun stockage ni appel réseau.
"""

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class Product:
    """Décrire un produit immuable du catalogue fourni par l'enseignant.

    Aucun effet de bord ; ces valeurs internes ne sont jamais fournies par le client HTTP.

    Attributes:
        product_id: Identifiant exact du produit.
        name: Nom du produit.
        unit: Unité de vente, "piece" ou "gram".
        unit_price_cents: Prix en centimes par pièce ou kilogramme.
        promotion: Offre "none", "percentage" ou "three_for_two".
        discount_percent: Pourcentage entier de 0 à 100, nul par défaut.
    """

    product_id: str
    name: str
    unit: str
    unit_price_cents: int
    promotion: str
    discount_percent: int = 0


CATALOG = {
    "toothbrush": Product("toothbrush", "Brosse à dents", "piece", 99, "three_for_two"),
    "apples": Product("apples", "Pommes", "gram", 199, "percentage", 20),
    "rice": Product("rice", "Sac de riz", "piece", 249, "percentage", 10),
    "milk": Product("milk", "Brique de lait", "piece", 100, "none"),
}


def validate_quantity(quantity: int) -> int:
    """Valider une quantité entière strictement positive, sans conversion.

    Args:
        quantity: Nombre de pièces ou grammes, strictement positif et hors booléen.

    Returns:
        La quantité fournie, sans modification.

    Raises:
        TypeError: Si quantity n'est pas un entier ou est un booléen.
        ValueError: Si quantity est inférieure ou égale à zéro.
    """
    if type(quantity) is not int:
        raise TypeError("quantity doit être un entier de pièces ou grammes, hors booléen.")
    if quantity <= 0:
        raise ValueError("quantity doit être strictement supérieur à 0.")
    return quantity


def round_half_up(numerator: int, denominator: int) -> int:
    """Arrondir un rapport positif au plus proche, avec le demi vers le haut.

    Args:
        numerator: Numérateur positif ou nul, hors booléen.
        denominator: Dénominateur strictement positif, hors booléen.

    Returns:
        Rapport arrondi au plus proche, avec le demi vers le haut.

    Raises:
        TypeError: Si un argument n'est pas un entier ou est un booléen.
        ValueError: Si numerator est négatif ou denominator est inférieur ou égal à zéro.
    """
    if type(numerator) is not int:
        raise TypeError("numerator doit être un entier positif ou nul, hors booléen.")
    if type(denominator) is not int:
        raise TypeError("denominator doit être un entier strictement positif, hors booléen.")
    if numerator < 0:
        raise ValueError("numerator doit être supérieur ou égal à 0.")
    if denominator <= 0:
        raise ValueError("denominator doit être strictement supérieur à 0.")
    return (2 * numerator + denominator) // (2 * denominator)


def get_product(product_id: str) -> Product:
    """Chercher un produit par son identifiant exact, sans alias ni normalisation.

    Args:
        product_id: Identifiant parmi "toothbrush", "apples", "rice" ou "milk".

    Returns:
        Produit immuable correspondant à l'identifiant.

    Raises:
        TypeError: Si product_id n'est pas une chaîne.
        ValueError: Si product_id est absent du catalogue.
    """
    if type(product_id) is not str:
        raise TypeError("product_id doit être une chaîne du catalogue.")
    if product_id not in CATALOG:
        raise ValueError(
            f"product_id inconnu : {product_id!r} ; attendu : toothbrush, apples, rice ou milk."
        )
    return CATALOG[product_id]


def aggregate_items(items: list[dict[str, object]]) -> list[dict[str, object]]:
    """Valider puis regrouper les doublons en conservant l'ordre de première apparition.

    Args:
        items: Liste, éventuellement vide, de dictionnaires contenant exactement
            "product_id" et "quantity".

    Returns:
        Nouvelle liste avec une entrée par produit et les quantités cumulées.

    Raises:
        TypeError: Si la liste, un dictionnaire ou un champ a un type invalide.
        KeyError: Si un champ obligatoire manque.
        ValueError: Si un champ supplémentaire est présent, un identifiant est inconnu
            ou une quantité est inférieure ou égale à zéro.
    """
    if type(items) is not list:
        raise TypeError("items doit être une liste d'objets product_id et quantity.")
    quantities: dict[str, int] = {}
    for item in items:
        if type(item) is not dict:
            raise TypeError("Chaque élément de items doit être un objet product_id et quantity.")
        for field in ("product_id", "quantity"):
            if field not in item:
                raise KeyError(f"items : champ obligatoire {field!r} manquant.")
        if set(item) != {"product_id", "quantity"}:
            raise ValueError("items : seuls les champs product_id et quantity sont attendus.")
        product = get_product(item["product_id"])
        quantity = validate_quantity(item["quantity"])
        quantities[product.product_id] = quantities.get(product.product_id, 0) + quantity
    return [
        {"product_id": product_id, "quantity": quantity}
        for product_id, quantity in quantities.items()
    ]


def line_subtotal_cents(unit_price_cents: int, quantity: int, unit: str) -> int:
    """Calculer le brut d'une ligne avant réduction, en centimes entiers.

    Les quantités doivent être agrégées avant cet appel.

    Args:
        unit_price_cents: Prix positif ou nul en centimes par pièce ou kilogramme.
        quantity: Quantité strictement positive en pièces ou grammes.
        unit: Unité "piece" ou "gram". Pour "gram", le prix est par kilogramme.

    Returns:
        Montant brut arrondi au centime, avec le demi vers le haut.

    Raises:
        TypeError: Si un argument a un type invalide.
        ValueError: Si le prix est négatif, la quantité invalide ou l'unité inconnue.
    """
    if type(unit_price_cents) is not int:
        raise TypeError("unit_price_cents doit être un entier en centimes, hors booléen.")
    if unit_price_cents < 0:
        raise ValueError("unit_price_cents doit être supérieur ou égal à 0.")
    validate_quantity(quantity)
    if type(unit) is not str:
        raise TypeError("unit doit être une chaîne : piece ou gram.")
    if unit not in {"piece", "gram"}:
        raise ValueError("unit doit être piece ou gram ; le prix au poids est par kilogramme.")
    denominator = 1000 if unit == "gram" else 1
    return round_half_up(unit_price_cents * quantity, denominator)


def three_for_two_discount_cents(unit_price_cents: int, quantity: int) -> int:
    """Calculer la réduction pour une pièce offerte par groupe complet de trois.

    Les pièces restantes sont payées au prix normal. La promotion démarre dès trois
    pièces. Aucun effet de bord.

    Args:
        unit_price_cents: Prix par pièce en centimes, positif ou nul.
        quantity: Nombre de pièces strictement positif.

    Returns:
        Réduction totale en centimes.

    Raises:
        TypeError: Si un argument n'est pas un entier ou est un booléen.
        ValueError: Si le prix est négatif ou la quantité n'est pas strictement positive.
    """
    line_subtotal_cents(unit_price_cents, quantity, "piece")
    return (quantity // 3) * unit_price_cents


def percentage_discount_cents(subtotal_cents: int, discount_percent: int) -> int:
    """Calculer la réduction, et non le montant net, pour un pourcentage entier.

    La réduction porte sur le brut de ligne déjà arrondi.

    Args:
        subtotal_cents: Montant brut positif ou nul en centimes.
        discount_percent: Pourcentage de réduction de 0 à 100 inclus.

    Returns:
        Réduction en centimes arrondie au plus proche, avec le demi vers le haut.

    Raises:
        TypeError: Si un argument n'est pas un entier ou est un booléen.
        ValueError: Si le brut est négatif ou le pourcentage est hors de l'intervalle 0–100.
    """
    if type(subtotal_cents) is not int:
        raise TypeError("subtotal_cents doit être un entier en centimes, hors booléen.")
    if type(discount_percent) is not int:
        raise TypeError("discount_percent doit être un entier, hors booléen.")
    if subtotal_cents < 0:
        raise ValueError("subtotal_cents doit être supérieur ou égal à 0.")
    if not 0 <= discount_percent <= 100:
        raise ValueError("discount_percent doit être compris entre 0 et 100 inclus.")
    return round(Fraction(subtotal_cents * discount_percent, 100))


def line_discount_cents(product_id: str, quantity: int) -> int:
    """Choisir la seule promotion configurée pour un produit du catalogue.

    Les promotions ne se cumulent pas.

    Args:
        product_id: Identifiant exact d'un produit du catalogue.
        quantity: Quantité strictement positive.

    Returns:
        Réduction en centimes, ou zéro si le produit n'a pas de promotion.

    Raises:
        TypeError: Si un argument a un type invalide.
        ValueError: Si une valeur ne respecte pas le contrat.
    """
    product = get_product(product_id)
    subtotal = line_subtotal_cents(product.unit_price_cents, quantity, product.unit)
    if product.promotion == "three_for_two":
        return three_for_two_discount_cents(product.unit_price_cents, quantity)
    if product.promotion == "percentage":
        return percentage_discount_cents(subtotal, product.discount_percent)
    if product.promotion == "none":
        return 0
    raise ValueError("promotion doit être none, percentage ou three_for_two.")


def build_receipt_line(product_id: str, quantity: int) -> dict[str, object]:
    """Construire une ligne de ticket pour une quantité déjà agrégée.

    Le total vaut le brut moins la réduction, sans nouvel arrondi.

    Args:
        product_id: Identifiant exact d'un produit du catalogue.
        quantity: Quantité agrégée strictement positive.

    Returns:
        Ligne contenant l'identité du produit et ses montants en centimes.

    Raises:
        TypeError: Si un argument a un type invalide.
        ValueError: Si une valeur ne respecte pas le contrat.
    """
    product = get_product(product_id)
    subtotal = line_subtotal_cents(product.unit_price_cents, quantity, product.unit)
    discount = line_discount_cents(product_id, quantity)
    return {
        "product_id": product.product_id,
        "name": product.name,
        "quantity": quantity,
        "unit": product.unit,
        "unit_price_cents": product.unit_price_cents,
        "subtotal_cents": subtotal,
        "discount_cents": discount,
        "total_cents": subtotal - discount,
    }


def checkout(items: list[dict[str, object]]) -> dict[str, object]:
    """Produire le ticket complet, après validation et agrégation du panier.

    Les totaux sont obtenus par somme des lignes, sans arrondi supplémentaire.

    Args:
        items: Panier au format décrit par aggregate_items. La liste peut être vide.

    Returns:
        Ticket avec les lignes, le sous-total, la réduction et le total en centimes.

    Raises:
        TypeError: Si le panier ou un de ses champs a un type invalide.
        KeyError: Si un champ obligatoire manque.
        ValueError: Si un champ supplémentaire ou une valeur hors contrat est présent.
    """
    lines = [
        build_receipt_line(item["product_id"], item["quantity"]) for item in aggregate_items(items)
    ]
    return {
        "lines": lines,
        "subtotal_cents": sum(line["subtotal_cents"] for line in lines),
        "discount_cents": sum(line["discount_cents"] for line in lines),
        "total_cents": sum(line["total_cents"] for line in lines),
    }
