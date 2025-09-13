"""
    将数据发送出去
"""
import websocket
import json
import time

WS_URL = "ws://72920e93.r29.cpolar.top/ws"
JSON_FILE = "demo.json"

def on_open(ws):
    try:
        with open(JSON_FILE, "rb") as f:        # 以二进制方式直接读
            raw = f.read()
        ws.send(raw)                            # 直接发原始字节
        print(f"✅ 已发送 {JSON_FILE} ({len(raw)} bytes)")
    except Exception as e:
        print("❌ 发送失败:", e)
    finally:
        time.sleep(0.5)
        ws.close()

def on_error(ws, error):
    print("发生错误:", error)

def on_close(ws, a, b):
    print("### 连接关闭 ###")

if __name__ == "__main__":
    ws = websocket.WebSocketApp(
        WS_URL,
        on_open=on_open,
        on_error=on_error,
        on_close=on_close
    )
    ws.run_forever()