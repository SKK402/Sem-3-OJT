import asyncio
import random
from datetime import datetime, timedelta

from faker import Faker
from sqlalchemy import delete

from app.database import AsyncSessionLocal
from app.models import Product


fake = Faker()

CATEGORIES = ["shoes", "bags", "laptops", "accessories"]
COLORS = ["black", "white", "red", "blue", "green"]


async def seed_products(count: int = 200) -> None:
    async with AsyncSessionLocal() as session:
        await session.execute(delete(Product))
        await session.commit()

        products = []
        for _ in range(count):
            category = random.choice(CATEGORIES)
            color = random.choice(COLORS)
            name = f"{color.title()} {category.title()} {fake.word()}"
            description = fake.sentence()
            price_cents = random.randint(1000, 40000)
            searchable_text = f"{name} {description} {category} {color}"
            products.append(
                Product(
                    sku=fake.unique.bothify(text="SKU-#####"),
                    name=name,
                    description=description,
                    category=category,
                    color=color,
                    price_cents=price_cents,
                    currency="USD",
                    stock_qty=random.randint(0, 100),
                    searchable_text=searchable_text.lower(),
                    created_at=datetime.utcnow() - timedelta(days=random.randint(0, 30)),
                )
            )
        session.add_all(products)
        await session.commit()


def main() -> None:
    asyncio.run(seed_products())


if __name__ == "__main__":
    main()

