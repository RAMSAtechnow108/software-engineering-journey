from app.models.category import Category


CATEGORY_SORT_FIELDS = {
    "id": Category.id,
    "name": Category.name
}

SORT_ORDER = {
    "asc",
    "desc"
}