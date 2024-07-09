import os
import dashscope
from dashscope.api_entities.dashscope_response import Message
from prompt import gen_prompt, user_prompt
import json


class ModelProvider(object):
    def __init__(self):
        self.api_key = os.environ.get("API_KEY")
        self.model_name = os.environ.get("MODEL_NAME")
        self._client = dashscope.Generation()

        self.max_retry_time = 3

    def chat(self, prompt, chat_history):
        cur_try_time = 0
        while cur_try_time < self.max_retry_time:
            cur_try_time += 1
            try:
                messages = [Message(role='system', content=prompt)]
                for his in chat_history:
                    messages.append(Message(role='user', content=his[0]))
                    messages.append(Message(role='system', content=his[1]))

                messages.append(Message(role='user', content=user_prompt))
                response = self._client.call(
                    model=self.model_name,
                    api_key=self.api_key,
                    messages=messages
                )
                """
                {
                    "status_code": 200, 
                    "request_id": "a24cb631-a63f-9f09-b571-1aecc3c1d3b4", 
                    "code": "", 
                    "message": "", 
                    "output": {
                        "text": null, 
                        "finish_reason": null, 
                        "choices": [{
                            "finish_reason": "null", 
                            "message": {
                                "role": "assistant", 
                                "content": "当然"}
                                }]
                            }, 
                        "usage": {
                            "input_tokens": 20, 
                            "output_tokens": 1, 
                            "total_tokens": 21}
                }
                """
                content = json.loads(response['output']['text'])
                return content
            except Exception as err:
                print("Error calling llm:{}".format(err))
            return {}

