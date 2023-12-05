from file_manager import load_file

class Architecure:
    def __init__(self):
        # Initialize memory, stack, registers, and program counter
        self.memory = {}
        self.stack = []
        self.registers = {'t0': "", 't1': "", 't2': "", 't3': ""}
        self.program_counter = 0

    def __str__(self):
        return f"Memory: {self.memory}\nStack: {self.stack}\nRegisters: {self.registers}\nProgram Counter: {self.program_counter}"

    def fetch_data(self, file_path):
        try:
            content = load_file(file_path)
        except (FileNotFoundError, ValueError) as e:
            raise ("Error: ", e)

        # Split the content into 32-bit chunks
        chunks = [content[i:i+32] for i in range(0, len(content), 32)]
        sliced_instruction = [self.sliced_instruction(chunk) for chunk in chunks]

    def sliced_instruction(self, instruction):
        op_code = instruction[0:5]
        param_type_1 = instruction[5:7]
        param_type_2 = instruction[7:9]
        operand_1 = instruction[9:18]
        operand_2 = instruction[18:27]
        verification_label_bit = instruction[27]
        label = instruction[28:32]

        sliced_instruction = {
            'op_code': op_code,
            'param_type_1': param_type_1,
            'param_type_2': param_type_2,
            'operand_1': operand_1,
            'operand_2': operand_2,
            'verification_label_bit': verification_label_bit,
            'label': label if verification_label_bit == '1' else None
        }

        print(sliced_instruction)

        return sliced_instruction


    def execute_instruction(self):
        pass




architecture = Architecure()
architecture.fetch_data("sample.txt")
print(architecture.fetch_data("sample.txt"))

