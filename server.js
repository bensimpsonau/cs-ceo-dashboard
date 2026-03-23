const express = require('express');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

// snapshot.json lives in dashboard-data/ inside the project root
const SNAPSHOT_PATH = path.join(__dirname, 'dashboard-data', 'snapshot.json');
const UPDATE_SECRET = process.env.DASHBOARD_UPDATE_SECRET || 'benbot2026';

app.use(express.json({ limit: '2mb' }));
app.use(express.static(path.join(__dirname, 'public')));

// ── GET /data ─────────────────────────────────────────────────────────────────
// Frontend polls this to get snapshot.json contents
app.get('/data', (req, res) => {
  try {
    if (!fs.existsSync(SNAPSHOT_PATH)) {
      return res.status(404).json({ error: 'snapshot not found' });
    }
    const raw = fs.readFileSync(SNAPSHOT_PATH, 'utf8');
    res.setHeader('Content-Type', 'application/json');
    res.send(raw);
  } catch (err) {
    console.error('GET /data error:', err.message);
    res.status(500).json({ error: 'failed to read snapshot' });
  }
});

// ── POST /update ──────────────────────────────────────────────────────────────
// BenBot pushes full snapshot JSON here
app.post('/update', (req, res) => {
  const auth = req.headers['authorization'] || '';
  if (auth !== `Bearer ${UPDATE_SECRET}`) {
    return res.status(401).json({ error: 'unauthorized' });
  }

  const data = req.body;
  if (!data || typeof data !== 'object') {
    return res.status(400).json({ error: 'invalid body' });
  }

  // Stamp server-side received time
  data._server_received = new Date().toISOString();

  try {
    fs.mkdirSync(path.dirname(SNAPSHOT_PATH), { recursive: true });
    fs.writeFileSync(SNAPSHOT_PATH, JSON.stringify(data, null, 2), 'utf8');
    console.log(`[${new Date().toISOString()}] snapshot updated`);
    res.json({ ok: true, updated: data._server_received });
  } catch (err) {
    console.error('POST /update error:', err.message);
    res.status(500).json({ error: 'failed to write snapshot' });
  }
});

// ── POST /refresh ─────────────────────────────────────────────────────────────
// "Refresh Now" button hits this — currently just acknowledges
app.post('/refresh', (req, res) => {
  console.log(`[${new Date().toISOString()}] refresh requested`);
  res.json({ ok: true, message: 'Refresh requested — BenBot will update within a few minutes.' });
});

// ── Serve index.html for all other routes ─────────────────────────────────────
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.listen(PORT, () => {
  console.log(`CEO Dashboard running on port ${PORT}`);
  console.log(`Snapshot path: ${SNAPSHOT_PATH}`);
});
