#include <stdio.h>
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
