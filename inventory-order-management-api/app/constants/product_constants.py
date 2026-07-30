from app.models.product import Product

PRODUCT_SORT_FIELDS = {
    "name": Product.name,
    "price": Product.price,
    "quantity": Product.quantity,
}

SORT_ORDER = {
    "asc",
    "desc"
}
