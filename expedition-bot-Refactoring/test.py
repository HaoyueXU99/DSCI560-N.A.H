

import openai

def get_intent(user_question):
    openai.api_key = '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'  # Replace with your actual OpenAI API key

    # Constructing the prompt
    prompt = f"Please determine the main intent of the following user query: '{user_question}'. The intent should be a single word or a short phrase."

    try:
        # Making a request to OpenAI
        response = openai.Completion.create(
          engine="davinci-002",  # Assuming GPT-4 is the latest; replace with the appropriate engine
          prompt=prompt,
          max_tokens=50  # Adjust as necessary
        )

        return response.choices[0].text.strip().lower()
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Example usage
user_question = "I want to book a flight from New York to Paris next month."
intent = get_intent(user_question)
print(f"Identified Intent: {intent}")
