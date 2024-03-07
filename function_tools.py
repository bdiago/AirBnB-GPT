import json
import openai
import requests
import streamlit as st
import pandas as pd
import time
import random
from tenacity import retry, wait_random_exponential, stop_after_attempt
from streamlit_extras.let_it_rain import rain


GPT_MODEL = "gpt-3.5-turbo-0613"

@retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(3))
def chat_completion_request(messages, tools=None, tool_choice=None, model=GPT_MODEL):
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + openai.api_key,
    }
    json_data = {"model": model, "messages": messages}
    if tools is not None:
        json_data.update({"tools": tools})
    if tool_choice is not None:
        json_data.update({"tool_choice": tool_choice})
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=json_data,
        )
        return response
    except Exception as e:
        print("Unable to generate ChatCompletion response")
        print(f"Exception: {e}")
        return e

tools = [
    {
        "type": "function",
        "function": {
            "name": "check_for_resume_inquiry",
            "description": "check if the user input is for the intent of seeing your resume.",
            "parameters": {
                "type": "object",
                "properties": {
                    "result": {
                        "type": "boolean",
                        "description": "the true or false result"
                    }
                },
                 "required": ["result"],
            },
        }
    }
]

def read_resume():
        with open("data/resume.txt") as f:
            resume = f.read()
        return resume 

def strip_resume(resume_doc):

    try:
        # Find the text after "RESUME:"
        start = resume_doc.index("RESUME:") + len("RESUME:")
        # Find the text before "PERSONAL INFO:"
        end = resume_doc.index("PERSONAL INFO:", start)
        # Extract the text between "RESUME:" and "PERSONAL INFO:"
        resume_info = resume_doc[start:end].strip()
        return resume_info
        
    except ValueError:
        resume_info = "The text does not contain 'RESUME:' or 'PERSONAL INFO:'"
        return resume_info
    
def standardize_resume_response(resume_info):
    
    return "Sure! here you go: \n\n {} \n\nLet me know if there anything specific you would like to know or discuss!".format(resume_info)


