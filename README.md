# Proyecto Final: Estructura y Programación de Computadoras
## 🛠️ Ensamblador IA-32 en Python

Este es un ensamblador simplificado para la arquitectura IA-32 (x86 de 32 bits), desarrollado en Python. Convierte un archivo `.asm` con instrucciones de ensamblador a un archivo de código máquina (en hexadecimal) y genera también una tabla de símbolos y una tabla de referencias pendientes.

## 🚀 Características

- Soporta instrucciones como `mov`, `add`, `div`, `call`, `jmp`, `cmp`, `je`, `jne`, `ret`, `hlt`, `xor`, `push`, `pop`, `xchg`, `inc`, `dec`, `shr`, entre otras.
- Manejo de etiquetas y saltos relativos.
- Identificación automática de registros e inmediatos.
- Generación de:
  - Código máquina (`codigo.txt`)
  - Tabla de símbolos (`tabla_simbolos.txt`)
  - Referencias pendientes (`referencias_pendientes.txt`)

## 📁 Estructura del proyecto
ensamblador.py # Código fuente principal del ensamblador
prueba1.asm # Archivo de entrada con código ensamblador (Código prueba)
prueba2.asm # Archivo de entrada con código ensamblador (Código prueba)
README.md # Este archivo


## 🧠 ¿Cómo funciona?

1. **Lectura del archivo `.asm`**.
2. **Procesamiento línea por línea**:
   - Reconoce etiquetas (`label:`) y las guarda con su dirección.
   - Identifica instrucciones, operandos y modos de direccionamiento.
   - Codifica cada instrucción a hexadecimal según el formato IA-32.
3. **Manejo de referencias pendientes**:
   - Guarda las etiquetas utilizadas antes de ser definidas.
   - Se resuelven al final cuando se conocen todas las direcciones.

## 🛠️ Instrucciones soportadas
    mov, add, div, inc, dec, shr, xor, push, pop, xchg,
    call, jmp, ret, hlt, cmp, je, jne, jbe, jl, jg, ja, jae, nop


## ▶️ ¿Cómo ejecutar?

1. Asegúrate de tener Python instalado (versión 3.6 o superior).
2. Guarda tu código ensamblador en un archivo `.asm`. Ejemplo: `ejemplo.asm`.
3. Módifica los argumentos de la línea 485 por el nombre de tu respectivo programa
3. Ejecuta el ensamblador desde terminal:

        ```bash
        python ensamblador.py

4. Revisa los archivos generados:
    codigo.txt
    tabla_simbolos.txt
    referencias_pendientes.txt


📦 Requisitos

    Python 3

    No se requieren librerías externas.

📝 Ejemplo de entrada (ejemplo.asm)

    _start:
    mov eax, 10
    call fib
    hlt
    fib:
        cmp eax, 1
        jbe .caso_base
        push ebx
        mov ebx, eax
        dec eax
        call fib
        xchg eax, ebx
        dec eax
        call fib
        add eax, ebx
        pop ebx
        ret
    .caso_base:
        mov eax, 1
        ret



🧪 Archivos generados

    codigo.txt: contiene el código máquina en formato 0xADDR: XX XX XX...

    tabla_simbolos.txt: etiquetas definidas con sus direcciones.

    referencias_pendientes.txt: etiquetas referenciadas antes de ser definidas, con dirección donde fueron referenciadas.

🧑‍💻 Autor

    Escobar Rodríguez Emanuel
    Proyecto académico / educativo

