#include <stdio.h>
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
