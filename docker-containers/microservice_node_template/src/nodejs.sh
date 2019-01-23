#!/usr/bin/env bash
set -e
exec "/usr/bin/nodejs_bin" "--max_old_space_size=${MAX_OLD_SPACE_SIZE_MB:-256}" "$@"
