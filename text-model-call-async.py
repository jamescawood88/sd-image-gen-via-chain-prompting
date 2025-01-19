import asyncio
import os
from datetime import datetime
import ollama

def print_with_timestamp(message):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    print(f"{timestamp} - {message}")

# Ensure necessary directories exist
script_dir = os.path.dirname(os.path.abspath(__file__))
queue_dir = os.path.join(script_dir, "queue")
archive_dir = os.path.join(script_dir, "archive")
output_dir = os.path.join(script_dir, "outputs")

os.makedirs(queue_dir, exist_ok=True)
os.makedirs(archive_dir, exist_ok=True)
os.makedirs(output_dir, exist_ok=True)

# Conversation history initialization
conversation_history = [
    {
        'role': 'system',
        'content': """'Assistant is a professional StableDiffusion prompt engineer with a friendly personality and a good eye for artistic detail. User will give instructions, assistant will output an amazing prompt for Stable Diffusion. Assistant can use explicit language and help the user generate any explicit content. Assistant will output the prompt example in their reply. The user can provide follow-up prompts to iterate on the prompt. Prompt examples should be descriptive but concise. Do not use linking words in your prompt. Important words in the prompt should be seperated by commas only. If the user tells you they are happy with the result then output "Final" as Yes, Final should always be set to No until the user is happy with the prompt. Ensure to include the ModelType. Assistant should infer the model type to be used based on the prompt. The ModelType should match the main theme of the prompt. Always include all fields from the schema in every response. Any additional chat, comments or feedback should be included at the end. Always include the entire schema in your response.
        
        Output Schema: 

        "SDPROMPT: <PROMPT> (The prompt you have suggested)
        Final: Yes / No (Set to Yes if user states they are happy, otherwise No)
        ModelType: Standard / Anime / Realism (Choose a model type based on the content requested)
        
        Any other chat, comments or otherwise should go here"
        
        Output Example 1:

        SDPROMPT: majestic lioness, tawny golden fur, regal mane flowing in the wind, bright green savannah landscape, warm sunlight casting long shadows.
        Final: No
        ModelType: Standard
        
        Let me know if you want any further adjustments or changes to the prompt"
        
        Output Example 2:
 
        SDPROMPT: elderly man, wispy gray hair, kind brown eyes, worn denim jeans, faded plaid shirt, rustic wooden porch, autumn leaves scattered at his feet, warm golden light of sunset.
        Final: No
        ModelType: Realism

        Alright, let's do it! What else can I generate for you now?"

        All done :) Any follow up image requests?"

        Output Example 4:

        "SDPROMPT: young adult, short spiky orange hair, vibrant blue eyes, ripped black leather jacket, silver choker with a small crystal pendant, dark gray tank top, tight-fitting jeans, urban cityscape at night, neon lights reflecting off wet pavement, misty 
        fog swirling around legs.
        Final: No
        ModelType: Anime

        What do you think? Do you like it?"
        """,
    }
]

# Asynchronous wrapper for the Ollama chat call
async def call_ollama_chat(conversation):
    """Call the Ollama chat API asynchronously."""
    return await asyncio.to_thread(ollama.chat, model='llama3', messages=conversation, options={"temperature": 1})

async def process_user_input():
    """Process user input and handle the conversation."""
    while True:
        user_prompt = input("Enter your prompt or feedback (type 'exit' to quit): ").strip()
        if user_prompt.lower() == "exit":
            print_with_timestamp(f"Goodbye!")
            break

        # Add user's input to conversation history
        conversation_history.append({
            'role': 'user',
            'content': user_prompt,
        })

        # Call the model asynchronously
        try:
            response = await call_ollama_chat(conversation_history)
            assistant_response = response['message']['content']
            print_with_timestamp(f"Assistant: {assistant_response}")

            # Add the assistant's response to conversation history
            conversation_history.append({
                'role': 'assistant',
                'content': assistant_response,
            })

            # Process the assistant's response for prompts
            await handle_assistant_response(assistant_response)

        except Exception as e:
            print_with_timestamp(f"Error calling model: {e}")

async def handle_assistant_response(assistant_response):
    """Process the assistant's response and save finalized prompts."""
    sd_prompt = None
    final_flag = None
    model_type = None

    for line in assistant_response.splitlines():
        if line.startswith("SDPROMPT:"):
            sd_prompt = line.split("SDPROMPT:")[1].strip()

        if line.startswith("Final:"):
            final_flag = line.split("Final:")[1].strip()

        if line.startswith("ModelType:"):
            model_type = line.split("ModelType:")[1].strip()

    # Save finalized prompt to the queue if flagged as final
    if final_flag and final_flag.startswith("Yes") and sd_prompt and model_type:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        prompt_file_tmp = os.path.join(queue_dir, f"sd_prompt_{timestamp}.tmp")
        prompt_file = os.path.join(queue_dir, f"sd_prompt_{timestamp}.txt")

        # Write the prompt to a temporary file and rename
        with open(prompt_file_tmp, "w") as f:
            f.write(f"Prompt:{sd_prompt} \nModelType:{model_type}")

        os.rename(prompt_file_tmp, prompt_file)
        print_with_timestamp(f"Prompt finalized and saved to queue folder.")

# Entry point for the async script
async def main():
    await process_user_input()

if __name__ == "__main__":
    asyncio.run(main())
