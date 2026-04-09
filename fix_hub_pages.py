#!/usr/bin/env python3
"""
Clean hub pages: strip duplicate CSN nav, old sidebar, old mobile header.
Keep proper shell.css structure + actual page content from <main>.
"""
import re
import os
import sys

HUB_DIR = "/Users/openclaw/.openclaw/workspace/dashboard/public/hub"

# Common sidebar nav for all hub pages
SIDEBAR_NAV = """
  <nav style="flex:1; padding: 8px 0;">
    <div class="ds-sidebar-section">Home</div>
    <a class="ds-sidebar-link" href="../index.html">
      <span class="ds-icon"><i class="ph ph-house"></i></span> Dashboard
    </a>
    <div class="ds-sidebar-section">Strategy Hub</div>
    <a class="ds-sidebar-link{active_positioning}" href="positioning.html">
      <span class="ds-icon"><i class="ph ph-crosshair"></i></span> Positioning &amp; ICP
    </a>
    <a class="ds-sidebar-link{active_brand}" href="brand.html">
      <span class="ds-icon"><i class="ph ph-palette"></i></span> Brand &amp; Voice
    </a>
    <a class="ds-sidebar-link{active_products}" href="products.html">
      <span class="ds-icon"><i class="ph ph-diamond"></i></span> Products
    </a>
    <a class="ds-sidebar-link{active_competitors}" href="competitors.html">
      <span class="ds-icon"><i class="ph ph-trophy"></i></span> Competitive Intel
    </a>
    <a class="ds-sidebar-link{active_operating}" href="operating-system.html">
      <span class="ds-icon"><i class="ph ph-gear"></i></span> Operating System
    </a>
    <a class="ds-sidebar-link{active_beginner}" href="beginner-journey.html">
      <span class="ds-icon"><i class="ph ph-path"></i></span> Beginner Journey
    </a>
    <div class="ds-sidebar-section">Content</div>
    <a class="ds-sidebar-link{active_social_strategy}" href="social-strategy.html">
      <span class="ds-icon"><i class="ph ph-chat-circle-dots"></i></span> Social Strategy
    </a>
    <a class="ds-sidebar-link{active_youtube}" href="youtube-strategy.html">
      <span class="ds-icon"><i class="ph ph-youtube-logo"></i></span> YouTube Strategy
    </a>
    <a class="ds-sidebar-link{active_instagram}" href="instagram-strategy.html">
      <span class="ds-icon"><i class="ph ph-instagram-logo"></i></span> Instagram Strategy
    </a>
    <a class="ds-sidebar-link{active_rollout}" href="social-media-rollout.html">
      <span class="ds-icon"><i class="ph ph-megaphone"></i></span> Social Rollout
    </a>
  </nav>
"""

# Page metadata
PAGES = {
    "brand.html": {"title": "Brand & Voice", "active": "active_brand", "breadcrumb": "Brand & Voice"},
    "competitors.html": {"title": "Competitive Intelligence", "active": "active_competitors", "breadcrumb": "Competitive Intel"},
    "positioning.html": {"title": "Positioning & ICP", "active": "active_positioning", "breadcrumb": "Positioning & ICP"},
    "products.html": {"title": "Products", "active": "active_products", "breadcrumb": "Products"},
    "operating-system.html": {"title": "Operating System", "active": "active_operating", "breadcrumb": "Operating System"},
    "beginner-journey.html": {"title": "Beginner Journey Map", "active": "active_beginner", "breadcrumb": "Beginner Journey"},
    "social-strategy.html": {"title": "Social & Content Strategy", "active": "active_social_strategy", "breadcrumb": "Social Strategy"},
    "youtube-strategy.html": {"title": "YouTube Strategy", "active": "active_youtube", "breadcrumb": "YouTube Strategy"},
    "instagram-strategy.html": {"title": "Instagram Strategy", "active": "active_instagram", "breadcrumb": "Instagram Strategy"},
    "social-media-rollout.html": {"title": "Social Media Rollout", "active": "active_rollout", "breadcrumb": "Social Rollout"},
}

def extract_main_content(html):
    """Extract content from <main class="flex-1 min-h-screen"> tag."""
    # Try to find <main class="flex-1 min-h-screen">
    patterns = [
        r'<main\s+class="flex-1\s+min-h-screen">\s*(.*?)\s*</main>',
        r'<main\s+class="flex-1\s+min-h-screen\s+[^"]*">\s*(.*?)\s*</main>',
        r'<main[^>]*>\s*(.*?)\s*</main>',
    ]
    for pattern in patterns:
        match = re.search(pattern, html, re.DOTALL)
        if match:
            content = match.group(1)
            # Remove the old breadcrumb bar (px-6 lg:px-10 py-3 border-b)
            content = re.sub(
                r'<div\s+class="px-6\s+lg:px-10\s+py-3\s+border-b[^"]*">\s*<div\s+class="flex\s+items-center[^"]*">.*?</div>\s*</div>',
                '', content, flags=re.DOTALL
            )
            # Remove leading/trailing whitespace
            content = content.strip()
            return content
    return None

