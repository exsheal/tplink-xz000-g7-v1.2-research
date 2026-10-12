.syntax unified
.arch armv5te
.arm
.text
.global web_replay
.type web_replay, %function
web_replay:
    push {r4-r10, lr}
    sub sp, sp, #4096
    mov r0, #0
    bl dm_shmInit
    ldr r1, =stage_attach
    bl report
    bne done

    add r0, sp, #16
    mov r1, #0
    ldr r2, =4080
    bl memset
    add r4, sp, #16
    add r6, sp, #32
    add r7, sp, #448
    add r8, sp, #704
    add r9, sp, #2048
    add r9, r9, #96
    add r10, r9, #224

    mov r0, #3
    ldr r1, =object_http
    mov r2, r4
    ldr r3, =414
    str r6, [sp]
    bl rdp_getObjStruct
    ldr r1, =stage_http_read
    bl report
    bne done

    mov r0, #3
    ldr r1, =object_user
    mov r2, r4
    mov r3, #256
    str r7, [sp]
    bl rdp_getObjStruct
    ldr r1, =stage_user_read
    bl report
    bne done

    mov r0, #3
    ldr r1, =object_device
    mov r2, r4
    ldr r3, =1428
    str r8, [sp]
    bl rdp_getObjStruct
    ldr r1, =stage_device_read
    bl report
    bne done

    ldr r0, =2030
    str r0, [r10]
    add r0, r10, #8
    mov r1, r6
    ldr r2, =414
    bl memcpy
    mov r0, #14
    mov r1, r9
    mov r2, r10
    bl msg_connCliAndSend
    ldr r1, =stage_http_send
    bl report
    bne done

    mov r0, r8
    bl rsl_sendHttpdAuthChallenge
    ldr r1, =stage_challenge_send
    bl report
    bne done

    mov r0, r7
    bl rsl_sendHttpdUserCfg
    ldr r1, =stage_user_send
    bl report

done:
    mov r0, r5
    add sp, sp, #4096
    pop {r4-r10, pc}
.size web_replay, .-web_replay

report:
    push {r4, lr}
    mov r5, r0
    mov r2, r0
    ldr r0, =report_format
    bl printf
    mov r0, r5
    cmp r0, #0
    pop {r4, pc}
.ltorg

object_http: .asciz "DEV2_HTTP_CFG"
object_user: .asciz "DEV2_USER_CFG"
object_device: .asciz "DEV2_DEV_INFO"
report_format: .asciz "ONT_WEB_REPLAY_%s_RC=%d\n"
stage_attach: .asciz "ATTACH"
stage_http_read: .asciz "HTTP_READ"
stage_user_read: .asciz "USER_READ"
stage_device_read: .asciz "DEVICE_READ"
stage_http_send: .asciz "HTTP_SEND"
stage_challenge_send: .asciz "CHALLENGE_SEND"
stage_user_send: .asciz "USER_SEND"
.balign 4
