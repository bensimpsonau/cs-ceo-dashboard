#!/usr/bin/env python3
"""
Collective Shift CEO Command Centre — Site-wide rebrand script.
Adds shared top nav (new structure), white theme, brand fonts to all target pages.
"""

import re
import os

ROOT = "/Users/openclaw/.openclaw/workspace/dashboard/public"

# ─────────────────────────────────────────────────────────
# SHARED TOP NAV (injected into every page)
# path_prefix: "" for root pages, "../" for /hub/, "../../" for /hub/modules/
# active_key: which top-level item to mark active
# ─────────────────────────────────────────────────────────

def build_top_nav(path_prefix, active_key):
    items = [
        ("ceo",      f"{path_prefix}index.html",                  "CEO Dashboard"),
        ("os",       f"{path_prefix}hub/operating-system.html",   "The Collective Shift Operating System"),
        ("product",  f"{path_prefix}hub/products.html",           "Product"),
        ("social",   f"{path_prefix}hub/youtube-strategy.html",   "Social Media"),
        ("docs",     f"{path_prefix}travis-briefing-2026-03-27.html", "Documents"),
    ]

    # dropdown menus
    os_items = [
        (f"{path_prefix}hub/operating-system.html",              "Operating System Overview"),
        (f"{path_prefix}hub/modules/m1-foundations.html",        "Module 1: Foundations"),
        (f"{path_prefix}hub/modules/m2-bitcoin.html",            "Module 2: Bitcoin"),
        (f"{path_prefix}hub/modules/m3-altcoins.html",           "Module 3: Digital Assets"),
        (f"{path_prefix}hub/modules/m4-how-we-invest.html",      "Module 4: How We Invest"),
        (f"{path_prefix}hub/modules/m5-buy-sell.html",           "Module 5: Buy & Sell"),
        (f"{path_prefix}hub/modules/m6-send-store.html",         "Module 6: Send & Store"),
        (f"{path_prefix}hub/modules/m7-tax.html",                "Module 7: Tax"),
        (f"{path_prefix}hub/modules/m8-sell-strategy.html",      "Module 8: Exit Strategy"),
        ("__divider__", "", ""),
        (f"{path_prefix}8-step-strategy-workbook.html",          "8-Step Strategy Workbook"),
        (f"{path_prefix}8-step-strategy-workbook-L1.html",       "↳ Level 1 Workbook"),
        (f"{path_prefix}8-step-strategy-workbook-L2.html",       "↳ Level 2 Workbook"),
        (f"{path_prefix}portfolio-calculator.html",              "Portfolio Allocation Calculator"),
    ]

    product_items = [
        (f"{path_prefix}hub/products.html#platinum",             "Platinum"),
        (f"{path_prefix}hub/products.html#accelerator",          "Accelerator"),
        (f"{path_prefix}hub/beginner-journey.html",              "Beginner's Journey"),
        (f"{path_prefix}hub/products.html#two-track",            "Two-Track System"),
    ]

    social_items = [
        (f"{path_prefix}hub/youtube-strategy.html",              "YouTube Strategy"),
        (f"{path_prefix}hub/social-strategy.html",               "Social Strategy"),
        (f"{path_prefix}hub/instagram-strategy.html",            "Instagram Strategy"),
        ("__divider__", "", ""),
        (f"{path_prefix}hub/brand.html",                         "Brand & Voice"),
        (f"{path_prefix}hub/positioning.html",                   "Positioning & ICP"),
        (f"{path_prefix}hub/competitors.html",                   "Competitors"),
    ]

    docs_items = [
        (f"{path_prefix}travis-briefing-2026-03-27.html",        "Travis CGO Briefing"),
        (f"{path_prefix}cs-education-system-overview.html",      "Education System Overview"),
        (f"{path_prefix}q2-market-briefing.html",                "Q2 Market Briefing"),
        (f"{path_prefix}webinar-q2-2026-is-now-the-time.html",   "Webinar: Is Now The Time?"),
    ]

    dropdowns = {
        "os": os_items,
        "product": product_items,
        "social": social_items,
        "docs": docs_items,
    }

    def render_dropdown(key, label, href, is_active):
        active_cls = "active" if is_active else ""
        items_html = ""
        for item in dropdowns.get(key, []):
            if item[0] == "__divider__":
                items_html += '<div class="csn-divider"></div>'
            else:
                items_html += f'<a href="{item[0]}" class="csn-dd-item">{item[1]}</a>'
        return f"""
      <div class="csn-item csn-has-dd {active_cls}">
        <a href="{href}" class="csn-link">{label}
          <svg class="csn-chevron" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M6 9l6 6 6-6"/></svg>
        </a>
        <div class="csn-dropdown">{items_html}</div>
      </div>"""

    nav_items_html = ""
    for (key, href, label) in items:
        is_active = (key == active_key)
        if key in dropdowns:
            nav_items_html += render_dropdown(key, label, href, is_active)
        else:
            active_cls = "active" if is_active else ""
            nav_items_html += f'\n      <div class="csn-item {active_cls}"><a href="{href}" class="csn-link">{label}</a></div>'

    # mobile dropdown items
    all_mobile_items = []
    for (key, href, label) in items:
        all_mobile_items.append(f'<a href="{href}" class="csn-mob-link csn-mob-top">{label}</a>')
        if key in dropdowns:
            for item in dropdowns[key]:
                if item[0] == "__divider__":
                    continue
                indent = "↳ " if item[1].startswith("↳") else "&nbsp;&nbsp;&nbsp;"
                display = item[1].lstrip("↳ ")
                all_mobile_items.append(f'<a href="{item[0]}" class="csn-mob-link csn-mob-sub">{indent}{display}</a>')

    mobile_html = "\n".join(all_mobile_items)

    return f"""<!-- ═══ COLLECTIVE SHIFT TOP NAV ═══ -->
<style>
  :root {{
    --csn-h: 56px;
    --csn-bg: #FFFFFF;
    --csn-border: #E8E8EA;
    --csn-text: #1B1925;
    --csn-muted: #4D4C55;
    --csn-orange: #FC5C03;
    --csn-orange-bg: #FEEEE5;
    --csn-dd-bg: #FFFFFF;
    --csn-dd-shadow: 0 8px 24px rgba(0,0,0,0.10), 0 2px 8px rgba(0,0,0,0.06);
    --csn-z: 9000;
  }}
  .csn-bar {{
    position: fixed;
    top: 0; left: 0; right: 0;
    height: var(--csn-h);
    background: var(--csn-bg);
    border-bottom: 1px solid var(--csn-border);
    display: flex;
    align-items: center;
    padding: 0 24px;
    gap: 0;
    z-index: var(--csn-z);
    font-family: 'Plus Jakarta Sans', 'Barlow', sans-serif;
  }}
  .csn-logo {{
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-weight: 700;
    font-size: 15px;
    color: var(--csn-orange);
    text-decoration: none;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    white-space: nowrap;
    margin-right: 32px;
    flex-shrink: 0;
  }}
  .csn-nav {{
    display: flex;
    align-items: center;
    gap: 2px;
    flex: 1;
  }}
  .csn-item {{
    position: relative;
  }}
  .csn-link {{
    display: flex;
    align-items: center;
    gap: 5px;
    padding: 8px 12px;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 500;
    color: var(--csn-muted);
    text-decoration: none;
    white-space: nowrap;
    transition: color 0.15s, background 0.15s;
    cursor: pointer;
  }}
  .csn-link:hover {{ color: var(--csn-orange); background: var(--csn-orange-bg); }}
  .csn-item.active > .csn-link {{ color: var(--csn-orange); font-weight: 600; }}
  .csn-chevron {{ transition: transform 0.2s; flex-shrink: 0; }}
  .csn-item.csn-has-dd:hover > .csn-link .csn-chevron {{ transform: rotate(180deg); }}
  /* Dropdown */
  .csn-dropdown {{
    display: none;
    position: absolute;
    top: calc(100% + 6px);
    left: 0;
    min-width: 240px;
    background: var(--csn-dd-bg);
    border: 1px solid var(--csn-border);
    border-radius: 12px;
    box-shadow: var(--csn-dd-shadow);
    padding: 6px;
    z-index: calc(var(--csn-z) + 1);
  }}
  .csn-item.csn-has-dd:hover > .csn-dropdown {{ display: block; }}
  .csn-dd-item {{
    display: block;
    padding: 8px 12px;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 500;
    color: var(--csn-muted);
    text-decoration: none;
    transition: color 0.12s, background 0.12s;
    white-space: nowrap;
  }}
  .csn-dd-item:hover {{ color: var(--csn-orange); background: var(--csn-orange-bg); }}
  .csn-divider {{ height: 1px; background: var(--csn-border); margin: 4px 8px; }}
  /* Mobile hamburger */
  .csn-hamburger {{
    display: none;
    background: none;
    border: none;
    cursor: pointer;
    color: var(--csn-muted);
    padding: 4px;
    margin-left: auto;
  }}
  /* Mobile drawer */
  .csn-mobile-menu {{
    display: none;
    position: fixed;
    top: var(--csn-h);
    left: 0; right: 0;
    background: var(--csn-bg);
    border-bottom: 1px solid var(--csn-border);
    padding: 8px 16px 16px;
    z-index: calc(var(--csn-z) - 1);
    max-height: calc(100vh - var(--csn-h));
    overflow-y: auto;
    box-shadow: 0 8px 24px rgba(0,0,0,0.08);
  }}
  .csn-mobile-menu.open {{ display: block; }}
  .csn-mob-link {{
    display: block;
    padding: 9px 12px;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 500;
    color: var(--csn-muted);
    text-decoration: none;
    transition: color 0.12s, background 0.12s;
  }}
  .csn-mob-link:hover {{ color: var(--csn-orange); background: var(--csn-orange-bg); }}
  .csn-mob-top {{ font-weight: 600; color: var(--csn-text); margin-top: 4px; }}
  .csn-mob-sub {{ font-size: 12px; padding-left: 20px; }}
  /* Body offset */
  body {{ padding-top: var(--csn-h) !important; }}
  @media (max-width: 1023px) {{
    .csn-nav {{ display: none; }}
    .csn-hamburger {{ display: block; }}
  }}
  @media (max-width: 640px) {{
    .csn-logo {{ font-size: 13px; margin-right: 16px; }}
  }}
</style>
<nav class="csn-bar" role="navigation" aria-label="Main navigation">
  <a href="{path_prefix}index.html" class="csn-logo">Collective Shift</a>
  <div class="csn-nav">{nav_items_html}
  </div>
  <button class="csn-hamburger" onclick="document.getElementById('csnMobileMenu').classList.toggle('open')" aria-label="Toggle navigation">
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 12h18M3 6h18M3 18h18"/></svg>
  </button>
</nav>
<div id="csnMobileMenu" class="csn-mobile-menu">
  {mobile_html}
</div>
<!-- ═══ END TOP NAV ═══ -->"""