def extract_custom_styles(html):
    """Extract page-specific styles (accordion, module cards etc) from the first <style> block."""
    # Look for custom CSS that's NOT the CSN nav styles and NOT the shell overrides
    # We want things like .mod-accordion, .metric-grid, etc
    styles = []
    
    # Find all style blocks
    style_blocks = re.findall(r'<style>(.*?)</style>', html, re.DOTALL)
    
    for block in style_blocks:
        # Skip blocks that are primarily CSN nav or shell overrides
        if '.csn-bar' in block or '.ds-sidebar {' in block:
            # But extract any custom component styles from these blocks
            lines = block.split('\n')
            in_custom = False
            custom_lines = []
            for line in lines:
                # Skip shell override classes
                if any(x in line for x in ['.ds-topbar', '.ds-sidebar', '.ds-main-content', '.ds-page-body', 
                                            '.csn-', '#csnMobileMenu', '.ds-sidebar-link', '.ds-sidebar-section',
                                            '.ds-topbar-search', '.ds-sidebar-overlay', '#overlay',
                                            '.ds-mobile-hamburger']):
                    in_custom = False
                    continue
                # Custom component styles
                if any(x in line for x in ['.mod-', '.metric-', '.phase-', '.table-', '.stat-', 
                                            '.accordion', '.card-', '.kpi-', '.progress-',
                                            '.tab-', '.journey-', '.funnel-', '.competitor-',
                                            '.timeline-', '.pillar-', '.content-', '.series-',
                                            '.format-', '.channel-', '.goal-', '.platform-',
                                            '.week-', '.month-', '.rollout-', '.stage-',
                                            '.badge', '.tag', '.chip', '.step-']):
                    in_custom = True
                if in_custom:
                    custom_lines.append(line)
                    if '}' in line and '{' not in line:
                        in_custom = False
            if custom_lines:
                styles.append('\n'.join(custom_lines))
        else:
            # First style block is typically page-specific custom styles
            # But filter out any reset/base styles
            filtered = re.sub(r'\*.*?\{.*?\}', '', block, flags=re.DOTALL)
            filtered = re.sub(r':root\s*\{.*?\}', '', filtered, flags=re.DOTALL)
            filtered = re.sub(r'body\s*\{.*?\}', '', filtered, flags=re.DOTALL)
            if filtered.strip():
                styles.append(filtered.strip())
    
    return '\n'.join(styles) if styles else ''


def build_sidebar(active_key):
    """Build sidebar with correct active state."""
    nav = SIDEBAR_NAV
    for key in ["active_positioning", "active_brand", "active_products", "active_competitors",
                "active_operating", "active_beginner", "active_social_strategy", "active_youtube",
                "active_instagram", "active_rollout"]:
        if key == active_key:
            nav = nav.replace("{" + key + "}", " active")
        else:
            nav = nav.replace("{" + key + "}", "")
    return nav


def build_page(filename, title, breadcrumb, active_key, content, custom_styles=""):
    """Build a clean hub page."""
    sidebar = build_sidebar(active_key)
    
    custom_style_block = ""
    if custom_styles:
        custom_style_block = f"\n<style>\n{custom_styles}\n</style>"
    
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=Barlow:wght@300;400;500;600;700&family=Source+Code+Pro:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://unpkg.com/@phosphor-icons/web@2.1.1/src/regular/style.css">
<link rel="stylesheet" href="/shell.css">
<title>{title} — Collective Shift Strategy Hub</title>
<script src="https://cdn.tailwindcss.com"></script>
<script>
tailwind.config = {{
  theme: {{
    extend: {{
      colors: {{
        cs: {{
          orange: '#FC5C03',
          'orange-light': '#FC8C4E',
          'orange-bg': '#FEDECC',
          'orange-hover': '#FEEEE5',
          green: '#08C394',
          purple: '#654FFC',
          navy: '#1A1A2E',
          'navy-light': '#252540',
          border: '#E8E8EA',
          text: '#1B1925',
          secondary: '#4D4C55',
          muted: '#807F86',
          page: '#F7F7F8',
        }}
      }},
      fontFamily: {{
        jakarta: ['Plus Jakarta Sans', 'sans-serif'],
        barlow: ['Barlow', 'sans-serif'],
        mono: ['Source Code Pro', 'monospace'],
      }},
      borderRadius: {{
        pill: '100px',
      }},
    }}
  }}
}}
</script>{custom_style_block}
</head>
<body>

