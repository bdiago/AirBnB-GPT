import time

import openai

# gets API Key from environment variable OPENAI_API_KEY
client = openai.OpenAI()

assistant = client.beta.assistants.retrieve("asst_PbagapHsH3kNBrGyweNAQfRs")

#thread = client.beta.threads.create()
thread = client.beta.threads.retrieve("thread_0Ln2C55tOBd1rHkxDRoRCKE5")
print(thread.id)

message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="How do guests contact you in case of any issues or emergencies during their stay?",
)

run = client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=assistant.id,
    instructions="Please address the user as Jane Doe. The user is staying at your airbnb.",
)

print("checking assistant status. ")
while True:
    run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

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
