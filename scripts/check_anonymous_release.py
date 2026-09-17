"""Check anonymous publication boundaries without storing private identities."""
import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
ALLOWED_REPO = 'https://github.com/Anonymous-for-Sub/D-JEPA'
ALLOWED_SITE = 'https://anonymous-for-sub.github.io/D-JEPA'


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.author_block = False
        self.notice_controls = 0
        self.dialog = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        self.links.extend(a[k] for k in ('href', 'src') if a.get(k))
        self.author_block |= any(x in a.get('class', '').split() for x in ('hero-authors', 'hero-affiliations', 'footer-lab'))
        self.notice_controls += 'data-release-notice' in a
        self.dialog |= tag == 'dialog' and a.get('id') == 'release-dialog'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--deny-pattern', action='append', default=[], help='Additional private identity regex; supplied at runtime, not stored')
    args = parser.parse_args()
    errors = []
    patterns = [re.compile(p, re.I) for p in args.deny_pattern]
    for path in ROOT.rglob('*'):
        if not path.is_file() or any(p in {'.git', '__pycache__', '.pytest_cache'} for p in path.parts):
            continue
        if path.is_symlink():
            errors.append(f'symlink: {path.relative_to(ROOT)}')
        if path.suffix.lower() in {'.pdf', '.pptx', '.docx'}:
            errors.append(f'publication document needs explicit anonymity review: {path.relative_to(ROOT)}')
        raw = path.read_bytes()
        text = raw.decode('utf-8', errors='ignore')
        # Ignore image payloads, which can coincidentally contain text-like bytes.
        text = re.sub(r'data:image/[^;]+;base64,[A-Za-z0-9+/=]+', '', text)
        if any(p.search(text) for p in patterns):
            errors.append(f'private identity match: {path.relative_to(ROOT)}')
    html = (ROOT / 'docs/index.html').read_text()
    page = Page()
    page.feed(html)
    if page.author_block or not page.dialog or page.notice_controls < 2:
        errors.append('author block present or release notice controls missing')
    if re.search(r'>\s*Paper\s*(?:<|$)', html):
        errors.append('paper button present')
    if any('huggingface.co/' in link or link.startswith('mailto:') for link in page.links):
        errors.append('attributed resource/contact link in homepage')
    for content in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S):
        if json.loads(content).get('author'):
            errors.append('author field in structured metadata')
    if ALLOWED_REPO not in html or ALLOWED_SITE not in html:
        errors.append('anonymous canonical site/code links missing')
    if (ROOT / '.git').exists():
        result = subprocess.run(['git', '-C', str(ROOT), 'log', '--all', '--format=%an <%ae> | %cn <%ce>'], capture_output=True, text=True)
        for line in result.stdout.splitlines():
            if line != 'Anonymous-for-Sub <Anonymous-for-Sub@users.noreply.github.com> | Anonymous-for-Sub <Anonymous-for-Sub@users.noreply.github.com>':
                errors.append('non-anonymous commit identity')
        remote = subprocess.run(['git', '-C', str(ROOT), 'remote', 'get-url', 'origin'], capture_output=True, text=True)
        if remote.returncode == 0 and not remote.stdout.strip().endswith(':Anonymous-for-Sub/D-JEPA.git'):
            errors.append('unexpected repository owner')
    print(json.dumps({'pass': not errors, 'errors': sorted(set(errors))}, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
