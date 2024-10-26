from huggingface_hub import InferenceClient

client = InferenceClient(api_key="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")

job = "Software Engineer at Google"

messages = [
	{ "role": "system", "content": f"""
You are a professional resume generator, specifically for this task you are generating the work experience description part of a resume for someone who is applying for a job.
Format what they did at their job with "*" as bulletpoints you are limited to only giving 3 bulletpoints.
You are generating it for {job}.
  """ }
]

stream = client.chat.completions.create(
    model="meta-llama/Llama-3.2-1B-Instruct", 
	messages=messages, 
	max_tokens=200,
    temperature=0,
	stream=True
)

output = ""
for chunk in stream:
    # print(chunk.choices[0].delta.content, end="")
    output += chunk.choices[0].delta.content

for line in output.split("\n"):
    if line.strip().startswith("**"):
        line.strip()
    elif line.strip().startswith("*"):
        print(line.strip())
