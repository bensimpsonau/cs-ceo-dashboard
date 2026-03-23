const express = require('express');
const fetch = require('node-fetch');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 4200;
const DASHBOARD_PASSWORD = process.env.DASHBOARD_PASSWORD || 'collectiveshift';
const WHOP_API_KEY = process.env.WHOP_API_KEY || '';
const NOTION_API_KEY = process.env.NOTION_API_KEY || '';
const NOTION_DB_ID = '2e73d88f-86fe-800b-a904-ea214244bb57';
const DATA_DIR = process.env.DATA_DIR ? path.resolve(process.env.DATA_DIR) : path.join(__dirname, 'dashboard-data');

app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// Simple auth middleware for API routes
function authMiddleware(req, res, next) {
  const token = req.headers['x-dashboard-token'] || req.query.token;
  if (token === DASHBOARD_PASSWORD) return next();
  res.status(401).json({ error: 'Unauthorized' });
}

// ---------- Helpers ----------

function readJsonFile(filePath) {
  try {
    const raw = fs.readFileSync(filePath, 'utf8');
    return JSON.parse(raw);
  } catch (e) {
    return null;
  }
}

async function fetchBtcPrice() {
  try {
    const res = await fetch(
      'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd',
      { timeout: 8000 }
    );
    const data = await res.json();
    return data?.bitcoin?.usd ?? null;
  } catch (e) {
    console.error('BTC fetch error:', e.message);
    return null;
  }
}

async function fetchFearGreed() {
  try {
    const res = await fetch('https://api.alternative.me/fng/?limit=1', { timeout: 8000 });
    const data = await res.json();
    const item = data?.data?.[0];
    return item ? { value: item.value, classification: item.value_classification } : null;
  } catch (e) {
    console.error('Fear/Greed fetch error:', e.message);
    return null;
  }
}

