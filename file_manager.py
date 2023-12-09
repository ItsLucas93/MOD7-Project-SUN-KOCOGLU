def load_file(file_path):
    try:
        with open(file_path, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f'File {file_path} not found')

    # Verify that the file is a valid file: only 0 and 1
    if not all(c in ['0', '1', '\n'] for c in content):
        if all(c in ['#CODE', '#DATA'] for c in content):
            content = translate_code_to_binary(file_path)
        else:
            raise ValueError(f'File {file_path} is not a valid file (Not only 0 and 1)')
    else:
        content = content.replace('\n', '')

    # Verify that the file is a valid file: can be divided into 32-bit chunks
    if len(content) % 32 != 0:
        raise ValueError(
            f'File {file_path} is not a valid file (Bits counting is not a multiple of 32: len = {len(content), len(content) % 32})')

    return content


def translate_code_to_binary(file_path):
        instructions = {'LDA': '00000', 'STR': '00001', 'PUSH': '00010', 'AND': '00011', 'OR': '00100', 'ADD': '00101',
                        'SUB': '00110', 'DIV': '00111', 'MUL': '01000', 'MOD': '01001', 'INC': '01010', 'DEC': '01011',
                        'BEQ': '01100', 'BNE': '01101', 'BBG': '01110', 'BSM': '01111', 'JMP': '10000', 'HLT': '10001',
                        'POP': '11000', 'NOT': '11001'}
        registers = {'t0': '000000000', 't1': '000000001', 't2': '000000010', 't3': '000000011'}
        variables = {}
        binary_code = ''

        with open(file_path, 'r') as f:
            lines = f.readlines()

        for line in lines:
            line = line.strip()
            if line.startswith('!'):
                continue
            elif line.startswith('#DATA'):
                mode = 'data'
                continue
            elif line.startswith('#CODE'):
                mode = 'code'
                continue

            if mode == 'data':
                var_name, initial_value = line.split()
                variables[var_name] = bin(int(initial_value))[2:].zfill(9)
            elif mode == 'code':
                parts = line.split()
                binary_instruction = instructions[parts[0]]
                for part in parts[1:]:
                    if part in registers:
                        binary_instruction += registers[part]
                    elif part in variables:
                        binary_instruction += variables[part]
                    else:
                        binary_instruction += bin(int(part))[2:].zfill(9)
                binary_code += binary_instruction

        return binary_code