<!-- Sidebar Overlay (mobile) -->
<div class="ds-sidebar-overlay" id="dsSidebarOverlay" onclick="document.getElementById('dsSidebar').classList.remove('open');this.classList.remove('open');"></div>

<!-- Sidebar -->
<aside class="ds-sidebar" id="dsSidebar">
  <div style="padding:16px 16px 8px;display:flex;align-items:center;gap:10px;">
    <span style="color:#FC5C03;font-family:'Plus Jakarta Sans',sans-serif;font-weight:700;font-size:15px;letter-spacing:0.04em;">COLLECTIVE SHIFT</span>
  </div>
{sidebar}
</aside>

<!-- Top Bar -->
<header class="ds-topbar">
  <div style="display:flex;align-items:center;gap:12px;">
    <button class="ds-mobile-hamburger" onclick="document.getElementById('dsSidebar').classList.add('open');document.getElementById('dsSidebarOverlay').classList.add('open');" style="background:none;border:none;cursor:pointer;padding:4px;">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#1B1925" stroke-width="2"><path d="M3 12h18M3 6h18M3 18h18"/></svg>
    </button>
    <span style="font-family:'Plus Jakarta Sans',sans-serif;font-weight:600;font-size:14px;color:#1B1925;">{breadcrumb}</span>
  </div>
</header>

<!-- Main Content -->
<div class="ds-main-content">
  <div class="ds-page-body">
    <!-- Breadcrumb -->
    <div style="display:flex;align-items:center;gap:6px;font-size:12px;font-family:'Source Code Pro',monospace;color:#807F86;margin-bottom:20px;">
      <a href="../index.html" style="color:#FC5C03;text-decoration:none;">Dashboard</a>
      <span>/</span>
      <span>{breadcrumb}</span>
    </div>

    <!-- Page Content -->
    <div style="max-width:1100px;">
      {content}
    </div>
  </div>
</div>

</body>
</html>'''


def process_file(filename):
    """Process a single hub page."""
    filepath = os.path.join(HUB_DIR, filename)
    if not os.path.exists(filepath):
        print(f"  SKIP: {filename} not found")
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()
    
    meta = PAGES.get(filename)
    if not meta:
        print(f"  SKIP: {filename} not in PAGES config")
        return False
    
    # Extract main content
    content = extract_main_content(html)
    if not content:
        print(f"  WARNING: Could not extract <main> content from {filename}")
        print(f"  Trying fallback extraction...")
        # Fallback: try to find content after "END TOP NAV" comment
        match = re.search(r'<!-- ═══ END TOP NAV ═══ -->(.*)$', html, re.DOTALL)
        if match:
            fallback = match.group(1)
            # Strip the old mobile header, overlay, old sidebar wrapper
            fallback = re.sub(r'<div class="lg:hidden.*?</div>', '', fallback, count=1, flags=re.DOTALL)
            fallback = re.sub(r'<div id="overlay".*?</div>', '', fallback, count=1, flags=re.DOTALL)
            # Try to get from <main> to </main>
            main_match = re.search(r'<main[^>]*>(.*?)</main>', fallback, re.DOTALL)
            if main_match:
                content = main_match.group(1).strip()
                # Remove old breadcrumb
                content = re.sub(
                    r'<div\s+class="px-6\s+lg:px-10\s+py-3\s+border-b[^"]*">.*?</div>\s*</div>',
                    '', content, flags=re.DOTALL
                )
            else:
                content = fallback
        if not content:
            print(f"  ERROR: No content found for {filename}")
            return False
    
    # Extract custom styles
    custom_styles = extract_custom_styles(html)
    
    # Build clean page
    new_html = build_page(
        filename,
        meta["title"],
        meta["breadcrumb"],
        meta["active"],
        content,
        custom_styles
    )
    
    # Write
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_html)
    
    print(f"  OK: {filename} ({len(html)} -> {len(new_html)} bytes)")
    return True


def main():
    print("Cleaning hub pages...")
    success = 0
    failed = 0
    for filename in sorted(PAGES.keys()):
        print(f"\nProcessing {filename}...")
        if process_file(filename):
            success += 1
        else:
            failed += 1
    
    print(f"\nDone: {success} cleaned, {failed} failed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
