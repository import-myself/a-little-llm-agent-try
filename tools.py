"""
1.write the file
2.read the file
3.append
4.web search
"""
import os
import json
from langchain_community.tools.tavily_search import TavilySearchResults
from dotenv import load_dotenv

load_dotenv()


def _get_workdir_root():
    workdir_root = os.environ.get("WORKDIR_ROOT")
    return workdir_root


WORKDIR_ROOT = _get_workdir_root()


def read_file(file_name):
    file_name = os.path.join(WORKDIR_ROOT, file_name)
    if not os.path.exists(file_name):
        return f"{file_name} not exist, please check the file exist before read"

    with open(file_name, 'r') as f:
        return "\n".join(f.readlines())


def append_to_file(file_name, content):
    file_name = os.path.join(WORKDIR_ROOT, file_name)
    if not os.path.exists(file_name):
        return f"{file_name} not exist, please check the file exist before append"

    with open(file_name, 'a') as f:
        f.write(content)
    return "append content to file success"


def write_to_file(file_name, content):
    file_name = os.path.join(WORKDIR_ROOT, file_name)
    if not os.path.exists(WORKDIR_ROOT):
        os.makedirs(WORKDIR_ROOT)

    with open(file_name, 'w', encoding='utf-8') as f:
        f.write(content)

    return "write content to file success"


def search(query):
    tavily = TavilySearchResults(max_results=5)

    try:
        ret = tavily.invoke(input=query)
        """
        ret:
        [{
            "content": "",
            "url": 
        }]
        """
        content_list = [obj['content'] for obj in ret]

        return "\n".join(content_list)

    except Exception as err:
        return "search err: {}".format(err)


tools_info = [
    {
        "name": "read_file",
        "description": "read file from agent generate, should write file before read",
        "args": [{
            "name": "file_name",
            "type": "string",
            "description": "read file name"
        }]
    },
    {
        "name": "append_to_file",
        "description": "append llm content to file, should write file before read",
        "args": [{
            "name": "file_name",
            "type": "string",
            "description": "file name",
        },
        {
            "name": "content",
            "type": "string",
            "description": "append to file content",
        }]
    },
    {
        "name": "write_to_file",
        "description": "write llm content to file",
        "args": [{
            "name": "file_name",
            "type": "string",
            "description": "file name",
        },
        {
            "name": "content",
            "type": "string",
            "description": "write to file content",
        }]
    },
    {
        "name": "search",
        "description": "This is a search engine, you can gain additional knowledge through this search engine when you"
                       "are unsure of what large model return",
        "args": [{
            "name": "query",
            "type": "string",
            "description": "search query to look up",
        }]
    },
    {
        "name": "finish",
        "description": "According to the observation, the goal has been accomplished and the final result has been obtained",
        "args": [{
            "name": "answer",
            "type": "string",
            "description": "The goal's final answer",
        }]
    }
]

tools_map = {
    "read_file": read_file,
    "append_to_file": append_to_file,
    "write_to_file": write_to_file,
    "search": search
}


def gen_tool_desc():
    tools_desc = []
    for idx, t in enumerate(tools_info):
        args_desc = []
        for info in t['args']:
            args_desc.append({
                "name": info["name"],
                "description": info["description"],
                "type": info["type"]
            })
        args_desc = json.dumps(args_desc, ensure_ascii=False)
        tool_desc = f"{idx + 1}. {t['name']}: {t['description']}, args: {args_desc}"
        tools_desc.append(tool_desc)
    tools_prompt = "\n".join(tools_desc)
    return tools_prompt
