import re


ANSI_ESCAPE = re.compile(r'\x1b\[[0-9;]*m')


class Display:

    def __init__(self):
        return

    def show(self, text, end='\n'):
        if isinstance(text, list):
            for line in text:
                print(f'\t| {line}', end=end)
        else:
            print(f'\t| {text}', end=end)

    def ask(self, question_context, question):

        print("")  # Go to new line
        self.show('--------------[ Question ] --------------------')
        if question_context is not None:
            self.show(question_context)
        self.show(f'{question} :', end='')
        answer = input()
        self.show('-----------------------------------------------')
        return answer

    def print_table(self, headers, rows, max_widths=None, row_colors=None,
                    cell_colors=None, title_lines=None):
        """Print a simple ASCII table.

        headers: list of column headers
        rows: list of row iterables (strings)
        max_widths: optional dict col_index->max width
        cell_colors: optional list of dicts mapping column indexes to ANSI colors
        title_lines: optional lines to display in a box matching the table width
        """
        # Normalize rows
        rows = [list(map(lambda x: '' if x is None else str(x), r)) for r in rows]
        col_count = len(headers)
        # compute widths
        widths = [len(h) for h in headers]
        for r in rows:
            for i in range(col_count):
                if i < len(r):
                    widths[i] = max(widths[i], len(ANSI_ESCAPE.sub('', r[i])))
        if max_widths:
            for i, w in (max_widths.items() if isinstance(max_widths, dict) else []):
                if 0 <= i < col_count:
                    widths[i] = min(widths[i], w)

        # build format
        sep = ' | '
        line = sep.join(h.ljust(widths[i]) for i, h in enumerate(headers))
        if title_lines:
            inner_width = len(line)
            border = '+' + '-' * (inner_width + 2) + '+'
            print(border)
            for title in title_lines:
                title = str(title)
                visible_title = ANSI_ESCAPE.sub('', title)
                if len(visible_title) > inner_width:
                    title = visible_title[:inner_width]
                    visible_title = title
                print('| ' + title + ' ' * (inner_width - len(visible_title)) + ' |')
            print(border)
        print(line)
        print('-' * len(line))
        for row_number, r in enumerate(rows):
            cells = []
            row_color = (row_colors[row_number]
                         if row_colors and row_number < len(row_colors)
                         else None)
            for i in range(col_count):
                cell = r[i] if i < len(r) else ''
                # truncate if too long
                w = widths[i]
                visible_cell = ANSI_ESCAPE.sub('', cell)
                if len(visible_cell) > w:
                    cell = visible_cell[: max(0, w-3)] + '...'
                    visible_cell = cell
                cell = cell + ' ' * max(0, w - len(visible_cell))
                if cell_colors and row_number < len(cell_colors):
                    color = cell_colors[row_number].get(i)
                    if color:
                        cell = f'{color}{cell}\033[0m'
                        # Restore the row color so the remainder of a
                        # highlighted row stays highlighted after a colored
                        # cell resets its own ANSI style.
                        if row_color:
                            cell += row_color
                cells.append(cell)
            line = sep.join(cells)
            if row_color:
                line = f'{row_color}{line}\033[0m'
            print(line)

    def _shorten_endpoint(self, endpoint):
        """Return a concise string for pfSense endpoint structures."""
        if endpoint is None:
            return ''
        if not isinstance(endpoint, dict):
            return str(endpoint)
        if 'any' in endpoint:
            return 'any'
        # common keys
        for k in ('address', 'network', 'ip', 'name'):
            if k in endpoint and isinstance(endpoint[k], str):
                return endpoint[k]
        if 'port' in endpoint:
            return str(endpoint['port'])
        # fallback: join simple scalar keys
        parts = []
        for k, v in endpoint.items():
            if isinstance(v, (str, int)):
                parts.append(f'{k}={v}')
        if parts:
            return ','.join(parts)
        try:
            import json

            return json.dumps(endpoint)
        except Exception:
            return str(endpoint)
