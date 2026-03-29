kill_port() {
  p="$(fuser $1/tcp || true)"
  if [[ ! -z "$p" ]]; then
    kill "$p"
  fi
}
