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

    def print_table(self, headers, rows, max_widths=None):
        """Print a simple ASCII table.

        headers: list of column headers
        rows: list of row iterables (strings)
        max_widths: optional dict col_index->max width
        """
        # Normalize rows
        rows = [list(map(lambda x: '' if x is None else str(x), r)) for r in rows]
        col_count = len(headers)
        # compute widths
        widths = [len(h) for h in headers]
        for r in rows:
            for i in range(col_count):
                if i < len(r):
                    widths[i] = max(widths[i], len(r[i]))
        if max_widths:
            for i, w in (max_widths.items() if isinstance(max_widths, dict) else []):
                if 0 <= i < col_count:
                    widths[i] = min(widths[i], w)

        # build format
        sep = ' | '
        line = sep.join(h.ljust(widths[i]) for i, h in enumerate(headers))
        print(line)
        print('-' * len(line))
        for r in rows:
            cells = []
            for i in range(col_count):
                cell = r[i] if i < len(r) else ''
                # truncate if too long
                w = widths[i]
                if len(cell) > w:
                    cell = cell[: max(0, w-3)] + '...'
                cells.append(cell.ljust(w))
            print(sep.join(cells))

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
