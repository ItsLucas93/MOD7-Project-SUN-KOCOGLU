from file_manager import load_file
from instructions import Instruction


class Architecure:
    def __init__(self):
        # Initialize memory, stack, registers, and program counter
        self.ptr_memory = {}
        self.memory = 512 * ["000000000"]  # 512 the maximum size of our memory, due to the 9-bit pointer
        self.memory_code = []
        self.stack = []
        self.registers = {'t0': "000000010", 't1': "000000000", 't2': "111111111", 't3': "000000000"}
        self.program_counter = 0
        self.instruction = Instruction(self)

    def __str__(self):
        return f"Pointer Memory: {self.ptr_memory}\nMemory: {self.memory}\nMemory code: {self.memory_code}\nStack: {self.stack}\nRegisters: {self.registers}\nProgram Counter: {self.program_counter}\n"

    def fetch_data(self, file_path):
        try:
            content = load_file(file_path)
        except (FileNotFoundError, ValueError) as e:
            raise ("Error: ", e)

        # Split the content into 32-bit chunks
        self.memory_code = [content[i:i + 32] for i in range(0, len(content), 32)]
        self.memory_code = [self.sliced_instruction(chunk) for chunk in self.memory_code]
        self.memory_code = [self.decode_instruction(instruction) for instruction in self.memory_code]

    def sliced_instruction(self, instruction):
        op_code = instruction[0:5]
        param_type_1 = instruction[5:7]
        param_type_2 = instruction[7:9]
        operand_1 = instruction[9:18]
        operand_2 = instruction[18:27]
        label = instruction[27:32]

        sliced_instruction = {
            'op_code': op_code,
            'param_type_1': param_type_1,
            'param_type_2': param_type_2,
            'operand_1': operand_1,
            'operand_2': operand_2,
            'label': label
        }

        return sliced_instruction

    def decode_instruction(self, instruction):
        try:
            instruction['op_code'] = self.instruction.decode_op_code(instruction['op_code'])
            instruction['param_type_1'] = self.instruction.decode_param_type(instruction['param_type_1'])
            instruction['param_type_2'] = self.instruction.decode_param_type(instruction['param_type_2'])
        except ValueError as e:
            raise ("Error: ", e)
        return instruction

    def execute_program(self):
        while self.program_counter < len(self.memory_code):
            self.execute_instruction(self.memory_code[self.program_counter])

    def execute_instruction(self, instruction):
        result = self.instruction.execute_instruction(instruction)
        print(f"Result = {result}")
        print(self)
        self.program_counter += 1

    def add_to_memory(self, variable_name, value):
        # Check if variable_name is already in memory
        if variable_name in self.ptr_memory:
            self.memory[int(self.ptr_memory[variable_name], 2)] = value
            return True

        liste_ptr_memory = list(self.ptr_memory.values())
        liste_ptr_memory = [int(i, 2) for i in liste_ptr_memory]

        for i in range(0, 512):
            if i in liste_ptr_memory:
                pass
            else:
                self.ptr_memory[variable_name] = bin(i)[2:].zfill(9)
                self.memory[i] = value
                return True  # Success

        return False  # No space in memory found

    def remove_from_memory(self, variable_name):
        if variable_name in self.ptr_memory:
            self.memory[int(self.ptr_memory[variable_name], 2)] = "0000000000"
            del self.ptr_memory[variable_name]
            return True  # Success
        return False  # Not found


architecture = Architecure()
architecture.add_to_memory("A", "000000000")
architecture.add_to_memory("B", "000000001")
architecture.add_to_memory("C", "000000010")
architecture.add_to_memory("D", "111000111")
architecture.fetch_data("sample.txt")
architecture.execute_program()
