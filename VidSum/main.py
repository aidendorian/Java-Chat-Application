from youtube_transcript_api import YouTubeTranscriptApi
import tkinter as tk
import tkinter.scrolledtext as st
import time
import torch
import ollama
import os
from openai import OpenAI
import argparse
import json 
import time

PINK = '\033[95m'
CYAN = '\033[96m'
YELLOW = '\033[93m'
NEON_GREEN = '\033[92m'
RESET_COLOR = '\033[0m'


def get_val():
    n = ey.get()
    open('sub.txt', 'w').close()
    transcript = YouTubeTranscriptApi.get_transcript(n.replace("https://www.youtube.com/watch?v=",""))
    for entry in transcript:
        f = open("sub.txt","a")
        a = (str)(entry["text"].encode('utf-8').strip())
        f.write(a.replace('b','')+" ")
    time.sleep(2)
    
    def open_file(filepath):
        with open(filepath, 'r', encoding='utf-8') as infile:
            return infile.read()


    def get_relevant_context(rewritten_input, vault_embeddings, vault_content, top_k=3):
        if vault_embeddings.nelement() == 0: 
            return []
        input_embedding = ollama.embeddings(model='mxbai-embed-large', prompt=rewritten_input)["embedding"]
        
        cos_scores = torch.cosine_similarity(torch.tensor(input_embedding).unsqueeze(0), vault_embeddings)
        top_k = min(top_k, len(cos_scores))
        # Sort the scores and get the top-k indices
        top_indices = torch.topk(cos_scores, k=top_k)[1].tolist()
        # Get the corresponding context from the vault
        relevant_context = [vault_content[idx].strip() for idx in top_indices]
        return relevant_context

    # Function to interact with the Ollama model
    def ollama_chat(user_input, system_message, vault_embeddings, vault_content, ollama_model, conversation_history):
        # Get relevant context from the vault
        relevant_context = get_relevant_context(user_input, vault_embeddings_tensor, vault_content, top_k=3)
        if relevant_context:
            # Convert list to a single string with newlines between items
            context_str = "\n".join(relevant_context)
            
        else:
            print(CYAN + "No relevant context found." + RESET_COLOR)
        
        # Prepare the user's input by concatenating it with the relevant context
        user_input_with_context = user_input
        if relevant_context:
            user_input_with_context = context_str + "\n\n" + user_input
        
        # Append the user's input to the conversation history
        conversation_history.append({"role": "user", "content": user_input_with_context})
        
        # Create a message history including the system message and the conversation history
        messages = [
            {"role": "system", "content": system_message},
            *conversation_history
        ]
        
        # Send the completion request to the Ollama model
        response = client.chat.completions.create(
            model=ollama_model,
            messages=messages
        )
        
        # Append the model's response to the conversation history
        conversation_history.append({"role": "assistant", "content": response.choices[0].message.content})
        
        # Return the content of the response from the model
        return response.choices[0].message.content

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Ollama Chat")
    parser.add_argument("--model", default="dolphin-llama3", help="Ollama model to use (default: llama3)")
    args = parser.parse_args()

    # Configuration for the Ollama API client
    client = OpenAI(
        base_url='http://localhost:11434/v1',
        api_key='dolphin-llama3'
    )

    # Load the vault content
    vault_content = []
    if os.path.exists("sub.txt"):
        with open("sub.txt", "r", encoding='utf-8') as vault_file:
            vault_content = vault_file.readlines()

    # Generate embeddings for the vault content using Ollama
    vault_embeddings = []
    for content in vault_content:
        response = ollama.embeddings(model='mxbai-embed-large', prompt=content)
        vault_embeddings.append(response["embedding"])

    # Convert to tensor and print embeddings
    vault_embeddings_tensor = torch.tensor(vault_embeddings) 
    print("Embeddings for each line in the vault:")
    print(vault_embeddings_tensor)

    conversation_history = []
    system_message = "You are a helpful assistant that is an expert at extracting the most useful information from a given text"

    
        
    user_input = "give a detailed summary of the contents in atleast 700 words, highlighting importants as bullet points and make sure to cover every major topic"



    response = ollama_chat(user_input, system_message, vault_embeddings_tensor, vault_content, args.model, conversation_history)
    data = {'input':response}
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        
    print(NEON_GREEN + "Response: \n\n" + response + RESET_COLOR)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    data = {'input':'-'}
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    
    
    
    

window = tk.Tk()
window.title("Summariser")


ey = tk.Entry(window)
ey.pack()


button = tk.Button(window, text="Summarise", command=get_val)
button.pack()
text_area = st.ScrolledText(window, width = 30,  height = 8,  font = ("Times New Roman", 15))
text_area.pack()

text_area.configure(state ='disabled')

window.mainloop()