task="${1:-deploy}"

if [[ -f ".venv/$task/bin/activate" ]]; then
  . .venv/$task/bin/activate
else
  exit
fi