# ─────────────────────────────────────────────────────────
# WHITE THEME HEAD BLOCK — replaces old dark-theme head content
# ─────────────────────────────────────────────────────────

WHITE_THEME_VARS = """
  :root {
    --bg: #FFFFFF;
    --bg-off: #F9F9F9;
    --bg-section: #F2F2F2;
    --text: #1B1925;
    --text-secondary: #4D4C55;
    --text-muted: #807F86;
    --orange: #FC5C03;
    --orange-light: #FC8C4E;
    --orange-bg: #FEDECC;
    --orange-hover: #FEEEE5;
    --green: #08C394;
    --purple: #654FFC;
    --red: #FF0A00;
    --border: #E8E8EA;
    --border-light: #D9D8DA;
    --card-bg: #FFFFFF;
    --card-shadow: 0 2px 4px rgba(0,0,0,0.04), 0 1px 5.5px rgba(0,0,0,0.03);
  }
"""

WHITE_FONT_LINK = '<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=Barlow:wght@300;400;500;600;700&family=Source+Code+Pro:wght@400;500;600&display=swap" rel="stylesheet">'

WHITE_PHOSPHOR = '<link rel="stylesheet" href="https://unpkg.com/@phosphor-icons/web@2.1.1/src/regular/style.css">'

# ─────────────────────────────────────────────────────────
# DARK→LIGHT CLASS REPLACEMENTS (Tailwind-based pages)
# ─────────────────────────────────────────────────────────

