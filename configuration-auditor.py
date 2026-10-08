#!/usr/bin/env python3
import argparse
import json
import os
from pathlib import Path

from core.display import Display
import html as _html
from core.registry import available_modules, load_module

modules_list = available_modules()

# Build top-level parser with subcommands: analyse | rules
parser = argparse.ArgumentParser(
    description='Configuration Auditor - apply a security benchmark to a device '
                'configuration file. Example: configuration-auditor.py analyse -m pfsense config.xml')
subparsers = parser.add_subparsers(dest='verb', required=True,
                                   help='Action to perform')

# Common arguments shared by verbs (minimal): module, output and config
parent_common = argparse.ArgumentParser(add_help=False)
parent_common.add_argument('-m', '--module', required=True, choices=modules_list,
                      help='Configuration module to use (required). '
                          f'Available: {", ".join(modules_list)}')
parent_common.add_argument('-o', '--output', help='Output CSV File')
parent_common.add_argument('-oh', '--output-html', help='Export a standalone HTML report with Aliases/Interfaces/Zones/Rules', dest='output_html')
# Note: `--interfaces` and `--zones` are now separate verbs
parent_common.add_argument('--autofix', help='Automatically try to fix errors in input file', action='store_true')
parent_common.add_argument('config', help='Configuration file exported from the device', nargs=1)

# analyse subcommand has the original flags that now apply only to analyse
analyse_parser = subparsers.add_parser('analyse', parents=[parent_common],
                               help='Run analysis checks')
analyse_parser.add_argument('-q', '--quiet', help='Not interactive: ignore manual steps', action='store_true')
analyse_parser.add_argument('-v', '--verbose', help='Increase verbosity', action='store_true')
analyse_parser.add_argument('-j', '--json', help='Input file is json already parsed by the module', action='store_true')
analyse_parser.add_argument('-l', '--levels', help='Levels to check. (default: 1)', nargs='+', default="1")
analyse_parser.add_argument('-i', '--ids', help='Checks id to perform. (default: all if applicable)', nargs='+', default=None)
analyse_parser.add_argument('-c', '--resume', help='Resume an audit that was already started. Automatic items are re-checked but manually set values are retrieved from cache.', action='store_true')
analyse_parser.add_argument('-w', '--wan', help='List of wan interfaces separated by spaces (example: --wan port1 port2)', nargs='+', default=None)

subparsers.add_parser('rules', parents=[parent_common], help='List firewall rules in a pretty table')
subparsers.add_parser('aliases', parents=[parent_common], help='List address/service aliases in a pretty table')
subparsers.add_parser('interfaces', parents=[parent_common], help='List interfaces in a pretty table')
subparsers.add_parser('zones', parents=[parent_common], help='List zones in a pretty table')

args = parser.parse_args()

filepath = args.config[0]
verbose = getattr(args, 'verbose', False)
quiet = getattr(args, 'quiet', False)
outputfile = args.output

# Display object
display = Display()

# Load the requested vendor module
try:
    module = load_module(args.module, display, verbose)
except ValueError as e:
    print(f'[!] {e}')
    exit(-1)

print(f'[+] Using module: {module.name} ({module.description})')

