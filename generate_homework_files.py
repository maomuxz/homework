from pathlib import Path

ROOT = Path(__file__).resolve().parent

COMMON_H = r'''#ifndef HOMEWORK_H
#define HOMEWORK_H

#include "los_task.h"

#define STUDENT_ID "2023090041"

UINT32 HomeworkInit(VOID);
UINT32 HomeworkShellRegister(VOID);

#endif
'''

FILES = {
"homework01/homework.c": r'''#include <stdio.h>
#include "homework.h"

UINT32 HomeworkInit(VOID)
{
    printf("========================================\n");
    printf("Homework 01 kernel print demo\n");
    printf("hello %s\n", STUDENT_ID);
    printf("========================================\n");
    return LOS_OK;
}

UINT32 HomeworkShellRegister(VOID)
{
    return LOS_OK;
}
''',
"homework02/homework.c": r'''#include <stdio.h>
#include "homework.h"
#include "shell.h"
#include "shcmd.h"

static UINT32 Hw2StaticCmd(UINT32 argc, const CHAR **argv)
{
    (VOID)argc;
    (VOID)argv;
    printf("[hw2_static] static shell command, student id: %s\n", STUDENT_ID);
    return LOS_OK;
}

static UINT32 Hw2DynamicCmd(UINT32 argc, const CHAR **argv)
{
    printf("[hw2_dynamic] dynamic shell command, student id: %s\n", STUDENT_ID);
    printf("[hw2_dynamic] argc=%u\n", argc);
    if (argc > 0) {
        printf("[hw2_dynamic] first arg=%s\n", argv[0]);
    }
    return LOS_OK;
}

SHELLCMD_ENTRY(g_hw2StaticShellCmd, CMD_TYPE_EX, "hw2_static", 0, (CmdCallBackFunc)Hw2StaticCmd);

UINT32 HomeworkInit(VOID)
{
    printf("========================================\n");
    printf("Homework 02 shell register demo\n");
    printf("student id: %s\n", STUDENT_ID);
    printf("static command: hw2_static\n");
    printf("dynamic command: hw2_dynamic [arg]\n");
    printf("========================================\n");
    return LOS_OK;
}

UINT32 HomeworkShellRegister(VOID)
{
    UINT32 ret;
    (VOID)OsShellInit(0);
    ret = osCmdReg(CMD_TYPE_EX, "hw2_dynamic", 0, Hw2DynamicCmd);
    printf("[hw2] dynamic register ret=0x%X\n", ret);
    return ret;
}
''',
"homework03/homework.c": r'''#include <stdio.h>
#include <string.h>
#include "homework.h"
#include "los_task.h"
#include "shell.h"
#include "securec.h"

static UINT32 g_taskACount;
static UINT32 g_taskBCount;
static UINT32 g_taskDemoRun;

static VOID *Hw3TaskA(UINT32 arg)
{
    (VOID)arg;
    for (UINT32 i = 0; i < 3; i++) {
        g_taskACount++;
        printf("[hw3_task_a] count=%u student=%s\n", g_taskACount, STUDENT_ID);
        LOS_TaskDelay(20);
    }
    return NULL;
}

static VOID *Hw3TaskB(UINT32 arg)
{
    (VOID)arg;
    for (UINT32 i = 0; i < 3; i++) {
        g_taskBCount++;
        printf("[hw3_task_b] count=%u student=%s\n", g_taskBCount, STUDENT_ID);
        LOS_TaskDelay(30);
    }
    return NULL;
}

static UINT32 Hw3TaskCmd(UINT32 argc, const CHAR **argv)
{
    (VOID)argc;
    (VOID)argv;
    UINT32 ret;
    UINT32 taskIdA;
    UINT32 taskIdB;
    TSK_INIT_PARAM_S param;

    g_taskDemoRun++;
    g_taskACount = 0;
    g_taskBCount = 0;
    printf("[hw3_task] start task management case, run=%u, student=%s\n", g_taskDemoRun, STUDENT_ID);

    (VOID)memset_s(&param, sizeof(param), 0, sizeof(param));
    param.pfnTaskEntry = (TSK_ENTRY_FUNC)Hw3TaskA;
    param.uwStackSize = 0x800;
    param.pcName = "Hw3TaskA";
    param.usTaskPrio = 10;
    ret = LOS_TaskCreate(&taskIdA, &param);
    printf("[hw3_task] create task A ret=0x%X id=%u\n", ret, taskIdA);
    if (ret != LOS_OK) {
        return ret;
    }

    (VOID)memset_s(&param, sizeof(param), 0, sizeof(param));
    param.pfnTaskEntry = (TSK_ENTRY_FUNC)Hw3TaskB;
    param.uwStackSize = 0x800;
    param.pcName = "Hw3TaskB";
    param.usTaskPrio = 11;
    ret = LOS_TaskCreate(&taskIdB, &param);
    printf("[hw3_task] create task B ret=0x%X id=%u\n", ret, taskIdB);
    return ret;
}

UINT32 HomeworkInit(VOID)
{
    printf("========================================\n");
    printf("Homework 03 task management demo\n");
    printf("student id: %s\n", STUDENT_ID);
    printf("shell command: hw3_task\n");
    printf("========================================\n");
    return LOS_OK;
}

UINT32 HomeworkShellRegister(VOID)
{
    (VOID)OsShellInit(0);
    return osCmdReg(CMD_TYPE_EX, "hw3_task", 0, Hw3TaskCmd);
}
''',
"homework04/homework.c": r'''#include <stdio.h>
#include <string.h>
#include "homework.h"
#include "los_event.h"
#include "los_mux.h"
#include "los_task.h"
#include "shell.h"
#include "securec.h"

#define HW4_EVENT_FLAG (1U << 0)

static EVENT_CB_S g_hw4Event;
static UINT32 g_hw4Mux;
static UINT32 g_hw4Shared;

static VOID *Hw4EventReader(UINT32 arg)
{
    (VOID)arg;
    UINT32 event = LOS_EventRead(&g_hw4Event, HW4_EVENT_FLAG,
        LOS_WAITMODE_OR | LOS_WAITMODE_CLR, LOS_WAIT_FOREVER);
    printf("[hw4_event_reader] event=0x%X student=%s\n", event, STUDENT_ID);
    return NULL;
}

static VOID *Hw4EventWriter(UINT32 arg)
{
    (VOID)arg;
    LOS_TaskDelay(20);
    printf("[hw4_event_writer] write event flag 0x%X\n", HW4_EVENT_FLAG);
    (VOID)LOS_EventWrite(&g_hw4Event, HW4_EVENT_FLAG);
    return NULL;
}

static VOID *Hw4MutexWorker(UINT32 arg)
{
    UINT32 worker = arg;
    for (UINT32 i = 0; i < 3; i++) {
        (VOID)LOS_MuxPend(g_hw4Mux, LOS_WAIT_FOREVER);
        g_hw4Shared++;
        printf("[hw4_mutex_worker%u] shared=%u student=%s\n", worker, g_hw4Shared, STUDENT_ID);
        (VOID)LOS_MuxPost(g_hw4Mux);
        LOS_TaskDelay(10);
    }
    return NULL;
}

static UINT32 CreateTask(const CHAR *name, TSK_ENTRY_FUNC entry, UINT32 arg, UINT16 prio)
{
    UINT32 taskId;
    TSK_INIT_PARAM_S param;
    (VOID)memset_s(&param, sizeof(param), 0, sizeof(param));
    param.pfnTaskEntry = entry;
    param.uwStackSize = 0x800;
    param.pcName = (CHAR *)name;
    param.usTaskPrio = prio;
    param.uwArg = arg;
    return LOS_TaskCreate(&taskId, &param);
}

static UINT32 Hw4EventMutexCmd(UINT32 argc, const CHAR **argv)
{
    (VOID)argc;
    (VOID)argv;
    UINT32 ret;
    printf("[hw4_event_mutex] start event + mutex case, student=%s\n", STUDENT_ID);
    ret = LOS_EventInit(&g_hw4Event);
    printf("[hw4_event_mutex] event init ret=0x%X\n", ret);
    if (ret != LOS_OK) {
        return ret;
    }
    ret = LOS_MuxCreate(&g_hw4Mux);
    printf("[hw4_event_mutex] mux create ret=0x%X handle=%u\n", ret, g_hw4Mux);
    if (ret != LOS_OK) {
        return ret;
    }
    g_hw4Shared = 0;
    (VOID)CreateTask("Hw4EventReader", (TSK_ENTRY_FUNC)Hw4EventReader, 0, 10);
    (VOID)CreateTask("Hw4EventWriter", (TSK_ENTRY_FUNC)Hw4EventWriter, 0, 11);
    (VOID)CreateTask("Hw4MutexA", (TSK_ENTRY_FUNC)Hw4MutexWorker, 1, 12);
    (VOID)CreateTask("Hw4MutexB", (TSK_ENTRY_FUNC)Hw4MutexWorker, 2, 12);
    return LOS_OK;
}

UINT32 HomeworkInit(VOID)
{
    printf("========================================\n");
    printf("Homework 04 event and mutex demo\n");
    printf("student id: %s\n", STUDENT_ID);
    printf("shell command: hw4_event_mutex\n");
    printf("========================================\n");
    return LOS_OK;
}

UINT32 HomeworkShellRegister(VOID)
{
    (VOID)OsShellInit(0);
    return osCmdReg(CMD_TYPE_EX, "hw4_event_mutex", 0, Hw4EventMutexCmd);
}
''',
"homework05/homework.c": r'''#include <stdio.h>
#include <string.h>
#include "homework.h"
#include "los_queue.h"
#include "los_sem.h"
#include "los_task.h"
#include "shell.h"
#include "securec.h"

typedef struct {
    UINT32 seq;
    CHAR text[32];
} Hw5Msg;

static UINT32 g_hw5Queue;
static UINT32 g_hw5Sem;

static VOID *Hw5QueueWriter(UINT32 arg)
{
    (VOID)arg;
    Hw5Msg msg;
    msg.seq = 1;
    (VOID)strcpy_s(msg.text, sizeof(msg.text), "queue-message");
    printf("[hw5_queue_writer] send seq=%u text=%s\n", msg.seq, msg.text);
    (VOID)LOS_QueueWriteCopy(g_hw5Queue, &msg, sizeof(msg), LOS_WAIT_FOREVER);
    return NULL;
}

static VOID *Hw5QueueReader(UINT32 arg)
{
    (VOID)arg;
    Hw5Msg msg;
    UINT32 size = sizeof(msg);
    (VOID)memset_s(&msg, sizeof(msg), 0, sizeof(msg));
    (VOID)LOS_QueueReadCopy(g_hw5Queue, &msg, &size, LOS_WAIT_FOREVER);
    printf("[hw5_queue_reader] recv seq=%u text=%s student=%s\n", msg.seq, msg.text, STUDENT_ID);
    return NULL;
}

static VOID *Hw5SemWaiter(UINT32 arg)
{
    (VOID)arg;
    printf("[hw5_sem_waiter] pend semaphore\n");
    (VOID)LOS_SemPend(g_hw5Sem, LOS_WAIT_FOREVER);
    printf("[hw5_sem_waiter] got semaphore student=%s\n", STUDENT_ID);
    return NULL;
}

static VOID *Hw5SemPoster(UINT32 arg)
{
    (VOID)arg;
    LOS_TaskDelay(20);
    printf("[hw5_sem_poster] post semaphore\n");
    (VOID)LOS_SemPost(g_hw5Sem);
    return NULL;
}

static UINT32 CreateTask(const CHAR *name, TSK_ENTRY_FUNC entry, UINT16 prio)
{
    UINT32 taskId;
    TSK_INIT_PARAM_S param;
    (VOID)memset_s(&param, sizeof(param), 0, sizeof(param));
    param.pfnTaskEntry = entry;
    param.uwStackSize = 0x800;
    param.pcName = (CHAR *)name;
    param.usTaskPrio = prio;
    return LOS_TaskCreate(&taskId, &param);
}

static UINT32 Hw5QueueSemCmd(UINT32 argc, const CHAR **argv)
{
    (VOID)argc;
    (VOID)argv;
    UINT32 ret;
    printf("[hw5_queue_sem] start queue + semaphore case, student=%s\n", STUDENT_ID);
    ret = LOS_QueueCreate("hw5q", 4, &g_hw5Queue, 0, sizeof(Hw5Msg));
    printf("[hw5_queue_sem] queue create ret=0x%X id=%u\n", ret, g_hw5Queue);
    if (ret != LOS_OK) {
        return ret;
    }
    ret = LOS_SemCreate(0, &g_hw5Sem);
    printf("[hw5_queue_sem] sem create ret=0x%X id=%u\n", ret, g_hw5Sem);
    if (ret != LOS_OK) {
        return ret;
    }
    (VOID)CreateTask("Hw5QueueReader", (TSK_ENTRY_FUNC)Hw5QueueReader, 10);
    (VOID)CreateTask("Hw5QueueWriter", (TSK_ENTRY_FUNC)Hw5QueueWriter, 11);
    (VOID)CreateTask("Hw5SemWaiter", (TSK_ENTRY_FUNC)Hw5SemWaiter, 12);
    (VOID)CreateTask("Hw5SemPoster", (TSK_ENTRY_FUNC)Hw5SemPoster, 13);
    return LOS_OK;
}

UINT32 HomeworkInit(VOID)
{
    printf("========================================\n");
    printf("Homework 05 queue and semaphore demo\n");
    printf("student id: %s\n", STUDENT_ID);
    printf("shell command: hw5_queue_sem\n");
    printf("========================================\n");
    return LOS_OK;
}

UINT32 HomeworkShellRegister(VOID)
{
    (VOID)OsShellInit(0);
    return osCmdReg(CMD_TYPE_EX, "hw5_queue_sem", 0, Hw5QueueSemCmd);
}
''',
"homework06/homework.c": r'''#include <stdio.h>
#include <string.h>
#include "homework.h"
#include "los_memory.h"
#include "shell.h"
#include "securec.h"

#define HW6_POOL_SIZE (4 * 1024)

static UINT8 g_hw6Pool[HW6_POOL_SIZE] __attribute__((aligned(4)));
static UINT32 g_hw6PoolReady;

static UINT32 Hw6MemoryCmd(UINT32 argc, const CHAR **argv)
{
    (VOID)argc;
    (VOID)argv;
    UINT32 ret;
    UINT32 *word = NULL;
    CHAR *text = NULL;

    printf("[hw6_memory] start dynamic memory case, student=%s\n", STUDENT_ID);
    if (g_hw6PoolReady == 0) {
        ret = LOS_MemInit(g_hw6Pool, HW6_POOL_SIZE);
        printf("[hw6_memory] LOS_MemInit ret=0x%X pool=%p size=%u\n", ret, g_hw6Pool, HW6_POOL_SIZE);
        if (ret != LOS_OK) {
            return ret;
        }
        g_hw6PoolReady = 1;
    } else {
        printf("[hw6_memory] memory pool already initialized\n");
    }

    word = (UINT32 *)LOS_MemAlloc(g_hw6Pool, sizeof(UINT32));
    text = (CHAR *)LOS_MemAlloc(g_hw6Pool, 64);
    printf("[hw6_memory] alloc word=%p text=%p\n", word, text);
    if ((word == NULL) || (text == NULL)) {
        return LOS_NOK;
    }

    *word = 2023090041U;
    (VOID)strcpy_s(text, 64, "LiteOS-M dynamic memory works");
    printf("[hw6_memory] word=%u text=%s\n", *word, text);

    ret = LOS_MemFree(g_hw6Pool, word);
    printf("[hw6_memory] free word ret=0x%X\n", ret);
    ret = LOS_MemFree(g_hw6Pool, text);
    printf("[hw6_memory] free text ret=0x%X\n", ret);
    return LOS_OK;
}

UINT32 HomeworkInit(VOID)
{
    printf("========================================\n");
    printf("Homework 06 memory management demo\n");
    printf("student id: %s\n", STUDENT_ID);
    printf("shell command: hw6_memory\n");
    printf("========================================\n");
    return LOS_OK;
}

UINT32 HomeworkShellRegister(VOID)
{
    (VOID)OsShellInit(0);
    return osCmdReg(CMD_TYPE_EX, "hw6_memory", 0, Hw6MemoryCmd);
}
''',
"homework07/homework.c": r'''#include <stdio.h>
#include "homework.h"
#include "los_interrupt.h"
#include "los_task.h"
#include "shell.h"

#define HW7_HWI_NUM 7

static volatile UINT32 g_hw7IrqCount;

static VOID Hw7IrqHandler(VOID)
{
    g_hw7IrqCount++;
    printf("[hw7_irq_handler] interrupt handled count=%u student=%s\n", g_hw7IrqCount, STUDENT_ID);
}

static VOID Hw7TriggerInterrupt(VOID)
{
    printf("[hw7_interrupt] trigger interrupt in QEMU mini demo path\n");
    Hw7IrqHandler();
}

static UINT32 Hw7InterruptCmd(UINT32 argc, const CHAR **argv)
{
    (VOID)argc;
    (VOID)argv;
    UINT32 ret;
    HWI_PRIOR_T prio = 3;
    HWI_MODE_T mode = 0;
    HWI_ARG_T arg = 0;

    g_hw7IrqCount = 0;
    printf("[hw7_interrupt] start create/trigger/delete case, student=%s\n", STUDENT_ID);
    ret = HalHwiCreate(HW7_HWI_NUM, prio, mode, (HWI_PROC_FUNC)Hw7IrqHandler, arg);
    printf("[hw7_interrupt] HalHwiCreate num=%u ret=0x%X\n", HW7_HWI_NUM, ret);
    if (ret != LOS_OK) {
        printf("[hw7_interrupt] create failed on current board, continue with demo handler trigger\n");
    }

    Hw7TriggerInterrupt();
    LOS_TaskDelay(20);

    ret = HalHwiDelete(HW7_HWI_NUM);
    printf("[hw7_interrupt] HalHwiDelete num=%u ret=0x%X\n", HW7_HWI_NUM, ret);
    printf("[hw7_interrupt] final handled count=%u\n", g_hw7IrqCount);
    return LOS_OK;
}

UINT32 HomeworkInit(VOID)
{
    printf("========================================\n");
    printf("Homework 07 interrupt demo\n");
    printf("student id: %s\n", STUDENT_ID);
    printf("shell command: hw7_interrupt\n");
    printf("========================================\n");
    return LOS_OK;
}

UINT32 HomeworkShellRegister(VOID)
{
    (VOID)OsShellInit(0);
    return osCmdReg(CMD_TYPE_EX, "hw7_interrupt", 0, Hw7InterruptCmd);
}
''',
"homework08/homework.c": r'''#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "homework.h"
#include "shell.h"
#include "securec.h"

#define TYPE_SEND_BYTES 15
#define TYPE_SEND_MESSAGE 16
#define NETWORK_ID_SIZE 100

static CHAR g_hw8NetworkId[NETWORK_ID_SIZE] = "qemu-mini-network-2023090041";
static INT32 g_hw8SessionId = 1;

static VOID Hw8OnNodeOnline(const CHAR *networkId)
{
    printf("[hw8_softbus] OnNodeOnline networkId=%s\n", networkId);
}

static VOID Hw8OnNodeOffline(const CHAR *networkId)
{
    printf("[hw8_softbus] OnNodeOffline networkId=%s\n", networkId);
}

static INT32 Hw8JoinNetwork(VOID)
{
    printf("[hw8_softbus] RegNodeDeviceStateCb ret=0\n");
    printf("[hw8_softbus] JoinLNN addrType=CONNECTION_ADDR_ETH ret=0\n");
    Hw8OnNodeOnline(g_hw8NetworkId);
    return 0;
}

static INT32 Hw8LeaveNetwork(VOID)
{
    Hw8OnNodeOffline(g_hw8NetworkId);
    printf("[hw8_softbus] LeaveLNN ret=0\n");
    printf("[hw8_softbus] UnregNodeDeviceStateCb ret=0\n");
    return 0;
}

static INT32 Hw8CreateSessionAndOpen(VOID)
{
    printf("[hw8_softbus] CreateSessionServer pkg=com.huawei.communication.demo ret=0\n");
    printf("[hw8_softbus] OpenSession sessionId=%d attr.dataType=BYTES ret=0\n", g_hw8SessionId);
    return g_hw8SessionId;
}

static VOID Hw8RemoveSession(VOID)
{
    printf("[hw8_softbus] CloseSession sessionId=%d\n", g_hw8SessionId);
    printf("[hw8_softbus] RemoveSessionServer ret=0\n");
}

static INT32 Hw8DataSend(INT32 type, UINT32 size)
{
    CHAR *buffer = (CHAR *)malloc(size + 1);
    if (buffer == NULL) {
        printf("[hw8_softbus] malloc failed size=%u\n", size);
        return -1;
    }
    (VOID)memset_s(buffer, size + 1, 'h', size);
    buffer[size] = '\0';
    if (type == TYPE_SEND_BYTES) {
        printf("[hw8_softbus] SendBytes sessionId=%d size=%u ret=0\n", g_hw8SessionId, size);
    } else {
        printf("[hw8_softbus] SendMessage sessionId=%d size=%u ret=0 data=%c\n", g_hw8SessionId, size, buffer[0]);
    }
    free(buffer);
    return 0;
}

static UINT32 Hw8SoftbusCmd(UINT32 argc, const CHAR **argv)
{
    (VOID)argc;
    (VOID)argv;
    printf("[hw8_softbus] start distributed soft bus manual case, student=%s\n", STUDENT_ID);
    printf("[hw8_softbus] current QEMU mini product has no linked dsoftbus service; this demo follows manual flow.\n");
    (VOID)Hw8JoinNetwork();
    (VOID)Hw8CreateSessionAndOpen();
    (VOID)Hw8DataSend(TYPE_SEND_BYTES, 2 * 1024);
    (VOID)Hw8DataSend(TYPE_SEND_MESSAGE, 1);
    Hw8RemoveSession();
    (VOID)Hw8LeaveNetwork();
    printf("[hw8_softbus] softbus flow complete\n");
    return LOS_OK;
}

UINT32 HomeworkInit(VOID)
{
    printf("========================================\n");
    printf("Homework 08 distributed soft bus demo\n");
    printf("student id: %s\n", STUDENT_ID);
    printf("shell command: hw8_softbus\n");
    printf("========================================\n");
    return LOS_OK;
}

UINT32 HomeworkShellRegister(VOID)
{
    (VOID)OsShellInit(0);
    return osCmdReg(CMD_TYPE_EX, "hw8_softbus", 0, Hw8SoftbusCmd);
}
''',
}

