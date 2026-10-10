from app.security.password import hash_password
from app.models.user import User
from app.constants.user_constants import UserRole
from app.repositories.user_repository import UserRepository

from app.repositories.inventory_repository import InventoryRepository




def test_customer_cannot_update_order_status(client):
    # Register a fresh customer
    registration_response = client.post(
        "/users/register",
        json={
            "name": "Order Auth Customer",
            "email": "orderauth@example.com",
            "phone": "9000000099",
            "password": "StrongPass123"
        }
    )

    assert registration_response.status_code == 201

    # Login with the newly registered customer
    login_response = client.post(
        "/auth/login",
        json={
            "email": "orderauth@example.com",
            "password": "StrongPass123"
        }
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    
    category_response = client.post(
        "/categories/",
        json={
            "name":"Electronics"
        }
    )
    
    assert category_response.status_code == 201
    
    category_id = category_response.json()["id"]

    product_response = client.post(
        "/products/",
        json={
            "name":"Keyboard",
            "price":1200,
            "category_id":category_id,
            "inventory":{
                "total_quantity":30
            }
        }
    )
    
    assert product_response.status_code == 201
    
    product_id = product_response.json()["id"]
    
    order_create = client.post(
        "/order/",
        headers={
            "Authorization":f"Bearer {token}"
        },
        json={
            "items":[
                {
                    "product_id":product_id,
                    "quantity":1
                }
            ]
        }
    )
    
    
    assert order_create.status_code == 201, order_create.text

    order_id = order_create.json()["id"]

    # Customer tries to update an order status
    
    response = client.patch(
        f"/order/{order_id}/status",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "status": "confirmed"
        }
    )

    assert response.status_code == 403

    assert response.json()["detail"] == "Only admin can update order status"
    
    

    
