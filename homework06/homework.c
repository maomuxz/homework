#include <stdio.h>
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
