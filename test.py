from openai import OpenAI

client = OpenAI(
    api_key="sk-1uKqG1fndfUGDjx15480AdF4D79140B3819dAeF8B0Bc6c6e",
    base_url="https://api.laozhang.ai/v1"
)

completion = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "user", "content": "hello"}
    ]
)
print(completion.choices[0].message)