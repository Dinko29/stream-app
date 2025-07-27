from fastapi import FastAPI, WebSocket
import cv2
import asyncio
from detect_and_track import detect_and_track
from homography import get_homography, map_point

app = FastAPI()

# Dummy homografija (treba postaviti stvarne točke)
src_points = [(0,0), (1280,0), (1280,720), (0,720)]
dst_points = [(0,0), (105,0), (105,68), (0,68)]  # Dimenzije terena u metrima
H = get_homography(src_points, dst_points)

@app.websocket('/ws/positions')
async def positions_ws(websocket: WebSocket):
    await websocket.accept()
    
    # Pokušaj otvoriti virtualnu kameru
    cap = cv2.VideoCapture(0)
    
    # Provjeri je li kamera uspješno otvorena
    if not cap.isOpened():
        print("Greška: Ne mogu otvoriti kameru s indeksom 0")
        # Pokušaj s drugim indeksima
        for i in range(1, 5):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                print(f"Uspješno otvorena kamera s indeksom {i}")
                break
        if not cap.isOpened():
            print("Greška: Nije pronađena dostupna kamera")
            await websocket.close()
            return
    
    print("Kamera uspješno otvorena!")
    print(f"Rezolucija: {int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x{int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}")
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Greška: Ne mogu čitati frame iz kamere")
                break
                
            # Debug: prikaži frame u prozoru
            cv2.imshow('Debug: Camera Feed', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
            objects = detect_and_track(frame)
            mapped = []
            for obj in objects:
                x1, y1, x2, y2 = obj['bbox']
                cx, cy = int((x1+x2)/2), int((y1+y2)/2)
                mx, my = map_point((cx, cy), H)
                mapped.append({
                    'id': obj['id'],
                    'class_id': obj['class_id'],
                    'x': mx,
                    'y': my
                })
            
            await websocket.send_json(mapped)
            await asyncio.sleep(0.04)  # ~25 FPS
            
    except Exception as e:
        print(f"Greška u WebSocket komunikaciji: {e}")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        await websocket.close()

@app.get("/")
async def root():
    return {"message": "Football Analytics Backend je pokrenut"}

@app.get("/test-camera")
async def test_camera():
    """Test endpoint za provjeru dostupnih kamera"""
    available_cameras = []
    for i in range(5):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            available_cameras.append({
                "index": i,
                "resolution": f"{width}x{height}"
            })
            cap.release()
    return {"available_cameras": available_cameras} 