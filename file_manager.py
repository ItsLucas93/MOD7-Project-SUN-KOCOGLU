def load_file(file_path):
    """
    Load the file and verify that it is a valid file
    File must store binary content (only 0 and 1) and can be divided into 32-bit chunks
    :param file_path: Path of the file to load
    :return: Content of the file
    """
    try:
        with open(file_path, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f'File {file_path} not found')

    # Verify that the file is a valid file: only 0 and 1
    if not all(c in ['0', '1', '\n'] for c in content):
        # if all(c in ['#CODE', '#DATA'] for c in content):
        #    content = translate_code_to_binary(file_path)
        # else:
        raise ValueError(f'File {file_path} is not a valid file (Not only 0 and 1)')
    else:
        content = content.replace('\n', '')

    # Verify that the file is a valid file: can be divided into 32-bit chunks
    if len(content) % 32 != 0:
        raise ValueError(
            f'File {file_path} is not a valid file (Bits counting is not a multiple of 32: len = {len(content), len(content) % 32})')

    return content
