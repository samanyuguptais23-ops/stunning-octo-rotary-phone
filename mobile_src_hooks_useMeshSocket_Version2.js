import { useEffect, useRef, useState } from "react";
import { SERVER_URL } from "../config";

export function useMeshSocket(deviceId, onMessage) {
  const wsRef = useRef(null);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    if (!deviceId) return;

    const ws = new WebSocket(`${SERVER_URL.replace("http", "ws")}/ws/${deviceId}`);
    wsRef.current = ws;

    ws.onopen = () => setConnected(true);
    ws.onclose = () => setConnected(false);
    ws.onerror = () => setConnected(false);

    ws.onmessage = (event) => {
      try {
        onMessage?.(JSON.parse(event.data));
      } catch {}
    };

    return () => ws.close();
  }, [deviceId]);

  return { connected };
}