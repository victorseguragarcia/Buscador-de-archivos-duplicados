import file_scanner

if __name__ == "__main__":
    folder = input("Introduce la ruta de la carpeta a escanear: ")
    duplicates = find_duplicates(folder)

    if duplicates:
        print("Archivos duplicados encontrados:")
        for dup in duplicates:
            print(f"{dup[0]} es duplicado de {dup[1]}")
    else:
        print("No se encontraron duplicados.")
