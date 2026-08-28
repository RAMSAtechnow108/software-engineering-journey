import asyncio
import httpx


async def send_order():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://127.0.0.1:8000/order/1",
            json={
                "items": [
                    {
                        "product_id": 1,
                        "quantity": 8
                    }
                ]
            }
        )

        return response


async def main():
    response_a, response_b = await asyncio.gather(
        send_order(),
        send_order()
    )

    print("Request A:", response_a.status_code)
    print("Request A:", response_a.json())
    print("Request B:", response_b.status_code)


if __name__ == "__main__":
    asyncio.run(main())