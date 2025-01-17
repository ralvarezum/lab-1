import argparse, sys, os, array
from os.path import getsize
import concurrent.futures

# Excepciones en caso de algun error.

class InvalidHeaderError(Exception):
    def __init__(self, message):
        print(message)

class FileNotFoundError(Exception):
    def __init__(self, message):
        print(message)

class InvalidNumber(Exception):
    def __init__(self,message):
        print(message)

# Trabajamos con la imagen para obtener el header y el body.

def parse_file(image,size):
    img_body =[]
    global header
    global body

    for iterador in range (int(getsize(image)/size)):
        img_body.append(os.read(image,size))
    img_body.append(os.read(image,(getsize(image)%size)))
    img_body = b''.join(img_body)

# Saltar comentarios.

    for i in range(img_body.count(b"\n# ")):
        comm1 = img_body.find(b"\n# ")
        comm2 = img_body.find(b"\n", comm1 + 1)
        img_body = img_body.replace(img_body[comm1:comm2], b"")

    header_finder = img_body.find(b"\n", img_body.find(b"\n", img_body.find(b"\n") +1) +1) +1
    header = img_body[:header_finder].decode() 
    body = img_body[header_finder:]
    data = [i for i in body] #lista-data
    return data

# Obtengo el ancho y alto de la imagen. Para luego trabajar con columnas y filas.

def width_and_height_img():
    row_and_column = (list(header.split('\n')))[1].split(' ')
    width = int(row_and_column[0])
    height = int(row_and_column[1])
    return width , height

# Creo una lista de listas por pixeles [[1,2,3].[1,2,3],[1,2,3]...]

def list_of_list(data,column):
    index = 0
    list_of_list = []
    list_x3 = []

    while index < (len(data)-2):
        list_of_list.append(data[index:index+3])
        index +=3
    
    for fila in range(0,(len(list_of_list)-1),column):
        list_x3.append(list_of_list[fila:fila+column])

    return list_x3

# Invierto la lista_x3

def invert_list(list_x3):
    list_inverted = []

    for fila in range (len(list_x3)):
        for column in range ((len(list_x3[fila])-1),-1,-1):
            list_inverted.append(list_x3[fila][column])

    return list_inverted

# Un hilo va cada color. Busca el valor rgb que lleva y lo pone como indice en la lista.

def create_one_list(list_inverted,channel_type):
    flat_list = []
    
    for filas in list_inverted:
            if channel_type == 0: #RED
                flat_list.append(filas[channel_type])
            elif channel_type == 1: #GREEN
                flat_list.append(filas[channel_type])
            elif channel_type == 2: #BLUE
                flat_list.append(filas[channel_type])
    return flat_list

# Finalmente, a partir de lo anterior, se crea una ultima lista para poder escribir la imagen.

def final_list(data,red_list,green_list,blue_list):
    complete_list = []
    count = 0
    while (len(complete_list)) != (len(data)-1):
        complete_list.append(red_list[count])
        complete_list.append(green_list[count])
        complete_list.append(blue_list[count])
        count += 1
    return complete_list

# En esta funcion re-construimos la imagen.

def write_img(list_inverted,namefile):

    archivo= array.array('B',list_inverted)

    with open(f'{namefile}_mirror.ppm', 'wb') as f:
        f.write(bytearray(header, 'ASCII'))
        archivo.tofile(f)
    
    print(f"Imagen espejada: {namefile}_mirror.ppm creada correctamente")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(usage="\ntp2.py [-h] [-s SIZE] [-f FILE]")
    parser.add_argument('-s', '--size', metavar='SIZE', type=int, default=1024, help="Bloque de lectura")
    parser.add_argument('-f', '--file', metavar='FILE', type=str, help="Archivo a procesar (.ppm)")
    args = parser.parse_args()  
    file = args.file
    size = args.size

    if not file.endswith(".ppm"):
        raise InvalidHeaderError('Not a ppm file!')
        
    if not file:
        raise FileNotFoundError('Path does not point to a regular file!')

    if (type(size) !=  int) or (size < 0):
        raise InvalidNumber('File is blank or invalid number')

    try:
        image= os.open(file, os.O_RDONLY)
        namefile = file.replace('.ppm','')

    except FileNotFoundError:
        print('No such file or directory: ' + file + ' ')
        sys.exit()

    data = parse_file(image,size)
    os.close(image)
    column, row = width_and_height_img()
    list_of_list_pix3 = list_of_list(data,column)
    list_inverted = invert_list(list_of_list_pix3)

    # concurrent.futures

    with concurrent.futures.ThreadPoolExecutor() as executor:
        f_red = executor.submit(create_one_list,list_inverted,0)
        f_green = executor.submit(create_one_list,list_inverted,1)
        f_blue = executor.submit(create_one_list,list_inverted,2)

        red_list = f_red.result()
        green_list = f_green.result() 
        blue_list = f_blue.result()
    complete_list = final_list(data,red_list,green_list,blue_list)

    write_img(complete_list,namefile)
    print('Terminado...')