class MessageBuilder:
    def __init__(self, response_format:bool = False):
        self.response_format = response_format
        self.provide_json_format = ' Provide the output in JSON format.'
        self.messages = []


    def add_message(self, role: str, message: str):
        """
        Adds a message with the specified role.
        Role must be one of: system, user, assistant.
        """
        if role == "system":
            return self.add_system_message(message)
        elif role == "user":
            return self.add_user_message(message)
        elif role == "assistant":
            return self.add_assistant_message(message)
        else:
            raise ValueError("Role must be 'system', 'user', or 'assistant'.")


    def add_system_message(self, message: str):
        if self.response_format:
            message += self.provide_json_format

        system_message = {
            "role": "system",
            "content": message
        }
            
        self.messages.append(system_message)
        return system_message

    def add_user_message(self, message: str):
        user_message = {
            "role": "user",
            "content": message
        }
        self.messages.append(user_message)
        return user_message
    

    def add_assistant_message(self, message: str):
        assistant_message = {
            "role": "assistant",
            "content": message
        }

        self.messages.append(assistant_message)
        return assistant_message

    def jsonl_payload(self):
        payload = {"messages": self.messages}
        return payload

    def reset_messages(self):
        self.messages = []


if __name__ == '__main__':
    platform = 'azure_openai'
    
    builder = MessageBuilder(platform=platform, response_format=True)
    
    builder.add_message(role="system",message="You are an...")
    builder.add_message(role="user",message="Why is...")
    builder.add_message(role="assistant",message="because...")

    messages = builder.jsonl_payload()



    
    
    