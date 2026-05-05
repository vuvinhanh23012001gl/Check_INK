
from fastapi import Request,WebSocket
from app.services.container import ServiceContainer

def get_services(request: Request) :
    return request.app.state.services

def get_services_ws(ws: WebSocket) :
    return ws.app.state.services

