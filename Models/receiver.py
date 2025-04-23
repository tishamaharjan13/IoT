import asyncio
import cv2
from aiortc import RTCPeerConnection, RTCSessionDescription, MediaStreamTrack
from aiortc.contrib.signaling import TcpSocketSignaling
from av import VideoFrame
from datetime import datetime, timedelta

class VideoReceiver:
    def __init__(self):
        self.track = None

    async def handle_track(self, track):
        self.track = track
        while True:
            try:
                frame = await asyncio.wait_for(track.recv(), timeout=5.0)
                if isinstance(frame, VideoFrame):
                    frame = frame.to_ndarray(format="bgr24")

                timestamp = (datetime.now() - timedelta(seconds=55)).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                cv2.putText(frame, timestamp, (10, frame.shape[0] - 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

                cv2.imshow("Live Stream", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("Stream ended by user. Reconnecting...")
                    break
            except asyncio.TimeoutError:
                print("Timeout waiting for frame.")
            except Exception as e:
                print(f"Stream error: {e}")
                break

        cv2.destroyAllWindows()

async def run_receiver():
    signaling = TcpSocketSignaling("127.0.0.1", 9991)
    pc = RTCPeerConnection()
    receiver = VideoReceiver()

    @pc.on("track")
    def on_track(track):
        if isinstance(track, MediaStreamTrack):
            print(f"Receiving track: {track.kind}")
            asyncio.ensure_future(receiver.handle_track(track))

    await signaling.connect()
    print("Receiver connected, waiting for offer...")

    offer = await signaling.receive()
    await pc.setRemoteDescription(offer)
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)
    await signaling.send(pc.localDescription)

    while pc.connectionState != "connected":
        await asyncio.sleep(0.1)

    print("Connected. Streaming started.")
    while pc.connectionState == "connected":
        await asyncio.sleep(1)

    await signaling.close()
    await pc.close()

async def main():
    while True:
        try:
            await run_receiver()
        except Exception as e:
            print(f"Receiver error: {e}")
        print("🔁 Reconnecting in 2 seconds...\n")
        await asyncio.sleep(2)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nReceiver stopped by user.")
