def format_bytes(data: bytes, mode: str) -> str:
    if mode == 'ASCII':
        try:
            return data.decode('utf-8')
        except UnicodeDecodeError:
            return data.decode('utf-8', errors='replace')
    else:
        return ' '.join(f'{b:02X}' for b in data)