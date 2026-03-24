# Imports
. bin/_logging.sh

# Params (
VENV_FOLDER=$1
# )

if [[ -z "$VENV_FOLDER" ]]; then
  echoError "Venv folder is missing."
  exit 1
fi

python -m venv "$VENV_FOLDER"
