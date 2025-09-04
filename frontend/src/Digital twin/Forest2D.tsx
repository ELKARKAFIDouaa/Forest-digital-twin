import React from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';

interface Props {
  forestId: number;
}

const mockSensors = [
  { id: 1, name: 'Sensor A', lat: 34.05, lng: -6.82, value: 24 },
  { id: 2, name: 'Sensor B', lat: 34.07, lng: -6.84, value: 21 },
];

const Forest2D: React.FC<Props> = ({ forestId }) => {
  return (
    <MapContainer center={[34.05, -6.82]} zoom={13} className="h-full w-full">
      <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      {mockSensors.map((sensor) => (
        <Marker key={sensor.id} position={[sensor.lat, sensor.lng]}>
          <Popup>
            {sensor.name}: {sensor.value}°C
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  );
};

export default Forest2D;
