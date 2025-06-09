from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from typing import List, Dict, Optional
from pydantic import BaseModel
import json
import asyncio
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/ws",
    tags=["websocket"],
    responses={
        404: {"description": "Not found"},
        1008: {"description": "Policy violation - Invalid client type"}
    }
)

class WebSocketMessage(BaseModel):
    """Base model for WebSocket messages"""
    type: str
    data: dict
    timestamp: Optional[str] = None

class WebSocketResponse(BaseModel):
    """Base model for WebSocket responses"""
    type: str
    data: dict
    timestamp: str
    error: Optional[str] = None

class ConnectionManager:
    def __init__(self):
        # Store active connections
        self.active_connections: Dict[str, List[WebSocket]] = {
            "diabetes": [],
            "malaria": [],
            "monitoring": []
        }
    
    async def connect(self, websocket: WebSocket, client_type: str):
        await websocket.accept()
        self.active_connections[client_type].append(websocket)
        logger.info(f"New {client_type} client connected. Total connections: {len(self.active_connections[client_type])}")
    
    def disconnect(self, websocket: WebSocket, client_type: str):
        self.active_connections[client_type].remove(websocket)
        logger.info(f"{client_type} client disconnected. Remaining connections: {len(self.active_connections[client_type])}")
    
    async def broadcast(self, message: dict, client_type: str):
        for connection in self.active_connections[client_type]:
            try:
                await connection.send_json(message)
            except WebSocketDisconnect:
                self.disconnect(connection, client_type)
            except Exception as e:
                logger.error(f"Error broadcasting to {client_type} client: {str(e)}")

manager = ConnectionManager()

@router.websocket("/monitor/{client_type}")
async def websocket_endpoint(
    websocket: WebSocket,
    client_type: str,
    response_model=WebSocketResponse
):
    """
    WebSocket endpoint for real-time disease monitoring
    
    Parameters:
    - client_type: Type of monitoring client (diabetes, malaria, or monitoring)
    
    Returns:
    - WebSocket connection with real-time updates
    
    Example WebSocket message format:
    ```json
    {
        "type": "update",
        "data": {
            "location": "Accra",
            "cases": 10,
            "risk_level": "high"
        }
    }
    ```
    """
    if client_type not in manager.active_connections:
        await websocket.close(code=1008)  # Policy Violation
        return
    
    await manager.connect(websocket, client_type)
    try:
        while True:
            # Wait for messages from the client
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                # Validate message format
                ws_message = WebSocketMessage(**message)
                
                # Process the message and broadcast updates
                response = WebSocketResponse(
                    timestamp=datetime.now().isoformat(),
                    type="update",
                    data=ws_message.data
                )
                await manager.broadcast(response.dict(), client_type)
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON received from {client_type} client")
                error_response = WebSocketResponse(
                    timestamp=datetime.now().isoformat(),
                    type="error",
                    data={},
                    error="Invalid JSON format"
                )
                await websocket.send_json(error_response.dict())
            except Exception as e:
                logger.error(f"Error processing message: {str(e)}")
                error_response = WebSocketResponse(
                    timestamp=datetime.now().isoformat(),
                    type="error",
                    data={},
                    error=str(e)
                )
                await websocket.send_json(error_response.dict())
    except WebSocketDisconnect:
        manager.disconnect(websocket, client_type)
    except Exception as e:
        logger.error(f"Error in websocket connection: {str(e)}")
        manager.disconnect(websocket, client_type)

async def send_disease_update(disease_type: str, data: dict):
    """
    Function to send real-time updates to connected clients
    
    Parameters:
    - disease_type: Type of disease (diabetes or malaria)
    - data: Dictionary containing update information
    
    Example usage:
    ```python
    await send_disease_update("diabetes", {
        "location": "Accra",
        "cases": 10,
        "risk_level": "high"
    })
    ```
    """
    message = WebSocketResponse(
        timestamp=datetime.now().isoformat(),
        type="disease_update",
        data=data
    )
    await manager.broadcast(message.dict(), disease_type) 