# If the user asked for the 'rules' verb, print/export firewall rules and exit.
if args.verb == 'rules':

    try:
        if getattr(args, 'json', False):
            device = module.parse_json(filepath)
        else:
            device = module.parse(filepath, autofix=args.autofix)
    except (NotImplementedError, ValueError) as e:
        print(f'[!] {e}')
        exit(-1)

    # Currently implemented for pfSense only
    if module.name != 'pfsense':
        print('[!] The rules verb is currently implemented only for pfSense')
        exit(-1)

    rules = device.get_filter_rules()
    # Build table rows
    rows = []
    for i, rule in enumerate(rules):
        if not isinstance(rule, dict):
            continue
        iface = rule.get('interface', '')
        action = rule.get('type', 'pass')
        proto = rule.get('protocol', '')
        src = display._shorten_endpoint(rule.get('source'))
        srcport = ''
        # pfSense places ports inside source/destination 'port' key when protocol present
        s = rule.get('source')
        if isinstance(s, dict) and s.get('port'):
            srcport = str(s.get('port'))
        dst = display._shorten_endpoint(rule.get('destination'))
        dstport = ''
        d = rule.get('destination')
        if isinstance(d, dict) and d.get('port'):
            dstport = str(d.get('port'))
        descr = rule.get('descr', '')
        disabled = 'yes' if 'disabled' in rule else ''
        log = 'yes' if 'log' in rule else ''
        rows.append([str(i), iface, action, proto, src, srcport, dst, dstport, descr, disabled, log])

    headers = ['#', 'Interface', 'Action', 'Proto', 'Source', 'S.Port', 'Dest', 'D.Port', 'Descr', 'Disabled', 'Log']
    display.print_table(headers, rows, max_widths={8: 30})

    # Export CSV if requested
    if outputfile is not None:
        print('------------------------------------------------')
        print(f'[+] Exporting rules in {outputfile}')
        with open(outputfile, 'w+') as fh:
            fh.write(','.join(headers) + '\n')
            for r in rows:
                # escape quotes
                line = ','.join('"{}"'.format(c.replace('"', '""')) for c in r)
                fh.write(line + '\n')
        print('[+] Finished')
    # If HTML export was requested, do not exit here - fall through to the
    # global HTML generator which will build a full report. Otherwise exit.
    if not getattr(args, 'output_html', None):
        exit(0)

