def load_file(file_path):
    try:
        with open(file_path, 'r') as f:
            content = f.read().replace('\n', '')
    except FileNotFoundError:
        raise FileNotFoundError(f'File {file_path} not found')

    if len(content) % 32 != 0:
        raise ValueError(f'File {file_path} is not a valid file (Bits counting is not a multiple of 32: len = {len(content), len(content) % 32})')

    return content

