import uuid

def test_create_product_without_token_returns_401(client):
    
    response = client.post(
        "/products/",
        json={
            "name":"Security Test Products",
            "price":100,
            "category_id":1,
            "inventory":{
                "total_quantity":5
            }
        }
    )
    
    assert response.status_code == 401
    
    
def test_customer_cannot_create_product(client,customer_token):
    
    

    response = client.post(
        "/products/",
        headers={"Authorization": f"Bearer {customer_token}"},
        json={
            "name":"Customer Forbiden Product",
            "price":100,
            "category_id":1,
            "inventory":{"total_quantity":5}
        }
    )
    
    assert response.status_code==403
    
    
def test_admin_can_create_product(client,admin_token):
    
    
    category_response = client.post(
            "/categories/",
            headers={"Authorization":f"Bearer {admin_token}"},
            json={
                "name":f"Security Test Category {uuid.uuid4().hex[:8]}"
            }
        )
    
    assert category_response.status_code == 201,category_response.text
    category_id = category_response.json()["id"]


    response = client.post(
        "/products/",
        headers={"Authorization":f"Bearer {admin_token}"},
        json={
            "name":"Admin Created Security Product",
            "price":100,
            "category_id":category_id,
            "inventory":{"total_quantity":5}
        }
    )
    
    assert response.status_code == 201, response.text
    data = response.json()

    assert data["name"] == "Admin Created Security Product"
    
    
    
def test_customer_cannot_update_product(client,customer_token):

    response = client.post(
        "/products/",
        headers={"Authorization":f"Bearer {customer_token}"},
        json={"name":"Unauthorized Product Update"}
    )
    
    assert response.status_code == 403
    

def test_customer_cannot_delete_product(client,customer_token):

    response = client.delete(
        "/products/1",
        headers={"Authorization":f"Bearer {customer_token}"}
    )
    
    assert response.status_code == 403
    
    
def test_admin_can_update_product(client,admin_token):
    

    category_response = client.post(
        "/categories/",
        headers={"Authorization":f"Bearer {admin_token}"},
        json={"name":f"Update Test Category {uuid.uuid4().hex[:8]}"}
    )
    assert category_response.status_code == 201, category_response.text
    
    category_id = category_response.json()["id"]

    product_response = client.post(
        "/products/",
        headers={"Authorization":f"Bearer {admin_token}"},
        json={
            "name":f"Original Product {uuid.uuid4().hex[:8]}",
            "price":100,
            "category_id":category_id,
            "inventory":{"total_quantity":5}
        }
    )
    
    assert product_response.status_code == 201, product_response.text
    
    product_id = product_response.json()["id"]

    update_name = f"Updated Product {uuid.uuid4().hex[:8]}"
    update_response = client.patch(
        f"/products/{product_id}",
        headers={"Authorization":f"Bearer {admin_token}"},
        json={"name":update_name}
    )
    
    assert update_response.status_code == 200, update_response.text
    assert update_response.json()["name"] == update_name


def test_admin_can_delete_product(client,admin_token):
    

    category_response = client.post(
        "/categories/",
        headers={"Authorization":f"Bearer {admin_token}"},
        json={"name":f"Delete Test Category {uuid.uuid4().hex[:8]}"}
    )
    assert category_response.status_code == 201, category_response.text
    category_id = category_response.json()["id"]

    product_response = client.post(
        "/products/",
        headers={"Authorization":f"Bearer {admin_token}"},
        json={
            "name":f"Delete Test Product {uuid.uuid4().hex[:8]}",
            "price":100,
            "category_id":category_id,
            "inventory":{"total_quantity":5}
        }
    )
    
    assert product_response.status_code==201, product_response.text
    product_id = product_response.json()["id"]

    delete_response = client.delete(
        f"/products/{product_id}",
        headers={"Authorization":f"Bearer {admin_token}"}
    )
    
    assert delete_response.status_code ==200, delete_response.text
    assert delete_response.json()["success"] is True
    
    
def test_get_products_without_token_is_allowed(client):
    response = client.get("/products/")
    assert response.status_code == 200, response.text
    


def test_get_product_without_token_is_allowed(client, admin_token):
    import uuid


    # Create a category first.
    category_response = client.post(
        "/categories/",
        headers={"Authorization":f"Bearer {admin_token}"},
        json={"name": f"Public Details Category {uuid.uuid4().hex[:8]}"}
    )
    assert category_response.status_code == 201, category_response.text
    category_id = category_response.json()["id"]

    # Create a product as admin.
    product_response = client.post(
        "/products/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": f"Public Product {uuid.uuid4().hex[:8]}",
            "price": 150,
            "category_id": category_id,
            "inventory": {"total_quantity": 5}
        }
    )
    assert product_response.status_code == 201, product_response.text
    product_id = product_response.json()["id"]

    # Fetch product details without an authentication token.
    response = client.get(f"/products/{product_id}")

    assert response.status_code == 200, response.text
    assert response.json()["id"] == product_id