# If HTML export requested, generate a full standalone HTML report with tabs
if getattr(args, 'output_html', None):
    try:
        if getattr(args, 'json', False):
            device = module.parse_json(filepath)
        else:
            device = module.parse(filepath, autofix=args.autofix)
    except (NotImplementedError, ValueError) as e:
        print(f'[!] {e}')
        exit(-1)

    def escape(s):
        return _html.escape(str(s)) if s is not None else ''

    # Gather Aliases
    aliases_rows = []
    try:
        aliases = device.get_aliases()
    except Exception:
        aliases = []
    for a in aliases:
        if not isinstance(a, dict):
            continue
        name = a.get('name', '')
        entries = []
        if a.get('address') is not None:
            addr = a['address']
            if isinstance(addr, list):
                entries = [str(x) for x in addr]
            else:
                entries = [str(addr)]
        elif a.get('content') is not None:
            c = a['content']
            if isinstance(c, list):
                entries = [str(x) for x in c]
            else:
                entries = [str(c)]
        descr = a.get('descr', '')
        aliases_rows.append((name, '; '.join(entries), descr))

    # Gather Interfaces
    interfaces_rows = []
    try:
        if module.name == 'pfsense':
            interfaces = device.get_interfaces()
            for name, iface in interfaces.items():
                if not isinstance(iface, dict):
                    interfaces_rows.append((name, '', '', ''))
                    continue
                dev = iface.get('if', '')
                descr = iface.get('descr', '')
                status = 'enabled' if 'enable' in iface else 'disabled'
                ipv4 = ''
                if iface.get('ipaddr'):
                    ipv4 = iface.get('ipaddr')
                    if iface.get('subnet'):
                        ipv4 = f"{ipv4}/{iface.get('subnet')}"
                ipv6 = ''
                if iface.get('ipaddrv6'):
                    ipv6 = iface.get('ipaddrv6')
                    if iface.get('subnetv6'):
                        ipv6 = f"{ipv6}/{iface.get('subnetv6')}"
                interfaces_rows.append((name, dev, descr, status, ipv4, ipv6))
        elif module.name == 'fortigate':
            interfaces = device.get_interfaces()
            for iface in interfaces:
                name = iface.get('edit', '')
                itype = iface.get('type', '')
                status = iface.get('status', '')
                ips = ''
                if 'ip' in iface and isinstance(iface['ip'], list):
                    ips = ','.join(iface['ip'])
                interfaces_rows.append((name, itype, status, ips))
    except Exception:
        interfaces_rows = []

    # Gather Zones
    zones_rows = []
    try:
        if hasattr(device, 'get_zones'):
            z = device.get_zones()
            if isinstance(z, list):
                for zone in z:
                    name = zone.get('edit', '') if isinstance(zone, dict) else str(zone)
                    interfaces = zone.get('interface', '') if isinstance(zone, dict) else ''
                    if isinstance(interfaces, list):
                        interfaces = ','.join(interfaces)
                    zones_rows.append((name, interfaces))
    except Exception:
        zones_rows = []

    # Gather Rules
    rules_rows = []
    parts = []
    try:
        if hasattr(device, 'get_filter_rules'):
            rules = device.get_filter_rules()
            for i, rule in enumerate(rules):
                if not isinstance(rule, dict):
                    continue
                iface = rule.get('interface', '')
                action = rule.get('type', 'pass')
                proto = rule.get('protocol', '')
                src = ''
                if isinstance(rule.get('source'), dict):
                    if 'any' in rule.get('source'):
                        src = 'any'
                    else:
                        src = ';'.join(str(v) for v in rule.get('source').values() if isinstance(v, (str, int)))
                else:
                    src = str(rule.get('source', ''))
                dst = ''
                if isinstance(rule.get('destination'), dict):
                    if 'any' in rule.get('destination'):
                        dst = 'any'
                    else:
                        dst = ';'.join(str(v) for v in rule.get('destination').values() if isinstance(v, (str, int)))
                else:
                    dst = str(rule.get('destination', ''))
                descr = rule.get('descr', '')
                rules_rows.append((str(i), iface, action, proto, src, dst, descr))
    except Exception:
        rules_rows = []

    parts.append('<!doctype html>')
    # Build HTML
    def table_html(headers, rows):
        th = ''.join(f'<th>{escape(h)}</th>' for h in headers)
        trs = []
        for r in rows:
            tds = ''.join(f'<td>{escape(c)}</td>' for c in r)
            trs.append(f'<tr>{tds}</tr>')
        # use Bulma table classes for nicer default styling
        return f'<table class="table is-fullwidth is-striped is-hoverable"><thead><tr>{th}</tr></thead><tbody>{"".join(trs)}</tbody></table>'

    aliases_html = table_html(['Name', 'Entries', 'Description'], aliases_rows)
    if module.name == 'pfsense':
        interfaces_html = table_html(['Name', 'Device', 'Descr', 'Status', 'IPv4', 'IPv6'], interfaces_rows)
    else:
        interfaces_html = table_html(['Name', 'Type', 'Status', 'IPs'], interfaces_rows)
    zones_html = table_html(['Name', 'Interfaces'], zones_rows)
    # Build maps for detail panes
    def slug(s):
        return ''.join(c if c.isalnum() else '_' for c in str(s))

    alias_map = {a[0]: {'entries': a[1], 'descr': a[2], 'id': 'alias_' + slug(a[0])} for a in aliases_rows}
    iface_map = {}
    if module.name == 'pfsense':
        for i in interfaces_rows:
            name = i[0]
            iface_map[name] = {'device': i[1], 'descr': i[2], 'status': i[3], 'ipv4': i[4], 'ipv6': i[5], 'id': 'iface_' + slug(name)}
    else:
        for i in interfaces_rows:
            name = i[0]
            iface_map[name] = {'type': i[1], 'status': i[2], 'ips': i[3], 'id': 'iface_' + slug(name)}

    # Build rules table with hoverable spans for interfaces and aliases
    def cell_with_detail(text):
        if text in iface_map:
            return f'<span class="has-detail" data-detail="{iface_map[text]["id"]}">{escape(text)}</span>'
        if text in alias_map:
            return f'<span class="has-detail" data-detail="{alias_map[text]["id"]}">{escape(text)}</span>'
        return escape(text)

    def action_cell(action):
        a = str(action or '').lower()
        if a == 'pass':
            return f'<span class="tag is-success">{escape(action)}</span>'
        if a in ('block', 'reject', 'deny'):
            return f'<span class="tag is-danger">{escape(action)}</span>'
        return escape(action)

    # construct rules table rows HTML
    rule_trs = []
    for r in rules_rows:
        # r = (idx, iface, action, proto, src, dst, descr)
        cells = [escape(r[0]), cell_with_detail(r[1]), action_cell(r[2]), escape(r[3]), cell_with_detail(r[4]), cell_with_detail(r[5]), escape(r[6])]
        tds = ''.join(f'<td>{c}</td>' for c in cells)
        rule_trs.append(f'<tr>{tds}</tr>')
    rules_html = f'<table><thead><tr>{"".join(f"<th>{escape(h)}</th>" for h in ["#","Interface","Action","Proto","Source","Dest","Descr"])}</tr></thead><tbody>{"".join(rule_trs)}</tbody></table>'

    # build hidden detail templates for aliases and interfaces
    alias_templates = []
    for name, info in alias_map.items():
        tid = info['id']
        alias_templates.append(f'<div id="{tid}" class="detail-template" style="display:none"><h3>Alias {escape(name)}</h3><div><strong>Entries:</strong><div>{escape(info["entries"])}</div><strong>Description:</strong><div>{escape(info["descr"])}</div></div></div>')

    iface_templates = []
    for name, info in iface_map.items():
        tid = info['id']
        if module.name == 'pfsense':
            iface_templates.append(f'<div id="{tid}" class="detail-template" style="display:none"><h3>Interface {escape(name)}</h3><div><div><strong>Device:</strong> {escape(info.get("device",""))}</div><div><strong>Description:</strong> {escape(info.get("descr",""))}</div><div><strong>Status:</strong> {escape(info.get("status",""))}</div><div><strong>IPv4:</strong> {escape(info.get("ipv4",""))}</div><div><strong>IPv6:</strong> {escape(info.get("ipv6",""))}</div></div></div>')
        else:
            iface_templates.append(f'<div id="{tid}" class="detail-template" style="display:none"><h3>Interface {escape(name)}</h3><div><div><strong>Type:</strong> {escape(info.get("type",""))}</div><div><strong>Status:</strong> {escape(info.get("status",""))}</div><div><strong>IPs:</strong> {escape(info.get("ips",""))}</div></div></div>')

    parts.append('<html>')
    parts.append('<head>')
    parts.append('<meta charset="utf-8">')
    parts.append('<title>Configuration Auditor report</title>')
    parts.append('<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bulma@0.9.4/css/bulma.min.css">')
    parts.append('<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bulma-prefers-color-scheme@1.0.3/dist/bulma-prefers-color-scheme.min.css">')
    parts.append('<style>')
    parts.append('/* Lightweight layout + theme variables */')
    parts.append(':root{--bg:#ffffff;--fg:#222222;--muted:#666666;--accent:#0b66c3;--table-border:#d0d7de;--panel-bg:#ffffff;--panel-border:#999999}')
    parts.append('.dark{--bg:#0f1720;--fg:#e6eef6;--muted:#9fb0c8;--accent:#4aa3ff;--table-border:#22313a;--panel-bg:#071016;--panel-border:#133042}')
    parts.append('html,body{height:100%;background:var(--bg);color:var(--fg);font-family:Inter,Segoe UI,Arial,Helvetica,sans-serif;margin:0;padding:18px}')
    parts.append('header{display:flex;align-items:center;justify-content:space-between;margin-bottom:14px}')
    parts.append('h1{font-size:18px;margin:0}')
    parts.append('.controls{display:flex;gap:8px;align-items:center}')
    parts.append('.tabs{margin-bottom:12px}')
    parts.append('.tab{display:none;padding-top:8px}')
    parts.append('.tabs button{background:transparent;border:1px solid var(--table-border);padding:6px 10px;border-radius:6px;color:var(--fg);cursor:pointer}')
    parts.append('.tabs button.active{background:var(--accent);color:#fff;border-color:var(--accent)}')
    parts.append('table{border-collapse:collapse;width:100%;background:var(--panel-bg);border:1px solid var(--table-border);border-radius:6px;overflow:hidden}')
    parts.append('th,td{padding:8px 10px;text-align:left;vertical-align:top;border-bottom:1px solid var(--table-border)}')
    parts.append('thead th{background:linear-gradient(180deg,rgba(0,0,0,0.03),transparent);font-weight:600}')
    parts.append('tbody tr:hover{background:rgba(0,0,0,0.03)}')
    parts.append('.has-detail{color:var(--accent);text-decoration:underline;cursor:pointer}')
    parts.append('.detail-template{display:none}')
    parts.append('#hover-pane{position:absolute;display:none;z-index:9999;min-width:220px;max-width:520px;background:var(--panel-bg);border:1px solid var(--panel-border);padding:10px;border-radius:6px;box-shadow:0 6px 20px rgba(2,6,23,0.35);color:var(--fg)}')
    parts.append('.detail-template h3{margin:0 0 6px 0;font-size:14px}')
    parts.append('.muted{color:var(--muted);font-size:12px;margin-top:6px}')
    # Note: Do not reimplement Bulma dark mode here; prefer Bulma or extensions.
    parts.append('</style>')
    parts.append('</head>')
    parts.append('<body>')
    parts.append('<h1>Configuration Auditor report</h1>')
    parts.append('<div class="tabs">')
    parts.append('<button onclick="show(\'aliases\')">Aliases</button>')
    parts.append('<button onclick="show(\'interfaces\')">Interfaces</button>')
    parts.append('<button onclick="show(\'zones\')">Zones</button>')
    parts.append('<button onclick="show(\'rules\')">Rules</button>')
    parts.append('</div>')
    parts.append('<div class="controls">')
    parts.append('<label for="theme-select" style="font-size:13px;margin-right:6px">Theme</label>')
    parts.append('<select id="theme-select"><option value="light">Light</option><option value="dark">Dark</option></select>')
    parts.append('</div>')
    parts.append('<div id="aliases" class="tab">')
    parts.append(aliases_html)
    parts.append('</div>')
    parts.append('<div id="interfaces" class="tab">')
    parts.append(interfaces_html)
    parts.append('</div>')
    parts.append('<div id="zones" class="tab">')
    parts.append(zones_html)
    parts.append('</div>')
    parts.append('<div id="rules" class="tab">')
    parts.append(rules_html)
    parts.append('</div>')
    # inject hidden templates for details and the floating hover pane
    parts.append('<div id="detail-templates" style="display:none">')
    for t in alias_templates:
        parts.append(t)
    for t in iface_templates:
        parts.append(t)
    parts.append('</div>')
    parts.append('<div id="hover-pane"></div>')
    parts.append('<script>')
    parts.append("function show(id){document.querySelectorAll('.tab').forEach(function(e){e.style.display='none'});document.getElementById(id).style.display='block';document.querySelectorAll('.tabs button').forEach(function(b){b.classList.remove('active')});var btns=document.querySelectorAll('.tabs button');for(var i=0;i<btns.length;i++){if(btns[i].getAttribute('onclick').includes("'"+id+"'")){btns[i].classList.add('active')}}}")
    parts.append("show('aliases')")
    # hover JS: add positioning, click-to-stick, and outside-click dismissal
    parts.append("""function positionPane(el,pane){
        var r = el.getBoundingClientRect();
        var left = r.right + window.scrollX + 10;
        var top = r.top + window.scrollY;
        var ww = window.innerWidth;
        if ((left + pane.offsetWidth) > ww) left = r.left + window.scrollX - pane.offsetWidth - 10;
        if (left < 10) left = 10;
        pane.style.left = left + 'px';
        pane.style.top = top + 'px';
    }

    function initHover(){
        document.querySelectorAll('.has-detail').forEach(function(el){
            el.addEventListener('mouseenter',function(ev){
                var id = el.getAttribute('data-detail');
                var tpl = document.getElementById(id);
                if (!tpl) return;
                var pane = document.getElementById('hover-pane');
                pane.innerHTML = '<button class="delete" id="detail-close" aria-label="close"></button>' + tpl.innerHTML;
                pane.style.display = 'block';
                pane.dataset.sticky = '0';
                pane.removeAttribute('data-current');
                positionPane(el,pane);
            });
            el.addEventListener('mouseleave',function(ev){
                var pane = document.getElementById('hover-pane');
                if (pane.dataset.sticky === '1') return;
                pane.style.display = 'none';
                pane.innerHTML = '';
                pane.removeAttribute('data-current');
            });
            el.addEventListener('click',function(ev){
                ev.stopPropagation();
                var id = el.getAttribute('data-detail');
                var tpl = document.getElementById(id);
                if (!tpl) return;
                var pane = document.getElementById('hover-pane');
                if (pane.dataset.sticky === '1' && pane.getAttribute('data-current') === id){
                    pane.dataset.sticky = '0'; pane.style.display = 'none'; pane.innerHTML = ''; pane.removeAttribute('data-current'); return;
                }
                pane.innerHTML = '<button class="delete" id="detail-close" aria-label="close"></button>' + tpl.innerHTML;
                pane.style.display = 'block';
                pane.dataset.sticky = '1';
                pane.setAttribute('data-current', id);
                positionPane(el,pane);
            });
        });

        // click outside hides non-sticky pane or unsticks sticky pane
        document.addEventListener('click',function(ev){
            var pane = document.getElementById('hover-pane'); if(!pane) return;
            var target = ev.target;
            if (pane.dataset.sticky === '1'){
                if (pane.contains(target) || target.closest('.has-detail')) return;
                pane.dataset.sticky = '0'; pane.style.display = 'none'; pane.innerHTML = ''; pane.removeAttribute('data-current');
            } else {
                pane.style.display = 'none'; pane.innerHTML = ''; pane.removeAttribute('data-current');
            }
        });

        // close button inside pane
        document.addEventListener('click',function(ev){
            if (ev.target && ev.target.id === 'detail-close'){
                var pane = document.getElementById('hover-pane');
                pane.dataset.sticky = '0'; pane.style.display = 'none'; pane.innerHTML = ''; pane.removeAttribute('data-current');
            }
        });

    }
    window.addEventListener('load',function(){initHover();initTheme();})""")
    parts.append('function initTheme(){var sel=document.getElementById("theme-select");var pref=localStorage.getItem("auditor-theme");if(!pref){pref=(window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches)?"dark":"light";}applyTheme(pref);sel.value=pref;sel.addEventListener("change",function(){applyTheme(sel.value)});}function applyTheme(t){if(t==="dark"){document.documentElement.classList.add("dark","is-dark");document.documentElement.setAttribute("data-theme","dark");}else{document.documentElement.classList.remove("dark","is-dark");document.documentElement.setAttribute("data-theme","light");}localStorage.setItem("auditor-theme",t);}')
    parts.append('</script>')
    parts.append('</body>')
    parts.append('</html>')
    full_html = '\n'.join(parts)

    outpath = getattr(args, 'output_html')
    try:
        with open(outpath, 'w', encoding='utf-8') as fh:
            fh.write(full_html)
        print(f'[+] HTML report written to {outpath}')
    except Exception as e:
        print(f'[!] Failed to write HTML: {e}')
    exit(0)