TAILWIND_REPLACEMENTS = [
    # body/bg
    (r'bg-cs-bg\b',         'bg-white'),
    (r'bg-cs-card\b',       'bg-white'),
    (r'bg-cs-bg-card\b',    'bg-white'),
    (r'bg-cs-bg-hover\b',   'bg-\[#F2F2F2\]'),
    (r'bg-cs-sidebar\b',    'bg-white'),
    # text
    (r'text-cs-text\b',     'text-\[#1B1925\]'),
    (r'text-cs-muted\b',    'text-\[#807F86\]'),
    (r'text-cs-body\b',     'text-\[#4D4C55\]'),
    # borders
    (r'border-cs-border\b', 'border-\[#E8E8EA\]'),
    # keep orange/green/turquoise as-is
]

INLINE_STYLE_DARK_REPLACEMENTS = [
    # body/bg inline styles
    ("background: #1B1925",      "background: #FFFFFF"),
    ("background:#1B1925",       "background:#FFFFFF"),
    ("background-color: #1B1925","background-color: #FFFFFF"),
    ("background-color:#1B1925", "background-color:#FFFFFF"),
    ("background: #02000D",      "background: #FFFFFF"),
    ("background:#02000D",       "background:#FFFFFF"),
    ("background: #242230",      "background: #FFFFFF"),
    ("background:#242230",       "background:#FFFFFF"),
    ("background: #242232",      "background: #FFFFFF"),
    ("background:#242232",       "background:#FFFFFF"),
    ("background: #16141E",      "background: #F9F9F9"),
    ("background:#16141E",       "background:#F9F9F9"),
    ("background: #2D2B3A",      "background: #F2F2F2"),
    ("background:#2D2B3A",       "background:#F2F2F2"),
    # color: white/light → dark
    ("color: #F9F9F9",           "color: #1B1925"),
    ("color:#F9F9F9",            "color:#1B1925"),
    ("color: rgba(255,255,255,0.85)", "color: #4D4C55"),
    ("color: rgba(255,255,255,0.6)",  "color: #807F86"),
    ("color: rgba(255,255,255,0.7)",  "color: #4D4C55"),
    ("color: rgba(255,255,255,0.45)", "color: #807F86"),
    # border-color
    ("border-color: #2E2C3E",    "border-color: #E8E8EA"),
    ("border-color:#2E2C3E",     "border-color:#E8E8EA"),
    ("border: 1px solid #2E2C3E","border: 1px solid #E8E8EA"),
    ("border: 1px solid #33313F","border: 1px solid #E8E8EA"),
    ("border-color: #33313F",    "border-color: #E8E8EA"),
    ("border: 1px solid rgba(255,255,255,0.1)", "border: 1px solid #E8E8EA"),
    ("border-color: rgba(255,255,255,0.1)", "border-color: #E8E8EA"),
    # Oswald → Plus Jakarta Sans
    ("font-family: 'Oswald'",    "font-family: 'Plus Jakarta Sans'"),
    ("font-family:'Oswald'",     "font-family:'Plus Jakarta Sans'"),
    ("'Oswald', sans-serif",     "'Plus Jakarta Sans', sans-serif"),
    # scrollbar dark
    ("background: #1B1925;\n  ::-webkit-scrollbar", "background: #FFFFFF;\n  ::-webkit-scrollbar"),
]

