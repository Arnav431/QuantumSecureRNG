def save_to_file(filename, data, binary=False):
    mode = "wb" if binary else "w"
    with open(filename, mode) as f:
        f.write(data)
