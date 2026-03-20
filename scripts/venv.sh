#!/bin/bash

task="${1:-deploy}"

. .venv/$task/bin/activate
