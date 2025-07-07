# sender.py
import asyncio
import cv2
from aiortc import RTCPeerConnection, VideoStreamTrack
from av import VideoFrame
import fractions
from datetime import datetime
from aiohttp import web
import json

pcs = set()

class CameraStreamTrack(VideoStreamTrack):
    def __init__(self):
        super().__init__()
        self.cap = cv2.VideoCapture(0)
        self.frame_count = 0

    async def recv(self):
        ret, frame = self.cap.read()
        if not ret:
            raise Exception("Camera frame read failed")

        timestamp = datetime.now().strftime("%H:%M:%S")
        cv2.putText(frame, timestamp, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        video_frame = VideoFrame.from_ndarray(frame, format="rgb24")
        video_frame.pts = self.frame_count
        video_frame.time_base = fractions.Fraction(1, 30)
        self.frame_count += 1
        return video_frame

async def offer(request):
    params = await request.json()
    offer = params["offer"]

    pc = RTCPeerConnection()
    pcs.add(pc)
    pc.addTrack(CameraStreamTrack())

    await pc.setRemoteDescription(offer)
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return web.Response(content_type="application/json", text=json.dumps({
        "answer": {
            "sdp": pc.localDescription.sdp,
            "type": pc.localDescription.type
        }
    }))

async def on_shutdown(app):
    coros = [pc.close() for pc in pcs]
    await asyncio.gather(*coros)
    pcs.clear()

app = web.Application()
app.router.add_post("/offer", offer)
app.on_shutdown.append(on_shutdown)

web.run_app(app, port=9991)
