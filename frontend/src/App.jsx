import React, { useEffect, useRef, useState } from 'react';

const FIELD_WIDTH = 1050; // px (10x veće od metara radi prikaza)
const FIELD_HEIGHT = 680;

const TEAM1_COLOR = '#e74c3c'; // crveni
const TEAM2_COLOR = '#3498db'; // plavi
const BALL_COLOR = '#FFD700';

function getTeamColor(obj) {
  if (obj.class_id === 32) return BALL_COLOR;
  return obj.id % 2 === 0 ? TEAM1_COLOR : TEAM2_COLOR;
}

function drawField(ctx) {
  ctx.fillStyle = '#228B22';
  ctx.fillRect(0, 0, FIELD_WIDTH, FIELD_HEIGHT);
  ctx.strokeStyle = '#fff';
  ctx.lineWidth = 2;
  ctx.strokeRect(0, 0, FIELD_WIDTH, FIELD_HEIGHT);
  ctx.beginPath();
  ctx.arc(FIELD_WIDTH/2, FIELD_HEIGHT/2, 91.5/105*FIELD_WIDTH, 0, 2*Math.PI);
  ctx.stroke();
  ctx.beginPath();
  ctx.moveTo(FIELD_WIDTH/2, 0);
  ctx.lineTo(FIELD_WIDTH/2, FIELD_HEIGHT);
  ctx.stroke();
}

function drawPlayers(ctx, players) {
  players.forEach(p => {
    ctx.beginPath();
    ctx.arc(p.x*10, p.y*10, p.class_id === 32 ? 8 : 14, 0, 2*Math.PI);
    ctx.fillStyle = getTeamColor(p);
    ctx.fill();
    ctx.strokeStyle = '#fff';
    ctx.stroke();
    ctx.font = 'bold 14px Arial';
    ctx.fillStyle = '#fff';
    ctx.fillText(`#${p.id}`, p.x*10-10, p.y*10-16);
  });
}

export default function App() {
  const canvasRef = useRef();
  const [players, setPlayers] = useState([]);

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/ws/positions');
    ws.onmessage = (e) => {
      const data = JSON.parse(e.data);
      setPlayers(data);
    };
    return () => ws.close();
  }, []);

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    drawField(ctx);
    drawPlayers(ctx, players);
  }, [players]);

  return (
    <div style={{textAlign: 'center', marginTop: 20}}>
      <h2>Football Analytics 2D Prikaz</h2>
      <div style={{marginBottom: 10}}>
        <span style={{color: TEAM1_COLOR, fontWeight: 'bold'}}>●</span> Tim 1 &nbsp;
        <span style={{color: TEAM2_COLOR, fontWeight: 'bold'}}>●</span> Tim 2 &nbsp;
        <span style={{color: BALL_COLOR, fontWeight: 'bold'}}>●</span> Lopta
      </div>
      <canvas ref={canvasRef} width={FIELD_WIDTH} height={FIELD_HEIGHT} style={{border: '2px solid #333'}} />
    </div>
  );
} 