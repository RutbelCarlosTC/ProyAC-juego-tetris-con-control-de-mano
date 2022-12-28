import pygame
import cv2
import mediapipe as mp
import os
import random

#mediapipe: preprando Manos
mpHands = mp.solutions.hands
hands = mpHands.Hands()
mpDraw = mp.solutions.drawing_utils

#Capturar cámara web
cam = cv2.VideoCapture(0)

#Preparar la posición de la ventana de pygame, las fuentes y la música de fondo
os.environ['SDL_VIDEO_WINDOW_POS'] ="560,30"
pygame.font.init()


#Variables globales
s_ancho = 800
s_alto = 690
juego_ancho = 300  
juego_alto = 600  

bloque_tam = 30
top_izq_x = (s_ancho - juego_ancho) // 2
top_der_y = s_alto - juego_alto - 10

#formas con todas las rotaciones posibles
S = [['.....',
      '.....',
      '..00.',
      '.00..',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '...0.',
      '.....']]

Z = [['.....',
      '.....',
      '.00..',
      '..00.',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '.0...',
      '.....']]

I = [['..0..',
      '..0..',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '0000.',
      '.....',
      '.....',
      '.....']]

O = [['.....',
      '.....',
      '.00..',
      '.00..',
      '.....']]

J = [['.....',
      '.0...',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..00.',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '...0.',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '.00..',
      '.....']]

L = [['.....',
      '...0.',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '..00.',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '.0...',
      '.....'],
     ['.....',
      '.00..',
      '..0..',
      '..0..',
      '.....']]

T = [['.....',
      '..0..',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '..0..',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '..0..',
      '.....']]

#indice 0-6 da una forma y sus colore correspondientes
formas = [S, Z, I, O, J, L, T]
formas_colores = [(0, 230, 115), (255, 51, 51), (0, 204, 255), (255, 255, 128), (0, 102, 255), (255, 140, 26), (204, 51, 255)]

#Clase para las Formas
class Pieza(object):  
    def __init__(self, x, y, forma):
        self.x = x
        self.y = y
        self.shape = forma
        self.color = formas_colores[formas.index(forma)]
        self.rotation = 0

#crear la cuadricula
def create_grid(pos_bloqueada={}):  # *
    cuadricula = [[(0,0,0) for _ in range(10)] for _ in range(20)]

    for i in range(len(cuadricula)):
        for j in range(len(cuadricula[i])):
            if (j, i) in pos_bloqueada:
                c = pos_bloqueada[(j,i)]
                cuadricula[i][j] = c
    return cuadricula

#convertir las formas en sus posiciones
def convertir_forma_pos(forma):
    posiciones = []
    format = forma.shape[forma.rotation % len(forma.shape)]

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                posiciones.append((forma.x + j, forma.y + i))

    for i, pos in enumerate(posiciones):
        posiciones[i] = (pos[0] - 2, pos[1] - 4)

    return posiciones

#probar si la forma que cae está o no en un espacio válido
def validar_espacio(forma, grid):
    accepted_pos = [[(j, i) for j in range(10) if grid[i][j] == (0,0,0)] for i in range(20)]
    accepted_pos = [j for sub in accepted_pos for j in sub]

    formatted = convertir_forma_pos(forma)

    for pos in formatted:
        if pos not in accepted_pos:
            if pos[1] > -1:
                return False
    return True

#check si el usuario ha perdido o no
def check_perdio(positions):
    for pos in positions:
        x, y = pos
        if y < 1:
            return True

    return False

#obtener una forma aleatoria
def get_forma():
    return Pieza(5, 0, random.choice(formas))

#poner un texto en el medio de la pantalla
def dibujar_texto_medio(superficie, text, size, color):
    font = pygame.font.SysFont("britannic", size, bold=True)
    label = font.render(text, 1, color)

    superficie.blit(label, (top_izq_x + juego_ancho /2 - (label.get_width()/2), top_der_y + juego_alto/2 - label.get_height()/2))

#dibuja las líneas en la cuadrícula
def dibujar_cuadricula(superficie, grid):
    sx = top_izq_x
    sy = top_der_y

    for i in range(len(grid)):
        pygame.draw.line(superficie, (128,128,128), (sx, sy + i*bloque_tam), (sx+juego_ancho, sy+ i*bloque_tam))
        for j in range(len(grid[i])):
            pygame.draw.line(superficie, (128, 128, 128), (sx + j*bloque_tam, sy),(sx + j*bloque_tam, sy + juego_alto))

