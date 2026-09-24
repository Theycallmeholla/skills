#!/usr/bin/env python3
import importlib.util
from pathlib import Path

MODULE = Path(__file__).with_name('probe_site.py')
spec = importlib.util.spec_from_file_location('probe_site', MODULE)
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)


def check(name, condition):
    if not condition:
        raise AssertionError(name)
    print(f'PASS {name}')


robots = probe.parse_robots('''
User-agent: *
Disallow: /blog/
Allow: /blog/public-post
Disallow: /*.pdf$
''')

check('specific allow beats broader disallow', probe.robots_decision(robots, 'OAI-SearchBot', 'https://example.com/blog/public-post')['allowed'] is True)
check('wildcard plus end-anchor blocks pdf', probe.robots_decision(robots, 'OAI-SearchBot', 'https://example.com/file.pdf')['allowed'] is False)
check('pdf rule does not match extra suffix', probe.robots_decision(robots, 'OAI-SearchBot', 'https://example.com/file.pdfx')['allowed'] is True)

ua_robots = probe.parse_robots('''
User-agent: *
Disallow: /

User-agent: OAI-SearchBot
Allow: /public
''')
check('specific user-agent group wins wildcard group', probe.robots_decision(ua_robots, 'Mozilla compatible OAI-SearchBot/1.0', 'https://example.com/private')['allowed'] is True)

parser = probe.PageParser()
parser.feed('<h1><span>Sites that sell.</span><span>Software that ships.</span></h1>')
check('heading text keeps word boundary', parser.headings[0]['text'] == 'Sites that sell. Software that ships.')

text, charset = probe.safe_decode('hello'.encode(), 'not-a-real-charset')
check('invalid charset falls back safely', text == 'hello' and charset in {'utf-8', 'windows-1252', 'utf-8-replace'})

recaptcha_page = '<h1>Contact</h1><script src="https://www.google.com/recaptcha/api.js"></script><p>Just a moment of your time</p>'
check('normal 200 page with reCAPTCHA is reachable', probe.classify_access({'status': 200, 'headers': {}, 'text': recaptcha_page})['state'] == 'reachable')
check('cf-mitigated header is a challenge', probe.classify_access({'status': 403, 'headers': {'cf-mitigated': 'challenge'}, 'text': ''})['state'] == 'blocked_or_challenged')
check('403 challenge page is a challenge', probe.classify_access({'status': 403, 'headers': {}, 'text': '<title>Just a moment...</title>'})['state'] == 'blocked_or_challenged')
check('plain 403 is blocked', probe.classify_access({'status': 403, 'headers': {}, 'text': 'Forbidden'})['state'] == 'blocked_or_limited')
check('baseline uses a normal browser user-agent', 'Chrome/' in probe.BROWSER_UA and 'Open-SaysAI-Audit' not in probe.BROWSER_UA)

agent_info = {'purpose': 'search/retrieval', 'ua': 'OAI-SearchBot'}
reachable_entry = probe.build_agent_entry(agent_info, {'status': 200, 'headers': {}, 'text': '<h1>Hi</h1>'}, 'reachable')
check('reachable agent result is labeled synthetic-UA evidence', reachable_entry['state'] == 'reachable' and reachable_entry['evidence_tier'] == 'synthetic_ua')
check('reachable agent result carries no block caveat', 'spoofed_ua_caveat' not in reachable_entry)
blocked_entry = probe.build_agent_entry(agent_info, {'status': 403, 'headers': {}, 'text': 'Forbidden'}, 'reachable')
check('UA-only block gets spoofed-UA caveat', blocked_entry['state'] == 'blocked_or_limited' and 'spoofed_ua_caveat' in blocked_entry)
error_entry = probe.build_agent_entry(agent_info, {'url': 'https://example.com', 'error': 'URLError: offline'}, 'unknown')
check('network error stays unknown with synthetic-UA tier', error_entry['state'] == 'unknown' and error_entry['evidence_tier'] == 'synthetic_ua' and 'error' in error_entry)
