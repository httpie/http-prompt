import click


class Printer():

    def __init__(self, fg=None, bg=None, err=False):
        self.fg = fg
        self.bg = bg
        self.err = err

    def write(self, data):
        if self.err:
            click.secho(data, fg=self.fg, bg=self.bg, nl=True, err=self.err)
        else:
            click.echo_via_pager(click.style(data, fg=self.fg, bg=self.bg))

    def close(self):
        pass
