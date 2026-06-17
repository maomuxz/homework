#!/usr/bin/env bash
set -euo pipefail

if [ $# -ne 1 ]; then
    echo "usage: $0 homework01|...|homework08" >&2
    exit 2
fi

HW="$1"
REPO="/home/ubuntu/southbound_development"
IMAGE="$REPO/$HW/OHOS_Image"
COMMANDS="$REPO/$HW/commands.txt"
LOG="$REPO/$HW/qemu.log"
PNG="$REPO/$HW/screenshot.png"
EXP="/tmp/${HW}_qemu.exp"

if [ ! -f "$IMAGE" ]; then
    echo "missing image: $IMAGE" >&2
    exit 2
fi

cat > "$EXP" <<EOF_EXP
#!/usr/bin/expect -f
set timeout 20
spawn qemu-system-arm -M mps2-an386 -kernel "$IMAGE" -nographic -monitor none
expect {
    "OHOS #" {}
    timeout {}
}
EOF_EXP

if [ -f "$COMMANDS" ]; then
    while IFS= read -r cmd; do
        [ -z "$cmd" ] && continue
        printf 'sleep 1\nsend "%s\\r"\nsleep 3\n' "$cmd" >> "$EXP"
    done < "$COMMANDS"
else
    printf 'sleep 4\n' >> "$EXP"
fi

cat >> "$EXP" <<'EOF_EXP_END'
send "\001x"
expect eof
EOF_EXP_END

chmod +x "$EXP"
set +e
timeout 35s expect "$EXP" > "$LOG" 2>&1
STATUS=$?
set -e
python3 "$REPO/scripts/text_to_png.py" "$LOG" "$PNG"
echo "qemu status=$STATUS log=$LOG screenshot=$PNG"
exit 0
