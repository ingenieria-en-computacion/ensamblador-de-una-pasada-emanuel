start:
    mov eax, 5          ; mov
    mov ebx, eax        ; mov
    add eax, 10         ; add
    inc ebx             ; inc
    dec eax             ; dec
    xor ecx, ecx        ; xor
    shr eax, 1          ; shr
    push eax            ; push
    pop edx             ; pop
    cmp eax, ebx        ; cmp
    je etiqueta_eq      ; je
    jne etiqueta_neq    ; jne
    jbe etiqueta_jbe    ; jbe
    jl etiqueta_jl      ; jl
    jg etiqueta_jg      ; jg
    ja etiqueta_ja      ; ja
    jae etiqueta_jae    ; jae
    call funcion        ; call
    jmp etiqueta_jmp    ; jmp

funcion:
    div ecx             ; div (división entre ecx)
    xchg eax, ebx       ; xchg
    ret                 ; ret

etiqueta_eq:
    hlt                 ; hlt

etiqueta_neq:
    nop                 ; instrucción para no hacer nada (opcional)

etiqueta_jbe:
    nop                 ; opcional

etiqueta_jl:
    nop                 ; opcional

etiqueta_jg:
    nop                 ; opcional

etiqueta_ja:
    nop                 ; opcional

etiqueta_jae:
    nop                 ; opcional

etiqueta_jmp:
    nop                 ; opcional
