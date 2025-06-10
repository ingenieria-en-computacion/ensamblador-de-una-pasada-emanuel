"""
Ensamblador básico de una pasada 
Autor: Escobar Rodríguez Emanuel
Fecha de creación: 07 de junio de 2025
Revisiones:
Fecha de última modificación: 09 de junio de 2025
"""

import re

class EnsambladorIA32:
    def __init__(self):
        self.tabla_simbolos = {}           # {label: direccion} Diccionario que guarda etiquetas y su dirección asignada.
        self.referencias_pendientes = {}   # {label: [lista_direcciones_de_referencia]} Etiquetas usadas antes de ser definidas, con las posiciones donde se referencian.
        self.codigo_hex = []                # lista de (direccion, [bytes]) Lista con tuplas (dirección, bytes) que representan el código máquina generado.
        self.contador_posicion = 0x1000    # Location counter, inicia en 0x1000 Apunta a la dirección actual donde se insertará el siguiente código (inicia en 0x1000).

        # Diccionario simple de registros a código (solo para mov y add simplificados)
        self.registros = {
            'eax': 0x00,
            'ecx': 0x01,
            'edx': 0x02,
            'ebx': 0x03,
            'esp': 0x04,
            'ebp': 0x05,
            'esi': 0x06,
            'edi': 0x07
        }

    def ensamblar(self, archivo_entrada):
        with open(archivo_entrada, 'r') as f:
            lineas = f.readlines()

        for linea in lineas:
            self.procesar_linea(linea)

        #Impresión en pantalla para probar funcionamiento
        # print("=== Tabla de símbolos ===")
        # for label, direccion in self.tabla_simbolos.items():
        #     print(f"{label}: 0x{direccion:04X}")

        # print("\n=== Referencias pendientes ===")
        # for label, direcciones in self.referencias_pendientes.items():
        #     print(f"{label}: {[f'0x{d:04X}' for d in direcciones]}")

        # print("\n=== Código máquina generado ===")
        # for direccion, bytes_ in self.codigo_hex:
        #     bytes_hex = ' '.join(f"{b:02X}" for b in bytes_)
        #     print(f"{hex(direccion)}: {bytes_hex}")


    def procesar_linea(self, linea):
        # Limpiar línea: quitar comentarios y espacios extras
        linea = linea.split(';')[0].strip()
        if not linea:
            return

        # Verificar si es etiqueta (termina con :)
        if linea.endswith(':'):
            etiqueta = linea[:-1].strip()
            self.procesar_etiqueta(etiqueta)
            return

        # Si es instrucción
        self.procesar_instruccion(linea)

        #print(f"Procesando línea: {linea}") #Verificar el procesado de linea imprimiendolo en pantalla


    def procesar_etiqueta(self, etiqueta):
        if etiqueta in self.tabla_simbolos:
            raise ValueError(f"Etiqueta {etiqueta} redefinida")
        self.tabla_simbolos[etiqueta] = self.contador_posicion

        # Si esta etiqueta estaba en referencias pendientes, no se elimina, porque
        # las referencias pendientes son para parchear después.
        # La resolución se hará después.

    def procesar_instruccion(self, instruccion):
        # Separa mnemónico y operandos
        partes = instruccion.split(None, 1)
        mnem = partes[0].lower()
        operandos = partes[1] if len(partes) > 1 else ''

        # Dispatch básico para instrucciones soportadas:
        if mnem == 'mov':
            self.codificar_mov(operandos)
        elif mnem == 'add':
            self.codificar_add(operandos)
        elif mnem == 'div':
            self.codificar_div(operandos)
        elif mnem == 'inc':
            self.codificar_inc(operandos)
        elif mnem == 'call':
            self.codificar_call(operandos)
        elif mnem == 'jmp':
            self.codificar_jmp(operandos)
        elif mnem == 'ret':
            self.codificar_ret()
        elif mnem == 'hlt':
            self.codificar_hlt()
        elif mnem == 'cmp':
            self.codificar_cmp(operandos)
        elif mnem == 'jbe':
            self.codificar_jcc(operandos, opcode=0x76)  # jbe/ jna
        elif mnem == 'je':
            self.codificar_jcc(operandos, opcode=0x74)  # je
        elif mnem == 'jne':
            self.codificar_jcc(operandos, opcode=0x75)  # jne
        elif mnem == 'jl':
            self.codificar_jcc(operandos, opcode=0x7C)  # jl 
        elif mnem == 'jg':
            self.codificar_jcc(operandos, opcode=0x7F)  # jg
        elif mnem == 'dec':
            self.codificar_dec(operandos)
        elif mnem == 'shr':
            self.codificar_shr(operandos)
        elif mnem == 'xor':
            self.codificar_xor(operandos)
        elif mnem == 'push':
            self.codificar_push(operandos)
        elif mnem == 'pop':
            self.codificar_pop(operandos)
        elif mnem == 'xchg':
            self.codificar_xchg(operandos)
        elif mnem == 'ja':
            self.codificar_jcc(operandos, opcode=0x77)  # ja/jnbe
        elif mnem == 'jae':
            self.codificar_jcc(operandos, opcode=0x73)  # jae/jnb
        elif mnem == 'nop':
            self.codificar_nop()
        else:
            raise NotImplementedError(f"Instrucción {mnem} no soportada aún")
        
    def es_registro(self, operando):
        registros = ['eax', 'ebx', 'ecx', 'edx', 'esi', 'edi', 'esp', 'ebp']
        return operando.lower() in registros

    def codificar_mov(self, operandos):
        # soporta mov reg, imm ; mov reg, reg ; mov reg, [label]
        op1, op2 = [x.strip() for x in operandos.split(',', 1)]

        if op1 in self.registros:
            if op2 in self.registros:
                # mov reg, reg => 0x8B /r (mov r32, r/m32)
                # ModR/M byte: 11 reg dest reg src
                opcode = 0x8B
                modrm = 0xC0 | (self.registros[op1] << 3) | self.registros[op2]
                bytes_cod = [opcode, modrm]
                self.agregar_codigo(bytes_cod)
            elif op2.startswith('0x') or op2.isdigit():
                # mov reg, imm32 => B8+reg (mov r32, imm32)
                imm = int(op2, 0)
                opcode = 0xB8 + self.registros[op1]
                imm_bytes = imm.to_bytes(4, 'little')
                bytes_cod = [opcode] + list(imm_bytes)
                self.agregar_codigo(bytes_cod)
            else:
                # mov reg, [label]  -> mov r32, m32
                # opcode 0x8B + ModRM mod=00 disp32 = addr etiqueta
                # ModRM: mod=00 reg=dest reg r/m=100 (SIB) o r/m=101 (disp32)
                # Aquí simplifico usamos mod=00 r/m=101 + disp32 (32bit displacement)
                opcode = 0x8B
                modrm = 0x05 | (self.registros[op1] << 3)  # mod=00, r/m=101 (disp32)
                bytes_cod = [opcode, modrm]

                # La dirección la dejo pendiente si no definida
                direccion = self.obtener_direccion_label(op2)
                disp_bytes = direccion.to_bytes(4, 'little')
                bytes_cod += list(disp_bytes)
                self.agregar_codigo(bytes_cod)
        else:
            raise NotImplementedError(f"mov con primer operando {op1} no soportado")

    def codificar_add(self, operandos):
        # soporta add reg, imm ; add reg, reg
        op1, op2 = [x.strip() for x in operandos.split(',', 1)]

        if op1 in self.registros:
            if op2 in self.registros:
                # add reg, reg -> 0x01 /r (add r/m32, r32)
                opcode = 0x01
                modrm = 0xC0 | (self.registros[op2] <<3) | self.registros[op1]
                bytes_cod = [opcode, modrm]
                self.agregar_codigo(bytes_cod)
            elif op2.startswith('0x') or op2.isdigit():
                # add reg, imm8/imm32 -> 83 /0 ib (si cabe en 8 bits) o 81 /0 id
                imm = int(op2, 0)
                if -128 <= imm <= 127:
                    opcode = 0x83
                    modrm = 0xC0 | (0 << 3) | self.registros[op1]  # /0 = add
                    imm_bytes = imm.to_bytes(1, 'little', signed=True)
                    bytes_cod = [opcode, modrm] + list(imm_bytes)
                else:
                    opcode = 0x81
                    modrm = 0xC0 | (0 << 3) | self.registros[op1]
                    imm_bytes = imm.to_bytes(4, 'little', signed=True)
                    bytes_cod = [opcode, modrm] + list(imm_bytes)
                self.agregar_codigo(bytes_cod)
            else:
                raise NotImplementedError(f"add con segundo operando {op2} no soportado")
        else:
            raise NotImplementedError(f"add con primer operando {op1} no soportado")
        
    def codificar_div(self, operandos):
        op = operandos.strip()

        if op in self.registros:
            # div reg -> F7 /6 modrm (mod=11, reg=6, rm=reg_code)
            opcode = 0xF7
            modrm = 0xC0 | (6 << 3) | self.registros[op]  # mod=11, reg=6, rm=reg_code
            self.agregar_codigo([opcode, modrm])
        else:
            # div [label] -> F7 /6 modrm disp32
            # Se usa mod=00 rm=101 para disp32
            opcode = 0xF7
            modrm = 0x05 | (6 << 3)  # mod=00, reg=6(div), rm=101 (disp32)
            bytes_cod = [opcode, modrm]

            direccion = self.obtener_direccion_label(op)
            disp_bytes = direccion.to_bytes(4, 'little')
            bytes_cod += list(disp_bytes)
            self.agregar_codigo(bytes_cod)

    def codificar_inc(self, operandos):
        op = operandos.strip()

        if op in self.registros:
            # inc reg32 = 0x40 + reg_code
            opcode = 0x40 + self.registros[op]
            self.agregar_codigo([opcode])
        else:
            # inc [label] = FF /0 modrm disp32
            opcode = 0xFF
            modrm = 0x05 | (0 << 3)  # mod=00, reg=000 (inc), rm=101 (disp32)
            bytes_cod = [opcode, modrm]

            direccion = self.obtener_direccion_label(op)
            disp_bytes = direccion.to_bytes(4, 'little')
            bytes_cod += list(disp_bytes)

            self.agregar_codigo(bytes_cod)


    def codificar_call(self, operandos):
        label = operandos.strip()
        opcode = 0xE8
        # La llamada es relativa a siguiente instrucción
        # Se reservan 4 bytes para el desplazamiento y parchea luego
        bytes_cod = [opcode, 0,0,0,0]
        self.agregar_codigo(bytes_cod)

        # Agregar referencia pendiente para parchear desplazamiento luego
        dir_referencia = self.contador_posicion - 4  # donde empieza el desplazamiento (inmediatamente después de opcode)
        self.agregar_referencia_pendiente(label, dir_referencia)

    def codificar_jmp(self, operandos):
        label = operandos.strip()
        opcode = 0xE9
        # Igual que call, desplazamiento relativo 4 bytes
        bytes_cod = [opcode, 0,0,0,0]
        self.agregar_codigo(bytes_cod)
        dir_referencia = self.contador_posicion - 4
        self.agregar_referencia_pendiente(label, dir_referencia)

    def codificar_ret(self):
        # opcode 0xC3
        self.agregar_codigo([0xC3])

    def codificar_hlt(self):
        # opcode 0xF4
        self.agregar_codigo([0xF4])

    def codificar_cmp(self, operandos):
        op1, op2 = [x.strip() for x in operandos.split(',', 1)]
        if op1 in self.registros:
            if op2.startswith('0x') or op2.isdigit():
                imm = int(op2,0)
                opcode = 0x81
                modrm = 0xF8 | self.registros[op1]  # /7 cmp r/m32, imm32
                imm_bytes = imm.to_bytes(4, 'little', signed=True)
                self.agregar_codigo([opcode, modrm] + list(imm_bytes))
            elif op2 in self.registros:
                # cmp reg, reg -> 39 /r
                opcode = 0x39
                modrm = 0xC0 | (self.registros[op2]<<3) | self.registros[op1]
                self.agregar_codigo([opcode, modrm])
            else:
                raise NotImplementedError("cmp con segundo operando no soportado")
        else:
            raise NotImplementedError("cmp con primer operando no soportado")

    def codificar_jcc(self, operandos, opcode):
        # salto condicional corto (8-bit relative)
        label = operandos.strip()
        # se reservan 2 bytes: opcode + disp8
        bytes_cod = [opcode, 0]
        self.agregar_codigo(bytes_cod)
        dir_referencia = self.contador_posicion -1  # el byte de desplazamiento es el siguiente al opcode
        self.agregar_referencia_pendiente(label, dir_referencia)

    def codificar_dec(self, operandos):
        op = operandos.strip()
        if op in self.registros:
            opcode = 0x48 + self.registros[op]  # dec reg32 = 48+reg
            self.agregar_codigo([opcode])
        else:
            raise NotImplementedError("dec solo para registros soportado")
        
    def codificar_shr(self, operandos):
        op1, op2 = [x.strip() for x in operandos.split(',', 1)]
        
        # Parseamos inmediato (puede ser decimal o hex)
        imm = int(op2, 0) & 0xFF  # solo un byte, el CPU usará 5 bits
        
        # Determinar si op1 es registro o memoria (suponiendo que self.es_registro y self.es_memoria existen)
        if self.es_registro(op1):
            reg_code = self.registros[op1]
            # Mod = 11 (registro directo)
            modrm = 0xC0 | (5 << 3) | reg_code  # 0xC0 = mod=11, reg=5 (shr), r/m=reg_code
            bytes_cod = [0xC1, modrm, imm]
            self.agregar_codigo(bytes_cod)
            
        elif self.es_memoria(op1):
            # Aquí tiene que obtener mod, rm, sib y desplazamiento según la dirección
            mod, rm, sib, disp_bytes = self.parsear_direccion(op1)
            modrm = (mod << 6) | (5 << 3) | rm
            bytes_cod = [0xC1, modrm]
            if sib is not None:
                bytes_cod.append(sib)
            bytes_cod.extend(disp_bytes)
            bytes_cod.append(imm)
            self.agregar_codigo(bytes_cod)
        else:
            raise ValueError("Operando no reconocido para shr")
        
    def codificar_xor(self, operandos):
        op1, op2 = [x.strip() for x in operandos.split(',', 1)]

        if op1 in self.registros:
            if op2 in self.registros:
                # xor reg, reg -> 0x31 /r (xor r/m32, r32)
                opcode = 0x31
                modrm = 0xC0 | (self.registros[op2] << 3) | self.registros[op1]
                self.agregar_codigo([opcode, modrm])
            elif op2.startswith('0x') or op2.lstrip('-').isdigit():
                imm = int(op2, 0)
                if -128 <= imm <= 127:
                    # xor reg, imm8 -> 0x83 /6 ib
                    opcode = 0x83
                    modrm = 0xC0 | (6 << 3) | self.registros[op1]  # /6 es XOR
                    imm_bytes = imm.to_bytes(1, 'little', signed=True)
                    self.agregar_codigo([opcode, modrm] + list(imm_bytes))
                else:
                    # xor reg, imm32 -> 0x81 /6 id
                    opcode = 0x81
                    modrm = 0xC0 | (6 << 3) | self.registros[op1]
                    imm_bytes = imm.to_bytes(4, 'little', signed=True)
                    self.agregar_codigo([opcode, modrm] + list(imm_bytes))
            else:
                raise NotImplementedError(f"xor con segundo operando {op2} no soportado")
        else:
            raise NotImplementedError(f"xor con primer operando {op1} no soportado")

    def codificar_push(self, operandos):
        op = operandos.strip()
        if op in self.registros:
            opcode = 0x50 + self.registros[op]
            self.agregar_codigo([opcode])
        else:
            raise NotImplementedError("push solo para registros soportado")

    def codificar_pop(self, operandos):
        op = operandos.strip()
        if op in self.registros:
            opcode = 0x58 + self.registros[op]
            self.agregar_codigo([opcode])
        else:
            raise NotImplementedError("pop solo para registros soportado")

    def codificar_xchg(self, operandos):
        op1, op2 = [x.strip() for x in operandos.split(',',1)]
        if op1 in self.registros and op2 in self.registros:
            # xchg reg, reg -> 0x87 /r
            opcode = 0x87
            modrm = 0xC0 | (self.registros[op2]<<3) | self.registros[op1]
            self.agregar_codigo([opcode, modrm])
        else:
            raise NotImplementedError("xchg solo entre registros soportado")
        
    def codificar_nop(self):
        # opcode NOP = 0x90, un solo byte
        self.agregar_codigo([0x90])

    def agregar_codigo(self, bytes_lista):
        # Guarda la secuencia de bytes en codigo_hex con direccion actual
        self.codigo_hex.append( (self.contador_posicion, bytes_lista) )
        self.contador_posicion += len(bytes_lista)

    def agregar_referencia_pendiente(self, label, direccion_referencia):
        if label not in self.referencias_pendientes:
            self.referencias_pendientes[label] = []
        self.referencias_pendientes[label].append(direccion_referencia)

    def obtener_direccion_label(self, label):
        # Retorna la direccion si ya esta definida, si no, 0 y agrega referencia pendiente
        if label in self.tabla_simbolos:
            return self.tabla_simbolos[label]
        else:
            # Direccion 0 como placeholder, se parcheará despues
            dir_ref = self.contador_posicion + 2  # La direccion donde aparece la etiqueta en codigo
            self.agregar_referencia_pendiente(label, dir_ref)
            return 0

    def resolver_referencias_pendientes(self):
        # Recorre referencias y parchea código en codigo_hex
        for label, lista_dir in self.referencias_pendientes.items():
            if label not in self.tabla_simbolos:
                raise ValueError(f"Etiqueta {label} usada pero no definida")
            addr_label = self.tabla_simbolos[label]

            for dir_ref in lista_dir:
                # Buscar el segmento en codigo_hex donde se encuentra dir_ref
                for i, (dir_base, bytes_lista) in enumerate(self.codigo_hex):
                    if dir_base <= dir_ref < dir_base + len(bytes_lista):
                        offset = dir_ref - dir_base
                        # Se parchea segun tipo de salto o llamada:
                        # Ejemplo para call/jmp (rel32):
                        # Rel = Addr_label - (Dir_ref + 4)
                        if len(bytes_lista) >= offset+4:
                            rel = addr_label - (dir_ref + 4)
                            rel_bytes = rel.to_bytes(4, 'little', signed=True)
                            for j in range(4):
                                bytes_lista[offset+j] = rel_bytes[j]
                        elif len(bytes_lista) >= offset+1:
                            # Para saltos cortos (jcc 8 bits)
                            rel8 = addr_label - (dir_ref + 1)
                            if not (-128 <= rel8 <= 127):
                                raise ValueError(f"Salto corto fuera de rango para etiqueta {label}")
                            bytes_lista[offset] = rel8 & 0xFF
                        else:
                            raise ValueError("Error al parchear referencia")
                        # Actualizar el segmento
                        self.codigo_hex[i] = (dir_base, bytes_lista)
                        break

    def generar_hex(self, archivo_salida):
        with open(archivo_salida, 'w') as f:
            for dir_base, bytes_lista in self.codigo_hex:
                linea = f"0x{dir_base:04X} " + ' '.join(f"{b:02X}" for b in bytes_lista)
                f.write(linea + '\n')

    def generar_reportes(self):
        with open('tabla_simbolos.txt', 'w') as f:
            f.write("Label\tDirección\n")
            for simb, dir in self.tabla_simbolos.items():
                f.write(f"{simb}\t0x{dir:04X}\n")

        with open('referencias_pendientes.txt', 'w') as f:
            f.write("Label\tDirección\n")
            for simb, dirs in self.referencias_pendientes.items():
                for d in dirs:
                    f.write(f"{simb}\t0x{d:04X}\n")

    def guardar_tabla_simbolos(self, nombre_archivo):
        with open(nombre_archivo, 'w') as f:
            for etiqueta, direccion in self.tabla_simbolos.items():
                f.write(f"{etiqueta} 0x{direccion:04X}\n")

    def guardar_referencias_pendientes(self, nombre_archivo):
        with open(nombre_archivo, 'w') as f:
            for etiqueta, direcciones in self.referencias_pendientes.items():
                for dir_ref in direcciones:
                    f.write(f"{etiqueta} 0x{dir_ref:04X}\n")

    def guardar_codigo_hex(self, nombre_archivo):
        with open(nombre_archivo, 'w') as f:
            for direccion, bytes_ in self.codigo_hex:
                bytes_str = ' '.join(f"{b:02X}" for b in bytes_)
                f.write(f"0x{direccion:04X}: {bytes_str}\n")


def main():
     ensamblador = EnsambladorIA32()
     ensamblador.ensamblar('prueba1.asm')  # Carga y procesa el archivo asm
     ensamblador.resolver_referencias_pendientes()  # Arregla saltos y llamadas pendientes
     ensamblador.generar_hex('codigo_hex.txt')  # Genera archivo con código máquina
     ensamblador.generar_reportes()  # Genera archivos de tabla de símbolos y referencias

     #Prueba adicional
    # ensamblador = EnsambladorIA32()
    # ensamblador.ensamblar("fib.asm")
    # ensamblador.guardar_tabla_simbolos("tabla_simbolos.txt")
    # ensamblador.guardar_referencias_pendientes("referencias_pendientes.txt")
    # ensamblador.guardar_codigo_hex("codigo_hex.txt")


if __name__ == '__main__':
    main()