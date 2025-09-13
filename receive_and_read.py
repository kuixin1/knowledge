"""
    接收JSON文件到 received_jsons 并自动解压其中的base64编码内容到 input
    当接收到第三个文件时执行特定操作，并持续监听后续文件
"""
import websocket
import threading
import time
import json
import os
import uuid
import base64
import shutil
from datetime import datetime

WS_URL = "ws://72920e93.r29.cpolar.top/ws"

# 文件保存路径
SAVE_DIR = "received_jsons"
DECODE_DIR = "input"
os.makedirs(SAVE_DIR, exist_ok=True)
os.makedirs(DECODE_DIR, exist_ok=True)

# 全局变量，记录接收到的文件数量
received_count = 0

def decode_base64_file(data):
    """解码base64文件并保存"""
    # 提取数据
    file_name = data["fileName"]
    file_type = data["fileType"]
    base64_content = data["file"]
    
    # 移除base64字符串中可能存在的换行符和空格
    clean_base64 = base64_content.replace('\n', '').replace('\r', '').strip()
    
    # 将base64解码为二进制数据
    try:
        file_data = base64.b64decode(clean_base64)
    except Exception as e:
        print(f"❌ Base64解码失败: {e}")
        return False
    
    # 组合完整文件名
    output_filename = f"{file_name}.{file_type}"
    output_path = os.path.join(DECODE_DIR, output_filename)
    
    # 保存文件
    try:
        with open(output_path, 'wb') as f:
            f.write(file_data)
        print(f"✅ 解码后的文件已保存为: {output_path}")
        print(f"文件大小: {len(file_data)} 字节")
        return True
    except Exception as e:
        print(f"❌ 保存解码文件失败: {e}")
        return False

def send_demo_json(ws):
    """发送demo.json文件到服务器"""
    demo_file_path = "demo.json"
    if not os.path.exists(demo_file_path):
        print(f"❌ {demo_file_path} 文件不存在，无法发送")
        return False
    
    try:
        with open(demo_file_path, 'r', encoding='utf-8') as f:
            demo_data = json.load(f)
        
        # 发送文件到服务器
        message = {
            "action": "send_file",
            "file_name": "demo.json",
            "file_content": demo_data,
            "timestamp": datetime.now().isoformat()
        }
        ws.send(json.dumps(message))
        print(f"✅ 已发送 {demo_file_path} 到服务器")
        
        # 发送成功后删除input和received_jsons目录下的所有文件和子目录
        clear_directories()
        return True
    except Exception as e:
        print(f"❌ 发送 {demo_file_path} 失败: {e}")
        return False

