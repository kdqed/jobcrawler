local lsp = require "plugins.lsp"

lsp.add_server {
  name = "pylsp",
  language = "python",
  file_patterns = { "%.py$" },
  command = { './.venv/bin/pylsp' },
  verbose = false
}
