const express = require('express');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = process.env.PORT || 3000;
const SNAPSHOT_PATH = path.join(__dirname, 'dashboard-data', 'snapshot.json');

// Basic auth for the entire CEO dashboard
const AUTH_USER = process.env.AUTH_USER || 'ben';
const AUTH_PASS = process.env.AUTH_PASS || 'cs2026ceo';

app.use((req, res, next) => {
  const auth = req.headers['authorization'];
  if (!auth || !auth.startsWith('Basic ')) {
    res.set('WWW-Authenticate', 'Basic realm="CS CEO Dashboard"');
    return res.status(401).send('Authentication required');
  }
  const decoded = Buffer.from(auth.split(' ')[1], 'base64').toString();
  const [user, pass] = decoded.split(':');
  if (user === AUTH_USER && pass === AUTH_PASS) {
    return next();
  }
  res.set('WWW-Authenticate', 'Basic realm="CS CEO Dashboard"');
  return res.status(401).send('Invalid credentials');
});

app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));
app.use('/slides', express.static(path.join(__dirname, 'slides')));

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
