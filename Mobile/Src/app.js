import React, { useEffect, useState } from 'react';
import axios from 'axios';

function App() {
  const [alerts, setAlerts] = useState([]);
  const [form, setForm] = useState({ patient_id: '', type: 'medication' });

  useEffect(() => {
    // Fetch alerts from Node.js backend
    axios.get('http://localhost:3001/api/alerts')
      .then(res => setAlerts(res.data))
      .catch(err => console.error(err));
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    axios.post('http://localhost:3001/api/alerts', form)
      .then(res => alert('Alert created!'))
      .catch(err => alert('Error creating alert'));
  };

  return (
    <div>
      <h1>Alert Dashboard</h1>
      <form onSubmit={handleSubmit}>
        <input
          placeholder="Patient ID"
          value={form.patient_id}
          onChange={e => setForm({ ...form, patient_id: e.target.value })}
        />
        <select
          value={form.type}
          onChange={e => setForm({ ...form, type: e.target.value })}
        >
          <option value="medication">Medication</option>
          <option value="assistance">Assistance</option>
          <option value="pain">Pain</option>
          <option value="emergency">Emergency</option>
        </select>
        <button type="submit">Create Alert</button>
      </form>
      <h2>Alerts</h2>
      <ul>
        {alerts.map((alert, idx) => (
          <li key={idx}>
            Patient: {alert.patient_id}, Type: {alert.type}, Context: {alert.emotional_context}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default App;