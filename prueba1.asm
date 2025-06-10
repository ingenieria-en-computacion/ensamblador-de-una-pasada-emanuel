_start:
    mov eax, 17
    call es_primo
    hlt

es_primo:
    cmp eax, 2
    je primo
    jl no_es_primo
    mov ebx, 2
    mov ecx, eax
    shr ecx, 1

bucle:
    cmp ebx, ecx
    jg primo
    push eax
    xor edx, edx
    div ebx
    pop eax
    cmp edx, 0
    je no_es_primo
    inc ebx
    jmp bucle

primo:
    mov eax, 1
    ret

no_es_primo:
    mov eax, 0
    ret