def upgrade_head(html, path_prefix):
    """Replace head fonts/tailwind config with brand-compliant versions."""
    # Remove old Oswald/dark font links
    html = re.sub(
        r'<link[^>]+googleapis\.com/css2\?family=[^>]+>',
        '', html
    )
    # Remove old phosphor link (we'll re-add)
    html = re.sub(
        r'<link[^>]+phosphor-icons[^>]+>',
        '', html
    )
    # Inject brand fonts + phosphor after <head> open or after <meta viewport>
    font_block = f'\n{WHITE_FONT_LINK}\n{WHITE_PHOSPHOR}\n'
    if '<meta name="viewport"' in html:
        html = html.replace(
            html[html.find('<meta name="viewport"'):html.find('>', html.find('<meta name="viewport"'))+1],
            html[html.find('<meta name="viewport"'):html.find('>', html.find('<meta name="viewport"'))+1] + font_block,
            1
        )
    else:
        html = html.replace('<head>', '<head>' + font_block, 1)

    # Update Tailwind config for white theme
    old_tw_configs = [
        # dark tailwind configs
        r"tailwind\.config\s*=\s*\{[^}]*cs:\s*\{[^}]*bg:\s*'#1B1925'[^}]*\}[^}]*\}[^}]*\}",
        r"tailwind\.config\s*=\s*\{[^}]*'#1B1925'[^}]*\}",
    ]
    new_tw_config = """tailwind.config = {
  theme: {
    extend: {
      colors: {
        cs: {
          orange: '#FC5C03',
          'orange-light': '#FC8C4E',
          'orange-bg': '#FEDECC',
          'orange-hover': '#FEEEE5',
          green: '#08C394',
          purple: '#654FFC',
          border: '#E8E8EA',
          text: '#1B1925',
          secondary: '#4D4C55',
          muted: '#807F86',
        }
      },
      fontFamily: {
        jakarta: ['Plus Jakarta Sans', 'sans-serif'],
        barlow: ['Barlow', 'sans-serif'],
        mono: ['Source Code Pro', 'monospace'],
      },
      borderRadius: {
        pill: '100px',
      }
    }
  }
}"""
    # Replace any existing tailwind config script
    html = re.sub(
        r'<script>\s*tailwind\.config\s*=\s*\{[\s\S]*?\}\s*</script>',
        f'<script>\n{new_tw_config}\n</script>',
        html,
        count=1
    )
    return html


