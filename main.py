from huggingface_hub import InferenceClient

class RephraseLlama:
    def __init__(self):
        self.client = InferenceClient(api_key="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")

    def rephrase(self, text) -> str:
        rephrased = [text]

        print(f"Current Text: {text}")

        user_message = input()
        chat_history = []
        while user_message != "Good":
            
            # build the prompt
            messages = [
                { "role": "user", "content": f"Given this chat history: {chat_history if chat_history else "None"}, rephrase this message: {rephrased[-1]}. YOUR RESPONSE SHOULD ONLY BE THE REPHRASED VERSION AND NOTHING ELSE." }
            ]
            
            stream = self.client.chat.completions.create(
                model="meta-llama/Llama-3.2-1B-Instruct", 
                messages=messages, 
                max_tokens=250,
                stream=False
            )
            llama_message = stream.choices[0].message.content
            print(llama_message)

            # save message in chat history
            chat_history.append({"role": "user", "content":user_message})
            chat_history.append({"role": "assistant", "content": llama_message})

            print("'Good' 'save' 'forget'")
            user_message = input()
            while user_message == "save" or user_message == "undo":
                if user_message == 'save':
                    rephrased.append(llama_message)
                elif user_message == 'forget':
                    if len(rephrased) > 1:
                        rephrased.pop()
                        chat_history.pop()
                        chat_history.pop()
                user_message = input()

        return llama_message

# chatter = llama()
fields = ["Beginning and end time of working the job","Job description"]
rephraser = RephraseLlama()

end = rephraser.rephrase("You figure out information needed to complete a single part of a resume. Once you have the needed information you focus on rewriting that information")
print(end)