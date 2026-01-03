import pandas as pd
from faker import Faker
import random

fake = Faker(['de_DE', 'nl_NL', 'fr_FR', 'en_GB'])
Faker.seed(42)

def generate_data(num_rows=50):
    data = []
    countries = ['DE', 'NL', 'FR', 'GB', 'IT', 'ES']
    
    for _ in range(num_rows):
        country = random.choice(countries)
        # Faker can generate IBANs for specific countries
        iban = fake.iban()
        
        # Vary amount formats
        amt_type = random.choice(['comma', 'dot', 'int', 'space'])
        base_val = random.uniform(1, 2000)
        
        if amt_type == 'comma':
            amount = f"{base_val:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        elif amt_type == 'dot':
            amount = f"{base_val:,.2f}"
        elif amt_type == 'int':
            amount = str(int(base_val))
        else:
            amount = f"{int(base_val)} €"

        data.append({
            "Recipient": fake.name(),
            "IBAN": iban,
            "BIC": "", # Leave empty to test auto-derivation
            "Amount": amount,
            "Purpose": fake.sentence(nb_words=4)
        })
    
    return pd.DataFrame(data)

if __name__ == "__main__":
    df = generate_data()
    output = "international_test_data.xlsx"
    df.to_excel(output, index=False)
    print(f"Generated {len(df)} rows of test data in {output}")
