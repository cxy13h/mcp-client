import json
from openai import OpenAI
from typing import Generator, Dict, Any, Optional
def format_tool(tool_json: dict) -> dict:
    """
    将工具的原始JSON模式描述转换为一个结构化的字典对象。

    Args:
        tool_json: 包含工具描述的原始字典。

    Returns:
        一个结构化、易于使用的字典。
    """
    optional_fields = {
    "ArgDescription": "description",
    "ArgType": "type",
    "ArgExamples": "examples",
    "ArgDefaultValue": "default",
    "ArgEnum": "enum"
}
    # 构建最终的输出字典
    output_dict = {
        "ToolName": tool_json.get("name", "N/A"),
        "ToolDescription": tool_json.get("description", "N/A"),
        "InputSchema": {
            "RequiredArgs": tool_json["inputSchema"].get("required", []),
            "Args": {}
        },
    }

    # 获取原始的输入参数属性
    properties = tool_json.get("inputSchema", {}).get("properties", {})

    # 遍历原始属性，并按照新格式填充到 InputSchema 中
    for arg_name, details in properties.items():
        output_dict["InputSchema"]["Args"][arg_name] = {}
        for output_key, details_key in optional_fields.items():
            if details_key in details and details[details_key] is not None:
                output_dict["InputSchema"]["Args"][arg_name][output_key] = details[details_key]

    return output_dict




def generate_tool_prompt(tool_definitions, toolAdditionalDescription, toolPromptTemplate):
    """
    将工具定义列表嵌入到提示词模板中。

    返回:
    str: 填充好工具信息的完整提示词。
    """
    # 1. 提取所有工具的名称
    tool_names = [tool.get("ToolName", "N/A") for tool in tool_definitions]
    # 2. 将每个工具的描述（字典）格式化为JSON字符串
    # 使用 json.dumps 可以保持良好的格式，并确保中文字符正确显示
    tool_descriptions = [
        json.dumps(tool, indent=4, ensure_ascii=False) 
        for tool in tool_definitions
    ]
    # 3. 准备要填充到模板中的最终字符串
    # 工具名列表用逗号和空格连接
    final_tool_names_str = ", ".join(f"`{name}`" for name in tool_names)
    
    # 每个工具的JSON描述用两个换行符隔开，使其在视觉上分离
    final_tools_str = "\n\n".join(tool_descriptions)
    
    # 4. 使用模板的 .format() 方法填充占位符
    tool_final_prompt = toolPromptTemplate.format(
        tool_name_list=final_tool_names_str,
        additional_description=toolAdditionalDescription,
        tools=final_tools_str
    )
    
    return tool_final_prompt

def get_final_prompt(all_tools: list):
    toolAdditionalDescriptionPath = "./Prompt/toolAdditionalDescriptionTemplate.txt"
    toolAdditionalDescription = "" 
    try:
        with open(toolAdditionalDescriptionPath, 'r', encoding='utf-8') as f1:
            toolAdditionalDescription = f1.read()
    except FileNotFoundError:
        print(f"错误：找不到文件 '{toolAdditionalDescriptionPath}'。请检查文件路径是否正确。")
  
    toolPromptTemplatePath = "./Prompt/toolPromptTemplate.txt"
    toolPromptTemplate = ""
    try:
        with open(toolPromptTemplatePath, 'r', encoding='utf-8') as f2:
            toolPromptTemplate = f2.read()
    except FileNotFoundError:
        print(f"错误：找不到文件 '{toolPromptTemplate}'。请检查文件路径是否正确。")

    # 3. 调用函数生成最终的提示词
    tool_prompt = generate_tool_prompt(all_tools, toolAdditionalDescription, toolPromptTemplate)


    llmPromptTemplatePath = "./Prompt/llmPromptTemplate.txt"
    llmPromptTemplate = ""
    try:
        with open(llmPromptTemplatePath, 'r', encoding='utf-8') as f3:
            llmPromptTemplate = f3.read()
    except FileNotFoundError:
        print(f"错误：找不到文件 '{llmPromptTemplate}'。请检查文件路径是否正确。")

    final_prompt = llmPromptTemplate.format(
        tools=tool_prompt,
        agent_scratchpad='''{"state": "User Input", "content":"我要查看当前数据库各个表的格式，并且为它们添加一些样本数据"}'''
    )
    return final_prompt



