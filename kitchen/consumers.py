import json
from channels.generic.websocket import AsyncWebsocketConsumer


class KitchenConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'kitchen'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'order_update',
                'data': data
            }
        )
    
    async def order_update(self, event):
        await self.send(text_data=json.dumps(event['data']))


class DisplayConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'display'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'order_update',
                'data': data
            }
        )
    
    async def order_update(self, event):
        await self.send(text_data=json.dumps(event['data']))
