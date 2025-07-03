import React, { useEffect, useState } from 'react';
import axios from 'axios';
import './App.css';

import { TextField, Button, MenuItem, AppBar, Toolbar, Typography, Container, Card, CardContent, Grid } from '@mui/material';

function App() {
  const [alerts, setAlerts] = useState([]);
  const [form, setForm] = useState({
    patient_id: '',
    type: 'medication',
    heart_rate: '',
    blood_pressure: '',
    mood_score: ''
  });

  useEffect(() => {
    axios.get('http://localhost:8000/alerts/')
      .then(res => setAlerts(res.data))
      .catch(err => console.error(err));
  }, []);

  // Store the latest AI advice after creating an alert
  const [aiAdvice, setAiAdvice] = useState(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    axios.post('http://localhost:8000/alerts/', form)
      .then(res => {
        setAiAdvice(res.data?.ai_advice || null);
        alert('Alert created!');
      })
      .catch(err => {
        setAiAdvice(null);
        alert('Error creating alert');
      });
  };

  return (
    <div className="App">
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Alert Dashboard
          </Typography>
        </Toolbar>
      </AppBar>
      <Container maxWidth="sm" sx={{ mt: 4 }}>
        <Card sx={{ mb: 4 }}>
          <CardContent>
            <Typography variant="h5" gutterBottom>
              Create Alert
            </Typography>
            <form onSubmit={handleSubmit}>
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <TextField
                    label="Patient ID"
                    fullWidth
                    value={form.patient_id}
                    onChange={e => setForm({ ...form, patient_id: e.target.value })}
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    select
                    label="Alert Type"
                    fullWidth
                    value={form.type}
                    onChange={e => setForm({ ...form, type: e.target.value })}
                  >
                    <MenuItem value="medication">Medication</MenuItem>
                    <MenuItem value="assistance">Assistance</MenuItem>
                    <MenuItem value="pain">Pain</MenuItem>
                    <MenuItem value="emergency">Emergency</MenuItem>
                  </TextField>
                </Grid>
                <Grid item xs={12} sm={4}>
                  <TextField
                    label="Heart Rate"
                    type="number"
                    fullWidth
                    value={form.heart_rate}
                    onChange={e => setForm({ ...form, heart_rate: e.target.value })}
                  />
                </Grid>
                <Grid item xs={12} sm={4}>
                  <TextField
                    label="Blood Pressure"
                    fullWidth
                    value={form.blood_pressure}
                    onChange={e => setForm({ ...form, blood_pressure: e.target.value })}
                  />
                </Grid>
                <Grid item xs={12} sm={4}>
                  <TextField
                    label="Mood Score"
                    type="number"
                    fullWidth
                    value={form.mood_score}
                    onChange={e => setForm({ ...form, mood_score: e.target.value })}
                  />
                </Grid>
                <Grid item xs={12}>
                  <Button type="submit" variant="contained" color="primary" fullWidth>
                    Create Alert
                  </Button>
                </Grid>
              </Grid>
            </form>
            {/* Show AI advice after alert creation */}
            {aiAdvice && (
              <Typography variant="subtitle1" color="secondary" sx={{ mt: 2 }}>
                AI Advice: {aiAdvice}
              </Typography>
            )}
          </CardContent>
        </Card>
        <Typography variant="h6" gutterBottom>Alerts</Typography>
        <Grid container spacing={2}>
          {alerts.map((alert, idx) => (
            <Grid item xs={12} key={idx}>
              <Card>
                <CardContent>
                  <Typography variant="subtitle1">
                    Patient: {alert.patient_id}, Type: {alert.type}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Heart Rate: {alert.heart_rate || 'N/A'} | Blood Pressure: {alert.blood_pressure || 'N/A'} | Mood Score: {alert.mood_score || 'N/A'}
                  </Typography>
                  {alert.ai_advice && (
                    <Typography variant="body2" color="primary" sx={{ mt: 1 }}>
                      AI Advice: {alert.ai_advice}
                    </Typography>
                  )}
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Container>
    </div>
  );
}

export default App;
