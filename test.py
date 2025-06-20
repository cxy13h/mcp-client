def parse_json_stream(stream):
    """
    流式解析JSON，返回 (key, value_chunk) 的生成器
    stream: 返回数据块的迭代器
    """
    buffer = ""
    depth = 0
    in_string = False
    escape = False
    
    key = ""
    value = ""
    reading_key = False
    reading_value = False
    
    for chunk in stream:
        buffer += chunk
        i = 0
        while i < len(buffer):
            c = buffer[i]
            
            # 处理转义
            if escape:
                escape = False
                if reading_key:
                    key += c
                elif reading_value:
                    value += c
                i += 1
                continue
                
            if c == '\\' and in_string:
                escape = True
                if reading_key:
                    key += c
                elif reading_value:
                    value += c
                i += 1
                continue
            
            # 字符串边界
            if c == '"':
                if reading_value:
                    value += c  # 值的引号要保留
                in_string = not in_string
                
                # 如果是键的结束引号
                if not in_string and reading_key:
                    reading_key = False
            
            # 非字符串内的处理
            elif not in_string:
                if c == '{':
                    depth += 1
                    if depth == 1:
                        # 开始新对象
                        key = ""
                        value = ""
                        reading_key = False
                        reading_value = False
                    elif reading_value:
                        value += c
                        
                elif c == '}':
                    depth -= 1
                    if depth > 0 and reading_value:
                        # 只有在不是最外层的 } 时才加入值
                        value += c
                    elif depth == 0:
                        # 对象结束
                        if key and value:
                            yield (key, value)
                            
                elif c == ':' and depth == 1:
                    # 从键转到值
                    reading_value = True
                    value = ""
                    
                elif c == ',' and depth == 1:
                    # 字段结束
                    if key and value:
                        yield (key, value)
                    key = ""
                    value = ""
                    reading_value = False
                    
                elif c not in ' \t\n\r':
                    if reading_value:
                        value += c
            else:
                # 在字符串内
                if reading_key:
                    key += c
                elif reading_value:
                    value += c
                    
            # 检测键的开始（在字符串刚开始时）
            if c == '"' and not reading_key and not reading_value and depth == 1 and in_string:
                reading_key = True
                key = ""
                    
            i += 1
            
        # 更新buffer
        buffer = buffer[i:]


# 使用示例
def demo():
    # 模拟流数据
    def data_stream():
        chunks = [
            '{"st',
            'ate": "processing", ',
            '"content": {"msg": "Hello ',
            'World", "data": [1, 2,',
            ' 3, 4, 5]',
            '}}'
        ]
        for chunk in chunks:
            yield chunk
    
    print("=== 解析结果 ===")
    for key, value in parse_json_stream(data_stream()):
        print(f"键: {key}")
        print(f"值: {value}")
    
    # # 写入文件
    # print("\n=== 写入文件 ===")
    # state_file = open("state.txt", "w")
    # content_file = open("content.txt", "w")
    
    # for key, value in parse_json_stream(data_stream()):
    #     if key == "state":
    #         state_file.write(value)
    #         print(f"写入 state.txt: {value}")
    #     elif key == "content":
    #         content_file.write(value)
    #         print(f"写入 content.txt: {value}")
    
    # state_file.close()
    # content_file.close()


# 调试版本 - 显示解析过程
def debug_parse():
    """调试版本，显示详细的解析过程"""
    
    def data_stream():
        chunks = ['{"state": "ok"}']
        for chunk in chunks:
            yield chunk
    
    buffer = ""
    depth = 0
    in_string = False
    key = ""
    value = ""
    reading_key = False
    reading_value = False
    
    for chunk in data_stream():
        buffer += chunk
        print(f"Buffer: {buffer}")
        
        for i, c in enumerate(buffer):
            print(f"字符: '{c}' | depth={depth} | in_string={in_string} | "
                  f"reading_key={reading_key} | reading_value={reading_value} | "
                  f"key='{key}' | value='{value}'")
            
            if c == '"':
                if reading_value:
                    value += c
                in_string = not in_string
                if not in_string and reading_key:
                    reading_key = False
                    print(f"  -> 键读取完成: '{key}'")
                elif in_string and not reading_key and not reading_value and depth == 1:
                    reading_key = True
                    key = ""
                    print(f"  -> 开始读取键")
                    
            elif c == ':' and not in_string and depth == 1:
                reading_value = True
                value = ""
                print(f"  -> 开始读取值")
                
            elif c == '{':
                depth += 1
                if reading_value:
                    value += c
                    
            elif c == '}':
                if reading_value:
                    value += c
                depth -= 1
                if depth == 0 and key and value:
                    print(f"  -> 输出: ({key}, {value})")
                    
            elif in_string:
                if reading_key:
                    key += c
                elif reading_value:
                    value += c
                    
            elif not in_string and c not in ' \t\n\r':
                if reading_value:
                    value += c


if __name__ == "__main__":
    # # 先运行调试版本看看解析过程
    # print("=== 调试模式 ===")
    # debug_parse()
    
    print("\n\n=== 正常运行 ===")
    demo()