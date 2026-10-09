#!/usr/bin/env python3
"""Build a one-tap copy page for a Pine script, for GitHub Pages.

Noman copies the script on his phone, so the page must work with one tap and no
selection: a COPY button using the async clipboard API, a SELECT ALL fallback for
browsers that refuse it, and the code shown read-only so nothing can be edited by
accident on the way.

The source is embedded in a `<script type="text/plain">` block rather than escaped
into a JavaScript string literal. Pine contains quotes, backslashes and newlines in
quantity, and a single missed escape produces a silently truncated script — which
is exactly the failure this page exists to prevent. textContent needs no escaping.

    python3 make_pine_copy_page.py in.pine out.html "Page title" "filename.pine"
"""
import html
import sys


TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
  * {{ box-sizing: border-box; }}
  body {{ margin:0; padding:14px; background:#111; color:#eee;
         font-family:-apple-system,Roboto,Segoe UI,sans-serif; }}
  h1 {{ font-size:17px; margin:0 0 4px; }}
  .meta {{ font-size:12px; color:#888; margin:0 0 12px; }}
  ol {{ font-size:13px; color:#bbb; margin:0 0 14px; padding-left:20px; line-height:1.6; }}
  ol b {{ color:#fff; }}
  button {{ width:100%; padding:20px; font-size:20px; font-weight:700;
            border:0; border-radius:12px; margin-bottom:10px; color:#fff; }}
  #copy {{ background:#0a8f3c; }}
  #sel  {{ background:#2b6cb0; }}
  #msg  {{ font-size:14px; min-height:22px; margin-bottom:10px; color:#4ade80;
           font-weight:600; line-height:1.4; }}
  textarea {{ width:100%; height:38vh; background:#000; color:#9ae6b4;
              border:1px solid #333; border-radius:10px; padding:10px;
              font-family:ui-monospace,Menlo,Consolas,monospace; font-size:11px;
              line-height:1.35; white-space:pre; }}
  .foot {{ font-size:12px; color:#777; margin-top:10px; line-height:1.6; }}
</style>
</head>
<body>
<h1>{title}</h1>
<p class="meta">{lines} lines &middot; {chars} characters &middot; {version}</p>
<ol>
  <li>Tap <b>COPY</b> below</li>
  <li>Open TradingView &rarr; <b>Pine Editor</b></li>
  <li><b>Long-press &rarr; Select all</b>, then <b>backspace</b> so the default
      template is gone</li>
  <li><b>Paste</b> &rarr; <b>Save</b> &rarr; <b>Add to chart</b></li>
</ol>
<div id="msg"></div>
<button id="copy">COPY</button>
<button id="sel">SELECT ALL (fallback)</button>
<textarea id="code" readonly spellcheck="false"></textarea>
<p class="foot">If COPY does nothing, tap SELECT ALL, then long-press inside the box
and choose Copy. The box is read-only so nothing can be changed by accident.</p>

<script type="text/plain" id="src">{code}</script>
<script>
const CODE = document.getElementById('src').textContent;
const ta  = document.getElementById('code');
const msg = document.getElementById('msg');
ta.value = CODE;

function ok(t, c) {{ msg.style.color = c; msg.textContent = t; }}

function legacyCopy() {{
  ta.focus();
  ta.setSelectionRange(0, CODE.length);
  let done = false;
  try {{ done = document.execCommand('copy'); }} catch (e) {{ done = false; }}
  return done;
}}

document.getElementById('copy').onclick = async () => {{
  if (navigator.clipboard && navigator.clipboard.writeText) {{
    try {{
      await navigator.clipboard.writeText(CODE);
      return ok('COPIED \\u2713  now paste it in TradingView', '#4ade80');
    }} catch (e) {{ /* fall through to the legacy path */ }}
  }}
  if (legacyCopy()) return ok('COPIED \\u2713  now paste it in TradingView', '#4ade80');
  ok('Copy blocked by the browser \\u2014 tap SELECT ALL, then long-press and Copy', '#fbbf24');
}};

document.getElementById('sel').onclick = () => {{
  ta.focus();
  ta.setSelectionRange(0, CODE.length);
  ok('Selected. Long-press the box and choose Copy.', '#4ade80');
}};
</script>
</body>
</html>
"""


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    src_path, out_path = sys.argv[1], sys.argv[2]
    title = sys.argv[3] if len(sys.argv) > 3 else "Pine Script"
    src = open(src_path, encoding="utf-8").read().rstrip("\n")

    bad = [(i, ch) for i, l in enumerate(src.split("\n"), 1)
           for ch in l if ord(ch) > 127]
    if bad:
        print(f"WARNING: {len(bad)} non-ASCII char(s) in {src_path} "
              f"(line {bad[0][0]}) — Pine will reject it")

    # A literal </script> inside the code would end the block early. Pine cannot
    # contain it, but guard anyway rather than emit a silently broken page.
    if "</script" in src.lower():
        print("ERROR: the source contains '</script' — cannot embed safely")
        return 1

    version = src.split("\n")[0].strip()
    page = TEMPLATE.format(title=html.escape(title), code=src,
                           lines=len(src.split("\n")), chars=len(src),
                           version=html.escape(version))
    open(out_path, "w", encoding="utf-8").write(page)

    # The page must not contain a stray non-ASCII byte outside the code block
    # either: those are what break a copy-paste in a browser.
    print(f"wrote {out_path}")
    print(f"  {len(src.split(chr(10)))} lines, {len(src)} chars, {version}")
    print(f"  non-ASCII in source: {len(bad)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
