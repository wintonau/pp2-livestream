import asyncio
import logging
from aiohttp import web
from aiortc import RTCPeerConnection, RTCSessionDescription

# Configure logging
logging.basicConfig(level=logging.INFO)

pcs = set()  # Set to keep track of peer connections

async def index(request):
    return web.Response(text="WebRTC Signaling Server is running.", content_type="text/plain")

async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    pc = RTCPeerConnection()
    pcs.add(pc)

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        if pc.connectionState == "failed":
            await pc.close()
            pcs.discard(pc)

    try:
        async for msg in ws:
            if msg.type == web.WSMsgType.TEXT:
                data = msg.json()
                if data["type"] == "offer":
                    offer = RTCSessionDescription(sdp=data["sdp"], type=data["type"])
                    await pc.setRemoteDescription(offer)
                    answer = await pc.createAnswer()
                    await pc.setLocalDescription(answer)
                    # Send answer back to client
                    await ws.send_json({
                        "sdp": pc.localDescription.sdp,
                        "type": pc.localDescription.type
                    })
                elif data["type"] == "candidate":
                    candidate = data["candidate"]
                    await pc.addIceCandidate(candidate)
    except Exception as e:
        logging.error(f"Error: {e}")
    finally:
        await pc.close()
        pcs.discard(pc)

    return ws

async def cleanup(app):
    # Close peer connections on shutdown
    coros = [pc.close() for pc in pcs]
    await asyncio.gather(*coros)

# Define the app and routes
app = web.Application()
app.router.add_get("/", index)
app.router.add_get("/ws", websocket_handler)
app.on_shutdown.append(cleanup)

# Run the server
if __name__ == "__main__":
    web.run_app(app, port=8080)
