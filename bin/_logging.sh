# --- Logging utilities.

# RED=1
# GREEN=2
# YELLOW=3
# BLUE=4
# MAGENTA=5
# CYAN=6

echoInfo() {
  echo "$(tput setaf 4)(-- INFO --) $1$(tput sgr 0)"
}

echoWarning() {
  echo "$(tput setaf 3)(-- WARNING --) $1$(tput sgr 0)"
}

echoError() {
  echo "$(tput setaf 1)(-- ERROR --) $1$(tput sgr 0)"
}

echoStart() {
  echo "$(tput setaf 6)(-- START --) $1$(tput sgr 0)"
}

echoSuccess() {
  echo "$(tput setaf 2)(-- SUCCESS --) $1$(tput sgr 0)"
}
