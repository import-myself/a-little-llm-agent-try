
# agent entrance

"""
todo:
    1.Setting of environment variables
    2.Tool introduction
    3.prompt template
    4.Model initialization
"""
import time
from tools import tools_map
from prompt import gen_prompt, user_prompt
from model_provider import ModelProvider
from dotenv import load_dotenv

load_dotenv()

mp = ModelProvider()


def parse_thoughts(response):
    """
        response:
        {
            "action": {
            "name": "action name",
            "args": {
                "args name": "args value"
                }
            },
            "thoughts":
            {
                "text": "thoughts",
                "plan": "plan",
                "criticism": "criticism",
                "speak": "The summary of the current step is returned to the user",
                "reasoning": ""
            }
        }
    """
    try:
        thoughts = response.get("thoughts")
        observation = response.get("observation")
        plan = response.get("plan")
        reasoning = response.get("reasoning")
        criticism = response.get("criticism")
        prompt = f"plan:{plan}\n reasoning:{reasoning}\n criticism:{criticism}\n observation:{observation}"
        return prompt
    except Exception as err:
        print("parse thoughts err: {}".format(err))
        return "{}".format(err)


def agent_execute(query, max_request_time =10):
    cur_request_time = 0
    chat_history = []
    agent_scratch = ''
    while cur_request_time < max_request_time:
        cur_request_time += 1
        """
        If the return result is as expected, it is returned directly
        """
        """
        prompt functions included:
            1. task description
            2. tool description
            3. user input: user_msg
            4. assistant input: assistant_msg
            5. restriction
            6. give a description of better practices
            
        """
        prompt = gen_prompt(query, agent_scratch)
        start_time = time.time()
        print("*****************{}.start call llm****************".format(cur_request_time), flush=True)
        # call llm
        """
        sys_prompt: 
        user_msg, assistant_msg, history
        """
        response = mp.chat(prompt, chat_history)

        end_time = time.time()
        print("*****************{}.call llm End, consume time:{}****************".format(cur_request_time,
                                                                                         end_time - start_time),
              flush=True)
        if not response or not isinstance(response, dict):
            print("Error calling llm, retry soon....", response)
            continue

        """
        response:
        {
            "action": {
            "name": "action name",
            "args": {
                "args name": "args value"
                }
            },
            "thoughts":
            {
                "text": "thoughts",
                "plan": "plan",
                "criticism": "criticism",
                "speak": "The summary of the current step is returned to the user",
                "reasoning": ""
            }
        }
        """

        action_info = response.get("action")
        action_name = action_info.get("name")
        action_args = action_info.get("args")
        print("present action name: ", action_name, action_args)

        if action_name == "finish":
            final_answer = action_args.get("answer")
            print("final_answer:", final_answer)
            break

        observation = response.get("observation")

        try:
            """
                Mapping A to a function: map -> {action_name: func}
            """
            # todo: Implement tools_map

            func = tools_map.get(action_name)

            call_func_result = func(**action_args)

        except Exception as err:
            print("Call tool exception:", err)
            call_func_result = "{}".format(err)

        agent_scratch = agent_scratch + "\n: observation: {}\n execute action result: {}".format(observation,
                                                                                                 call_func_result)

        assistant_msg = parse_thoughts(response)
        chat_history.append([user_prompt, assistant_msg])

    if cur_request_time == max_request_time:
        print("Unfortunately, this mission failed")
    else:
        print("Congratulations, the mission was a success")


def main():
    # Requirement: Support multiple user interactions
    max_request_time = 10
    while True:
        query = input("Please enter your goal:")
        if query == 'exit':
            return
        agent_execute(query, max_request_time=max_request_time)


if __name__ == '__main__':
    main()