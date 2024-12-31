import tkinter as tk
from tkinter import filedialog, messagebox
import os
import hashlib
import shutil
from concurrent.futures import ThreadPoolExecutor

def calculate_hash(file_path):
    """Calcula el hash SHA256 de un archivo."""
    hasher = hashlib.sha256()
    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()

def find_duplicates(file_paths, min_size=0, max_size=None):
    """Busca archivos duplicados en una lista de archivos."""
    hashes = {}
    duplicates = []

    print("Escaneando archivos seleccionados...")

    def process_file(file_path):
        """Procesa un archivo para detectar duplicados."""
        try:
            file_size = os.path.getsize(file_path)

            # Filtra por tamaño de archivo (si está entre min_size y max_size)
            if file_size < min_size or (max_size and file_size > max_size):
                return None

            # Calcula el hash del archivo
            file_hash = calculate_hash(file_path)

            # Detecta duplicados
            if file_hash in hashes:
                return (file_path, hashes[file_hash], file_size)
            else:
                hashes[file_hash] = file_path
                return None
        except Exception as e:
            print(f"Error al procesar {file_path}: {e}")
            return None

    # Usamos ThreadPoolExecutor para paralelizar el procesamiento de archivos
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_file, file_path) for file_path in file_paths]
        for future in futures:
            result = future.result()
            if result:
                duplicates.append(result)

    if not duplicates:
        print("No se encontraron archivos duplicados.")

    return duplicates

def move_duplicates(duplicates, destination_folder):
    """Mueve los archivos duplicados a una carpeta de destino utilizando multithreading."""
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    def move_file(dup):
        """Mueve un archivo duplicado a la carpeta de destino."""
        file_path, original_path, _ = dup
        try:
            # Mueve el archivo duplicado
            dest = os.path.join(destination_folder, os.path.basename(file_path))
            shutil.move(file_path, dest)
            print(f"Movido: {file_path} -> {dest}")
        except Exception as e:
            print(f"Error al mover {file_path}: {e}")

    # Usamos ThreadPoolExecutor para mover los archivos duplicados en paralelo
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(move_file, dup) for dup in duplicates]
        for future in futures:
            future.result()  # Espera que se complete cada tarea

def delete_duplicates(duplicates):
    """Elimina los archivos duplicados utilizando multithreading."""
    def delete_file(dup):
        """Elimina un archivo duplicado."""
        file_path, original_path, _ = dup
        try:
            os.remove(file_path)
            print(f"Eliminado: {file_path}")
        except Exception as e:
            print(f"Error al eliminar {file_path}: {e}")

    # Usamos ThreadPoolExecutor para eliminar los archivos duplicados en paralelo
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(delete_file, dup) for dup in duplicates]
        for future in futures:
            future.result()  # Espera que se complete cada tarea

class DuplicateFinderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Buscador de Archivos Duplicados")
        self.root.geometry("600x600")  # Definir el tamaño de la ventana
        self.root.config(bg="#f4f4f4")  # Color de fondo suave

        self.folder_path = ""
        self.duplicates = []

        # Título
        self.title_label = tk.Label(self.root, text="Buscador de Archivos Duplicados", font=("Helvetica", 16, "bold"), bg="#f4f4f4")
        self.title_label.pack(pady=10)

        # Carpeta seleccionada
        self.folder_label = tk.Label(self.root, text="Selecciona la carpeta o archivos:", font=("Arial", 12), bg="#f4f4f4")
        self.folder_label.pack(pady=5)

        self.select_folder_button = tk.Button(self.root, text="Seleccionar Archivos", command=self.select_files, 
                                              font=("Arial", 12), bg="#4CAF50", fg="white", relief="flat", 
                                              width=20, height=2)
        self.select_folder_button.pack(pady=10)

        # Tamaño mínimo (en MB)
        self.min_size_label = tk.Label(self.root, text="Tamaño mínimo (MB):", font=("Arial", 12), bg="#f4f4f4")
        self.min_size_label.pack(pady=5)

        self.min_size_entry = tk.Entry(self.root, font=("Arial", 12), width=20, relief="solid")
        self.min_size_entry.insert(0, "0")  # Valor predeterminado a 0
        self.min_size_entry.pack(pady=5)

        # Tamaño máximo (en MB)
        self.max_size_label = tk.Label(self.root, text="Tamaño máximo (MB):", font=("Arial", 12), bg="#f4f4f4")
        self.max_size_label.pack(pady=5)

        self.max_size_entry = tk.Entry(self.root, font=("Arial", 12), width=20, relief="solid")
        self.max_size_entry.pack(pady=5)

        # Botón para iniciar la búsqueda de duplicados
        self.find_button = tk.Button(self.root, text="Buscar Duplicados", command=self.find_duplicates,
                                     font=("Arial", 12), bg="#2196F3", fg="white", relief="flat", 
                                     width=20, height=2)
        self.find_button.pack(pady=20)

        # Área de texto para mostrar los duplicados encontrados
        self.duplicates_text = tk.Text(self.root, height=10, width=50, font=("Arial", 12), wrap=tk.WORD, 
                                       bg="#f0f0f0", relief="solid")
        self.duplicates_text.pack(pady=10)

        # Botón para mover duplicados
        self.move_button = tk.Button(self.root, text="Mover Duplicados", command=self.move_duplicates, 
                                     font=("Arial", 12), bg="#FFC107", fg="white", relief="flat", 
                                     width=20, height=2)
        self.move_button.pack(pady=10)

        # Botón para eliminar duplicados
        self.delete_button = tk.Button(self.root, text="Eliminar Duplicados", command=self.delete_duplicates, 
                                       font=("Arial", 12), bg="#F44336", fg="white", relief="flat", 
                                       width=20, height=2)
        self.delete_button.pack(pady=10)

    def select_files(self):
        """Abre el cuadro de diálogo para seleccionar archivos."""
        self.file_paths = filedialog.askopenfilenames(title="Seleccionar Archivos", filetypes=(("Todos los Archivos", "*.*"),))
        if self.file_paths:
            print(f"Archivos seleccionados: {self.file_paths}")

    def find_duplicates(self):
        """Busca los duplicados con los parámetros de tamaño mínimo y máximo."""
        try:
            # Convierte MB a bytes
            min_size = int(self.min_size_entry.get()) * 1024 * 1024
            max_size = int(self.max_size_entry.get()) * 1024 * 1024 if self.max_size_entry.get() else None
            self.duplicates = find_duplicates(self.file_paths, min_size, max_size)
            
            if self.duplicates:
                print(f"Se encontraron {len(self.duplicates)} archivos duplicados.")
                self.show_duplicates()
                messagebox.showinfo("Éxito", f"Se encontraron {len(self.duplicates)} archivos duplicados.")
            else:
                messagebox.showinfo("Sin duplicados", "No se encontraron archivos duplicados.")
        except ValueError:
            messagebox.showerror("Error", "Por favor ingrese valores válidos para el tamaño.")

    def show_duplicates(self):
        """Muestra los duplicados encontrados en el TextBox."""
        self.duplicates_text.delete(1.0, tk.END)  # Borra contenido previo
        for dup in self.duplicates:
            file_path, original_path, file_size = dup
            file_size_mb = file_size / (1024 * 1024)  # Convertir tamaño a MB
            self.duplicates_text.insert(tk.END, f"Archivo: {file_path}\nTamaño: {file_size_mb:.2f} MB\nOriginal: {original_path}\n\n")

    def move_duplicates(self):
        """Mueve los duplicados a una carpeta especificada."""
        if self.duplicates:
            destination_folder = filedialog.askdirectory(title="Selecciona carpeta de destino para mover los duplicados")
            if destination_folder:
                move_duplicates(self.duplicates, destination_folder)
                messagebox.showinfo("Éxito", "Los duplicados han sido movidos.")

    def delete_duplicates(self):
        """Elimina los duplicados."""
        if self.duplicates:
            confirm = messagebox.askyesno("Confirmación", "¿Seguro que quieres eliminar los duplicados?")
            if confirm:
                delete_duplicates(self.duplicates)
                messagebox.showinfo("Éxito", "Los duplicados han sido eliminados.")
        else:
            messagebox.showwarning("Sin duplicados", "No hay duplicados para eliminar.")
            
if __name__ == "__main__":
    root = tk.Tk()
    app = DuplicateFinderApp(root)
    root.mainloop()
