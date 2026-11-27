#!/usr/bin/env bash
set -e

pid_file=/tmp/risk-dashboard.pid
if [ -f "$pid_file" ] && kill -0 "$(cat "$pid_file")" 2>/dev/null; then
    exit 0
fi

nohup streamlit run app.py --server.address 0.0.0.0 --server.port 8501 \
    > /tmp/risk-dashboard.log 2>&1 &
echo $! > "$pid_file"
