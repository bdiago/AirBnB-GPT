import argparse
from dataclasses import asdict
import json
import os
import streamlit as st
from retrieval import VirtualAssistant
from interfaces import Streamlit


OUTPUT_ROOT = "output"


# def create_chatbot
@st.cache_resource
def create_chatbot():
    chatbot = VirtualAssistant()
    return chatbot

def main():
    #change your character defualts here
    parser = argparse.ArgumentParser()
    
    parser.add_argument(
        "--character_name",
        type=str, 
        default="Jon"
    )
    parser.add_argument(
        "--chatbot_type",
        type=str,
        default="retrieval",
        choices=["summary", "retrieval", "summary_retrieval"],
    )
    parser.add_argument(
        "--interface", type=str, default="streamlit", choices=["cli", "streamlit"]
    )
    args = parser.parse_args()

    if args.interface == "cli":
        chatbot = create_chatbot(
            args.corpus,
            args.character_name,
            args.chatbot_type,
            args.retrieval_docs,
            args.summary_type,
        )
        app = CommandLine(chatbot=chatbot)
    elif args.interface == "streamlit":
        # chatbot = st.cache_resource(create_chatbot)
        chatbot = create_chatbot()
          
           
        # the streamlit UI begins here and finishes in interfaces/streamlit_ui.py
        st.title("<>{}</> GPT".format(args.character_name))
        st.write("An AI thats trained to be like {}! Ask {} anything about the your airbnb stay!".format(args.character_name, args.character_name))
        with st.expander("details"):
            st.markdown("""*This AI assistant references details to simulate conversation. It's not a real person,
                         so some info might be wrong. AI can sometimes generate unexpected responses. Use it for fun.*""")
            st.markdown(f"**chatbot type**: *{args.chatbot_type}*")
            # if st.button('Chaos Mode'):
            #     add_balloons()
            
            app = Streamlit(chatbot=chatbot)
    else:
        raise ValueError(f"Unknown interface: {args.interface}")
    st.divider()
  
    app.run()


if __name__ == "__main__":
    main()
