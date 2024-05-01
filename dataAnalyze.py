# http://43.136.70.112:8000
# refresh_token:eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJ1c2VyLWNlbnRlciIsImV4cCI6MTcyMTg4ODE5MywiaWF0IjoxNzE0MTEyMTkzLCJqdGkiOiJjb2xrZGdiNWNmdWozZzkxZ3NiMCIsInR5cCI6InJlZnJlc2giLCJzdWIiOiJjb2t2c2VqNWNmdWozZ2J0bTJ2MCIsInNwYWNlX2lkIjoiY29rdnNlajVjZnVqM2didG0ydWciLCJhYnN0cmFjdF91c2VyX2lkIjoiY29rdnNlajVjZnVqM2didG0ydTAifQ.T8pIgOdodEBzDfjyWhnFY4xULodGDKHIHCkQKBJW-b7uV7OVYFX5EQDbfJNXnXYe-5y8mPOG6pexQH-GNpPFmg
import json
import time

import requests

import host

# 设置你的刷新令牌
refresh_token = ('eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9'
                 '.eyJpc3MiOiJ1c2VyLWNlbnRlciIsImV4cCI6MTcyMTg4ODE5MywiaWF0IjoxNzE0MTEyMTkzLCJqdGkiOiJjb2xrZG'
                 'diNWNmdWozZzkxZ3NiMCIsInR5cCI6InJlZnJlc2giLCJzdWIiOiJjb2t2c2VqNWNmdWozZ2J0bTJ2MCIsInNwYWNlX2lkIj'
                 'oiY29rdnNlajVjZnVqM2didG0ydWciLCJhYnN0cmFjdF91c2VyX2lkIjoiY29rdnNlajVjZnVqM2didG0ydTAifQ.T8pIgOdo'
                 'dEBzDfjyWhnFY4xULodGDKHIHCkQKBJW-b7uV7OVYFX5EQDbfJNXnXYe-5y8mPOG6pexQH-GNpPFmg')

# 设置请求头部
headers = {
    'Authorization': f'Bearer {refresh_token}'
}

import re

def extract_text_between_markers(text, start_marker, end_marker):
    pattern = re.compile(re.escape(start_marker) + r'(.*?)' + re.escape(end_marker), re.DOTALL)
    matches = pattern.findall(text)
    return matches


# 从文件中读取数据
now = time.strftime("%Y-%m-%d", time.localtime())
file_path = fr'排行榜\新片\{now}.txt'
with open(file_path, 'r', encoding='utf-8') as file:
    file_content = file.read()

# 您想要提取的文本部分的起始和结束标记
start_marker = 'Start'
end_marker = 'End'

# 提取文本
extracted_texts = extract_text_between_markers(file_content, start_marker, end_marker)


for i in range(len(extracted_texts)):
    question = f'请根据文本内容结合观众评论从主题与内容，剧情与结构，角色与表演，导演与风格，社会影响等方面客观的详细的评价这部电影\n{extracted_texts[i]}'

    lines = extracted_texts[i].split('\n')

    title = ''
    for line in lines:
        if '片名:' in line:
            parts = line.split(':')
            title = parts[1].strip()
            break

    # 设置POST请求的数据
    payload = {
        'model': 'kimi',  # 模型名称可以根据要求随意填写
        'messages': [
            {
                'role': 'user',
                'content': f'{question}'  # 这里填写你想要测试的内容
            }
        ],
        'use_search': True,  # 是否开启联网搜索
        'stream': False  # 是否使用SSE流
    }

    # 发送POST请求到指定的接口，示例URL请替换为实际的API URL
    response = requests.post(host.hostUrl, headers=headers, json=payload)

    # 验证响应状态码
    if response.status_code == 200:
        response_json = response.json()
        # 获取assistant的回答
        for choice in response_json['choices']:
            answer = choice['message']['content']
            # 打印回答
            print(answer)
            # 查找第一个 # 的位置
            hash_index = answer.find('#')

            # 如果找到了 #, 则删除它之前的内容
            if hash_index != -1:
                answer = answer[hash_index:]
            else:
                answer = answer  # 如果没有找到 #，则保持原样

            print(answer)
            with open(fr'排行榜\新片\{now}\{title}.md', 'w', encoding='utf-8') as file:
                file.write(answer)
    else:
        print(f"Error: {response.status_code}")
