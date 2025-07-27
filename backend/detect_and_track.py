import cv2
import numpy as np
from ultralytics import YOLO

# Inicijalizacija modela
model = YOLO('yolov8n.pt')  # Može se zamijeniti custom modelom za nogomet

# Kategorije koje nas zanimaju (ovisno o modelu)
PLAYER_CLASSES = [0]  # Pretpostavka: 0 = osoba
BALL_CLASS = 32      # Pretpostavka: 32 = sportska lopta (COCO dataset)

# Poboljšani tracker koristeći OpenCV
class SimpleTracker:
    def __init__(self):
        self.next_id = 1
        self.tracks = {}
        self.max_disappeared = 5  # Smanjeno za brže reagiranje
        self.max_distance = 50    # Smanjeno za preciznije mapiranje
        
    def update(self, detections):
        # Ako nema postojećih trackova, dodaj sve detekcije
        if not self.tracks:
            for det in detections:
                self.tracks[self.next_id] = {
                    'bbox': det['bbox'],
                    'class_id': det['class_id'],
                    'disappeared': 0
                }
                self.next_id += 1
            return list(self.tracks.keys())
        
        # Poboljšano mapiranje - najbliži track dobiva detekciju
        used_tracks = set()
        used_detections = set()
        
        for track_id, track in self.tracks.items():
            if track_id in used_tracks:
                continue
                
            best_distance = float('inf')
            best_detection = None
            
            for i, det in enumerate(detections):
                if i in used_detections:
                    continue
                    
                # Izračunaj udaljenost između centara
                track_center = np.array([
                    (track['bbox'][0] + track['bbox'][2]) / 2,
                    (track['bbox'][1] + track['bbox'][3]) / 2
                ])
                det_center = np.array([
                    (det['bbox'][0] + det['bbox'][2]) / 2,
                    (det['bbox'][1] + det['bbox'][3]) / 2
                ])
                
                distance = np.linalg.norm(track_center - det_center)
                if distance < best_distance and distance < self.max_distance:
                    best_distance = distance
                    best_detection = i
            
            if best_detection is not None:
                # Ažuriraj track
                self.tracks[track_id]['bbox'] = detections[best_detection]['bbox']
                self.tracks[track_id]['disappeared'] = 0
                used_tracks.add(track_id)
                used_detections.add(best_detection)
            else:
                # Povećaj broj frameova bez detekcije
                self.tracks[track_id]['disappeared'] += 1
        
        # Dodaj nove detekcije
        for i, det in enumerate(detections):
            if i not in used_detections:
                self.tracks[self.next_id] = {
                    'bbox': det['bbox'],
                    'class_id': det['class_id'],
                    'disappeared': 0
                }
                self.next_id += 1
        
        # Ukloni trackove koji su nestali predugo
        tracks_to_remove = []
        for track_id, track in self.tracks.items():
            if track['disappeared'] > self.max_disappeared:
                tracks_to_remove.append(track_id)
        
        for track_id in tracks_to_remove:
            del self.tracks[track_id]
        
        return list(self.tracks.keys())

# Globalni tracker
tracker = SimpleTracker()

def detect_and_track(frame):
    results = model(frame, conf=0.5)  # Dodan confidence threshold
    detections = []
    
    for r in results:
        boxes = r.boxes
        if boxes is not None:
            for box in boxes:
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                if cls in PLAYER_CLASSES or cls == BALL_CLASS:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    detections.append({
                        'bbox': [x1, y1, x2, y2],
                        'class_id': cls
                    })
    
    # Ažuriraj tracker
    active_tracks = tracker.update(detections)
    
    # Vrati rezultate
    output = []
    for track_id in active_tracks:
        track = tracker.tracks[track_id]
        output.append({
            'id': track_id,
            'bbox': track['bbox'],
            'class_id': track['class_id']
        })
    
    return output

# Primjer korištenja s videom
if __name__ == '__main__':
    cap = cv2.VideoCapture(0)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        objects = detect_and_track(frame)
        # Prikaz rezultata (za debug)
        for obj in objects:
            x1, y1, x2, y2 = map(int, obj['bbox'])
            color = (0, 255, 0) if obj['class_id'] in PLAYER_CLASSES else (0, 0, 255)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, f"ID:{obj['id']}", (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        cv2.imshow('Detection', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows() 