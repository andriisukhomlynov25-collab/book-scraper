import json
from openai import OpenAI

client = OpenAI(
  api_key="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"
)

prompt = "знайди 3 посилання на маркетплейси з книгою The Ukrainian Division 'Galicia', 1943-45. A Memoir / Wolf-Dietrich Heike / Toronto; Paris; Munich"

try:
    if hasattr(client, 'responses'):
        response = client.responses.create(
            model="gpt-4o", # or gpt-5.4-mini
            input=prompt,
        )
        print("Using responses.create:")
        print(response)
    else:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        print("Using chat.completions.create:")
        print(response.choices[0].message.content)
except Exception as e:
    print(f"Error: {e}")
