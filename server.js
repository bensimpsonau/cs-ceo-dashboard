const express = require('express');
const path = require('path');
const fs = require('fs');
const { execFile } = require('child_process');
const multer = require('multer');
const FormData = require('form-data');

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

// TRANSCRIPTION SETUP:
// Add OPENAI_API_KEY to Render environment variables (the same key used locally in ~/.zshenv)
// Required for the /api/transcribe endpoint used by Content Studio video upload

// GITHUB AUTO-SYNC SETUP:
// Add GITHUB_TOKEN to Render env vars (a GitHub Personal Access Token with repo write permissions)
// Generate at: github.com → Settings → Developer Settings → Personal Access Tokens → Fine-grained
// Required permissions: Contents (read & write) on bensimpsonau/cs-ceo-dashboard
// Once set, every task/content update on the dashboard auto-commits to GitHub

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

// ═══════════════════════════════════════════
// GitHub Auto-Sync
// Push tasks.json / content-board-data.json to GitHub on every write
// Requires GITHUB_TOKEN env var in Render
// ═══════════════════════════════════════════
async function pushFileToGitHub(filePath, content, commitMessage) {
  const GITHUB_TOKEN = process.env.GITHUB_TOKEN;
  if (!GITHUB_TOKEN) {
    console.log('GITHUB_TOKEN not set — skipping GitHub sync');
    return;
  }
  
  const repo = 'bensimpsonau/cs-ceo-dashboard';
  const branch = 'main';
  // Determine the relative path in the repo
  const repoPath = filePath.includes('content-board-data') 
    ? 'public/content-board-data.json'
    : 'public/tasks.json';
  const apiUrl = `https://api.github.com/repos/${repo}/contents/${repoPath}`;
  
  try {
    // Get current file SHA (required for update)
    const getRes = await fetch(apiUrl + `?ref=${branch}`, {
      headers: {
        'Authorization': `Bearer ${GITHUB_TOKEN}`,
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'cs-ceo-dashboard'
      }
    });
    
    if (!getRes.ok) {
      console.log('GitHub API GET failed:', getRes.status, await getRes.text());
      return;
    }
    
    const fileData = await getRes.json();
    const sha = fileData.sha;
    const encodedContent = Buffer.from(JSON.stringify(content, null, 2)).toString('base64');
    
    // Update file via GitHub API
    const putRes = await fetch(apiUrl, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${GITHUB_TOKEN}`,
        'Content-Type': 'application/json',
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'cs-ceo-dashboard'
      },
      body: JSON.stringify({
        message: commitMessage,
        content: encodedContent,
        sha: sha,
        branch: branch
      })
    });
    
    if (putRes.ok) {
      console.log(`GitHub sync: ${repoPath} committed`);
    } else {
      console.log('GitHub API PUT failed:', putRes.status, await putRes.text());
    }
  } catch (err) {
    console.log('GitHub sync error:', err.message);
  }
}

function readTasks() {
  try {
    return JSON.parse(fs.readFileSync(TASKS_PATH, 'utf8'));
  } catch (err) {
    return { updated: new Date().toISOString(), tasks: [] };
  }
}

async function writeTasks(data, commitMsg) {
  data.updated = new Date().toISOString();
  fs.writeFileSync(TASKS_PATH, JSON.stringify(data, null, 2));
  // Fire-and-forget GitHub sync
  pushFileToGitHub(TASKS_PATH, data, commitMsg || 'Auto-sync: tasks updated from dashboard').catch(e => console.log('GitHub sync failed:', e.message));
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
    await writeTasks(data, `Auto-sync: Task completed — ${task.name}`);

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
    await writeTasks(data, `Auto-sync: Task updated — ${task.name}`);

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
    await writeTasks(data, `Auto-sync: Task added — ${name}`);

    // Post Discord notification
    await postToDiscord(
      `📋 New task added from dashboard: **${name}** (${newTask.category}, ${newTask.priority})`
    );

    res.json({ success: true, task: newTask });
  } catch (err) {
    res.status(500).json({ error: 'Failed to add task', detail: err.message });
  }
});

// ═══════════════════════════════════════════
// Content Board — API Endpoints
// ═══════════════════════════════════════════
const CONTENT_BOARD_PATH = path.join(__dirname, 'public', 'content-board-data.json');
let contentBoard = { cards: [] };
try { contentBoard = JSON.parse(fs.readFileSync(CONTENT_BOARD_PATH, 'utf8')); } catch(e) {
  // Initialize with default cards if file doesn't exist
  contentBoard = { cards: [] };
}

// POST /api/content/status
app.post('/api/content/status', async (req, res) => {
  const { cardId, status, updatedAt } = req.body;
  const card = contentBoard.cards.find(c => c.id === cardId);
  if (card) {
    card.status = status;
    card.updatedAt = updatedAt;
    fs.writeFileSync(CONTENT_BOARD_PATH, JSON.stringify(contentBoard, null, 2));
    pushFileToGitHub(CONTENT_BOARD_PATH, contentBoard, `Auto-sync: Content ${status} — ${card ? card.title : 'updated'}`).catch(() => {});
    // Discord notification when content is posted
    if (DISCORD_WEBHOOK_URL && status === 'posted') {
      await postToDiscord(
        `📤 Content posted: **${card.title}**\nPlatform: ${card.platform} | Date: ${(updatedAt || '').split('T')[0]}`
      );
    }
  }
  res.json({ success: true });
});

// POST /api/content/add
app.post('/api/content/add', async (req, res) => {
  const { title, platform, type, copy, cta, status, scheduledDate } = req.body;
  const newCard = {
    id: 'c' + Date.now(),
    title,
    platform,
    type,
    copy: copy || '',
    cta: cta || '',
    status: status || 'draft',
    scheduledDate: scheduledDate || '',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  };
  contentBoard.cards.push(newCard);
  fs.writeFileSync(CONTENT_BOARD_PATH, JSON.stringify(contentBoard, null, 2));
  pushFileToGitHub(CONTENT_BOARD_PATH, contentBoard, `Auto-sync: Content added — ${title}`).catch(() => {});
  if (DISCORD_WEBHOOK_URL) {
    await postToDiscord(
      `📋 New content added: **${title}**\nPlatform: ${platform} | Status: ${status || 'draft'}`
    );
  }
  res.json({ success: true, card: newCard });
});

// GET /api/content/cards
app.get('/api/content/cards', (req, res) => {
  res.json(contentBoard);
});

// ═══════════════════════════════════════════
// POST /api/transcribe
// Accepts a video/audio file, extracts audio via ffmpeg, sends to Whisper API
// ═══════════════════════════════════════════
const transcribeUpload = multer({
  dest: '/tmp/cs-transcribe/',
  limits: { fileSize: 500 * 1024 * 1024 } // 500MB limit
});

app.post('/api/transcribe', transcribeUpload.single('file'), async (req, res) => {
  if (!req.file) return res.status(400).json({ error: 'No file uploaded' });

  const inputPath = req.file.path;
  const audioPath = inputPath + '.mp3';
  const OPENAI_API_KEY = process.env.OPENAI_API_KEY;

  if (!OPENAI_API_KEY) {
    fs.unlinkSync(inputPath);
    return res.status(500).json({ error: 'OPENAI_API_KEY not configured on server' });
  }

  try {
    // Step 1: Extract audio with ffmpeg
    await new Promise((resolve, reject) => {
      execFile('ffmpeg', [
        '-i', inputPath,
        '-vn',
        '-acodec', 'libmp3lame',
        '-q:a', '5',
        '-ac', '1',       // mono
        '-ar', '16000',   // 16kHz — optimal for Whisper
        audioPath,
        '-y'
      ], (err) => {
        if (err) reject(err); else resolve();
      });
    });

    // Step 2: Check file size — Whisper API limit is 25MB
    const audioStats = fs.statSync(audioPath);
    if (audioStats.size > 25 * 1024 * 1024) {
      // File too large — try lower bitrate re-encode
      const audioPath2 = inputPath + '_small.mp3';
      await new Promise((resolve, reject) => {
        execFile('ffmpeg', [
          '-i', audioPath,
          '-acodec', 'libmp3lame',
          '-q:a', '9',
          '-ac', '1',
          '-ar', '16000',
          audioPath2,
          '-y'
        ], (err) => {
          if (err) reject(err); else resolve();
        });
      });
      fs.unlinkSync(audioPath);
      fs.renameSync(audioPath2, audioPath);
    }

    // Step 3: Send to OpenAI Whisper
    const form = new FormData();
    form.append('file', fs.createReadStream(audioPath), {
      filename: 'audio.mp3',
      contentType: 'audio/mpeg'
    });
    form.append('model', 'whisper-1');
    form.append('language', 'en');

    const whisperRes = await fetch('https://api.openai.com/v1/audio/transcriptions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${OPENAI_API_KEY}`,
        ...form.getHeaders()
      },
      body: form
    });

    if (!whisperRes.ok) {
      const err = await whisperRes.text();
      throw new Error(`Whisper API error: ${whisperRes.status} ${err}`);
    }

    const result = await whisperRes.json();
    res.json({ transcript: result.text });

  } catch (err) {
    console.error('Transcription error:', err.message);
    res.status(500).json({ error: 'Transcription failed', detail: err.message });
  } finally {
    // Cleanup temp files
    try { fs.unlinkSync(inputPath); } catch(e) {}
    try { fs.unlinkSync(audioPath); } catch(e) {}
  }
});