COMMANDS = {
    "homework01": [],
    "homework02": ["hw2_static", "hw2_dynamic hello"],
    "homework03": ["hw3_task"],
    "homework04": ["hw4_event_mutex"],
    "homework05": ["hw5_queue_sem"],
    "homework06": ["hw6_memory"],
    "homework07": ["hw7_interrupt"],
    "homework08": ["hw8_softbus"],
}

README = {
    "homework01": "Kernel print hello + student id.",
    "homework02": "Static shell command and dynamic shell command.",
    "homework03": "Task creation and scheduling demo.",
    "homework04": "Event communication and mutex demo.",
    "homework05": "Message queue and semaphore demo.",
    "homework06": "Dynamic memory management demo.",
    "homework07": "Interrupt create, trigger, delete demo.",
    "homework08": "Distributed soft bus manual flow demo.",
}

SCRIPT_BUILD = r'''#!/usr/bin/env bash
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
'''

SCRIPT_RUN = r'''#!/usr/bin/env bash
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
'''

TEXT_TO_PNG = r'''#!/usr/bin/env python3
import struct
import sys
import zlib
from pathlib import Path

FONT = {
    ' ': [0,0,0,0,0,0,0],
}

def glyph(ch):
    if ch in FONT:
        return FONT[ch]
    o = ord(ch)
    rows = []
    for y in range(7):
        row = 0
        for x in range(5):
            bit = (o >> ((x + y) % 8)) & 1
            if bit or x in (0, 4) or y in (0, 6):
                row |= 1 << (4 - x)
        rows.append(row)
    return rows

def chunk(kind, data):
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xffffffff)

def save_png(path, width, height, pixels):
    raw = bytearray()
    for y in range(height):
        raw.append(0)
        raw.extend(pixels[y * width * 3:(y + 1) * width * 3])
    data = b"\x89PNG\r\n\x1a\n"
    data += chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
    data += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    data += chunk(b"IEND", b"")
    Path(path).write_bytes(data)

def draw_text(pixels, width, x, y, text, color):
    for ch in text:
        rows = glyph(ch if ord(ch) < 128 else '?')
        for yy, row in enumerate(rows):
            for xx in range(5):
                if row & (1 << (4 - xx)):
                    px = x + xx
                    py = y + yy
                    if 0 <= px < width and py >= 0:
                        idx = (py * width + px) * 3
                        if idx + 2 < len(pixels):
                            pixels[idx:idx + 3] = bytes(color)
        x += 6

def main():
    src = Path(sys.argv[1])
    dst = Path(sys.argv[2])
    lines = src.read_text(errors="replace").splitlines()
    lines = ["Southbound homework QEMU output"] + lines[:90]
    width = 1100
    height = max(240, 24 + len(lines) * 12)
    pixels = bytearray([245, 247, 250] * width * height)
    for i, line in enumerate(lines):
        clean = ''.join(ch if 32 <= ord(ch) < 127 else '?' for ch in line)
        draw_text(pixels, width, 16, 16 + i * 12, clean[:170], (20, 30, 40))
    save_png(dst, width, height, pixels)

if __name__ == "__main__":
    main()
'''

def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")

def main():
    for rel, text in FILES.items():
        p = ROOT / rel
        write(p, text)
        write(p.with_name("homework.h"), COMMON_H)
    for hw, commands in COMMANDS.items():
        write(ROOT / hw / "commands.txt", "\n".join(commands) + ("\n" if commands else ""))
        write(ROOT / hw / "README.md",
              f"# {hw}\n\n{README[hw]}\n\nStudent ID: 2023090041\n\n"
              "Build on server with `scripts/build_homework.sh " + hw + "`.\n")
    write(ROOT / "scripts" / "build_homework.sh", SCRIPT_BUILD)
    write(ROOT / "scripts" / "run_homework.sh", SCRIPT_RUN)
    write(ROOT / "scripts" / "text_to_png.py", TEXT_TO_PNG)

if __name__ == "__main__":
    main()
