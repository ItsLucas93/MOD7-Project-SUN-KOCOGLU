"""
LDA - OP Code 00000
STR - OP Code 00001
PUSH - OP Code 00010
AND - OP Code 00011
OR - OP Code 00100
ADD - OP Code 00101
SUB - OP Code 00110
DIV - OP Code 00111
MUL - OP Code 01000
MOD - OP Code 01001
INC - OP Code 01010
DEC - OP Code 01011
BEQ - OP Code 01100
BNE - OP Code 01101
BBG - OP Code 01110
BSM - OP Code 01111
JMP - OP Code 10000
HLT - OP Code 10001

POP - OP Code 11000
NOT - OP Code 11001

Two personalised OP codes:
VAD - OP Code 11110 (Variable ADD)
VDE - OP Code 11111 (Variable DELETE)

Type parameters:
    00 - Register
    01 - Constant
    10 - Memory
    11 - Label

Bits reading:
5 - OP Code
2 - Type parameter 1
2 - Type parameter 2
9 - Operand 1
9 - Operand 2
5 - Label
"""
import re

class Instruction:
    def __init__(self, architecture):
        self.architecture = architecture
        self.instructions = {
            "00000": "LDA",
            "00001": "STR",
            "00010": "PUSH",
            "00011": "AND",
            "00100": "OR",
            "00101": "ADD",
            "00110": "SUB",
            "00111": "DIV",
            "01000": "MUL",
            "01001": "MOD",
            "01010": "INC",
            "01011": "DEC",
            "01100": "BEQ",
            "01101": "BNE",
            "01110": "BBG",
            "01111": "BSM",
            "10000": "JMP",
            "10001": "HLT",
            "11000": "POP",
            "11001": "NOT",
            "11110": "VAD",
            "11111": "VDE"
        }

        self.instructions = {v: k for k, v in self.instructions.items()}

    @staticmethod
    def decode_op_code(string):
        match string:
            case "00000":
                return "LDA"
            case "00001":
                return "STR"
            case "00010":
                return "PUSH"
            case "00011":
                return "AND"
            case "00100":
                return "OR"
            case "00101":
                return "ADD"
            case "00110":
                return "SUB"
            case "00111":
                return "DIV"
            case "01000":
                return "MUL"
            case "01001":
                return "MOD"
            case "01010":
                return "INC"
            case "01011":
                return "DEC"
            case "01100":
                return "BEQ"
            case "01101":
                return "BNE"
            case "01110":
                return "BBG"
            case "01111":
                return "BSM"
            case "10000":
                return "JMP"
            case "10001":
                return "HLT"
            case "11000":
                return "POP"
            case "11001":
                return "NOT"
            case "11110":
                return "VAD"
            case "11111":
                return "VDE"
        raise ValueError("Invalid OP Code")

    def decode_param_type(self, string):
        match string:
            case "00":
                return "register"
            case "01":
                return "constant"
            case "10":
                return "memory"
            case "11":
                return "label"
        raise ValueError("Invalid param type")

    def execute_instruction(self, instruction):
        if instruction['op_code'] in self.instructions:
            return eval("self." + instruction['op_code'] + "(instruction)")
        else:
            raise ValueError("Instruction not found")

    def give_address_memory(self, instruction, param_number):
        match param_number:
            case 1:
                index_param = 'param_type_1'
                index_operand = 'operand_1'
            case 2:
                index_param = 'param_type_2'
                index_operand = 'operand_2'
            case _: raise ValueError("Invalid param number")

        if instruction[index_param] == "memory":
            try:
                # Get variable name from pointer memory
                for key, value in self.architecture.ptr_memory.items():
                    if value == instruction[index_operand] or key == instruction[index_operand]:
                        instruction[index_operand] = key
                        return instruction
            except IndexError:
                raise ValueError("Invalid memory position")
            raise ValueError("Invalid memory position: variable not found")
        raise ValueError("Invalid param type")

    def give_address_register(self, instruction, param_number):
        match param_number:
            case 1:
                index_param = 'param_type_1'
                index_operand = 'operand_1'
            case 2:
                index_param = 'param_type_2'
                index_operand = 'operand_2'
            case _: raise ValueError("Invalid param number")

        if instruction[index_param] == "register":
            match instruction[index_operand]:
                case "000000000" | "t0": instruction[index_operand] = "t0"
                case "000000001" | "t1": instruction[index_operand] = "t1"
                case "000000010" | "t2": instruction[index_operand] = "t2"
                case "000000011" | "t3": instruction[index_operand] = "t3"
                case _: raise ValueError("Invalid register")
            return instruction
        raise ValueError("Invalid param type")

    def LDA(self, instruction):
        """
        Bits used: 11111 11 11 111111111 111111111 XXXXX
        Op code: 00000
        instruction.param_type_1: must be a register
        instruction.operand_1: Destination register
        instruction.param_type_2: Source register/constant/variable
        instruction.operand_2: Source register/constant/variable
        """
        # Select register from param_type_1
        if instruction['param_type_1'] != "register" or instruction['param_type_2'] == "label":
            raise ValueError("Invalid param type")

        # Give address of Destination register
        instruction = self.give_address_register(instruction, 1)

        # Give address of Source if register
        if instruction['operand_2'] and instruction['param_type_2'] == "register":
            instruction = self.give_address_register(instruction, 2)

        # Give adress of Source if memory
        if instruction['operand_2'] and instruction['param_type_2'] == "memory":
            instruction = self.give_address_memory(instruction, 2)

        # Execute instruction
        match instruction['param_type_2']:
            case "register":
                if instruction['operand_1'] in self.architecture.registers and instruction['operand_2'] in self.architecture.registers:
                    self.architecture.registers[instruction['operand_1']] = self.architecture.registers[instruction['operand_2']]
            case "constant":
                if instruction['operand_1'] in self.architecture.registers:
                    self.architecture.registers[instruction['operand_1']] = instruction['operand_2']
            case "memory":
                if instruction['operand_1'] in self.architecture.registers and instruction['operand_2'] in self.architecture.ptr_memory:
                    self.architecture.registers[instruction['operand_1']] = self.architecture.memory[int(self.architecture.ptr_memory[instruction['operand_2']], 2)]
            case _:
                return "ERROR UNRECOGNIZED INSTRUCTION"

        return "LDA" + " " + instruction['operand_1'] + " " + instruction['operand_2']

    def STR(self, instruction):
        """
        Bits used: 00001 10 11 111111111 111111111 XXXXX
        Op code: 00001
        instruction.param_type_1: must be a variable
        instruction.operand_1: Destination variable
        instruction.param_type_2: Source register/constant
        instruction.operand_2: Source register/constant
        """
        # Verify parameters
        if instruction['param_type_1'] != "memory" or instruction['param_type_2'] not in ["register", "constant"]:
            raise ValueError("Invalid param type")

        # Give address of Destination variable
        instruction = self.give_address_memory(instruction, 1)

        # Give address of Source if register
        if instruction['operand_2'] and instruction['param_type_2'] == "register":
            instruction = self.give_address_register(instruction, 2)

        # Execute instruction
        match instruction['param_type_2']:
            case "register":
                if instruction['operand_1'] in self.architecture.ptr_memory and instruction['operand_2'] in self.architecture.registers:
                    self.architecture.memory[int(self.architecture.ptr_memory[instruction['operand_1']], 2)] = self.architecture.registers[instruction['operand_2']]
            case "constant":
                if instruction['operand_1'] in self.architecture.ptr_memory:
                    self.architecture.memory[int(self.architecture.ptr_memory[instruction['operand_1']], 2)] = instruction['operand_2']
            case _:
                return "ERROR UNRECOGNIZED INSTRUCTION"

        return "STR" + " " + instruction['operand_1'] + " " + instruction['operand_2']

    def PUSH(self, instruction):
        """
        Bits used: 00010 11 XX 111111111 XXXXXXX XXXXX
        Op code: 00010
        instruction.param_type_1: Must be a register/constant/variable
        instruction.operand_1: Source register/constant/variable
        Push the value of the register/constant/variable to the stack
        """
        # Verify parameters
        if instruction['param_type_1'] not in ["memory", "register", "constant"]:
            raise ValueError("Invalid param type")

        # Give address of Source if register
        if instruction['operand_1'] and instruction['param_type_1'] == "register":
            instruction = self.give_address_register(instruction, 1)

        # Give address of Source if memory
        if instruction['operand_1'] and instruction['param_type_1'] == "memory":
            instruction = self.give_address_memory(instruction, 1)

        # Pushing to the stack
        if len(self.architecture.stack) > 4096:
            raise OverflowError("Stack overflow")

        # Execute instruction
        match instruction['param_type_1']:
            case "register":
                if instruction['operand_1'] in self.architecture.registers:
                    self.architecture.stack.append(self.architecture.registers[instruction['operand_1']])
            case "constant":
                self.architecture.stack.append(instruction['operand_1'])
            case "memory":
                if instruction['operand_1'] in self.architecture.ptr_memory:
                    self.architecture.stack.append(self.architecture.memory[int(self.architecture.ptr_memory[instruction['operand_1']], 2)])
            case _:
                return "ERROR UNRECOGNIZED INSTRUCTION"
        return "PUSH" + " " + instruction['operand_1']

    def POP(self, instruction):
        """
        Bits used: 11000 00 XX 0000011 XXXXXXX XXXXX
        Op code: 11000
        instruction.param_type_1: Must be a register
        instruction.operand_1: Destination register
        Pop the value of the stack to the register
        """
        # Verify parameters
        if instruction['param_type_1'] != "register":
            raise ValueError("Invalid param type")

        # Give address of Destination register
        instruction = self.give_address_register(instruction, 1)

        # Poping from the stack
        if len(self.architecture.stack) == 0:
            raise OverflowError("Stack underflow")

        # Execute instruction
        if instruction['operand_1'] in self.architecture.registers:
            self.architecture.registers[instruction['operand_1']] = self.architecture.stack.pop()
        else:
            raise ValueError("Invalid register")
        return "POP" + " " + instruction['operand_1']

    def AND(self, instruction):
        """
        Bits used: 00011 00 00 111111111 111111111 XXXXX
        Op code: 00011
        instruction.param_type_1: must be a register
        instruction.operand_1: Destination register
        instruction.param_type_2: Source register/constant/variable
        instruction.operand_2: Source register/constant/variable
        Perform a bitwise AND operation between the two operands and store the result in the destination register
        """
        # Verify parameters
        if instruction['param_type_1'] != "register" or instruction['param_type_2'] not in ["register", "constant", "memory"]:
            raise ValueError("Invalid param type")

        # Give address of Destination register
        instruction = self.give_address_register(instruction, 1)
        operand_1 = self.architecture.registers[instruction['operand_1']]

        # Give address of Source if register
        if instruction['operand_2'] and instruction['param_type_2'] == "register":
            instruction = self.give_address_register(instruction, 2)
            operand_2 = self.architecture.registers[instruction['operand_2']]

        # Give address of Source if memory
        elif instruction['operand_2'] and instruction['param_type_2'] == "memory":
            instruction = self.give_address_memory(instruction, 2)
            operand_2 = self.architecture.memory[int(self.architecture.ptr_memory[instruction['operand_2']], 2)]

        elif instruction['operand_2'] and instruction['param_type_2'] == "constant":
            operand_2 = instruction['operand_2']

        # Execute instruction
        result = ""

        for i in range(0, len(operand_1)):
            result += str(int(operand_1[i]) & int(operand_2[i]))

        self.architecture.registers[instruction['operand_1']] = result
        return "AND" + " " + instruction['operand_1'] + " " + instruction['operand_2']

    def OR(self, instruction):
        """
        Bits used: 00100 00 00 111111111 111111111 XXXXX
        Op code: 00100
        instruction.param_type_1: must be a register
        instruction.operand_1: Destination register
        instruction.param_type_2: Source register/constant/variable
        instruction.operand_2: Source register/constant/variable
        Perform a bitwise OR operation between the two operands and store the result in the destination register
        """
        # Verify parameters
        if instruction['param_type_1'] != "register" or instruction['param_type_2'] not in ["register", "constant", "memory"]:
            raise ValueError("Invalid param type")

        # Give address of Destination register
        instruction = self.give_address_register(instruction, 1)
        operand_1 = self.architecture.registers[instruction['operand_1']]

        # Give address of Source if register
        if instruction['operand_2'] and instruction['param_type_2'] == "register":
            instruction = self.give_address_register(instruction, 2)
            operand_2 = self.architecture.registers[instruction['operand_2']]

        # Give address of Source if memory
        elif instruction['operand_2'] and instruction['param_type_2'] == "memory":
            instruction = self.give_address_memory(instruction, 2)
            operand_2 = self.architecture.memory[int(self.architecture.ptr_memory[instruction['operand_2']], 2)]

        elif instruction['operand_2'] and instruction['param_type_2'] == "constant":
            operand_2 = instruction['operand_2']

        # Execute instruction
        result = ""

        for i in range(0, len(operand_1)):
            result += str(int(operand_1[i]) | int(operand_2[i]))

        self.architecture.registers[instruction['operand_1']] = result
        return "OR" + " " + instruction['operand_1'] + " " + instruction['operand_2']

    def NOT(self, instruction):
        """
        Bits used: 11001 00 XX 111111111 XXXXXXX XXXXX
        Op code: 11001
        instruction.param_type_1: must be a register
        instruction.operand_1: Destination register
        Perform a bitwise NOT operation on the refered register and store the result in the destination register
        """
        # Verify parameters
        if instruction['param_type_1'] != "register":
            raise ValueError("Invalid param type")

        # Give address of Destination register
        instruction = self.give_address_register(instruction, 1)

        # Execute instruction
        operand_1 = self.architecture.registers[instruction['operand_1']]
        result = ""

        for i in range(0, len(operand_1)):
            result += str(int(not int(operand_1[i])))

        self.architecture.registers[instruction['operand_1']] = result
        return "NOT" + " " + instruction['operand_1']

    def ADD(self, instruction):
        """
        Bits used: 00101 00 00 111111111 111111111 XXXXX
        Op code: 00101
        instruction.param_type_1: must be a register
        instruction.operand_1: Destination register
        instruction.param_type_2: Source register/constant/variable
        instruction.operand_2: Source register/constant/variable
        Perform an addition between the two operands and store the result in the destination register
        """
        # Verify parameters
        if instruction['param_type_1'] != "register" or instruction['param_type_2'] not in ["register", "constant", "memory"]:
            raise ValueError("Invalid param type")

        # Give address of Destination register
        instruction = self.give_address_register(instruction, 1)
        operand_1 = self.architecture.registers[instruction['operand_1']]

        # Give address of Source if register
        if instruction['operand_2'] and instruction['param_type_2'] == "register":
            instruction = self.give_address_register(instruction, 2)
            operand_2 = self.architecture.registers[instruction['operand_2']]

        # Give address of Source if memory
        elif instruction['operand_2'] and instruction['param_type_2'] == "memory":
            instruction = self.give_address_memory(instruction, 2)
            operand_2 = self.architecture.memory[int(self.architecture.ptr_memory[instruction['operand_2']], 2)]

        elif instruction['operand_2'] and instruction['param_type_2'] == "constant":
            operand_2 = instruction['operand_2']

        # Execute instruction
        operand_1 = int(operand_1, 2)
        operand_2 = int(operand_2, 2)
        result = operand_1 + operand_2
        if result > 511:
            raise OverflowError("Overflow")

        result = bin(result)[2:].zfill(9)
        self.architecture.registers[instruction['operand_1']] = result
        return "ADD" + " " + instruction['operand_1'] + " " + instruction['operand_2']

    def SUB(self, instruction):
        """
        Bits used: 00110 00 00 111111111 111111111 XXXXX
        Op code: 00110
        instruction.param_type_1: must be a register
        instruction.operand_1: Destination register
        instruction.param_type_2: Source register/constant/variable
        instruction.operand_2: Source register/constant/variable
        Perform a subtraction between the two operands and store the result in the destination register
        """
        # Verify parameters
        if instruction['param_type_1'] != "register" or instruction['param_type_2'] not in ["register", "constant", "memory"]:
            raise ValueError("Invalid param type")

        # Give address of Destination register
        instruction = self.give_address_register(instruction, 1)
        operand_1 = self.architecture.registers[instruction['operand_1']]

        # Give address of Source if register
        if instruction['operand_2'] and instruction['param_type_2'] == "register":
            instruction = self.give_address_register(instruction, 2)
            operand_2 = self.architecture.registers[instruction['operand_2']]

        # Give address of Source if memory
        elif instruction['operand_2'] and instruction['param_type_2'] == "memory":
            instruction = self.give_address_memory(instruction, 2)
            operand_2 = self.architecture.memory[int(self.architecture.ptr_memory[instruction['operand_2']], 2)]

        elif instruction['operand_2'] and instruction['param_type_2'] == "constant":
            operand_2 = instruction['operand_2']

        # Execute instruction
        operand_1 = int(operand_1, 2)
        operand_2 = int(operand_2, 2)
        result = operand_2 - operand_1
        if result < 0:
            raise OverflowError("Underflow")

        result = bin(result)[2:].zfill(9)
        self.architecture.registers[instruction['operand_1']] = result
        return "SUB" + " " + instruction['operand_1'] + " " + instruction['operand_2']

    def DIV(self, instruction):
        """
        Bits used: 00111 00 00 111111111 111111111 XXXXX
        Op code: 00111
        instruction.param_type_1: must be a register
        instruction.operand_1: Destination register
        instruction.param_type_2: Source register/constant/variable
        instruction.operand_2: Source register/constant/variable
        Perform a division between the two operands and store the result in the destination register
        """
        # Verify parameters
        if instruction['param_type_1'] != "register" or instruction['param_type_2'] not in ["register", "constant", "memory"]:
            raise ValueError("Invalid param type")

        # Give address of Destination register
        instruction = self.give_address_register(instruction, 1)
        operand_1 = self.architecture.registers[instruction['operand_1']]

        # Give address of Source if register
        if instruction['operand_2'] and instruction['param_type_2'] == "register":
            instruction = self.give_address_register(instruction, 2)
            operand_2 = self.architecture.registers[instruction['operand_2']]

        # Give address of Source if memory
        elif instruction['operand_2'] and instruction['param_type_2'] == "memory":
            instruction = self.give_address_memory(instruction, 2)
            operand_2 = self.architecture.memory[int(self.architecture.ptr_memory[instruction['operand_2']], 2)]

        elif instruction['operand_2'] and instruction['param_type_2'] == "constant":
            operand_2 = instruction['operand_2']

        # Execute instruction
        operand_1 = int(operand_1, 2)
        operand_2 = int(operand_2, 2)

        if operand_1 == 0:
            raise ZeroDivisionError("Division by zero")

        result = operand_2 // operand_1
        # Overflow and underflow not possible
        # if result > 511:
        #    raise OverflowError("Overflow")

        print(operand_2, operand_1, result)
        result = bin(result)[2:].zfill(9)
        self.architecture.registers[instruction['operand_1']] = result
        return "DIV" + " " + instruction['operand_1'] + " " + instruction['operand_2']

    def MUL(self, instruction):
        """
        Bits used: 01000 00 00 111111111 111111111 XXXXX
        Op code: 01000
        instruction.param_type_1: must be a register
        instruction.operand_1: Destination register
        instruction.param_type_2: Source register/constant/variable
        instruction.operand_2: Source register/constant/variable
        Perform a multiplication between the two operands and store the result in the destination register
        """
        # Verify parameters
        if instruction['param_type_1'] != "register" or instruction['param_type_2'] not in ["register", "constant", "memory"]:
            raise ValueError("Invalid param type")

        # Give address of Destination register
        instruction = self.give_address_register(instruction, 1)
        operand_1 = self.architecture.registers[instruction['operand_1']]

        # Give address of Source if register
        if instruction['operand_2'] and instruction['param_type_2'] == "register":
            instruction = self.give_address_register(instruction, 2)
            operand_2 = self.architecture.registers[instruction['operand_2']]

        # Give address of Source if memory
        elif instruction['operand_2'] and instruction['param_type_2'] == "memory":
            instruction = self.give_address_memory(instruction, 2)
            operand_2 = self.architecture.memory[int(self.architecture.ptr_memory[instruction['operand_2']], 2)]

        elif instruction['operand_2'] and instruction['param_type_2'] == "constant":
            operand_2 = instruction['operand_2']

        # Execute instruction
        operand_1 = int(operand_1, 2)
        operand_2 = int(operand_2, 2)
        result = operand_2 * operand_1
        if result > 511:
            raise OverflowError("Overflow")

        result = bin(result)[2:].zfill(9)
        self.architecture.registers[instruction['operand_1']] = result
        return "MUL" + " " + instruction['operand_1'] + " " + instruction['operand_2']

    def MOD(self, instruction):
        """
        Bits used: 01001 00 00 111111111 111111111 XXXXX
        Op code: 01001
        instruction.param_type_1: must be a register
        instruction.operand_1: Destination register
        instruction.param_type_2: Source register/constant/variable
        instruction.operand_2: Source register/constant/variable
        Perform a modulo between the two operands and store the result in the destination register
        """
        # Verify parameters
        if instruction['param_type_1'] != "register" or instruction['param_type_2'] not in ["register", "constant", "memory"]:
            raise ValueError("Invalid param type")

        # Give address of Destination register
        instruction = self.give_address_register(instruction, 1)
        operand_1 = self.architecture.registers[instruction['operand_1']]

        # Give address of Source if register
        if instruction['operand_2'] and instruction['param_type_2'] == "register":
            instruction = self.give_address_register(instruction, 2)
            operand_2 = self.architecture.registers[instruction['operand_2']]

        # Give address of Source if memory
        elif instruction['operand_2'] and instruction['param_type_2'] == "memory":
            instruction = self.give_address_memory(instruction, 2)
            operand_2 = self.architecture.memory[int(self.architecture.ptr_memory[instruction['operand_2']], 2)]

        elif instruction['operand_2'] and instruction['param_type_2'] == "constant":
            operand_2 = instruction['operand_2']

        # Execute instruction
        operand_1 = int(operand_1, 2)
        operand_2 = int(operand_2, 2)
        if operand_1 == 0:
            raise ZeroDivisionError("Division by zero")
        result = operand_2 % operand_1
        if result > 511:
            raise OverflowError("Overflow")

        result = bin(result)[2:].zfill(9)
        self.architecture.registers[instruction['operand_1']] = result
        return "MOD" + " " + instruction['operand_1'] + " " + instruction['operand_2']

    def INC(self, instruction):
        """
        Bits used: 01010 00 XX 111111111 XXXXXXXX XXXXX
        Op code: 01010
        instruction.param_type_1: must be a register
        instruction.operand_1: Destination register
        Increment the value of the register by 1
        """
        # Verify parameters
        if instruction['param_type_1'] != "register":
            raise ValueError("Invalid param type")
        # Give address of Destination register
        instruction = self.give_address_register(instruction, 1)
        # Execute instruction

        operand_1 = self.architecture.registers[instruction['operand_1']]
        result = ""
        binary_value = int(operand_1, 2)
        binary_value += 1
        result = bin(binary_value)[2:].zfill(len(operand_1))
        print(result)
        if len(result) > 9:
            raise OverflowError("Overflow")

        self.architecture.registers[instruction['operand_1']] = result

        return "INC" + " " + instruction['operand_1']


    def DEC(self, instruction):
        """
        Bits used: 01011 00 XX 111111111 XXXXXXXX XXXXX
        Op code: 01011
        instruction.param_type_1: must be a register
        instruction.operand_1: Destination register
        Decrement the value of the register by 1
        """
        # Verify parameters
        if instruction['param_type_1'] != "register":
            raise ValueError("Invalid param type")
        # Give address of Destination register
        instruction = self.give_address_register(instruction, 1)
        # Execute instruction

        operand_1 = self.architecture.registers[instruction['operand_1']]
        result = ""
        binary_value = int(operand_1, 2)
        if binary_value == 0:
            raise OverflowError("Underflow")
        binary_value -= 1
        result = bin(binary_value)[2:].zfill(len(operand_1))
        print(result)
        self.architecture.registers[instruction['operand_1']] = result

        return "DEC" + " " + instruction['operand_1']

    def BEQ(self, instruction):
        """
        Bits used: 01100 00 00 111111111 111111111 00000
        Op code: 01100
        instruction.param_type_1: Can be a register/constant/variable
        instruction.operand_1: Operand1 register/constant/variable
        instruction.param_type_2: Can be a register/constant/variable
        instruction.operand_2: Operand2 register/constant/variable
        instruction.label: Line to jump to (PC)
        Perform a comparison between the two operands and jump to the label if they are equal
        """
        # Verify parameters
        if instruction['param_type_1'] not in ["memory", "register", "constant"] or instruction ['param_type_2'] not in ["memory", "register", "constant"]:
            raise ValueError("Invalid param type")

        # Give address of Destination register
        if instruction['operand_1'] and instruction['param_type_1'] == "register":
            instruction = self.give_address_register(instruction, 1)
            operand_1 = self.architecture.registers[instruction['operand_1']]

        elif instruction['operand_1'] and instruction['param_type_1'] == "memory":
            instruction = self.give_address_memory(instruction, 1)
            operand_1 = self.architecture.memory[int(self.architecture.ptr_memory[instruction['operand_1']], 2)]

        elif instruction['operand_1'] and instruction['param_type_1'] == "constant":
            operand_1 = instruction['operand_1']

        # Give address of Source if register
        if instruction['operand_2'] and instruction['param_type_2'] == "register":
            instruction = self.give_address_register(instruction, 2)
            operand_2 = self.architecture.registers[instruction['operand_2']]

        elif instruction['operand_2'] and instruction['param_type_2'] == "memory":
            instruction = self.give_address_memory(instruction, 2)
            operand_2 = self.architecture.memory[int(self.architecture.ptr_memory[instruction['operand_2']], 2)]

        elif instruction['operand_2'] and instruction['param_type_2'] == "constant":
            operand_2 = instruction['operand_2']

        # Execute instruction
        operand_1 = int(operand_1, 2)
        operand_2 = int(operand_2, 2)
        result = bool(operand_1 == operand_2)
        if result:
            self.architecture.program_counter = int(instruction['label'], 2)

        return "BEQ" + " " + instruction['operand_1'] + " " + instruction['operand_2'] + " " + instruction['label']

    def BNE(self, instruction):
        """
        Bits used: 01101 00 00 111111111 111111111 00000
        Op code: 01101
        instruction.param_type_1: Can be a register/constant/variable
        instruction.operand_1: Operand1 register/constant/variable
        instruction.param_type_2: Can be a register/constant/variable
        instruction.operand_2: Operand2 register/constant/variable
        instruction.label: Line to jump to (PC)
        Perform a comparison between the two operands and jump to the label if they are not equal
        """
        # Verify parameters
        if instruction['param_type_1'] not in ["memory", "register", "constant"] or instruction ['param_type_2'] not in ["memory", "register", "constant"]:
            raise ValueError("Invalid param type")

        # Give address of Destination register
        if instruction['operand_1'] and instruction['param_type_1'] == "register":
            instruction = self.give_address_register(instruction, 1)
            operand_1 = self.architecture.registers[instruction['operand_1']]

        elif instruction['operand_1'] and instruction['param_type_1'] == "memory":
            instruction = self.give_address_memory(instruction, 1)
            operand_1 = self.architecture.memory[int(self.architecture.ptr_memory[instruction['operand_1']], 2)]

        elif instruction['operand_1'] and instruction['param_type_1'] == "constant":
            operand_1 = instruction['operand_1']

        # Give address of Source if register
        if instruction['operand_2'] and instruction['param_type_2'] == "register":
            instruction = self.give_address_register(instruction, 2)
            operand_2 = self.architecture.registers[instruction['operand_2']]

        elif instruction['operand_2'] and instruction['param_type_2'] == "memory":
            instruction = self.give_address_memory(instruction, 2)
            operand_2 = self.architecture.memory[int(self.architecture.ptr_memory[instruction['operand_2']], 2)]

        elif instruction['operand_2'] and instruction['param_type_2'] == "constant":
            operand_2 = instruction['operand_2']

        # Execute instruction
        operand_1 = int(operand_1, 2)
        operand_2 = int(operand_2, 2)
        result = bool(operand_1 != operand_2)
        if result:
            self.architecture.program_counter = int(instruction['label'], 2)

        return "BNE" + " " + instruction['operand_1'] + " " + instruction['operand_2'] + " " + instruction['label']

    def BBG(self, instruction):
        """
        Bits used: 01110 00 00 111111111 111111111 00000
        Op code: 01110
        instruction.param_type_1: Can be a register/constant/variable
        instruction.operand_1: Operand1 register/constant/variable
        instruction.param_type_2: Can be a register/constant/variable
        instruction.operand_2: Operand2 register/constant/variable
        instruction.label: Line to jump to (PC)
        Perform a comparison between the two operands and jump to the label if the first operand is bigger than the second
        """
        # Verify parameters
        if instruction['param_type_1'] not in ["memory", "register", "constant"] or instruction ['param_type_2'] not in ["memory", "register", "constant"]:
            raise ValueError("Invalid param type")

        # Give address of Destination register
        if instruction['operand_1'] and instruction['param_type_1'] == "register":
            instruction = self.give_address_register(instruction, 1)
            operand_1 = self.architecture.registers[instruction['operand_1']]

        elif instruction['operand_1'] and instruction['param_type_1'] == "memory":
            instruction = self.give_address_memory(instruction, 1)
            operand_1 = self.architecture.memory[int(self.architecture.ptr_memory[instruction['operand_1']], 2)]

        elif instruction['operand_1'] and instruction['param_type_1'] == "constant":
            operand_1 = instruction['operand_1']

        # Give address of Source if register
        if instruction['operand_2'] and instruction['param_type_2'] == "register":
            instruction = self.give_address_register(instruction, 2)
            operand_2 = self.architecture.registers[instruction['operand_2']]

        elif instruction['operand_2'] and instruction['param_type_2'] == "memory":
            instruction = self.give_address_memory(instruction, 2)
            operand_2 = self.architecture.memory[int(self.architecture.ptr_memory[instruction['operand_2']], 2)]

        elif instruction['operand_2'] and instruction['param_type_2'] == "constant":
            operand_2 = instruction['operand_2']

        # Execute instruction
        operand_1 = int(operand_1, 2)
        operand_2 = int(operand_2, 2)
        result = bool(operand_1 > operand_2)
        if result:
            self.architecture.program_counter = int(instruction['label'], 2)

        return "BBG" + " " + instruction['operand_1'] + " " + instruction['operand_2'] + " " + instruction['label']

    def BSM(self, instruction):
        """
        Bits used: 01111 00 00 111111111 111111111 00000
        Op code: 01111
        instruction.param_type_1: Can be a register/constant/variable
        instruction.operand_1: Operand1 register/constant/variable
        instruction.param_type_2: Can be a register/constant/variable
        instruction.operand_2: Operand2 register/constant/variable
        instruction.label: Line to jump to (PC)
        Perform a comparison between the two operands and jump to the label if the first operand is smaller than the second
        """
        # Verify parameters
        if instruction['param_type_1'] not in ["memory", "register", "constant"] or instruction ['param_type_2'] not in ["memory", "register", "constant"]:
            raise ValueError("Invalid param type")

        # Give address of Destination register
        if instruction['operand_1'] and instruction['param_type_1'] == "register":
            instruction = self.give_address_register(instruction, 1)
            operand_1 = self.architecture.registers[instruction['operand_1']]

        elif instruction['operand_1'] and instruction['param_type_1'] == "memory":
            instruction = self.give_address_memory(instruction, 1)
            operand_1 = self.architecture.memory[int(self.architecture.ptr_memory[instruction['operand_1']], 2)]

        elif instruction['operand_1'] and instruction['param_type_1'] == "constant":
            operand_1 = instruction['operand_1']

        # Give address of Source if register
        if instruction['operand_2'] and instruction['param_type_2'] == "register":
            instruction = self.give_address_register(instruction, 2)
            operand_2 = self.architecture.registers[instruction['operand_2']]

        elif instruction['operand_2'] and instruction['param_type_2'] == "memory":
            instruction = self.give_address_memory(instruction, 2)
            operand_2 = self.architecture.memory[int(self.architecture.ptr_memory[instruction['operand_2']], 2)]

        elif instruction['operand_2'] and instruction['param_type_2'] == "constant":
            operand_2 = instruction['operand_2']

        # Execute instruction
        operand_1 = int(operand_1, 2)
        operand_2 = int(operand_2, 2)
        result = bool(operand_1 < operand_2)
        if result:
            self.architecture.program_counter = int(instruction['label'], 2)

        return "BSM" + " " + instruction['operand_1'] + " " + instruction['operand_2'] + " " + instruction['label']

    def JMP(self, instruction):
        """
        Bits used: 10000 11 XX XXXXXXXX XXXXXXX 00000
        Op code: 10000
        instruction.param_type_1: must be a label
        instruction.label: Line to jump to (PC)
        Jump to the line (Affect PC)
        """
        # Verify parameters
        if instruction['param_type_1'] != "label":
            raise ValueError("Invalid param type")

        # Execute instruction
        self.architecture.program_counter = int(instruction['label'], 2)

        return "JMP" + " " + instruction['label']

    def HLT(self, instruction):
        """
        Bits used: 10001 XX XX XXXXXXXX XXXXXXXX XXXXX
        Op code: 10001
        Declare the end of the program
        """
        # Execute instruction
        self.architecture.program_counter = len(self.architecture.memory_code) - 1

        return "HLT"

    def VAD(self, instruction):
        """
        Specific Design from here
        Bits used: 11110 01 XX XX 111111111111111111111
        Op code: 11110
        instruction.param_type_1: must be a constant
        instruction.operand_1 + instruction.operand_2 + instruction.label: variable name in ASCII binary

        operand 1: ASCII value of the variable name
        operand 2: value of the variable
        """
        if instruction['param_type_1'] != "constant" or instruction['param_type_2'] != "constant":
            raise ValueError("Invalid param type")

        # Valdiators
        # ASCII must not contain space and special characters
        string = instruction['operand_1'][2:] + instruction['operand_2'] + instruction['label']
        string = chr(int("0b0" + string[0:7], 2)) + chr(int("0b0" + string[7:14], 2)) + chr(int("0b0" + string[14:21], 2))
        regex = r'[a-zA-Z]*'
        if not re.fullmatch(regex, string):
            raise ValueError("Invalid variable name")

        # Check if variable already exists
        if string in self.architecture.ptr_memory.keys():
            raise ValueError("Variable already exists")

        # Execute instruction
        self.architecture.add_to_memory(string, None)
        return "VAD" + " " + string

    def VDE(self, instruction):
        """
        Specific Design from here
        Bits used: 11111 01 XX XX 111111111111111111111
        Op code: 11111
        instruction.param_type_1: must be a constant
        instruction.operand_1 + instruction.operand_2 + instruction.label: variable name in ASCII binary

        operand 1: ASCII value of the variable name
        operand 2: value of the variable
        """
        if instruction['param_type_1'] != "constant" or instruction['param_type_2'] != "constant":
            raise ValueError("Invalid param type")

        # Valdiators
        # ASCII must not contain space and special characters
        string = instruction['operand_1'][2:] + instruction['operand_2'] + instruction['label']
        string = chr(int("0b0" + string[0:7], 2)) + chr(int("0b0" + string[7:14], 2)) + chr(int("0b0" + string[14:21], 2))
        regex = r'[a-zA-Z]*'
        if not re.fullmatch(regex, string):
            raise ValueError("Invalid variable name")

        # Check if variable already exists
        if string not in self.architecture.ptr_memory.keys():
            raise ValueError("Variable does not exists")

        # Execute instruction
        self.architecture.remove_from_memory(string)
        return "VDE" + " " + string