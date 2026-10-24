"""build_db.py: Speed/Rush split of the 'other routes', TCGplayer picture per printing in the card detail, character portraits + skills, events data."""
import shutil
shutil.copy('tools/build_db.py', 'tools/build_db.before_patch19.py')
t = open('tools/build_db.py', encoding='utf-8').read()


def rep(a, b):
    global t
    assert t.count(a) == 1, a[:80]
    t = t.replace(a, b)


rep("""def dl_src(kind, name, stype, rel):
    key = (kind, name)
    if key not in dl_set_idx:
        dl_set_idx[key] = len(dl_set_list)
        dl_set_list.append({'n': name, 'kind': kind, 't': stype or '', 'rel': rel or '', 'k': [], 'img': (dl_set_info.get(name, {}).get('bannerImage') or '') if kind == 'set' else ''})
    return dl_set_idx[key]""",
    """def dl_src(kind, name, stype, rel, rush=False):
    key = (kind, name, rush if kind == 'other' else False)      # the same route (tickets, Card Trader...) is listed apart for Speed Duel and Rush Duel
    if key not in dl_set_idx:
        dl_set_idx[key] = len(dl_set_list)
        dl_set_list.append({'n': name, 'kind': kind, 't': stype or '', 'rel': rel or '', 'k': [], 'rush': bool(rush) if kind == 'other' else False,
                            'img': (dl_set_info.get(name, {}).get('bannerImage') or '') if kind == 'set' else ''})
    return dl_set_idx[key]""")
rep("si = dl_src('other', sname, 'Otra vía', '')", "si = dl_src('other', sname, 'Otra vía', '', bool(d.get('rush')))")
rep("pr.append([tcg_set_idx[sname], num, rc.strip('()') or ''.join(w[0] for w in rn.split()).upper(), round(pf, 2)])",
    "pr.append([tcg_set_idx[sname], num, rc.strip('()') or ''.join(w[0] for w in rn.split()).upper(), round(pf, 2), tcgp_pid(sname, code, rn)])")
rep("""dl_out = sorted(dl_set_list, key=lambda s: (s['rel'] or '0000'), reverse=True)
dump_js('sets-dl', dl_out)""", """dl_out = sorted(dl_set_list, key=lambda s: (s['rel'] or '0000'), reverse=True)
# character portraits, skills (how each character gives them) and in-game events (tools/dlx.py)
dlx = json.load(open('src/dl_extra.json', encoding='utf-8'))
portrait = {c['n']: c for c in dlx['chars']}
for s_ in dl_out:
    if s_['kind'] == 'char':
        s_['img'] = (portrait.get(s_['n']) or {}).get('p', '')
chars_out = {c['n']: {'p': c['p'], 'v': c['v'], 'w': c['w'], 's': []} for c in dlx['chars']}
for sk in dlx['skills']:
    for cname, how in sk['c']:
        if cname in chars_out:
            chars_out[cname]['s'].append([sk['n'], sk['d'], how, 1 if sk['rush'] else 0])
dump_js('dlinfo', {'chars': chars_out, 'events': [e for e in dlx['events'] if e['e'] and e['e'] >= '2026-06-01']})
dump_js('sets-dl', dl_out)

# ---------------- tournaments: TCG and Genesys events with their results (YGOMeta) ----------------
evs = json.load(open('src/ygm_events.json', encoding='utf-8'))
tops = json.load(open('src/ygm_topdecks.json', encoding='utf-8'))
by_ev = {}
for dk in tops:
    ev = dk.get('event') or {}
    if ev.get('_id') and not dk.get('ocg') and isinstance(dk.get('tournamentPlacement'), int) and dk['tournamentPlacement'] <= 8:
        by_ev.setdefault(ev['_id'], []).append([dk['tournamentPlacement'], dk.get('author') or '?', (dk.get('deckType') or {}).get('name') or '?', dk.get('url') or ''])
ev_out = []
for e in evs:
    if e.get('format') in ('TCG', 'Genesys') and e['date'] >= '2026-08-20' and 'Test Event' not in e['name']:
        ev_out.append({'n': e['name'], 'd': e['date'][:10], 'f': e['format'], 'c': e.get('country') or '', 'p': e.get('playerCount') or 0,
                       'ty': (e.get('tournamentType') or {}).get('name') or '', 'top': sorted(by_ev.get(e['_id'], []))})
ev_out.sort(key=lambda x: (x['d'], x['p']), reverse=True)
dump_js('events', ev_out)
print('tournaments:', len(ev_out), 'with results:', sum(1 for x in ev_out if x['top']))""")
open('tools/build_db.py', 'w', encoding='utf-8').write(t)
print('ok')
