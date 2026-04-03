const express = require('express');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = process.env.PORT || 3000;
const SNAPSHOT_PATH = path.join(__dirname, 'dashboard-data', 'snapshot.json');
const TASKS_PATH = path.join(__dirname, 'public', 'tasks.json');

// TWO-WAY SYNC SETUP:
// 1. Go to Render dashboard → cs-ceo-dashboard → Environment
// 2. Add DISCORD_WEBHOOK_URL = [your Discord webhook URL]
// 3. To get webhook URL: Discord → #ceo-benbot channel → Edit → Integrations → Webhooks → New Webhook → Copy URL
// 4. Once set, task completions and new tasks will post to #ceo-benbot automatically
const DISCORD_WEBHOOK_URL = process.env.DISCORD_WEBHOOK_URL || '';

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

// ═══════════════════════════════════════════
// Discord Webhook Helper
// ═══════════════════════════════════════════
async function postToDiscord(content) {
  if (!DISCORD_WEBHOOK_URL) {
    console.log('Discord webhook not configured — skipping notification');
    return;
  }
  try {
    const res = await fetch(DISCORD_WEBHOOK_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content })
    });
    if (!res.ok) console.log('Discord webhook error:', res.status);
  } catch (err) {
    console.log('Discord webhook failed:', err.message);
  }
}

function readTasks() {
  try {
    return JSON.parse(fs.readFileSync(TASKS_PATH, 'utf8'));
  } catch (err) {
    return { updated: new Date().toISOString(), tasks: [] };
  }
}

function writeTasks(data) {
  data.updated = new Date().toISOString();
  fs.writeFileSync(TASKS_PATH, JSON.stringify(data, null, 2));
}

// ═══════════════════════════════════════════
// GET /api/status
// ═══════════════════════════════════════════
app.get('/api/status', (req, res) => {
  const data = readTasks();
  res.json({
    webhookConfigured: !!DISCORD_WEBHOOK_URL,
    tasksCount: data.tasks ? data.tasks.length : 0
  });
});

// ═══════════════════════════════════════════
// POST /api/tasks/complete
// ═══════════════════════════════════════════
app.post('/api/tasks/complete', async (req, res) => {
  try {
    const { taskId, completedAt } = req.body;
    if (!taskId) return res.status(400).json({ error: 'taskId required' });

    const data = readTasks();
    const task = data.tasks.find(t => t.id === taskId);
    if (!task) return res.status(404).json({ error: 'Task not found' });

    task.status = 'done';
    task.completedAt = completedAt || new Date().toISOString().split('T')[0];
    task.updatedAt = new Date().toISOString().split('T')[0];
    writeTasks(data);

    // Post Discord notification
    await postToDiscord(
      `✅ Task completed from dashboard\n**${task.name}**\nCategory: ${task.category || 'general'} | Completed: ${task.completedAt}`
    );

    res.json({ success: true, task });
  } catch (err) {
    res.status(500).json({ error: 'Failed to complete task', detail: err.message });
  }
});

// ═══════════════════════════════════════════
// POST /api/tasks/update
// ═══════════════════════════════════════════
app.post('/api/tasks/update', async (req, res) => {
  try {
    const { taskId, updates } = req.body;
    if (!taskId) return res.status(400).json({ error: 'taskId required' });

    const data = readTasks();
    const task = data.tasks.find(t => t.id === taskId);
    if (!task) return res.status(404).json({ error: 'Task not found' });

    const oldStatus = task.status;
    Object.assign(task, updates, { updatedAt: new Date().toISOString().split('T')[0] });
    writeTasks(data);

    // Notify Discord if status changed
    if (updates.status && updates.status !== oldStatus) {
      await postToDiscord(
        `🔄 Task updated from dashboard\n**${task.name}**\nStatus: ${oldStatus} → ${updates.status}`
      );
    }

    res.json({ success: true, task });
  } catch (err) {
    res.status(500).json({ error: 'Failed to update task', detail: err.message });
  }
});

// ═══════════════════════════════════════════
// POST /api/tasks/add
// ═══════════════════════════════════════════
app.post('/api/tasks/add', async (req, res) => {
  try {
    const { name, priority, category, due, notes } = req.body;
    if (!name) return res.status(400).json({ error: 'name required' });

    const newTask = {
      id: 'u' + Date.now(),
      name,
      priority: priority || 'medium',
      category: category || 'general',
      due: due || '',
      notes: notes || '',
      status: 'todo',
      createdAt: new Date().toISOString().split('T')[0],
      updatedAt: new Date().toISOString().split('T')[0],
      completedAt: '',
      source: 'dashboard',
      subtasks: [],
      files: []
    };

    const data = readTasks();
    data.tasks.push(newTask);
    writeTasks(data);

    // Post Discord notification
    await postToDiscord(
      `📋 New task added from dashboard: **${name}** (${newTask.category}, ${newTask.priority})`
    );

    res.json({ success: true, task: newTask });
  } catch (err) {
    res.status(500).json({ error: 'Failed to add task', detail: err.message });
  }
});

app.listen(PORT, () => {
  console.log(`CS CEO Dashboard running on http://localhost:${PORT}`);
});
