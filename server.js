const express = require('express');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = process.env.PORT || 3000;
const SNAPSHOT_PATH = path.join(__dirname, 'dashboard-data', 'snapshot.json');

app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// GET /api/snapshot
app.get('/api/snapshot', (req, res) => {
  try {
    const data = fs.readFileSync(SNAPSHOT_PATH, 'utf8');
    res.json(JSON.parse(data));
  } catch (err) {
    res.status(500).json({ error: 'Could not read snapshot', detail: err.message });
  }
});

// POST /update — auth: Bearer benbot2026
app.post('/update', (req, res) => {
  const auth = req.headers['authorization'] || '';
  if (auth !== 'Bearer benbot2026') {
    return res.status(401).json({ error: 'Unauthorized' });
  }
  try {
    const current = JSON.parse(fs.readFileSync(SNAPSHOT_PATH, 'utf8'));
    const merged = Object.assign({}, current, req.body, { last_updated: new Date().toISOString() });
    fs.writeFileSync(SNAPSHOT_PATH, JSON.stringify(merged, null, 2));
    res.json({ ok: true, last_updated: merged.last_updated });
  } catch (err) {
    res.status(500).json({ error: 'Could not write snapshot', detail: err.message });
  }
});

app.listen(PORT, () => {
  console.log(`CS CEO Dashboard running on http://localhost:${PORT}`);
});
