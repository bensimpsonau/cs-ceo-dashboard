#!/usr/bin/env python3
"""Build standalone /os/ site by copying and stripping CEO dashboard nav from module pages."""

import os
import re
import shutil

BASE = "/Users/openclaw/.openclaw/workspace/dashboard/public"
OUT = os.path.join(BASE, "os")

# CSS to inject
HIDE_CSS = """
/* OS standalone overrides */
.sidebar, aside.sidebar, nav.sidebar, .csn-bar, .csn-mobile-menu, #csnMobileMenu,
.overlay, #overlay, .mobile-header, .hamburger, [class*="hamburger"], .breadcrumb,
nav[role="navigation"], .csn-mob-link, .csn-mob-top, .csn-mob-sub, a[class*="csn-mob"] {
  display: none !important;
}
body { display: block !important; }
main, .main, .content, .page-content {
  margin-left: 0 !important; padding-left: 0 !important;
  width: 100% !important; max-width: 100% !important;
}
"""

HEADER_HTML = '''<div class="os-header-bar" style="background:#fff;border-bottom:1px solid #E8E8EA;padding:14px 32px;display:flex;align-items:center;gap:10px;position:sticky;top:0;z-index:9999;">
  <a href="/os/" style="display:flex;align-items:center;gap:10px;text-decoration:none;">
    <div style="width:26px;height:26px;background:#FC5C03;border-radius:5px;display:flex;align-items:center;justify-content:center;color:#fff;font-weight:700;font-size:13px;font-family:'Plus Jakarta Sans',sans-serif;">CS</div>
    <span style="font-family:'Plus Jakarta Sans',sans-serif;font-weight:600;font-size:15px;color:#1B1925;">Collective Shift</span>
  </a>
  <div style="width:1px;height:18px;background:#E8E8EA;margin:0 2px;"></div>
  <span style="font-family:'Barlow',sans-serif;font-weight:400;font-size:13px;color:#807F86;">Operating System</span>
</div>
'''

def process_file(src, dst):
    """Read source HTML, inject CSS overrides and header, strip CEO Dashboard refs, write to dst."""
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    
    with open(src, 'r', encoding='utf-8', errors='replace') as f:
        html = f.read()
    
    # Inject CSS: before </style> if exists, otherwise before </head>
    if '</style>' in html:
        html = html.replace('</style>', HIDE_CSS + '\n</style>', 1)
    elif '</head>' in html:
        html = html.replace('</head>', '<style>' + HIDE_CSS + '</style>\n</head>', 1)
    else:
        html = '<style>' + HIDE_CSS + '</style>\n' + html
    
    # Inject header after <body...>
    body_match = re.search(r'<body[^>]*>', html, re.IGNORECASE)
    if body_match:
        insert_pos = body_match.end()
        html = html[:insert_pos] + '\n' + HEADER_HTML + html[insert_pos:]
    else:
        html = HEADER_HTML + html
    
    # Remove CEO Dashboard text
    html = html.replace('CEO Dashboard', '')
    
    with open(dst, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"  ✓ {os.path.relpath(dst, OUT)}")

# File mappings: (source_relative_to_BASE, dest_relative_to_OUT)
mappings = []

# L1 modules
for i in range(1, 9):
    names = {
        1: 'foundations', 2: 'bitcoin', 3: 'altcoins', 4: 'how-we-invest',
        5: 'buy-sell', 6: 'send-store', 7: 'tax', 8: 'sell-strategy'
    }
    fname = f"m{i}-beginner-{names[i]}.html"
    mappings.append((f"hub/l1/{fname}", f"l1/{fname}"))

# L2 modules
for i in range(1, 9):
    names = {
        1: 'foundations', 2: 'bitcoin', 3: 'altcoins', 4: 'how-we-invest',
        5: 'buy-sell', 6: 'send-store', 7: 'tax', 8: 'sell-strategy'
    }
    fname = f"m{i}-advanced-{names[i]}.html"
    mappings.append((f"hub/l2/{fname}", f"l2/{fname}"))

# Tools
mappings.append(("8-step-strategy-workbook.html", "tools/workbook.html"))
mappings.append(("8-step-strategy-workbook-L1.html", "tools/workbook-l1.html"))
mappings.append(("8-step-strategy-workbook-L2.html", "tools/workbook-l2.html"))
mappings.append(("portfolio-calculator.html", "tools/calculator.html"))

# Team presentation
mappings.append(("cs-education-system-overview.html", "team-presentation.html"))

print("Processing module pages...")
for src_rel, dst_rel in mappings:
    src = os.path.join(BASE, src_rel)
    dst = os.path.join(OUT, dst_rel)
    if os.path.exists(src):
        process_file(src, dst)
    else:
        print(f"  ✗ MISSING: {src_rel}")

print(f"\nDone! Processed {len(mappings)} files.")
