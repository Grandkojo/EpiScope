import json
from channels.generic.websocket import AsyncWebsocketConsumer

class EpidemicDashboardConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def receive(self, text_data):
        data = json.loads(text_data)
        topic = data.get('topic')

        if topic in ['diabetes', 'cholera', 'meningitis']:
            await self.channel_layer.group_add(topic, self.channel_name)
        else:
            await self.send(text_data=json.dumps({'error': 'Invalid topic'}))

    async def disconnect(self, close_code):
        for topic in ['diabetes', 'cholera', 'meningitis']:
            await self.channel_layer.group_discard(topic, self.channel_name)

    async def send_data(self, event):
       await self.send(text_data=json.dumps({
           "topic": event['topic'],
           "data": event['data']
       }))