def apply_inline_style_replacements(html):
    """Apply dark→light color replacements in <style> blocks and inline styles."""
    for old, new in INLINE_STYLE_DARK_REPLACEMENTS:
        html = html.replace(old, new)

    # Also replace in <style> blocks specifically
    def replace_in_styles(m):
        s = m.group(0)
        for old, new in INLINE_STYLE_DARK_REPLACEMENTS:
            s = s.replace(old, new)
        return s

    html = re.sub(r'<style[\s\S]*?</style>', replace_in_styles, html)
    return html


def apply_tailwind_class_replacements(html):
    """Replace dark Tailwind classes with light equivalents."""
    for pattern, replacement in TAILWIND_REPLACEMENTS:
        html = re.sub(pattern, replacement, html)
    return html


def inject_top_nav(html, path_prefix, active_key):
    """Inject the top nav bar right after <body> tag (or after the first div if needed)."""
    top_nav = build_top_nav(path_prefix, active_key)

    # Remove any existing csn-bar (in case we're re-running)
    html = re.sub(r'<!-- ═══ COLLECTIVE SHIFT TOP NAV ═══ -->[\s\S]*?<!-- ═══ END TOP NAV ═══ -->', '', html)

    # Inject after <body ...> tag
    body_match = re.search(r'<body[^>]*>', html)
    if body_match:
        insert_pos = body_match.end()
        html = html[:insert_pos] + '\n' + top_nav + '\n' + html[insert_pos:]
    return html


def upgrade_sidebar_dark(html, path_prefix):
    """Update dark sidebar HTML patterns to white theme (for dark pages with sidebar)."""
    # Update sidebar background classes
    html = re.sub(r'class="sidebar\s+w-64\s+min-h-screen\s+bg-cs-card', 
                  'class="sidebar w-64 min-h-screen bg-white', html)
    # Update nav links to white theme
    html = html.replace("bg-cs-card border-b border-cs-border", "bg-white border-b border-[#E8E8EA]")
    # Update sidebar section text
    html = html.replace("text-cs-muted text-xs mt-1 font-mono", "text-[#807F86] text-xs mt-1 font-mono")
    return html


def rebuild_dark_page_as_white(html, path_prefix, active_key, page_type="default"):
    """Full transform: dark page → white-themed page with top nav."""
    html = upgrade_head(html, path_prefix)
    html = apply_inline_style_replacements(html)
    html = apply_tailwind_class_replacements(html)
    html = upgrade_sidebar_dark(html, path_prefix)
    html = inject_top_nav(html, path_prefix, active_key)
    return html


