import time

import openai

# gets API Key from environment variable OPENAI_API_KEY
client = openai.OpenAI()

# assistant = client.beta.assistants.retrieve("asst_4rjUSv6okbrDVxECAfhtTE9f")

# Upload a file with an "assistants" purpose
file = client.files.create(
  file=open("OG/qna.txt", "rb"),
  purpose='assistants'
)

# Create an assistant using the file ID
assistant = client.beta.assistants.create(
  instructions="you are a virtual airbnb assistant that helps guests with questions about the property in which they are staying_.",
  model="gpt-3.5-turbo-1106",
  tools=[{"type": "retrieval"}],
  file_ids=[file.id]
)

print("new assistant: " + assistant.id)

thread = client.beta.threads.create()
#thread = client.beta.threads.retrieve("thread_TJl0zb0zY4CqAU4DhXuPHcN2")
print(thread.id)



message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="Are there any outdoor amenities such as a grill or patio furniture available for use?",
)

run = client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=assistant.id,
    instructions="Please address the user as Jane Doe. The user is staying at your airbnb.",
)

print("checking assistant status. ")
while True:
    run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
    # run = client.beta.threads.runs.retrieve(thread_id="thread_0Ln2C55tOBd1rHkxDRoRCKE5", run_id="run_kLNRJ9KdpBNsox1Dq9JjH1eT")

    if run.status == "completed":
        print("done!")
        messages = client.beta.threads.messages.list(thread_id=thread.id)

        print("messages: ")
        for message in messages:
            assert message.content[0].type == "text"
            print({"role": message.role, "message": message.content[0].text.value})

        # client.beta.assistants.delete(assistant.id)

        break
    else:
        print("in progress...")
        time.sleep(5)


# def main():
#     print("Welcome to the OpenAI Assistant!")

#     while True:
#         user_input = input("You: ")
#         if user_input.lower() in ['exit', 'quit']:
#             print("Goodbye!")
#             break
        
#         # Call the assistant function with user input
#         response = ask_assistant(user_input)

#         # Print the assistant's response
#         print("Assistant:", response)

# if __name__ == "__main__":
#     main()