def test_admin_can_update_order_status(client,db):
    
    email = "admin@example.com"
    password = "AdminPass123"
    
    user_repository = UserRepository(db)
    admin = user_repository.get_user_by_email(email)
    
    if admin is None:
        admin = user_repository.create_admin_user(email=email, password_hash=hash_password(password))

    else:
        admin.password_hash = hash_password(password)
        admin.role = UserRole.ADMIN
        admin.is_active=True
        
    db.commit()
    
    login_response = client.post(
        "/auth/login",
        json={"email":email, "password":password},
    )
    
    assert login_response.status_code == 200 , login_response.text
    token = login_response.json()["access_token"]

    # Create a category
    category_response = client.post(
        "/categories/",
        json={"name": "Admin Test Electronics"},
    )
    assert category_response.status_code == 201, category_response.text
    category_id = category_response.json()["id"]

    # Create a product
    product_response = client.post(
        "/products/",
        json={
            "name": "Admin Test Keyboard",
            "price": 1200,
            "category_id": category_id,
            "inventory": {"total_quantity": 30},
        },
    )
    assert product_response.status_code == 201, product_response.text
    product_id = product_response.json()["id"]

    # Register a customer who will own this order
    registration_response = client.post(
        "/users/register",
        json={
            "name": "Admin Order Customer",
            "email": "admin-order-customer@example.com",
            "phone": "9000000088",
            "password": "StrongPass123",
        },
    )
    assert registration_response.status_code == 201, registration_response.text

    # Login as that customer to create an order
    customer_login = client.post(
        "/auth/login",
        json={
            "email": "admin-order-customer@example.com",
            "password": "StrongPass123",
        },
    )
    assert customer_login.status_code == 200, customer_login.text
    customer_token = customer_login.json()["access_token"]

    order_response = client.post(
        "/order/",
        headers={"Authorization": f"Bearer {customer_token}"},
        json={
            "items": [
                {"product_id": product_id, "quantity": 1}
            ]
        },
    )
    assert order_response.status_code == 201, order_response.text
    order_id = order_response.json()["id"]

    # Admin updates the newly created order
    response = client.patch(
        f"/order/{order_id}/status",
        headers={"Authorization": f"Bearer {token}"},
        json={"status": "confirmed"},
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["id"] == order_id
    assert data["status"] == "confirmed"




def test_customer_cannot_cancel_another_customers_order(client):
    # Register Customer A
    customer_a_registration = client.post(
        "/users/register",
        json={
            "name": "Customer A",
            "email": "customer-a-cancel@example.com",
            "phone": "9000000071",
            "password": "StrongPass123",
        },
    )
    assert customer_a_registration.status_code == 201, customer_a_registration.text

    # Register Customer B
    customer_b_registration = client.post(
        "/users/register",
        json={
            "name": "Customer B",
            "email": "customer-b-cancel@example.com",
            "phone": "9000000072",
            "password": "StrongPass123",
        },
    )
    assert customer_b_registration.status_code == 201, customer_b_registration.text

    # Login Customer A
    customer_a_login = client.post(
        "/auth/login",
        json={
            "email": "customer-a-cancel@example.com",
            "password": "StrongPass123",
        },
    )
    assert customer_a_login.status_code == 200, customer_a_login.text
    customer_a_token = customer_a_login.json()["access_token"]

    # Login Customer B
    customer_b_login = client.post(
        "/auth/login",
        json={
            "email": "customer-b-cancel@example.com",
            "password": "StrongPass123",
        },
    )
    assert customer_b_login.status_code == 200, customer_b_login.text
    customer_b_token = customer_b_login.json()["access_token"]

    # Create category
    category_response = client.post(
        "/categories/",
        json={"name": "Ownership Test Category"},
    )
    assert category_response.status_code == 201, category_response.text
    category_id = category_response.json()["id"]

    # Create product with inventory
    product_response = client.post(
        "/products/",
        json={
            "name": "Ownership Test Product",
            "price": 500,
            "category_id": category_id,
            "inventory": {"total_quantity": 20},
        },
    )
    assert product_response.status_code == 201, product_response.text
    product_id = product_response.json()["id"]

    # Customer B creates an order
    order_response = client.post(
        "/order/",
        headers={"Authorization": f"Bearer {customer_b_token}"},
        json={
            "items": [{"product_id": product_id, "quantity": 1}]
        },
    )
    assert order_response.status_code == 201, order_response.text
    order_id = order_response.json()["id"]

    # Customer A attempts to cancel Customer B's order
    cancel_response = client.patch(
        f"/order/{order_id}/cancel",
        headers={"Authorization": f"Bearer {customer_a_token}"},
    )

    assert cancel_response.status_code == 403, cancel_response.text


def test_customer_can_cancel_own_order(client,db):
    # Register customer
    customer_registration = client.post(
        "/users/register",
        json={
            "name": "Customer Own Cancel",
            "email": "customer-own-cancel-202610@example.com",
            "phone": "9000000723",
            "password": "StrongPass123",
        },
    )
    assert customer_registration.status_code == 201, customer_registration.text

    # Login customer
    customer_login = client.post(
        "/auth/login",
        json={
            "email": "customer-own-cancel-202610@example.com",
            "password": "StrongPass123",
        },
    )
    assert customer_login.status_code == 200, customer_login.text
    token = customer_login.json()["access_token"]

    # Create unique category
    category_response = client.post(
        "/categories/",
        json={"name": "Own Cancel Category 202610"},
    )
    assert category_response.status_code == 201, category_response.text
    category_id = category_response.json()["id"]

    # Create unique product with inventory
    product_response = client.post(
        "/products/",
        json={
            "name": "Own Cancel Product 202610",
            "price": 500,
            "category_id": category_id,
            "inventory": {"total_quantity": 20},
        },
    )
    assert product_response.status_code == 201, product_response.text
    product_id = product_response.json()["id"]

    # Create order
    order_response = client.post(
        "/order/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "items": [
                {"product_id": product_id, "quantity": 1}
            ]
        },
    )
    assert order_response.status_code == 201, order_response.text
    order_id = order_response.json()["id"]
    
    inventory_repository = InventoryRepository(db)

    inventory_before = inventory_repository.get_inventory_by_product_id(
        product_id
    )

    reserved_before = inventory_before.reserved_quantity
    total_before = inventory_before.total_quantity

    # Customer cancels own order
    cancel_response = client.patch(
        f"/order/{order_id}/cancel",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert cancel_response.status_code == 200, cancel_response.text
    assert cancel_response.json()["status"].lower() == "cancelled"

    inventory_after = inventory_repository.get_inventory_by_product_id(
    product_id
)

    assert inventory_after.reserved_quantity == reserved_before - 1
    assert inventory_after.total_quantity == total_before



def test_customer_cannot_cancel_order_twice(client,db):
    # Register customer
    customer_registration = client.post(
        "/users/register",
        json={
            "name": "Customer Double Cancel",
            "email": "customer-double-cancel-202610@example.com",
            "phone": "9000000724",
            "password": "StrongPass123",
        },
    )
    assert customer_registration.status_code == 201, customer_registration.text

    # Login customer
    customer_login = client.post(
        "/auth/login",
        json={
            "email": "customer-double-cancel-202610@example.com",
            "password": "StrongPass123",
        },
    )
    assert customer_login.status_code == 200, customer_login.text
    token = customer_login.json()["access_token"]

    # Create unique category
    category_response = client.post(
        "/categories/",
        json={"name": "Double Cancel Category 202610"},
    )
    assert category_response.status_code == 201, category_response.text
    category_id = category_response.json()["id"]

    # Create unique product with inventory
    product_response = client.post(
        "/products/",
        json={
            "name": "Double Cancel Product 202610",
            "price": 500,
            "category_id": category_id,
            "inventory": {"total_quantity": 20},
        },
    )
    assert product_response.status_code == 201, product_response.text
    product_id = product_response.json()["id"]

    # Create order
    order_response = client.post(
        "/order/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "items": [
                {"product_id": product_id, "quantity": 1}
            ]
        },
    )
    assert order_response.status_code == 201, order_response.text
    order_id = order_response.json()["id"]

    # First cancellation should succeed
    first_response = client.patch(
        f"/order/{order_id}/cancel",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert first_response.status_code == 200, first_response.text
    assert first_response.json()["status"].lower() == "cancelled"
    
    
    
    inventory_repository = InventoryRepository(db)

    inventory_after_first = (
        inventory_repository.get_inventory_by_product_id(product_id)
    )

    reserved_after_first = inventory_after_first.reserved_quantity
    total_after_first = inventory_after_first.total_quantity


    # Second cancellation should be rejected
    second_response = client.patch(
        f"/order/{order_id}/cancel",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert second_response.status_code == 409, second_response.text
    assert (
        second_response.json()["error_code"]
        == "INVALID_ORDER_STATUS_TRANSITION"
    )

    
    inventory_after_second = (
        inventory_repository.get_inventory_by_product_id(product_id)
    )

    assert (
        inventory_after_second.reserved_quantity
        == reserved_after_first
    )
    assert (
        inventory_after_second.total_quantity
        == total_after_first
    )