def add_nav_only(html, path_prefix, active_key):
    """For pages already white-themed — just add/update the top nav."""
    html = upgrade_head(html, path_prefix)
    html = inject_top_nav(html, path_prefix, active_key)
    return html


# ─────────────────────────────────────────────────────────
# PROCESS EACH FILE
# ─────────────────────────────────────────────────────────

def process(filepath, path_prefix, active_key, already_white=False):
    if not os.path.exists(filepath):
        print(f"  ⚠️  SKIP (not found): {filepath}")
        return
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()

    if already_white:
        html = add_nav_only(html, path_prefix, active_key)
    else:
        html = rebuild_dark_page_as_white(html, path_prefix, active_key)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"  ✅  {filepath.replace(ROOT, '')}")


# ─────────────────────────────────────────────────────────
# INSTAGRAM STRATEGY PLACEHOLDER
# ─────────────────────────────────────────────────────────

INSTAGRAM_PLACEHOLDER = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Instagram Strategy — Collective Shift</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=Barlow:wght@300;400;500;600;700&family=Source+Code+Pro:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://unpkg.com/@phosphor-icons/web@2.1.1/src/regular/style.css">
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: 'Barlow', sans-serif; background: #FFFFFF; color: #1B1925; line-height: 1.6; }
  .page-content { max-width: 900px; margin: 0 auto; padding: 64px 40px; }
  .eyebrow { font-family: 'Source Code Pro', monospace; font-size: 12px; font-weight: 600; letter-spacing: 0.14em; text-transform: uppercase; color: #FC5C03; margin-bottom: 16px; display: flex; align-items: center; gap: 8px; }
  .eyebrow::before { content: ''; display: inline-block; width: 20px; height: 2px; background: #FC5C03; border-radius: 2px; }
  h1 { font-family: 'Plus Jakarta Sans', sans-serif; font-weight: 700; font-size: clamp(32px, 5vw, 56px); line-height: 1.1; letter-spacing: -0.02em; color: #1B1925; margin-bottom: 16px; }
  .subtitle { font-size: 18px; color: #4D4C55; max-width: 600px; margin-bottom: 48px; }
  .placeholder-card { background: #F9F9F9; border: 1px solid #E8E8EA; border-radius: 16px; padding: 48px; text-align: center; }
  .placeholder-card .icon { font-size: 48px; margin-bottom: 16px; }
  .placeholder-card h2 { font-family: 'Plus Jakarta Sans', sans-serif; font-weight: 600; font-size: 20px; margin-bottom: 12px; }
  .placeholder-card p { color: #807F86; font-size: 15px; line-height: 1.6; max-width: 480px; margin: 0 auto; }
  .badge { display: inline-flex; align-items: center; gap: 6px; background: #FEEEE5; color: #FC5C03; border-radius: 100px; padding: 6px 16px; font-size: 12px; font-weight: 600; font-family: 'Source Code Pro', monospace; letter-spacing: 0.08em; margin-top: 24px; }
</style>
</head>
<body>

<main class="page-content">
  <div class="eyebrow">Social Media</div>
  <h1>Instagram Strategy</h1>
  <p class="subtitle">Collective Shift's Instagram playbook — content formats, posting cadence, and growth strategy.</p>

  <div class="placeholder-card">
    <div class="icon"><i class="ph ph-instagram-logo"></i></div>
    <h2>Coming Soon</h2>
    <p>The Instagram Strategy document is being developed. This will cover content formats, posting schedules, caption frameworks, hashtag strategy, and growth tactics tailored to the Collective Shift brand.</p>
    <div class="badge">🔄 In Progress — March 2026</div>
  </div>
</main>

</body>
</html>"""


def create_instagram_placeholder():
    path = os.path.join(ROOT, "hub/instagram-strategy.html")
    if not os.path.exists(path):
        with open(path, 'w', encoding='utf-8') as f:
            f.write(INSTAGRAM_PLACEHOLDER)
        print("  ✅  Created /hub/instagram-strategy.html")
    # Now add nav to it
    process(path, "../", "social", already_white=True)


# ─────────────────────────────────────────────────────────
# HUB INDEX REBUILD — rename to "The Collective Shift Operating System"
# ─────────────────────────────────────────────────────────

def update_hub_index():
    path = os.path.join(ROOT, "hub/index.html")
    if not os.path.exists(path):
        print(f"  ⚠️  SKIP: hub/index.html not found")
        return
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()

    # Update title
    html = re.sub(r'<title>.*?</title>', '<title>The Collective Shift Operating System</title>', html)
    # Update H1/heading text
    html = re.sub(r'Strategy Hub', 'The Collective Shift Operating System', html)
    html = re.sub(r'STRATEGY HUB', 'THE SHIFT OS', html)

    # Apply full rebrand
    html = upgrade_head(html, "../")
    html = apply_inline_style_replacements(html)
    html = apply_tailwind_class_replacements(html)
    html = upgrade_sidebar_dark(html, "../")
    html = inject_top_nav(html, "../", "os")

    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    print("  ✅  /hub/index.html → The Collective Shift Operating System")


# ─────────────────────────────────────────────────────────
# STRATEGY-HUB.HTML — add redirect + nav
# ─────────────────────────────────────────────────────────

def update_old_strategy_hub():
    path = os.path.join(ROOT, "strategy-hub.html")
    if not os.path.exists(path):
        return
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()

    # Add a meta redirect at top
    redirect_tag = '<meta http-equiv="refresh" content="0;url=hub/index.html">'
    if redirect_tag not in html:
        html = html.replace('<head>', f'<head>\n{redirect_tag}', 1)

    html = apply_inline_style_replacements(html)
    html = inject_top_nav(html, "", "os")

    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    print("  ✅  /strategy-hub.html (redirect added)")


# ─────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────

def main():
    print("\n🔄 Collective Shift CEO Command Centre — Site-wide rebrand\n")

    # ── Create placeholder ──
    print("Creating placeholders...")
    create_instagram_placeholder()

    # ── Tier 1: Core pages ──
    print("\nTier 1 — Core pages...")

    # CEO Dashboard (dark → white)
    process(f"{ROOT}/index.html", "", "ceo")

    # Hub index (special handling)
    update_hub_index()

    # Hub pages (dark → white)
    process(f"{ROOT}/hub/operating-system.html",   "../", "os")
    process(f"{ROOT}/hub/youtube-strategy.html",   "../", "social", already_white=True)
    process(f"{ROOT}/hub/social-strategy.html",    "../", "social")
    process(f"{ROOT}/hub/products.html",           "../", "product")
    process(f"{ROOT}/hub/brand.html",              "../", "social")
    process(f"{ROOT}/hub/positioning.html",        "../", "social")
    process(f"{ROOT}/hub/competitors.html",        "../", "social")
    process(f"{ROOT}/hub/beginner-journey.html",   "../", "product")

    # Tools
    process(f"{ROOT}/portfolio-calculator.html",       "", "os")
    process(f"{ROOT}/8-step-strategy-workbook.html",   "", "os", already_white=True)
    process(f"{ROOT}/8-step-strategy-workbook-L1.html","", "os", already_white=True)
    process(f"{ROOT}/8-step-strategy-workbook-L2.html","", "os", already_white=True)

    # ── Tier 2: Documents ──
    print("\nTier 2 — Documents...")
    process(f"{ROOT}/q2-market-briefing.html",                  "", "docs")
    process(f"{ROOT}/webinar-q2-2026-is-now-the-time.html",     "", "docs")
    process(f"{ROOT}/travis-briefing-2026-03-27.html",          "", "docs", already_white=True)
    process(f"{ROOT}/projects/index.html",                      "../", "ceo")
    update_old_strategy_hub()

    # ── Module pages ──
    print("\nModule detail pages...")
    modules = [
        "m1-foundations", "m2-bitcoin", "m3-altcoins", "m4-how-we-invest",
        "m5-buy-sell", "m6-send-store", "m7-tax", "m8-sell-strategy"
    ]
    for m in modules:
        process(f"{ROOT}/hub/modules/{m}.html", "../../", "os")

    print("\n✅  All pages processed.\n")


if __name__ == "__main__":
    main()