#borrar una fila
def borrrar_filas(cuadricula, bloqueado):

    inc = 0
    for i in range(len(cuadricula)-1, -1, -1):
        fila = cuadricula[i]
        if (0,0,0) not in fila:
            inc += 1
            ind = i
            for j in range(len(fila)):
                try:
                    del bloqueado[(j,i)]
                except:
                    continue

    if inc > 0:
        for key in sorted(list(bloqueado), key=lambda x: x[1])[::-1]:
            x, y = key
            if y < ind:
                newKey = (x, y + inc)
                bloqueado[newKey] = bloqueado.pop(key)

    return inc

#dibuja la ventana que muestra la siguiente forma
def dibujar_sgte_forma(shape, superficie):
    font = pygame.font.SysFont('britannic', 30)
    label = font.render('Sgte Figura:', 1, (255,255,255))

    sx = top_izq_x + juego_ancho + 50
    sy = top_der_y + juego_alto/2 - 100
    format = shape.shape[shape.rotation % len(shape.shape)]

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                pygame.draw.rect(superficie, shape.color, (sx + j*bloque_tam, sy + i*bloque_tam, bloque_tam, bloque_tam), 0)

    superficie.blit(label, (sx + 10, sy - 40))

#dibujar la ventana principal
def dibujar_ventana(superficie, grid, score=0):
    superficie.fill((0, 0, 0))

    pygame.font.init()
    font = pygame.font.SysFont('britannic', 60)
    label = font.render('TETRIS', 1, (255, 255, 255))

    superficie.blit(label, (top_izq_x + juego_ancho / 2 - (label.get_width() / 2), 15))

    #mostrar puntaje actual
    font = pygame.font.SysFont('britannic', 30)
    label = font.render('Puntaje: ' + str(score), 1, (255,255,255))

    sx = top_izq_x + juego_ancho + 50
    sy = top_der_y + juego_alto/2 - 100

    superficie.blit(label, (sx + 20, sy + 160))

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            pygame.draw.rect(superficie, grid[i][j], (top_izq_x + j*bloque_tam, top_der_y + i*bloque_tam, bloque_tam, bloque_tam), 0)

    pygame.draw.rect(superficie, (215, 215, 215), (top_izq_x, top_der_y, juego_ancho, juego_alto), 5)

    dibujar_cuadricula(superficie, grid)

#agregue puntajes que correspondan a la cantidad de filas borradas
def add_puntaje(rows):
    conversion = {
        0: 0,
        1: 40,
        2: 100,
        3: 300,
        4: 1200
    }
    return conversion.get(rows)

