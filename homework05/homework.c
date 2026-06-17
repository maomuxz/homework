#include <stdio.h>
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