def parse_json_stream_by_chunks(stream):
    """
    基于chunk的流式解析器，每次yield整个chunk而不是单个字符
    返回 (event_type, key, value_chunk) 的生成器
    
    event_type 可以是：
    - "key_complete": 键读取完成
    - "value_chunk": 值的一个chunk
    - "value_complete": 值读取完成
    """
    buffer = ""
    depth = 0
    in_string = False
    escape = False
    
    current_key = ""
    current_value = ""
    reading_key = False
    reading_value = False
    
    for chunk in stream:
        buffer += chunk
        i = 0
        
        # 记录这个chunk中值的起始位置
        value_chunk_start = -1
        
        while i < len(buffer):
            c = buffer[i]
            
            # 处理转义
            if escape:
                escape = False
                if reading_key:
                    current_key += c
                elif reading_value:
                    current_value += c
                    if value_chunk_start == -1:
                        value_chunk_start = len(current_value) - 1
                i += 1
                continue
                
            if c == '\\' and in_string:
                escape = True
                if reading_key:
                    current_key += c
                elif reading_value:
                    current_value += c
                    if value_chunk_start == -1:
                        value_chunk_start = len(current_value) - 1
                i += 1
                continue
            
            # 字符串边界
            if c == '"':
                if reading_value:
                    current_value += c
                    if value_chunk_start == -1:
                        value_chunk_start = len(current_value) - 1
                        
                in_string = not in_string
                
                # 键的结束
                if not in_string and reading_key:
                    reading_key = False
                    yield ("key_complete", current_key, "")
            
            # 非字符串内的处理
            elif not in_string:
                if c == '{':
                    depth += 1
                    if depth > 1 and reading_value:
                        current_value += c
                        if value_chunk_start == -1:
                            value_chunk_start = len(current_value) - 1
                        
                elif c == '}':
                    depth -= 1
                    if depth > 0 and reading_value:
                        # 内层的 } 要加入值
                        current_value += c
                        if value_chunk_start == -1:
                            value_chunk_start = len(current_value) - 1
                    elif depth == 0:
                        # 最外层的 } 表示整个JSON结束
                        if reading_value:
                            # 值结束，输出最后的chunk
                            if value_chunk_start != -1:
                                chunk_content = current_value[value_chunk_start:]
                                if chunk_content:
                                    yield ("value_chunk", current_key, chunk_content)
                            yield ("value_complete", current_key, current_value)
                            reading_value = False
                            current_value = ""
                        
                elif c == ':' and depth == 1:
                    reading_value = True
                    current_value = ""
                    value_chunk_start = -1
                    
                elif c == ',' and depth == 1:
                    if reading_value:
                        # 值结束，输出最后的chunk
                        if value_chunk_start != -1:
                            chunk_content = current_value[value_chunk_start:]
                            if chunk_content:
                                yield ("value_chunk", current_key, chunk_content)
                        yield ("value_complete", current_key, current_value)
                        reading_value = False
                        current_value = ""
                    current_key = ""
                    
                elif c not in ' \t\n\r':
                    if reading_value:
                        current_value += c
                        if value_chunk_start == -1:
                            value_chunk_start = len(current_value) - 1
                            
            else:
                # 在字符串内
                if reading_key:
                    current_key += c
                elif reading_value:
                    current_value += c
                    if value_chunk_start == -1:
                        value_chunk_start = len(current_value) - 1
                    
            # 检测键的开始
            if c == '"' and not reading_key and not reading_value and depth == 1 and in_string:
                reading_key = True
                current_key = ""
                    
            i += 1
            
        # 处理完这个chunk后，如果正在读值且有新内容，yield这个chunk的内容
        if reading_value and value_chunk_start != -1:
            chunk_content = current_value[value_chunk_start:]
            if chunk_content:
                yield ("value_chunk", current_key, chunk_content)
                
        # 更新buffer
        buffer = buffer[i:]

def parse_llm_stream(response):
    """将LLM响应转换为字符流"""
    for chunk in response:
        if chunk.choices and chunk.choices[0].delta.content:
            content = chunk.choices[0].delta.content
            # print(f"\033[90m{content}\033[0m", end="", flush=True)
            yield content

def invoke(prompt: str) -> tuple[str, str, str]:
    llm_client = OpenAI(
        api_key="AIzaSyCvJwFk7igZTb7lU3MUCbGKufWGPgKP2p0",
        base_url="https://cxy13h.xyz/v1beta/openai/",
        default_headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
)
    response = llm_client.chat.completions.create(
        model="gemini-2.5-flash",
        messages=[{"role": "user", "content": prompt}],
        stream=True
    )
    for event_type, key, content in parse_json_stream_by_chunks(parse_llm_stream(response)):
        if event_type == "key_complete":
            print(f"\n[{key}]: ", end="", flush=True)
        elif event_type == "value_chunk":
            # 输出整个chunk，而不是单个字符
            print(content, end="", flush=True)
        elif event_type == "value_complete":
            if key == "state":
                last_state = content
            elif key == "content":
                last_content = content
                prompt += f"\n{{\"state\": {last_state}, \"content\":{last_content}}}"
            print()  # 换行
    return last_state, last_content, prompt