# interfaces verb
if args.verb == 'interfaces':
    try:
        if getattr(args, 'json', False):
            device = module.parse_json(filepath)
        else:
            device = module.parse(filepath, autofix=args.autofix)
    except (NotImplementedError, ValueError) as e:
        print(f'[!] {e}')
        exit(-1)

    # pfSense: interfaces as dict; FortiGate: list
    if module.name == 'pfsense':
        interfaces = device.get_interfaces()
        if not interfaces:
            print('[!] No interfaces found in configuration')
            exit(0)
        rows = []
        for name, iface in interfaces.items():
            if not isinstance(iface, dict):
                rows.append([name, '', '', ''])
                continue
            dev = iface.get('if', '')
            descr = iface.get('descr', '')
            status = 'enabled' if 'enable' in iface else 'disabled'
            ipv4 = ''
            if iface.get('ipaddr'):
                ipv4 = iface.get('ipaddr')
                if iface.get('subnet'):
                    ipv4 = f"{ipv4}/{iface.get('subnet')}"
            ipv6 = ''
            if iface.get('ipaddrv6'):
                ipv6 = iface.get('ipaddrv6')
                if iface.get('subnetv6'):
                    ipv6 = f"{ipv6}/{iface.get('subnetv6')}"
            rows.append([name, dev, descr, status, ipv4, ipv6])
        headers = ['Name', 'Device', 'Descr', 'Status', 'IPv4', 'IPv6']
        display.print_table(headers, rows, max_widths={2:40,4:20,5:20})
        exit(0)
    elif module.name == 'fortigate':
        interfaces = device.get_interfaces()
        rows = []
        for iface in interfaces:
            name = iface.get('edit', '')
            itype = iface.get('type', '')
            status = iface.get('status', '')
            ips = ''
            if 'ip' in iface and isinstance(iface['ip'], list):
                ips = ','.join(iface['ip'])
            rows.append([name, itype, status, ips])
        headers = ['Name', 'Type', 'Status', 'IPs']
        display.print_table(headers, rows, max_widths={3:40})
        exit(0)
    else:
        device.show_interfaces()
        exit(0)

