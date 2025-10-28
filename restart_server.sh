#!/bin/bash
# Quick script to restart the Streamo-Chromecast server

echo "🛑 Stopping existing server instances..."
pkill -f "server_chromecast.py"
pkill -f "video_streamer_chromecast.py"
sleep 1

echo "🧹 Checking for orphaned processes..."
if ps aux | grep -E "(server_chromecast|video_streamer)" | grep -v grep | grep -v restart_server; then
    echo "⚠️  Some processes still running. Force killing..."
    pkill -9 -f "server_chromecast.py"
    pkill -9 -f "video_streamer_chromecast.py"
    sleep 1
fi

echo "✅ Server stopped"
echo ""
echo "To start the server, run:"
echo "  python3 server_chromecast.py"
echo ""
echo "Or run with GUI:"
echo "  python3 video_streamer_chromecast.py"
