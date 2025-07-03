const express = require('express');
const axios = require('axios');
const cors = require('cors');

const app = express();
app.use(cors());
app.use(express.json());

// Proxy endpoint to get alerts from FastAPI backend
app.get('/api/alerts', async (req, res) => {
  try {
    // Replace with your FastAPI backend URL
    const response = await axios.get('http://localhost:8000/alerts');
    res.json(response.data);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch alerts' });
  }
});

// Proxy endpoint to create a new alert
app.post('/api/alerts', async (req, res) => {
  try {
    const response = await axios.post('http://localhost:8000/alerts/', req.body);
    res.json(response.data);
  } catch (error) {
    res.status(500).json({ error: 'Failed to create alert' });
  }
});

app.listen(3001, () => {
  console.log('Node.js proxy server running on http://localhost:3001');
});