# zones verb
if args.verb == 'zones':
    try:
        if getattr(args, 'json', False):
            device = module.parse_json(filepath)
        else:
            device = module.parse(filepath, autofix=args.autofix)
    except (NotImplementedError, ValueError) as e:
        print(f'[!] {e}')
        exit(-1)

    if module.name == 'fortigate':
        zones = device.get_zones()
        rows = []
        for z in zones:
            name = z.get('edit', '')
            interfaces = z.get('interface', '')
            if isinstance(interfaces, list):
                interfaces = ','.join(interfaces)
            rows.append([name, interfaces])
        headers = ['Name', 'Interfaces']
        display.print_table(headers, rows, max_widths={1:60})
        exit(0)
    else:
        print('[!] Zones are not supported for this module')
        exit(0)

# aliases verb
if args.verb == 'aliases':
    try:
        if getattr(args, 'json', False):
            device = module.parse_json(filepath)
        else:
            device = module.parse(filepath, autofix=args.autofix)
    except (NotImplementedError, ValueError) as e:
        print(f'[!] {e}')
        exit(-1)

    if module.name != 'pfsense':
        print('[!] The aliases verb is currently implemented only for pfSense')
        exit(-1)

    aliases = device.get_aliases()
    rows = []
    for a in aliases:
        if not isinstance(a, dict):
            continue
        name = a.get('name', '')
        # alias can be a list or string under 'address' or 'content' depending on type
        entries = []
        if a.get('address') is not None:
            addr = a['address']
            if isinstance(addr, list):
                entries = [str(x) for x in addr]
            else:
                entries = [str(addr)]
        elif a.get('content') is not None:
            c = a['content']
            if isinstance(c, list):
                entries = [str(x) for x in c]
            else:
                entries = [str(c)]
        descr = a.get('descr', '')
        # For compact table, join entries with '; '
        rows.append([name, '; '.join(entries), descr])

    headers = ['Name', 'Entries', 'Description']
    display.print_table(headers, rows, max_widths={1: 60, 2: 30})

    if outputfile is not None:
        print('------------------------------------------------')
        print(f'[+] Exporting aliases in {outputfile}')
        with open(outputfile, 'w+') as fh:
            fh.write(','.join(headers) + '\n')
            for r in rows:
                line = ','.join('"{}"'.format(c.replace('"', '""')) for c in r)
                fh.write(line + '\n')
        print('[+] Finished')
    exit(0)

