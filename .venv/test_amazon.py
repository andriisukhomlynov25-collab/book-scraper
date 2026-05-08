import re

def test_price_parser(price_text):
    print(f"Original text: '{price_text}'")
    
    # Шукаємо всі можливі ціни в тексті (наприклад, $5.98 - $12.00)
    # Цей регулярний вираз шукає числа з крапкою/комою або просто числа
    matches = re.findall(r'\d+[.,]\d+|\d+', price_text.replace(',', '.'))
    
    if matches:
        # Беремо першу знайдену ціну (щоб уникнути злипання $5.98 і $12.00 у 59812.00)
        first_price = matches[0]
        try:
            float_price = float(first_price)
            print(f"Parsed price: {float_price}\n")
            return float_price
        except ValueError:
            print("Failed to convert to float.\n")
            return None
    else:
        print("No numbers found.\n")
        return None

# Тестуємо різні варіанти, які можуть трапитися на Amazon
test_cases = [
    "$12.00",
    "Paperback $5.98 - $12.00",
    "US $19.95",
    "£18.95",
    "Get it for 5,99",
    "List Price: $19.99",
    "12"
]

for case in test_cases:
    test_price_parser(case)
