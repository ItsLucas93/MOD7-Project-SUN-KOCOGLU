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
1 - Verification bit
4 - Label
"""

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
            "11001": "NOT"
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


    def LDA(self, instruction):
        """
        Bits used: 11111 11 11 111111111 111111111 X XXXX
        Op code: 00000
        instruction.param_type_1: must be a register
        instruction.operand_1: Destination register
        instruction.param_type_2: Source register/constant/variable
        instruction.operand_2: Source register/constant/variable
        """
        # Select register from param_type_1
        if instruction['param_type_1'] != "register" or instruction['param_type_2'] == "label":
            raise ValueError("Invalid param type")

        # Give adress of Destination register
        match instruction['operand_1']:
            case "000000000": instruction['operand_1'] = "t0"
            case "000000001": instruction['operand_1'] = "t1"
            case "000000010": instruction['operand_1'] = "t2"
            case "000000011": instruction['operand_1'] = "t3"
            case _: raise ValueError("Invalid register")

        # Give address of Source if register
        register_destination = None
        if instruction['operand_2'] and instruction['param_type_2'] == "register":
            match instruction['operand_2']:
                case "000000000": register_destination = "t0"
                case "000000001": register_destination = "t1"
                case "000000010": register_destination = "t2"
                case "000000011": register_destination = "t3"
                case _: raise ValueError("Invalid register")
            if register_destination is None:
                raise ValueError("Invalid register")
            else:
                instruction['operand_2'] = register_destination

        # Give adress of Source if memory
        elif instruction['param_type_2'] == "memory":
            try:
                # Get variable name from pointer memory
                boolean = False
                for key, value in self.architecture.ptr_memory.items():
                    if value == instruction['operand_2']:
                        instruction['operand_2'] = key
                        boolean = True
                        break
                if not boolean:
                    raise ValueError("Invalid memory position: variable not found")
            except IndexError:
                raise ValueError("Invalid memory position")

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
        Bits used: 11111 11 11 111111111 111111111 X XXXX
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
        try:
            # Get variable name from pointer memory
            boolean = False
            for key, value in self.architecture.ptr_memory.items():
                if value == instruction['operand_1']:
                    instruction['operand_1'] = key
                    boolean = True
                    break
            if not boolean:
                raise ValueError("Invalid memory position: variable not found")
        except IndexError:
            raise ValueError("Invalid memory position")

        # Give address of Source if register
        if instruction['operand_2'] and instruction['param_type_2'] == "register":
            match instruction['operand_2']:
                case "000000000": instruction['operand_2'] = "t0"
                case "000000001": instruction['operand_2'] = "t1"
                case "000000010": instruction['operand_2'] = "t2"
                case "000000011": instruction['operand_2'] = "t3"
                case _: raise ValueError("Invalid register")

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