# Cache file is scoped per module so different vendors don't collide.
cache_file_path = str(Path.home()) + f'/.cache/configuration-auditor-{module.name}.json'

# Create/Open cache file
if not os.path.exists(cache_file_path):
    if args.resume:
        print('[!] Cannot resume this benchmark because there is no cache file')
        exit(-1)
    else:
        print(f'[!] Creating local cache file in {cache_file_path}')
        cache_file = open(cache_file_path, mode='a')
        cache_file.write("{}")
        cache_file.close()
cache_file = open(cache_file_path, "r+")
cache = json.load(cache_file)
cache_file.close()

if filepath not in cache.keys():
    # There is no cache for this configuration file
    if args.resume:
        print(f'[!] Cannot resume this benchmark because there is no cache results for config {filepath}')
        exit(-1)
    cached_results = {}
else:
    cached_results = cache[filepath]

# Parse the configuration file into a Device via the selected module
try:
    if getattr(args, 'json', False):
        device = module.parse_json(filepath)
    else:
        device = module.parse(filepath, autofix=args.autofix)
except (NotImplementedError, ValueError) as e:
    print(f'[!] {e}')
    exit(-1)

if getattr(args, 'wan', None) is not None:
    print(f'[+] Configuring WAN interfaces: {", ".join(args.wan)}')
    device.set_wan_interfaces(args.wan)

