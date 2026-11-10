import uuid
from app.repositories.user_repository import UserRepository
from app.security.password import hash_password


def test_order_lifecycle_e2e(client,customer_token,admin_token):
    
    suffix = uuid.uuid4().hex[:8]
    
    category_response = client.post(
        "/categories/",
        headers={"Authorization":f"Bearer {admin_token}"},
        json={
            "name":f"E2E Category {suffix}"
        }
    )
    
    assert category_response.status_code == 201, category_response.text
    
    
    category_id = category_response.json()["id"]
    
    
    product_response = client.post(
        "/products/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": f"Test Product {uuid.uuid4().hex[:8]}",
            "price": 100,
            "category_id": category_id,
            "inventory": {
                "total_quantity": 5,
            },
        },
    )

    assert product_response.status_code == 201, product_response.text    
    product_id  = product_response.json()["id"]


    inventory_response = client.get(
        f"/inventory/{product_id}",
        headers={"Authorization":f"Bearer {admin_token}"}
        )

    assert inventory_response.status_code == 200, inventory_response.text
    
    inventory_data = inventory_response.json()

    assert inventory_data["total_quantity"]==5
    assert inventory_data["reserved_quantity"]==0
    assert inventory_data["available_quantity"]==5
    
    
    order_response = client.post(
        "/order/",
        headers={"Authorization": f"Bearer {customer_token}"},
        json={
            "items":[
                {
                    "product_id":product_id,
                    "quantity":2
                }
            ]
        }
    )
    
    assert order_response.status_code==201, order_response.text
    order_data = order_response.json()
    order_id = order_data["id"]

    assert order_data["status"]=="pending"
    assert order_data["items"][0]["product_id"] == product_id
    assert order_data["items"][0]["quantity"]==2
    
    
    inventory_response = client.get(
    f"/inventory/{product_id}",
    headers={"Authorization": f"Bearer {admin_token}"}
)

    assert inventory_response.status_code ==200, inventory_response.text
    
    inventory_data=  inventory_response.json()
    assert inventory_data["total_quantity"] == 5
    assert inventory_data["reserved_quantity"]==2
    assert inventory_data["available_quantity"] ==3
    
    
    confirm_response = client.patch(
        f"/order/{order_id}/status",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "status":"confirmed"
        }
    )
    
    assert confirm_response.status_code == 200, confirm_response.text
    
    confirm_response = confirm_response.json()
    assert confirm_response["id"] == order_id
    assert confirm_response["status"] =="confirmed"
    
    
    ship_response = client.patch(
        f"/order/{order_id}/status",
        headers= {"Authorization":f"Bearer {admin_token}"},
        json={"status":"shipped"}
    )
    
    assert ship_response.status_code == 200, ship_response.text
    
    shipped_order = ship_response.json()
    assert shipped_order["id"] == order_id
    assert shipped_order["status"]=="shipped"
    
    inventory_response = client.get(
    f"/inventory/{product_id}",
    headers={"Authorization": f"Bearer {admin_token}"}
)

    assert inventory_response.status_code == 200, inventory_response.text
    
    inventory_data = inventory_response.json()

    assert inventory_data["total_quantity"] == 3
    assert inventory_data["reserved_quantity"]==0
    assert inventory_data["available_quantity"]==3