#LA FUNCIÓN PRINCIPAL QUE EJECUTA EL JUEGO
def main(win):
    posic_bloqueadas = {}
    cuadricula = create_grid(posic_bloqueadas)

    cambio_pieza = False
    run = True
    actual_pieza = get_forma()
    sgte_pieza = get_forma()
    reloj = pygame.time.Clock()
    tiempo_caida = 0
    velocidad_caida_real = 0.45
    velocidad_caida = velocidad_caida_real
    level_time = 0
    puntaje = 0

    fotogramas_izq = 0
    fotogramas_der = 0
    fotogramas_rotac = 0
    fotogramas_abaj = 0
    fotogramas_arrib = 0.1

    #bucle principal
    while run:
        cuadricula = create_grid(posic_bloqueadas)

        tiempo_caida += reloj.get_rawtime()
        level_time += reloj.get_rawtime()
        reloj.tick()

        #Configurar el rastreador de manos
        success, img = cam.read()
        imgg = cv2.flip(img, 1)
        imgRGB = cv2.cvtColor(imgg, cv2.COLOR_BGR2RGB)
        results = hands.process(imgRGB)

        if results.multi_hand_landmarks:
            for handLms in results.multi_hand_landmarks:
                for id, lm in enumerate(handLms.landmark):
                    h, w, c = imgg.shape
                    if id == 0:
                        x = []
                        y = []
                    x.append(int((lm.x) * w))
                    y.append(int((1 - lm.y) * h))

                   #Esto rastreará los gestos de las manos
                    if len(y) > 20:
                        if (x[0] > x[3] > x[4]) and not(y[20] > y[17]):
                           fotogramas_izq += 1
                        if not(x[0] > x[3] > x[4]) and (y[20] > y[17]):
                            fotogramas_der += 1
                        if (x[0] > x[3] > x[4]) and (y[20] > y[17]):
                            fotogramas_rotac += 1


                mpDraw.draw_landmarks(imgg, handLms, mpHands.HAND_CONNECTIONS)

        else:
            fotogramas_abaj += 1

        cv2.namedWindow("WebCam")
        cv2.moveWindow("WebCam", 20, 121)
        cv2.imshow("WebCam", imgg)
        cv2.waitKey(1)

       #cada 10 segundos, las formas se mueven 0,03 segundos más rápido (máximo en 0,25)
        if level_time/1000 > 10:
            level_time = 0
            if velocidad_caida_real > 0.25:
                velocidad_caida_real -= 0.03

       #si ha pasado suficiente tiempo (velocidad de caída), la pieza se mueve hacia abajo 1 bloque
        if tiempo_caida/1000 > velocidad_caida:
            tiempo_caida = 0
            actual_pieza.y += 1
            if not(validar_espacio(actual_pieza, cuadricula)) and actual_pieza.y > 0:
                actual_pieza.y -= 1
                cambio_pieza = True

       #"si hace un gesto hacia la IZQUIERDA durante al menos 4 fotogramas, la pieza se mueve hacia la IZQUIERDA"
        if fotogramas_izq >= 4:
            actual_pieza.x -= 1
            if not (validar_espacio(actual_pieza, cuadricula)):
                actual_pieza.x += 1
            fotogramas_izq = 0
            fotogramas_der = 0
            fotogramas_rotac = 0
            fotogramas_abaj = 0

       #"si gesticula hacia la DERECHA durante al menos 4 fotogramas, la pieza se mueve hacia la DERECHA"
        if fotogramas_der >= 4:
            actual_pieza.x += 1
            if not (validar_espacio(actual_pieza, cuadricula)):
                actual_pieza.x -= 1
            fotogramas_izq = 0
            fotogramas_der = 0
            fotogramas_rotac = 0
            fotogramas_abaj = 0

        #"si gesticula para GIRAR durante al menos 4 fotogramas, la pieza GIRAR"
        if fotogramas_rotac >= 4:
            actual_pieza.rotation += 1
            if not (validar_espacio(actual_pieza, cuadricula)):
                actual_pieza.rotation -= 1
            fotogramas_izq = 0
            fotogramas_der = 0
            fotogramas_rotac = 0
            fotogramas_abaj = 0

        #"si hace un gesto para ABAJO (sin mano en la pantalla) durante al menos 5 fotogramas, la pieza ABAJO (se mueve muy rápido)"
        if fotogramas_abaj >= 5:
            velocidad_caida = fotogramas_arrib
            fotogramas_izq = 0
            fotogramas_der = 0
            fotogramas_rotac = 0
            fotogramas_abaj = 0

        figura_pos = convertir_forma_pos(actual_pieza)

        #colorea la cuadrícula donde está la forma
        for i in range(len(figura_pos)):
            x, y = figura_pos[i]
            if y > -1:
                cuadricula[y][x] = actual_pieza.color

        if cambio_pieza:
            for pos in figura_pos:
                p = (pos[0], pos[1])
                posic_bloqueadas[p] = actual_pieza.color
            actual_pieza = sgte_pieza
            sgte_pieza = get_forma()
            cambio_pieza = False
            puntaje += add_puntaje(borrrar_filas(cuadricula, posic_bloqueadas))
            velocidad_caida = velocidad_caida_real
            fotogramas_abaj = 0

        dibujar_ventana(win, cuadricula, puntaje)
        dibujar_sgte_forma(sgte_pieza, win)
        pygame.display.update()

        if check_perdio(posic_bloqueadas):
            dibujar_texto_medio(win, "Perdiste!", 70, (255,255,255))
            pygame.display.update()
            pygame.time.delay(1500)
            run = False

#Pantalla de menú que llevará a la función principal
def main_menu(win):
    run = True
    while run:
        win.fill((0,0,0))
        dibujar_texto_medio(win, 'Presione cualquier tecla para comenzar', 50, (255,255,255))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                main(win)
                
    pygame.display.quit()

win = pygame.display.set_mode((s_ancho, s_alto))
pygame.display.set_caption('TETRIS')
main_menu(win)
