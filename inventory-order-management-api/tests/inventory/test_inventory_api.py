import uuid


def create_product_with_inventory(client, admin_token):
    
    suffix = uuid.uuid4().hex[:8]
    category_response = client.post(
        "/categories/",
        headers = {"Authorization":f"Bearer {admin_token}"},
        json = {"name":f"Inventory Test Category {suffix}"}
    )
    
    assert category_response.status_code == 201, category_response.text
    
    category_id = category_response.json()["id"]

    product_response = client.post(
        "/products/",
        headers={"Authorization":f"bearer {admin_token}"},
        json={
            "name":f"Inventory Test Product {suffix}",
            "price":100,
            "category_id":category_id,
            "inventory":{"total_quantity":5}
        }
    )
    
    assert product_response.status_code==201,product_response.text
    
    return product_response.json()["id"]
    

def test_get_inventory_without_token(client):
    response = client.get("/inventory/1")
    assert response.status_code == 401
    

def test_update_inventory_without_token(client):
    response = client.patch(
        "/inventory/1",
        json={"total_quantity":15}
    )
    
    assert response.status_code==401
    
def test_get_inventory_with_customer_token(client,customer_token):
    response = client.get(
        "/inventory/1",
        headers={"Authorization":f"Bearer {customer_token}"}
    )
    assert response.status_code==403


def test_update_inventory_with_customer_token(client,customer_token):
    response = client.patch(
        "/inventory/1",
        headers={"Authorization":f"Bearer {customer_token}"},
        json={"total_quantity":15}
    )
    assert response.status_code == 403
    
    
def test_get_inventory_with_admin_token(client,admin_token):
    
    product_id = create_product_with_inventory(client,admin_token)
    response = client.get(
    f"/inventory/{product_id}",
        headers={"Authorization":f"Bearer {admin_token}"}
    )
    assert response.status_code == 200, response.text
    
    data = response.json()
    
    assert data["total_quantity"] == 5
    assert data["reserved_quantity"] == 0
    assert data["available_quantity"] == 5
    
    
def test_update_inventory_with_admin_token(client, admin_token):
    product_id = create_product_with_inventory(client, admin_token)

    response = client.patch(
        f"/inventory/{product_id}",
        headers = {"Authorization":f"Bearer {admin_token}"},
        json={"total_quantity":12}
    )
    
    assert response.status_code == 200, response.text
    
    data= response.json()

    assert data["total_quantity"]==12
    assert data["reserved_quantity"]==0
    assert data["available_quantity"]