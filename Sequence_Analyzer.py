"""
FASTA File Gene Analysis Tool

This script provides a graphical user interface (GUI) for analyzing FASTA files. It allows users to:
- Load a FASTA file and extract gene or organism information.
- Calculate the GC content of each sequence.
- Display the extracted data in a new window.
- Export the results to a TXT file.

The script supports two types of FASTA entries:
1. Entries with metadata in brackets (e.g., gene, protein information).
2. Entries without metadata (assumed to be complete genomes).

Functions:
    calcular_gc(secuencia):
        Calculate the GC content of a DNA sequence.

    leer_archivo_fasta(archivo):
        Parse a FASTA file, extracting gene or organism data and their GC content.

    cargar_archivo():
        Open a dialog to load a FASTA file and process its contents.

    exportar_a_txt():
        Export the processed gene or organism data to a TXT file.

GUI Elements:
    - A button to load a FASTA file and display results.
    - A button to export results to a TXT file.

Usage:
    Run the script to open the GUI. Use the buttons to load a FASTA file and process it.
"""

import tkinter as tk
from tkinter import filedialog, messagebox


# Función para calcular el contenido de GC
def calcular_gc(secuencia):
    """Calculate the GC content of a DNA sequence.

    Args:
        secuencia (str): A string representing the DNA sequence.

    Returns:
        float: The GC content as a percentage of the total sequence length.
    """
    gc_content = (secuencia.count("G") + secuencia.count("C")) / len(secuencia) * 100
    return gc_content


# Función para leer el archivo FASTA, procesar las líneas y extraer la información
def leer_archivo_fasta(archivo):
    """Read a FASTA file to extract gene/s and calculate GC content.

    Args:
        archivo (str): The path to the FASTA file.

    Returns:
        list[dict]: A list of dictionaries containing information about genes or organisms:
            - "Gen": Name of the gene or organism if the file has complete genoma.
            - "Contenido GC": GC content as a percentage.
            - "Funcionalidad Proteína": Description or type (e.g., "proteína" or "genoma completo").
    """
    genes = []
    try:
        with open(archivo, "r") as file:
            lineas = file.readlines()

        i = 0
        while i < len(lineas):
            linea = lineas[i].strip()

            if "[" not in linea:  #Si no tiene corchetes ---> tipo 2
                tipo_entrada = "organismo"
                tipo_info = "genoma completo"
            else:  # si tiene corchetes ---> tipo 1
                tipo_entrada = "gen"
                tipo_info = "proteína"

            if linea.startswith(">"):
                if tipo_entrada == "gen":
                    partes = linea.split("[")
                    nombre_gen = "Desconocido"
                    funcionalidad_proteina = "Desconocida"

                    for gn in partes:
                        if "gene=" in gn:
                            nombre_gen = gn.split("gene=")[-1].split("]")[0]
                        elif "locus_tag=" in gn and nombre_gen == "Desconocido":
                            nombre_gen = gn.split("locus_tag=")[-1].split("]")[0]
                        elif "protein=" in gn:
                            funcionalidad_proteina = gn.split("protein=")[-1].split("]")[0]

                    secuencia = ""
                    i += 1
                    while i < len(lineas) and not lineas[i].startswith(">"):
                        secuencia += lineas[i].strip()
                        i += 1

                    #Se caclula el contenido GC
                    gc_content = calcular_gc(secuencia) if secuencia else 0

                    #Agregamos información en fomrato dict a la lista
                    genes.append({
                        "Gen": nombre_gen,
                        "Contenido GC": round(gc_content, 2),
                        "Funcionalidad Proteína": funcionalidad_proteina
                    })

                # Type 2 entry (without brackets)
                elif tipo_entrada == "organismo":
                    partes = linea.split(" ")
                    nombre_organismo = " ".join(partes[1:3])  # Extract full organism name

                    # Extract associated sequence
                    secuencia = ""
                    i += 1
                    while i < len(lineas) and not lineas[i].startswith(">"):
                        secuencia += lineas[i].strip()
                        i += 1

                    # calcular contenido GC
                    gc_content = calcular_gc(secuencia) if secuencia else 0

                    #Se agrega el diccionario obtenido a la lista
                    genes.append({
                        "Gen": nombre_organismo,
                        "Contenido GC": round(gc_content, 2),
                        "Funcionalidad Proteína": tipo_info
                    })

            else:
                i += 1

        return genes

    except Exception as e:
        messagebox.showerror("Error", f"Error al leer el archivo: {e}")
        return []


#Creamos la ventana principal
ventana = tk.Tk()
ventana.title("Análisis de Genes")

#Variable para almacenar los genes
genes_global = []


#Función que nos abre una ventana para seleccionar el archivo de nuestro interés
def cargar_archivo():
    """Open a file dialog to load a FASTA file and display extracted gene or organism data."""
    archivo = filedialog.askopenfilename(filetypes=[("Archivos FASTA o TXT", "*.fasta *.txt")])
    if archivo:
        genes = leer_archivo_fasta(archivo)
        if genes:
            genes_global.extend(genes)

            ventana_emergente = tk.Toplevel(ventana)
            ventana_emergente.title("Información de Genes")

            text_box = tk.Text(ventana_emergente)
            text_box.pack(pady=100,padx=100)

            encabezado = "{:<20} {:<15} {:<50}\n".format("Gen", "Contenido GC (%)", "Funcionalidad Proteína")
            separador = "-" * 75 + "\n"
            text_box.insert(tk.END, encabezado)
            text_box.insert(tk.END, separador)

            for gen in genes:
                fila = "{:<20} {:<15} {:<50}\n".format(gen["Gen"], gen["Contenido GC"], gen["Funcionalidad Proteína"])
                text_box.insert(tk.END, fila)
        else:
            messagebox.showwarning("Advertencia", "No se encontraron genes válidos en el archivo.")


# Crear un botón para cargar el archivo FASTA
cargar_button = tk.Button(ventana, text="Cargar Archivo FASTA", command=cargar_archivo)
cargar_button.pack(pady=10, padx=100, ipadx=80)


# Función para exportar los resultados a un archivo de texto
def exportar_a_txt():
    """Export the processed gene or organism data to a TXT file."""
    if genes_global:
        archivo = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Archivos de Texto", "*.txt")])
        if archivo:
            try:
                with open(archivo, "w") as f:
                    encabezado = "{:<20} {:<15} {:<50}\n".format("Gen", "Contenido GC (%)", "Funcionalidad Proteína")
                    f.write(encabezado)
                    f.write("-" * 85 + "\n")
                    for gen in genes_global:
                        fila = "{:<20} {:<15} {:<50}\n".format(gen["Gen"], gen["Contenido GC"],
                                                               gen["Funcionalidad Proteína"])
                        f.write(fila)
                messagebox.showinfo("Éxito", f"Archivo guardado en: {archivo}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar el archivo: {e}")
        else:
            messagebox.showwarning("Advertencia", "No se seleccionó un archivo para guardar.")
    else:
        messagebox.showwarning("Advertencia", "No hay datos para exportar.")


# Crear un botón para exportar a TXT
exportar_button = tk.Button(ventana, text="Exportar a TXT", command=exportar_a_txt)
exportar_button.pack(pady=40,ipady=10)

# Ejecutar la interfaz
ventana.mainloop()

