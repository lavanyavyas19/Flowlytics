import pandas as pd
import random
from datetime import datetime, timedelta

random.seed(42)

NUM_ROWS = 10000

products = {
    "Electronics": ["Laptop", "Mouse", "Keyboard", "Monitor", "Headphones"],
    "Furniture": ["Office Chair", "Desk", "Lamp"],
    "Education": ["Books", "Notebook"],
    "Accessories": ["Backpack", "Wallet"]
}

cities = ["Mumbai", "Pune", "Bangalore", "Delhi", "Hyderabad"]
payment_methods = ["UPI", "Card", "Cash"]

start_date = datetime(2024, 1, 1)

rows = []

for i in range(NUM_ROWS):
    category = random.choice(list(products.keys()))
    product = random.choice(products[category])

    quantity = random.choice([1, 2, 3, None])  # dirty nulls
    price = random.choice([500, 1200, 2500, 15000, 65000, None])  # dirty nulls

    row = {
        "transaction_id": f"TXN{100000+i if random.random() > 0.02 else 100010}",  # duplicates
        "transaction_date": (
            start_date + timedelta(days=random.randint(0, 90))
        ).strftime("%Y-%m-%d"),
        "customer_id": f"CUST{random.randint(1, 500)}",
        "product": product,
        "category": category,
        "quantity": quantity,
        "price": price,
        "payment_method": random.choice(payment_methods),
        "city": random.choice(cities)
    }

    rows.append(row)

df = pd.DataFrame(rows)

# Introduce dirty data
df.loc[random.sample(range(NUM_ROWS), 50), "transaction_date"] = "invalid_date"
df.loc[random.sample(range(NUM_ROWS), 50), "city"] = None

df.to_csv("transactions.csv", index=False)

print("transactions.csv generated with dirty data.")
