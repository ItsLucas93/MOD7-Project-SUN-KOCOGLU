from file_manager import load_file
from instructions import Instruction


class Architecture:
    def __init__(self):
        # Initialize memory, stack, registers, and program counter
        self.ptr_memory = {}
        self.memory = 512 * ["000000000"]  # 512 the maximum size of our memory, due to the 9-bit pointer
        self.memory_code = []
        self.stack = []
        self.registers = {'t0': "000000000", 't1': "000000000", 't2': "000000000", 't3': "000000000"}
        self.program_counter = 0
        self.instruction = Instruction(self)

    def __str__(self):
        """
        :return: String representation of the architecture
        """
        return f"Pointer Memory: {self.ptr_memory}\nMemory: {self.memory}\nMemory code: {self.memory_code}\nStack: {self.stack}\nRegisters: {self.registers}\nProgram Counter: {self.program_counter}\n"

    def fetch_data(self, file_path):
        """
        Load the file and split it into 32-bit chunks
        :param file_path: Path of the file to load
        """
        try:
            content = load_file(file_path)
        except (FileNotFoundError, ValueError) as e:
            raise ("Error: ", e)

        # Split the content into 32-bit chunks
        self.memory_code = [content[i:i + 32] for i in range(0, len(content), 32)]
        self.memory_code = [self.sliced_instruction(chunk) for chunk in self.memory_code]
        self.memory_code = [self.decode_instruction(instruction) for instruction in self.memory_code]

    def sliced_instruction(self, instruction):
        """
        Slice the instruction into its different parts
        :param instruction: Instruction to slice
        :return: Dictionary containing the different parts of the instruction
        """
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
        """
        Decode the instruction
        :param instruction: Instruction to decode
        :return: Dictionary containing the decoded instruction
        """
        try:
            instruction['op_code'] = self.instruction.decode_op_code(instruction['op_code'])
            instruction['param_type_1'] = self.instruction.decode_param_type(instruction['param_type_1'])
            instruction['param_type_2'] = self.instruction.decode_param_type(instruction['param_type_2'])
        except ValueError as e:
            raise ("Error: ", e)
        return instruction

    def execute_program(self, mode):
        """
        Execute the program
        :param mode: Mode of execution (full or step)
        :return: Result of the execution if HLT, VAD or VDE is encountered
        """
        if mode == "full":
            return self.execute_full_program()
        elif mode == "step":
            return self.execute_step_program()

    def execute_step_program(self):
        """
        Execute the program step by step
        :return: Result of the execution if HLT, VAD or VDE is encountered
        """
        result = self.execute_instruction(self.memory_code[self.program_counter])
        print(result)
        if result == "HLT":
            return "END"
        elif "VAD" in result:
            return "VAD"
        elif "VDE" in result:
            return "VDE"

    def clear_memory(self):
        """
        Clear the memory, memory_code, ptr_memory, stack, register, registers, and program counter
        """
        self.memory = 512 * ["000000000"]
        self.memory_code = []
        self.ptr_memory = {}
        self.stack = []
        self.registers = {'t0': "000000000", 't1': "000000000", 't2': "000000000", 't3': "000000000"}
        self.program_counter = 0
        self.instruction = Instruction(self)

    def execute_full_program(self):
        """
        Execute the program entirely
        :return: Result of the execution if HLT is encountered
        """
        while self.program_counter < len(self.memory_code):
            result = self.execute_instruction(self.memory_code[self.program_counter])
            if result == "HLT":
                return "END"

    def execute_instruction(self, instruction):
        """
        Send the instruction to the instruction class to be executed
        Increment the program counter
        :param instruction: Instruction to execute
        :return: Result of the execution
        """
        result = self.instruction.execute_instruction(instruction)
        print(f"Result = {result}")
        print(self)
        self.program_counter += 1
        return result

    def add_to_memory(self, variable_name, value):
        """
        Add a variable to the simulated memory
        Can add up to 512 variables (9-bit pointer)
        Search for the first available space in memory and add the variable there
        :param variable_name: Name of the variable to add
        :param value: Value of the variable to add
        :return: True if the variable was successfully added, False otherwise
        """
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
                if value:
                    self.memory[i] = value
                return True  # Success

        return False  # No space in memory found

    def remove_from_memory(self, variable_name):
        """
        Remove a variable from the simulated memory
        Check if the pointer is in memory pointer, if yes remove it with associated value stored in memory
        :param variable_name: Name of the variable to remove
        :return: True if the variable was successfully removed, False otherwise
        """
        # Check if variable_name is already in memory
        if variable_name in self.ptr_memory:
            # Check if other instruction uses the same variable name, if yes replace it with memory address
            for instruction in self.memory_code:
                if instruction['param_type_1'] == 'memory' and instruction['operand_1'] == variable_name:
                    instruction['operand_1'] = self.ptr_memory[variable_name]
                if instruction['param_type_2'] == 'memory' and instruction['operand_2'] == variable_name:
                    instruction['operand_2'] = self.ptr_memory[variable_name]
            self.memory[int(self.ptr_memory[variable_name], 2)] = "0000000000"
            del self.ptr_memory[variable_name]
            return True  # Success
        return False  # Not found
