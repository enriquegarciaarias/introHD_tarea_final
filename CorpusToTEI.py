#!/usr/bin/env python
# -*- coding: utf-8 -*-
#   IntroHD Corpus Tarea Final
#   Procesar corpus para TEI
# ---------------------------------------------------------------------------------
import re
import sys
import os
import datetime

fi_titles = "Work/jauregui_titulos.txt"  # "fichero de entrada"
fi_headers = 'Work/tei_headers.txt'
foa = "Resultados/jauregui_tei.txt"  # "fichero de salida" con el resultado
fob = "Resultados/jauregui_rimas.txt"  # "fichero de salida" con el resultado
cod = "utf_8"
directorio = "Sonetos"


#
# ---------------------------------------------------------------------------------
# Descripción	: Asigna los títulos de los Sonetos
# Parámetros	: Fichero de trabajo con títulos y nombre de archivo relacionado
# Retorno 		: lista con títulos y archivos, número de archivos
# ---------------------------------------------------------------------------------
def proc_title_file(fit):
    result = []
    i = 0
    with open(fit, "r") as fti:
        for line in fti:
            pattern = r"^<file>([^\<]+)\<\/file\><title>([^\<]+)<\/title\>$"
            match = re.search(pattern, line)
            if match is not None:
                result.append({"file": match.group(1) + ".txt", "title": match.group(2)})
                i += 1
    return result, i

#
# ---------------------------------------------------------------------------------
# Descripción	: Compone cada línea del fichero de salida y extrae la rima
# Parámetros	: Línea soneto leida
# Retorno 		: Línea con el formato requerido, palabra rima
# ---------------------------------------------------------------------------------
def proc_line(d):
    a = proc_regex(d)
    if not a:
        return False
    try:
        ap = str(a.group(3))
    except:
        pass
    if ap == "None":
        ap = ""
    nueva_linea = "<l>" + str(a.group(1)) + '<w type="rhyme">' + str(a.group(2)) + "</w>" + ap + "</l>"
    return nueva_linea, a.group(2)

#
# ---------------------------------------------------------------------------------
# Descripción	: Procesa cada fichero soneto
# Parámetros	: path al fichero
# Retorno 		: Lineas con el nuevo formato, rimas
# ---------------------------------------------------------------------------------
def proceso_file(file_path):
    ls = []
    fs = []
    nuevo_lg = True
    end_lg = False
    with open(file_path, "r") as fis:
        while True:
            linea = fis.readline()
            if not linea:
                ls.append('</div>')
                break
            if re.search("[a-z]", linea):
                if nuevo_lg:
                    ls.append('<lg>')
                    nuevo_lg = False
                    end_lg = False
                line_line, line_last = proc_line(linea)
                if line_line:
                    ls.append(line_line)
                    fs.append(line_last)
            else:  # la línea está en blanco
                if end_lg:  # pueden haber varias líneas en blanco
                    continue
                ls.append("</lg>")
                nuevo_lg = True
                end_lg = True
    #                    print(linea)
    return ls, fs

#
# ---------------------------------------------------------------------------------
# Descripción	: Procesa todos los sonetos
# Parámetros	: lista de títulos y ficheros, path a los ficheros
# Retorno 		: lista TEI y lista rimas
# ---------------------------------------------------------------------------------
def proc_sonetos(tit, path):
    result = []
    ultim = []
    tei_file = []
    last_file = []
    for dato in tit:
        file_path = path + '/' + dato["file"]
        if os.path.isfile(file_path):
            result.append('<div>')
            result.append('<head>' + dato["title"] + '</head>')
            tei_file, last_file = proceso_file(file_path)
        result.extend(tei_file)
        ultim.extend(last_file)

    result.append('</body>')
    result.append('</text>')
    result.append('</TEI>')
    return {'result': result, 'last': ultim}

#
# ---------------------------------------------------------------------------------
# Descripción	: Identificay separa las palabras "rima"
# Parámetros	: linea de texto soneto
# Retorno 		: textos separados
# ---------------------------------------------------------------------------------
def proc_regex(d):
    d = re.sub(r"\r?\n?", "", d)  # reemplaza carriage return y line feed
    d = re.sub("^[ ]+|[ ]+$", "", d)  # reemplaza espacios al inicio y al final
    pattern = r"^(.*)\b(\w+)([^\w]+)?$"  # localiza la última palabra
    match = re.search(pattern, d)
    return match

#
# ---------------------------------------------------------------------------------
# Descripción	: Personalización los headers TEI
# Parámetros	: linea de texto soneto
# Retorno 		: lista con las sustituciones a realizas
# ---------------------------------------------------------------------------------
def fill_teihead(fh):
    ct = datetime.datetime.now().isoformat()
    custom = [[r"\<title\>\*\*\<", "Sonetos"],
            [r"\<author\>\*\*\<", "Jáuregui, Juan de"],
            [r"\<date\>\*\*\<", ct],
            [r"\<sourceDesc\>\*\*\<",
             '<p>Jáuregui, Juan de. <title>Poesía</title>. Ed. De Juan Matas Caballero. Madrid: Cátedra, 1993. Impreso.</p>']]
    with open(fh, 'r') as h:
        ls = h.readlines()
    headers = []
    for li in ls:
        for c in custom:
            if re.search(c[0], li):
                li = re.sub(r"\*\*", c[1], li)
        headers.append(li)
    return headers

#
# ---------------------------------------------------------------------------------
# Descripción	: Grabación en los ficheros de salida
# Parámetros	: lineas, fichero salida TEI, fichero salida rimas
# Retorno 		: líneas grabadas
# ---------------------------------------------------------------------------------
def write_results(src, fa, fb):
    ib = 0
    with open(fb, 'w') as f:
        for d in src['last']:
            f.write(d + '\n')
            ib += 1
    ia = 0
    custom = fill_teihead(fi_headers)
    with open(fa, 'w') as f:
        for li in custom:
            f.write(li)
            ia += 1
        for d in src['result']:
            f.write(d + '\n')
            ia += 1
    return ia, ib


# ***************************************************************************************************
# Lógica principal
print()
print("\tUNED",
      "\tTratamiento del corpus",
      "\t________________________________________________",
      sep="\n")
titles, files = proc_title_file(fi_titles)
tei = proc_sonetos(titles, directorio)
inda, indb = write_results(tei, foa, fob)

print("\t________________________________________________",
      "\tProceso ha finalizado ",
      "\tSonetos: " + str(files),
      "\tRegistros TEI: " + str(inda),
      "\tRegistros rima: " + str(indb),
      sep="\n")
