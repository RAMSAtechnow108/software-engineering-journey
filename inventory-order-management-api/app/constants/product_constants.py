from app.models.product import Product

PRODUCT_SORT_FIELDS = {
    "name": Product.name,
    "price": Product.price
}

SORT_ORDER = {
    "asc",
    "desc"
}
