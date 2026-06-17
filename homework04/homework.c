#include <stdio.h>
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
