from datetime import datetime
import json
from tornado.websocket import WebSocketHandler

# WebSocket Handler for log broadcasting
class LogWebSocketHandler(WebSocketHandler):
    clients = set()
    
    def check_origin(self, origin):
        return True
        
    def open(self):
        LogWebSocketHandler.clients.add(self)
        
    def on_close(self):
        LogWebSocketHandler.clients.remove(self)

def broadcast_log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_message = f"{message}"
    for client in LogWebSocketHandler.clients:
        client.write_message(json.dumps({"log": formatted_message}))