def load_file(file_path):
    try:
        with open(file_path, 'r') as f:
            content = f.read().replace('\n', '')
    except FileNotFoundError:
        raise FileNotFoundError(f'File {file_path} not found')

    # Verify that the file is a valid file: can be divided into 32-bit chunks
    if len(content) % 32 != 0:
        raise ValueError(f'File {file_path} is not a valid file (Bits counting is not a multiple of 32: len = {len(content), len(content) % 32})')

    # Verify that the file is a valid file: only 0 and 1
    if not all(c in '01' for c in content):
        raise ValueError(f'File {file_path} is not a valid file (Not only 0 and 1)')

    return content