// ──────────────────────────────────────────────────────
// POST /api/blueprint-email
// Captures lead from allocation blueprint quiz
// ──────────────────────────────────────────────────────
app.post('/api/blueprint-email', (req, res) => {
  const { name, email, answers, score } = req.body;
  if (!name || !email) {
    return res.status(400).json({ error: 'Name and email are required' });
  }
  // TODO: Wire up email sending (see EMAIL SEQUENCE below)
  // For now, log the lead and return success
  console.log(`[Blueprint Lead] ${name} <${email}> | Score: ${score} | Answers:`, JSON.stringify(answers));
  res.json({ ok: true });
});

// EMAIL SEQUENCE:
// Email 1 (immediate): Subject: "Your Digital Asset Blueprint — [First Name]"
//   Body: personalized score + blueprint sections as HTML
//   Include: score number, protection gap label, exchange list, storage approach, security checklist, tax tools, CTA to book strategy call
// Email 2 (day 2 follow-up): Subject: "How sophisticated investors are allocating to digital assets"
//   Body: 3-paragraph educational email about institutional allocation trends (BlackRock 1-2%, Bitwise 5%, etc.)
//   CTA: Watch the free VSL → https://collectiveshift.io/vsl (placeholder)
// Implementation: Use SendGrid, Mailgun, or Resend (add SENDGRID_API_KEY or RESEND_API_KEY to Render env vars)

app.listen(PORT, () => {
  console.log(`CS CEO Dashboard running on http://localhost:${PORT}`);
});
