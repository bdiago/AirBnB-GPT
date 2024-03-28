import time
import openai
import streamlit as st
from function_tools import check_for_qa_number, find_files_in_dir

class VirtualAssistant:
    # def __init__(self, corpus, character_name, chatbot_type, retrieval_docs, summary_type):
    def __init__(self):
        # self.corpus = corpus
        # self.character_name = character_name
        # self.chatbot_type = chatbot_type
        # self.retrieval_docs = retrieval_docs
        # self.summary_type = summary_type
        self.filepaths = []
        openai.api_key = st.secrets["OPENAI_API_KEY"]
        self.client = openai.OpenAI()
        file = self.client.files.create(
            file=open("OG/qna.txt", "rb"),
            purpose='assistants'
        )
        self.assistant = self.client.beta.assistants.create(
            instructions="you are a virtual airbnb assistant that helps guests with questions about the property in which they are staying. please stay in character and answer the user's questions as if you were an airbnb host.",
            model="gpt-3.5-turbo-1106",
            tools=[{"type": "retrieval"}],
            file_ids=[file.id]
        )
        self.thread = self.client.beta.threads.create()

    def chatbot(self, input):
        message = self.client.beta.threads.messages.create(
            thread_id=self.thread.id,
            role="user",
            content = input,
        )
        run = self.client.beta.threads.runs.create(
            thread_id=self.thread.id,
            assistant_id=self.assistant.id,
            instructions="Please address the user as Jane Doe. The user is staying at your airbnb.",
        )
        while True:
            run = self.client.beta.threads.runs.retrieve(thread_id=self.thread.id, run_id=run.id)
            if run.status == "completed":
                messages = self.client.beta.threads.messages.list(thread_id=self.thread.id)
        
                for message in reversed(messages.data):
                    assert message.content[0].type == "text"
                    if message.role == "assistant":
                        response = message.content[0].text.value
                        print({"role": message.role, "message": message.content[0].text.value})
                # self.client.beta.assistants.delete(self.assistant.id)
                break
            else:
                time.sleep(3)
        return response

    def greet(self):    
        return "hello! I am your virtual assistant. How can I help you today?"

    def step(self, input):
        number = check_for_qa_number(input)
        if number > 0:
            
            self.filepaths = find_files_in_dir(number, '/Users/Shared/Youtube/AirBnB-GPT/pictures')
            print(self.filepaths)
            print("qna number found")
            
        return self.chatbot(input)




# def main():
#     assistant = VirtualAssistant()
    
#     print(assistant.greet())
    

#     while True:
#         user_input = input("You: ")
#         if user_input.lower() in ['exit', 'quit']:
#             print("Goodbye!")
#             break
        
#         # Call the assistant function with user input
#         response = assistant.step(user_input)

#         # Print the assistant's response
#         print("Assistant:", response)

# if __name__ == "__main__":
#     main()