def clear_directories():
    """清空input和received_jsons目录下的所有文件和子目录"""
    try:
        # 清空input目录
        if os.path.exists(DECODE_DIR):
            for filename in os.listdir(DECODE_DIR):
                file_path = os.path.join(DECODE_DIR, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print(f'❌ 删除 {file_path} 失败: {e}')
            print("✅ 已清空input目录")
        else:
            os.makedirs(DECODE_DIR, exist_ok=True)
        
        # 清空received_jsons目录
        if os.path.exists(SAVE_DIR):
            for filename in os.listdir(SAVE_DIR):
                file_path = os.path.join(SAVE_DIR, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print(f'❌ 删除 {file_path} 失败: {e}')
            print("✅ 已清空received_jsons目录")
        else:
            os.makedirs(SAVE_DIR, exist_ok=True)
        
        return True
    except Exception as e:
        print(f"❌ 清空目录失败: {e}")
        return False

def check_and_execute_import(ws):
    """检查input目录并执行相应的导入操作"""
    global received_count
    
    # 检查input目录是否有文件
    input_files = os.listdir(DECODE_DIR)
    has_files = len(input_files) > 0
    
    print(f"📁 input目录文件数量: {len(input_files)}")
    
    # 执行相应的导入操作
    if has_files:
        print("✅ input目录有文件，执行 import a")
        # 这里可以添加实际的导入代码
        import generate_by_txt
    else:
        print("✅ input目录没有文件，执行 import b")
        # 这里可以添加实际的导入代码
        import generate_by_png
    
    # 发送demo.json文件
    send_demo_json(ws)

def save_json_file(filename, content, ws):
    """保存 JSON 文件到 received_jsons，文件名完全由用户传入（不加后缀）"""
    global received_count
    
    # 1. 不再强制添加 .json
    save_path = os.path.join(SAVE_DIR, filename)

    try:
        # 2. 保存 JSON 内容
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(content, f, indent=4, ensure_ascii=False)

        print(f"✅ JSON 文件保存成功: {save_path}")

        # 3. 如果内容里包含 base64 文件，继续解码
        if isinstance(content, dict) and all(k in content for k in ('fileName', 'file', 'fileType')):
            print("检测到 base64 编码的文件内容，开始解码...")
            decode_base64_file(content)
        
        # 增加接收计数
        received_count += 1
        print(f"📊 已接收文件数量: {received_count}")
        
        # 当接收到第三个文件时执行特定操作
        if received_count == 3:
            print("🎯 接收到第三个文件，执行特定操作")
            check_and_execute_import(ws)

        return True
    except Exception as e:
        print(f"❌ 保存文件失败: {e}")
        return False

def on_message(ws, message):
    """接收到消息时的回调函数"""
    try:
        # 尝试解析JSON数据
        data = json.loads(message)
        
        # 情况1：消息包含完整文件信息
        if 'file_name' in data and 'file_content' in data:
            filename = data['file_name']
            content = data['file_content']
            print(f"收到JSON文件: {filename}")
            save_json_file(filename, content, ws)
        
        # 情况2：消息本身就是文件内容
        elif isinstance(data, (dict, list)):
            filename = f"data_{datetime.now().strftime('%H%M%S')}.json"
            print(f"收到JSON数据，使用默认文件名: {filename}")
            save_json_file(filename, data, ws)
        
        # 情况3：包含原始文件名和内容字段
        elif 'name' in data and 'content' in data:
            filename = data['name']
            content = data['content']
            print(f"收到JSON文件: {filename}")
            save_json_file(filename, content, ws)
        
        else:
            print(f"收到未识别格式的JSON消息: {data}")
    
    except json.JSONDecodeError:
        # 普通文本消息
        print(f"收到文本消息: {message}")
        
        # 尝试作为JSON文件保存
        try:
            parsed = json.loads(message)
            filename = f"textdata_{datetime.now().strftime('%H%M%S')}.json"
            save_json_file(filename, parsed, ws)
        except:
            print("消息不是有效JSON格式")

def on_error(ws, error):
    """发生错误时的回调函数"""
    print(f"发生错误: {error}")

def on_close(ws, close_status_code, close_msg):
    """连接关闭时的回调函数"""
    print("### 连接关闭 ###")
    print(f"关闭状态码: {close_status_code}")
    print(f"关闭原因: {close_msg or '无'}")

def on_open(ws):
    """连接建立时的回调函数"""
    print(f"### 连接已建立 @ {WS_URL} ###")
    
    def run():
        # 发送文件请求指令
        request = json.dumps({
            "action": "request_json_file",
            "client_id": str(uuid.uuid4())[:8],
            "timestamp": datetime.now().isoformat()
        })
        print(f"发送JSON文件请求: {request}")
        ws.send(request)
        
        # 保持连接打开以接收文件
        print("等待接收JSON文件...")
        # 无限循环，保持连接
        while True:
            time.sleep(60)  # 每分钟检查一次连接状态
            # 可以添加心跳包发送逻辑保持连接

    threading.Thread(target=run, daemon=True).start()

if __name__ == "__main__":
    print(f"准备接收JSON文件，保存到: {os.path.abspath(SAVE_DIR)}")
    print(f"解码后的文件将保存到: {os.path.abspath(DECODE_DIR)}")
    print("等待服务器发送JSON文件...")
    
    # 设置WebSocket连接
    ws = websocket.WebSocketApp(
        WS_URL,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    
    # 设置连接参数
    ws.run_forever(
        ping_interval=30,
        ping_timeout=10,
        reconnect=5
    )