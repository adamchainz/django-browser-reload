from __future__ import annotations

from typing import Any

from django.http import HttpRequest, HttpResponse

BASKET = [
    {"name": "Teapot", "price": 25, "quantity": 1},
    {"name": "Teacup", "price": 8, "quantity": 4},
    # Oops, forgot the quantity!
    {"name": "Saucer", "price": 5},
]


def index(request: HttpRequest) -> HttpResponse:
    return HttpResponse(f"Basket total: £{basket_total(BASKET)}")


def basket_total(items: list[dict[str, Any]]) -> int:
    return sum(item["price"] * item["quantity"] for item in items)
