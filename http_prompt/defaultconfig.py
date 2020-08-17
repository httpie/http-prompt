# Highlighting style for prompt commands. Available values:
# algol, algol_nu, autumn, borland, bw, colorful, default, emacs, friendly,
# fruity, igor, lovelace, manni, monokai, murphy, native, paraiso-dark,
# paraiso-light, pastie, perldoc, rrt, solarized, tango, trac, vim, vs, xcode.
# Preview themes at http://http-prompt.com/themes
command_style = 'solarized'

# Highlighting style for HTTPie's output. Available values are the same as
# command_style. Set this to None to use HTTPie's default style, which you
# can refer to https://httpie.org/doc#config-file-location
output_style = None

# The tool used to paginate output. Available values: 'less' and 'more'.
# Note that 'more' does not support ANSI colors.
pager = 'less'

# What to do when a response has a 'Set-Cookie' header? Available values:
# 'auto': set the cookie automatically and silently
# 'ask': ask the user if they want to set the cookie
# 'off': do nothing with the 'Set-Cookie' header
set_cookies = 'auto'

# Enable Vi editor mode? Available values: True / False.
# When Vi mode is enabled, you use Vi-like keybindings to edit your commands.
# When it is disabled, you use Emacs keybindings.
vi = False

# Prompt format using the urlparse module terms.
# Available values:
# 'scheme': URL scheme specifier
# 'netloc': Network location part ([] compliant on dots)
# 'path': Hierarchical path ([] compliant on slashes)
# 'params': Parameters for last path element
# 'query': Query component
# 'fragment': Fragment identifier
# You can add a pythonic [] operator (e.g. path[-2:] returns the last two
# elements of the variable path).
# See https://docs.python.org/2/library/urlparse.html#module-urlparse
prompt = '{scheme}{netloc}{path}{params}{query}{fragment}'
