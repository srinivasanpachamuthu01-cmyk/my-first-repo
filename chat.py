Python 3.14.4 (tags/v3.14.4:23116f9, Apr  7 2026, 14:10:54) [MSC v.1944 64 bit (AMD64)] on win32
Enter "help" below or click "Help" above for more information.
set OPENAI_API_KEY=YOUR_OPENAI_API_KEY
    ```
*   **Windows (PowerShell):**
    
```powershell
    $env:OPENAI_API_KEY="YOUR_OPENAI_API_KEY"
    ```

### Step 3: Write the Code
Create a new file named `openai_chatbot.py` and paste the following code. 

> **Note on Memory:** Unlike the Google SDK, OpenAI's API doesn't have a built-in "chat" object that manages history automatically in the background. Instead, **we maintain a simple Python list called `messages`**. Every time you or the bot speaks, we append the message to that list and send the whole history back to OpenAI so it remembers the context.

```python
import os
import sys
from openai import OpenAI

def run_openai_chatbot():
    # 1. Verify the OpenAI API key exists
    if not os.environ.get("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not found.")
        print("Please set your API key in the terminal before running.")
        sys.exit(1)

    print("Initializing your OpenAI assistant...")
    
    # 2. Initialize the OpenAI client (it automatically looks for the OPENAI_API_KEY environment variable)
    client = OpenAI()
    
    # 3. Create our conversation history list and prime it with a system instruction
    messages = [
        {"role": "system", "content": "You are a helpful, friendly, and slightly witty AI companion."}
    ]
    
...     print("\n==============================================")
...     print("🤖 OpenAI Chatbot initialized! Type 'quit' or 'exit' to stop.")
...     print("==============================================\n")
...     
...     # 4. Start the continuous interaction loop
...     while True:
...         try:
...             user_input = input("You: ").strip()
...             
...             # Check for exit commands
...             if user_input.lower() in ['quit', 'exit']:
...                 print("Bot: Goodbye! Have a fantastic day!")
...                 break
...                 
...             if not user_input:
...                 continue
...                 
...             # 5. Add the user's message to our local history list
...             messages.append({"role": "user", "content": user_input})
...             
...             # 6. Send the entire message history to OpenAI
...             completion = client.chat.completions.create(
...                 model="gpt-4o-mini",
...                 messages=messages
...             )
...             
...             # 7. Extract the bot's reply text
...             bot_reply = completion.choices[0].message.content
...             print(f"Bot: {bot_reply}\n")
...             
...             # 8. Append the bot's response to the history so it remembers it next time
...             messages.append({"role": "assistant", "content": bot_reply})
...             
...         except Exception as e:
...             print(f"\nAn error occurred: {e}\n")
...             break
... 
... if __name__ == "__main__":
