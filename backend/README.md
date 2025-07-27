# Football Analytics Backend

## Ovisnosti

Instaliraj potrebne pakete:
```
pip install -r requirements.txt
```

## Pokretanje API-ja

Pokreni FastAPI server:
```
uvicorn main:app --reload
```

## Detekcija i praćenje
- Koristi YOLOv8 i DeepSORT za detekciju i praćenje igrača i lopte.
- Video ulaz: promijeni 'sample.mp4' u `main.py` na svoj video.

## WebSocket endpoint
- `/ws/positions` šalje pozicije igrača/lopte u realnom vremenu.

## Napomena
- Za precizno mapiranje koristi stvarne točke terena i slike u `homography.py`. 