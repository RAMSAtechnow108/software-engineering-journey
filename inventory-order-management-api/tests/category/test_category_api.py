import uuid


def test_create_category_with_invalid_token(client):
    headers = {
        "Authorization": f"Bearer {uuid.uuid4().hex[:8]}"
    }

    response = client.post(
        "/categories/",
        headers=headers,
        json={"name": f"Invalid Category {uuid.uuid4().hex[:8]}"}
    )

    assert response.status_code == 401, response.text

def test_create_category_without_admin_token(client):
    
    category_response = client.post(
        "/categories/",
        json={"name":f"Test Category Creation{uuid.uuid4().hex[:10]}"}
    )

    assert category_response.status_code==401, category_response.text
    
def test_create_category_with_admin_token(client, admin_token):
    
    category_response = client.post(
        "/categories/",
        headers={"Authorization":f"Bearer {admin_token}"},
        json={"name":f"Test Admin Category {uuid.uuid4().hex[:8]}"}
    )
    
    assert category_response.status_code == 201, category_response.text
    
    
    
    
    
def test_create_category_with_customer_token(client,customer_token):
    category_response = client.post(
        "/categories/",
        headers={"Authorization":f"Bearer {customer_token}"},
        json={"name":f"Test Customer Category {uuid.uuid4().hex[:8]}"}
    )
    
    assert category_response.status_code == 403, category_response.text



    
def test_patch_category_with_admin_token(client, admin_token):
    headers={"Authorization":f"Bearer {admin_token}"}
    
    original_name = f"Test Category {uuid.uuid4().hex[:8]}"
    
    category_response = client.post(
        "/categories/",
        headers=headers,
        json={"name":original_name}
    )
    
    assert category_response.status_code == 201, category_response.text
    
    category_id = category_response.json()["id"]

    updated_name = f"Update Category {uuid.uuid4().hex[:8]}"
    
    response =client.patch(
        f"/categories/{category_id}",
        headers=headers,
        json={"name":updated_name}
    )
    
    assert response.status_code ==200, response.text
    
    updated_category = response.json()
    
    assert updated_category["id"] == category_id
    assert updated_category["name"] == updated_name
    assert updated_category ["name"] != original_name
    
    

def test_patch_category_with_customer_token(client, admin_token,customer_token):
    
    admin_headers = {"Authorization":f"Bearer {admin_token}"}
    customer_header = {"Authorization":f"Bearer {customer_token}"}
    original_name = f"Customer Category {uuid.uuid4().hex[:8]}"

    category_response = client.post(
        "/categories/",
        headers = admin_headers,
        json={"name":original_name}
    )
    
    assert category_response.status_code == 201, category_response.text
    category_id = category_response.json()["id"]
    
    
    updated_name = f"Updated Category {uuid.uuid4().hex[:8]}"
    
    resposne = client.patch(
        f"/categories/{category_id}",
        headers=customer_header,
        json = {"name":updated_name}
    )
    
    assert resposne.status_code == 403, resposne.text
    


def test_delete_category_without_token(client,admin_token):
    headers={"Authorization":f"Bearer {admin_token}"}
    
    category_response = client.post(
        "/categories/",
        headers=headers,
        json={"name":f"Test Category {uuid.uuid4().hex[:8]}"}
    )
    
    assert category_response.status_code == 201, category_response.text
    
    category_id = category_response.json()["id"]
    
    category_response = client.delete(
        f"/categories/{category_id}"
    )
    
    assert category_response.status_code== 401, category_response.text

def test_delete_category_with_customer_token(client,customer_token,admin_token):
    
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    customer_headers = {"Authorization": f"Bearer {customer_token}"}

    category_response = client.post(
        "/categories/",
        headers=admin_headers,
        json= {"name": f"Test Category {uuid.uuid4().hex[:8]}"}
    )
    
    assert category_response.status_code == 201, category_response.text
    category_id = category_response.json()["id"]

    response = client.delete(
        f"/categories/{category_id}",
        headers=customer_headers,
    )
    
    assert response.status_code == 403
    
    

def test_delete_category_with_admin_token(client,admin_token):
    
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    category_response = client.post(
        "/categories/",
        headers=admin_headers,
        json= {"name": f"Test Category {uuid.uuid4().hex[:8]}"}
    )
    
    assert category_response.status_code == 201, category_response.text
    category_id = category_response.json()["id"]

    response = client.delete(
        f"/categories/{category_id}",
        headers=admin_headers,
    )
    
    assert response.status_code == 200, response.text
    assert response.json()["success"] is True
    
    get_response = client.get(
        f"/categories/{category_id}",
        headers = admin_headers
    )
    
    assert get_response.status_code == 404, get_response.text
    
    
def test_getting_all_categories(client):
    category_response = client.get(
        "/categories/"
    )
    
    assert category_response.status_code == 200, category_response
    
def test_get_categories_by_id(client,admin_token):
    
        
    category_response = client.post(
        "/categories/",
        headers={"Authorization":f"Bearer {admin_token}"},
        json={"name":f"Test Admin Category {uuid.uuid4().hex[:8]}"}
    )
    
    assert category_response.status_code == 201, category_response.text
    category_id = category_response.json()["id"]

    category_response = client.get(
        f"/categories/{category_id}",
        
    )
    
    assert category_response.status_code == 200, category_response.text
    assert category_response.json()["id"] == category_id