def check_for_resume(input):
    resume_doc = read_resume()
    resume_info = strip_resume(resume_doc)

    messages = []
    #need to inset 
    messages.append({"role": "system", "content": """You are engaging in dialog with a human.
you tasked with understanding if the intent of their turn in the conversation is to see your resume. use this definition of what an intent is for your bases: "An intent categorizes an end-user's intention for one conversation turn."

Below are 20 examples phrases of asking to see your resume:
                     
1. Is there a grocery store nearby, and if so, how far is it from the house?
-Yes, there's a supermarket called FreshMart just a 5-minute drive away.

2. Do you need a code to access the Wi-Fi network, and if yes, what is it?
-Yes, the Wi-Fi password is "Guest1234".

3. Are there any specific instructions for using the thermostat or controlling the heating/cooling?
-Simply adjust the thermostat using the buttons on the panel. Heat is controlled with the up arrow, and cool with the down arrow.

4.Where can guests find extra blankets or pillows if needed?
-Extra blankets and pillows are stored in the closet in the master bedroom.

5. Is there a designated area for recycling, and if so, where is it located?
-Yes, the recycling bins are located in the garage next to the trash cans.

6.Are there any outdoor amenities such as a grill or patio furniture available for use?
-Yes, there's a charcoal grill and a set of patio furniture in the backyard.

7.Do you have any recommendations for local attractions or activities in the area?
-You might enjoy visiting the nearby Smith Park for hiking trails and picnics.

8.Are there any restrictions on noise levels or quiet hours in the neighborhood?
-Please keep noise to a minimum after 10 PM to respect our neighbors.

9. Is there a coffee maker available in the house, and if yes, what type (drip, Keurig, etc.)?
-Yes, there's a drip coffee maker in the kitchen cupboard along with filters.

10. How do guests dispose of trash during their stay?
-Trash can be placed in the bin outside the house. Trash pickup is on Mondays.

11. Are there any safety precautions guests should be aware of while staying at the house?
-Please ensure all doors and windows are locked when leaving the house and be cautious when using the fireplace.

12.Is there a designated parking spot for guests, and if yes, where is it located?
-Yes, there's a designated parking spot in the driveway for one car. Additional parking is available on the street.

13.Are pets allowed in the house, and if so, are there any specific rules or guidelines?
-Sorry, pets are not allowed in the house due to allergies.

14.Where can guests find the nearest public transportation options?
-The nearest bus stop is just a 10-minute walk down the street.

15.Are there any entertainment options available in the house, such as board games or streaming services?
-Yes, we have a selection of board games in the living room cabinet and a Netflix account for streaming.

16.Are there any local restaurants or cafes within walking distance of the house?
-Yes, there are several restaurants and cafes within a 15-minute walk from the house.

17.Do you provide any toiletries or bathroom essentials for guests, such as shampoo or soap?
-Yes, we provide shampoo, conditioner, and body wash in the shower. Extra towels are in the linen closet.

18.Is there a dishwasher available for guests to use, and if yes, where are the detergent and dishwasher pods located?
-Yes, the dishwasher is located next to the sink. Dishwasher detergent and pods are under the sink.

19.Are there any security measures in place at the house, such as a security system or smart locks?
-Yes, we have a security system installed. The code is 1234.

20.How do guests check out of the house, and are there any specific instructions for departure?
-Simply ensure all lights are turned off, windows are closed, and keys are left on the kitchen counter.

21.Is there a first aid kit available in case of emergencies, and if yes, where is it located?
-Yes, the first aid kit is located in the bathroom cabinet under the sink.

22.Are there any restrictions on smoking or vaping inside the house or on the property?
-Smoking and vaping are not allowed inside the house. There's a designated smoking area outside.

23.How do guests operate any electronic devices or appliances in the house, such as the TV or microwave?
-Instructions for operating electronic devices and appliances are in the guest manual on the coffee table.

24.Are there any local parks or outdoor recreational areas nearby that guests might enjoy?
-Yes, there's a beautiful park with walking trails just a short drive away.

25.Do you provide any breakfast or snack options for guests, and if yes, what is available?
-We provide complimentary coffee, tea, and a selection of granola bars for guests.

26.Are there any specific rules or guidelines for using the laundry facilities, if available?
-Laundry detergent is provided. Please be mindful of water usage and clean the lint trap after each use.

27. How do guests contact you in case of any issues or emergencies during their stay?
-You can reach us by phone or text at (555) 123-4567.

28. Are there any special events or festivals happening in the area during the guest's stay?
-Check the local events calendar for any upcoming festivals or events.

29.Are there any restaurants or stores that offer delivery to the house?
-Yes, several restaurants in the area offer delivery. Menus and contact information are in the guest manual.

30.Is there a guest book or feedback form where guests can leave comments or suggestions about their stay?
-Yes, there's a guest book on the coffee table where you can leave comments and suggestions. We appreciate your feedback!


Determine if the next input by the user is for the intent of seeing your resume
"""})
    
    messages.append({"role": "user", "content": input})
    chat_response = chat_completion_request(
        messages, tools=tools, tool_choice={"type": "function", "function": {"name": "check_for_resume_inquiry"}}
    )
    print(chat_response)
    chat_response = chat_response.json()["choices"][0]["message"]["tool_calls"][0]["function"]["arguments"]

    resume_info = strip_resume(resume_doc)

    print("input: "+input+" result: "+ str((json.loads(chat_response))["result"]))
    return bool((json.loads(chat_response))["result"]), resume_info
    


def add_balloons():

    emoji_list = ["🎈","🔥","💯","🤖"]

    rain(
        emoji=random.choice(emoji_list),
        font_size=random.randint(54, 300),
        falling_speed=5,
        animation_length="infinite",
    )


