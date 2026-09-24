import { useEffect, useRef } from "react";

type Props = {
  origem: { latitude: number; longitude: number };
  destino: { latitude: number; longitude: number };
  geometria?: number[][]; // [lon, lat][]
  altura?: number;
};

declare global {
  interface Window {
    L?: any;
  }
}

function loadLeaflet(): Promise<any> {
  if (window.L) return Promise.resolve(window.L);
  return new Promise((resolve, reject) => {
    const cssId = "leaflet-css";
    if (!document.getElementById(cssId)) {
      const link = document.createElement("link");
      link.id = cssId;
      link.rel = "stylesheet";
      link.href = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.css";
      document.head.appendChild(link);
    }
    const script = document.createElement("script");
    script.src = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.js";
    script.async = true;
    script.onload = () => resolve(window.L);
    script.onerror = () => reject(new Error("Falha ao carregar Leaflet."));
    document.body.appendChild(script);
  });
}

/** Mapa gratuito (OpenStreetMap + Leaflet). Sem chave Google. */
export default function MapaRota({ origem, destino, geometria = [], altura = 280 }: Props) {
  const ref = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    let map: any;
    let cancelled = false;

    void (async () => {
      try {
        const L = await loadLeaflet();
        if (cancelled || !ref.current) return;

        const latO = Number(origem.latitude);
        const lonO = Number(origem.longitude);
        const latD = Number(destino.latitude);
        const lonD = Number(destino.longitude);

        map = L.map(ref.current).setView([latO, lonO], 13);
        L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
          attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
          maxZoom: 19,
        }).addTo(map);

        const casa = L.marker([latO, lonO]).addTo(map).bindPopup("Residência do aluno");
        const escola = L.marker([latD, lonD]).addTo(map).bindPopup("Escola");

        const latLngs =
          geometria.length >= 2
            ? geometria.map((pair) => [Number(pair[1]), Number(pair[0])] as [number, number])
            : [
                [latO, lonO] as [number, number],
                [latD, lonD] as [number, number],
              ];

        const line = L.polyline(latLngs, { color: "#e76f51", weight: 4 }).addTo(map);
        map.fitBounds(line.getBounds().extend(casa.getLatLng()).extend(escola.getLatLng()), { padding: [24, 24] });
        setTimeout(() => {
          if (!cancelled && map) map.invalidateSize();
        }, 80);
      } catch (error) {
        if (ref.current) {
          ref.current.textContent = error instanceof Error ? error.message : "Falha ao carregar o mapa.";
        }
      }
    })();

    return () => {
      cancelled = true;
      if (map) map.remove();
    };
  }, [origem.latitude, origem.longitude, destino.latitude, destino.longitude, geometria]);

  return <div ref={ref} className="mapa-rota" style={{ height: altura }} />;
}