async function fetchNotionTasks() {
  if (!NOTION_API_KEY) return { error: 'No Notion API key configured' };
  try {
    const now = new Date();
    const endOfWeek = new Date(now);
    endOfWeek.setDate(now.getDate() + (7 - now.getDay()));
    const todayStr = now.toISOString().split('T')[0];
    const endOfWeekStr = endOfWeek.toISOString().split('T')[0];

    const res = await fetch(`https://api.notion.com/v1/databases/${NOTION_DB_ID}/query`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${NOTION_API_KEY}`,
        'Notion-Version': '2022-06-28',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        page_size: 100,
        sorts: [{ property: 'Due date', direction: 'ascending' }]
      }),
      timeout: 10000
    });

    if (!res.ok) {
      const errText = await res.text();
      console.error('Notion error:', res.status, errText);
      return { error: `Notion API error: ${res.status}` };
    }

    const data = await res.json();
    const results = data.results || [];

    const tasks = results.map(page => {
      const props = page.properties || {};

      // Extract task name — actual property: "Task name"
      const nameVal = props['Task name'] || props['Name'] || props['Task'] || props['Title'] || props['title'];
      let name = 'Untitled';
      if (nameVal?.title?.length > 0) name = nameVal.title.map(t => t.plain_text).join('');

      // Extract status — actual property: "Status" (type: status)
      const statusVal = props['Status'] || props['status'];
      let status = 'Unknown';
      if (statusVal?.status?.name) status = statusVal.status.name;
      else if (statusVal?.select?.name) status = statusVal.select.name;

      // Extract due date — actual property: "Due date"
      const dueDateVal = props['Due date'] || props['Due Date'] || props['Due'] || props['date'];
      let dueDate = null;
      if (dueDateVal?.date?.start) dueDate = dueDateVal.date.start;

      // Extract assignee — actual property: "Assignee" (type: people)
      const assigneeVal = props['Assignee'] || props['Owner'] || props['Assigned To'] || props['Person'];
      let assignee = null;
      if (assigneeVal?.people?.length > 0) {
        assignee = assigneeVal.people.map(p => p.name || p.id).join(', ');
      }

      return { id: page.id, name, status, dueDate, assignee, url: page.url };
    });

    const overdue = tasks.filter(t =>
      t.dueDate && t.dueDate < todayStr &&
      !['Done', 'Complete', 'Completed', 'Cancelled', 'Canceled'].includes(t.status)
    );

    const dueThisWeek = tasks.filter(t =>
      t.dueDate && t.dueDate >= todayStr && t.dueDate <= endOfWeekStr &&
      !['Done', 'Complete', 'Completed', 'Cancelled', 'Canceled'].includes(t.status)
    );

    const inProgress = tasks.filter(t =>
      ['In Progress', 'In progress', 'in-progress', 'WIP'].includes(t.status)
    );

    return { overdue, dueThisWeek, inProgress, total: tasks.length };
  } catch (e) {
    console.error('Notion fetch error:', e.message);
    return { error: e.message };
  }
}

async function fetchWhopActivity() {
  if (!WHOP_API_KEY) return { error: 'No Whop API key configured' };
  try {
    // Fetch recent memberships/passes from Whop
    const res = await fetch(
      'https://api.whop.com/api/v5/company/memberships?page=1&per_page=10&sort_by=created_at&sort_order=desc',
      {
        headers: {
          'Authorization': `Bearer ${WHOP_API_KEY}`,
          'Content-Type': 'application/json'
        },
        timeout: 10000
      }
    );

    if (!res.ok) {
      const errText = await res.text();
      console.error('Whop memberships error:', res.status, errText);

      // Try alternate endpoint
      const res2 = await fetch(
        'https://api.whop.com/api/v2/memberships?page=1&per=10',
        {
          headers: {
            'Authorization': `Bearer ${WHOP_API_KEY}`,
            'Content-Type': 'application/json'
          },
          timeout: 10000
        }
      );

      if (!res2.ok) {
        const err2 = await res2.text();
        return { error: `Whop API error: ${res.status}`, detail: errText };
      }

      const data2 = await res2.json();
      return { memberships: data2.data || data2.memberships || [], source: 'v2' };
    }

    const data = await res.json();
    return { memberships: data.data || data.memberships || [], source: 'v5' };
  } catch (e) {
    console.error('Whop fetch error:', e.message);
    return { error: e.message };
  }
}

// ---------- API Endpoints ----------

// Health check (no auth)
app.get('/health', (req, res) => res.json({ ok: true, time: new Date().toISOString() }));

// Auth check
app.post('/api/auth', (req, res) => {
  const { password } = req.body;
  if (password === DASHBOARD_PASSWORD) {
    res.json({ ok: true, token: DASHBOARD_PASSWORD });
  } else {
    res.status(401).json({ ok: false, error: 'Wrong password' });
  }
});

// KPIs from file
app.get('/api/kpis', authMiddleware, (req, res) => {
  const kpis = readJsonFile(path.join(DATA_DIR, 'kpis.json'));
  if (!kpis) return res.json({ error: 'KPI file not found' });
  res.json(kpis);
});

// Agent status from file
app.get('/api/agents', authMiddleware, (req, res) => {
  const agents = readJsonFile(path.join(DATA_DIR, 'agent-status.json'));
  if (!agents) return res.json({ error: 'Agent status file not found' });
  res.json(agents);
});

// BTC + Fear & Greed (live)
app.get('/api/market', authMiddleware, async (req, res) => {
  const [btc, fg] = await Promise.all([fetchBtcPrice(), fetchFearGreed()]);
  res.json({ btc_price: btc, fear_greed: fg, fetched_at: new Date().toISOString() });
});

// Notion tasks (live)
app.get('/api/tasks', authMiddleware, async (req, res) => {
  const tasks = await fetchNotionTasks();
  res.json({ ...tasks, fetched_at: new Date().toISOString() });
});

// Whop activity (live)
app.get('/api/whop', authMiddleware, async (req, res) => {
  const whop = await fetchWhopActivity();
  res.json({ ...whop, fetched_at: new Date().toISOString() });
});

// Combined dashboard data (one call to rule them all)
app.get('/api/dashboard', authMiddleware, async (req, res) => {
  const [market, tasks, whop] = await Promise.all([
    fetchBtcPrice().then(btc => ({ btc })),
    fetchFearGreed().then(fg => ({ fg })),
    fetchNotionTasks(),
    fetchWhopActivity()
  ].reduce((_, v) => v, Promise.all([
    fetchBtcPrice(),
    fetchFearGreed(),
    fetchNotionTasks(),
    fetchWhopActivity()
  ])));

  const kpis = readJsonFile(path.join(DATA_DIR, 'kpis.json'));
  const agents = readJsonFile(path.join(DATA_DIR, 'agent-status.json'));

  res.json({
    kpis,
    agents,
    market: { btc_price: market, fear_greed: tasks },
    notion: whop,
    whop: { memberships: [] },
    fetched_at: new Date().toISOString()
  });
});

// Combined endpoint — all data in one call
app.get('/api/all', authMiddleware, async (req, res) => {
  try {
    const [btcPrice, fearGreed, notionTasks, whopActivity] = await Promise.all([
      fetchBtcPrice(),
      fetchFearGreed(),
      fetchNotionTasks(),
      fetchWhopActivity()
    ]);

    const kpis = readJsonFile(path.join(DATA_DIR, 'kpis.json')) || {};
    const agents = readJsonFile(path.join(DATA_DIR, 'agent-status.json')) || {};

    // Merge live market data into kpis
    if (btcPrice != null) kpis.btc_price = btcPrice;
    if (fearGreed != null) kpis.fear_greed = fearGreed;
    kpis.last_updated = new Date().toISOString();

    res.json({
      kpis,
      agents,
      notion: notionTasks,
      whop: whopActivity,
      fetched_at: new Date().toISOString()
    });
  } catch (e) {
    console.error('/api/all error:', e);
    res.status(500).json({ error: e.message });
  }
});

app.listen(PORT, () => {
  console.log(`🚀 CEO Dashboard running on http://localhost:${PORT}`);
  console.log(`   Password: ${DASHBOARD_PASSWORD}`);
});