# Display interfaces (vendor-specific formatting is delegated to the device)
# `interfaces` is provided only for the `interfaces` verb; guard access.
if getattr(args, 'interfaces', False):
    device.show_interfaces()
    exit(0)

# Display zones (vendor-specific formatting is delegated to the device)
# `zones` is provided only for the `zones` verb; guard access.
if getattr(args, 'zones', False):
    device.show_zones()
    exit(0)

if args.verb == 'analyse':
    print(f'[+] Starting checks for levels: {",".join(getattr(args, "levels", ["1"]))}')

    if getattr(args, 'ids', None) is not None:
        print(f'[+] Limiting to checks {", ".join(args.ids)}')

# Discover checks provided by the module
module.load_checks()

# Instantiate checkers
performed_checks = []

if args.verb == 'analyse':
    checkers = [check_class(device, display, verbose) for check_class in module.check_classes()]
    for checker in checkers:
        if not checker.is_valid():
            continue

        if getattr(args, 'ids', None) is not None and checker.get_id() not in args.ids:
            continue

        if checker.enabled and checker.is_level_applicable(getattr(args, 'levels', ["1"])):
            if checker.auto:
                checker.run()
            else:
                if quiet:
                    checker.skip()
                else:
                    if getattr(args, 'resume', False):
                        if checker.get_id() in cached_results.keys():
                            # There is a cached result for this check
                            checker.restore_from_cache(cached_results[checker.get_id()])
                        else:
                            # There is no cached result, we have to perform the step
                            checker.run()
                    else:
                        checker.run()
            performed_checks.append(checker)

            # Save to cache
            cached_results[checker.get_id()] = {
                "result": checker.result,
                "message": checker.message,
                "question": checker.question,
                "question_context": checker.question_context,
                "answer": checker.answer,
            }

print('[+] Finished')
print('------------------------------------------------')
print('[+] Here is a summary:')

for performed_check in performed_checks:
    print(f'[{performed_check.get_id()}]\t[{performed_check.result}]\t{performed_check.title}')

# Save cache file
cache[filepath] = cached_results
cache_file = open(cache_file_path, "w")
json.dump(cache, cache_file)
cache_file.close()

# Export
if outputfile is not None:
    print('------------------------------------------------')
    print(f'[+] Exporting results in {outputfile}')
    outputfile = open(outputfile, "w+")
    outputfile.write("Check ID,Result,Check Title,Levels,Log\n")
    for performed_check in performed_checks:
        cleaned_message = performed_check.get_log().replace('"', '\'')
        levels = ",".join(str(x) for x in performed_check.levels)
        line = f'{performed_check.get_id()},{performed_check.result},{performed_check.title},"{levels}","{cleaned_message}"\n'
        outputfile.write(line)
    outputfile.close()
    print('[+] Finished')
