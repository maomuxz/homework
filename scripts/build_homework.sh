#!/usr/bin/env bash
set -euo pipefail

if [ $# -ne 1 ]; then
    echo "usage: $0 homework01|...|homework08" >&2
    exit 2
fi

HW="$1"
REPO="/home/ubuntu/southbound_development"
OHOS="/home/ubuntu/openharmony_full"
TEST_DIR="$OHOS/device/qemu/arm_mps2_an386/test"
OUT_IMAGE="$OHOS/out/arm_mps2_an386/qemu_mini_system_demo/bin/OHOS_Image"

if [ ! -f "$REPO/$HW/homework.c" ]; then
    echo "missing $REPO/$HW/homework.c" >&2
    exit 2
fi

cp "$REPO/$HW/homework.c" "$TEST_DIR/homework.c"
cp "$REPO/$HW/homework.h" "$TEST_DIR/homework.h"

cat > "$TEST_DIR/test_demo.c" <<'EOF_TEST_DEMO'
#include "los_task.h"
#include "los_debug.h"
#include "homework.h"

static VOID *ShellRegTaskEntry(UINT32 arg)
{
    (VOID)arg;
    LOS_TaskDelay(50);
    (VOID)HomeworkShellRegister();
    return NULL;
}

unsigned int LosAppInit(VOID)
{
    UINT32 ret;
    UINT32 taskId;
    TSK_INIT_PARAM_S taskParam = { 0 };

    ret = HomeworkInit();
    if (ret != LOS_OK) {
        return ret;
    }

    taskParam.pfnTaskEntry = (TSK_ENTRY_FUNC)ShellRegTaskEntry;
    taskParam.uwStackSize = 0x1000;
    taskParam.pcName = "ShellRegTask";
    taskParam.usTaskPrio = 5;
    (VOID)LOS_TaskCreate(&taskId, &taskParam);
    return LOS_OK;
}
EOF_TEST_DEMO

cat > "$TEST_DIR/BUILD.gn" <<'EOF_BUILD'
static_library("demo") {
  sources = [
    "homework.c",
    "test_demo.c",
  ]
  include_dirs = [
    "//kernel/liteos_m/kernel/include",
    "//kernel/liteos_m/kernel/arch/include",
    "//kernel/liteos_m/utils",
    "//kernel/liteos_m/kal/cmsis",
    "//kernel/liteos_m/components/shell/include",
    "//third_party/bounds_checking_function/include",
    "//utils/native/lite/include",
  ]
}
EOF_BUILD

mkdir -p "$REPO/$HW"
sudo docker exec -w /root/openharmony ohos_builder python3 build.py | tee "$REPO/$HW/build.log"
cp "$OUT_IMAGE" "$REPO/$HW/OHOS_Image"
echo "built $HW -> $REPO/$HW/OHOS_Image"
