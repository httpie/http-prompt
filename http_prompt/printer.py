import click


class Printer():

    def __init__(self, fg=None, bg=None, nl=False, err=False):
        self.fg = fg
        self.bg = bg
        self.nl = nl
        self.err = err

    def write(self, data):
        if self.err:
            click.secho(data, fg=self.fg, nl=self.nl, err=self.err)
        else:
            click.style
            click.echo_via_pager(click.style(data, fg=self.fg, bg=self.bg), nl=self.nl)

    def close(self):
        pass
