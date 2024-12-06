import cv2
import os

# Caminho para o classificador Haar Cascade
harcascade = "Process/Car-Number-Plates-Detection-main/model/haarcascade_russian_plate_number.xml"

# Caminho para a imagem de entrada (pode alterar para qualquer imagem)
input_image_path = "/Users/franciscocrespo/Desktop/Escola/TAM/AcessControlSystem/Process/Car-Number-Plates-Detection-main/images/plate9.jpg"

# Lê a imagem
img = cv2.imread(input_image_path)

if img is None:
    print("Erro ao carregar a imagem!")
    exit()

# Caminho de saída para salvar as imagens recortadas (diretório relativo)
output_dir = os.path.join(os.path.dirname(__file__), 'plates')

# Cria a pasta de saída, caso não exista
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Definir a área mínima para considerar a detecção
min_area = 500
count = 0

# Carregar o classificador Haar Cascade
plate_cascade = cv2.CascadeClassifier(harcascade)

# Converter a imagem para escala de cinza
img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Detectar as placas na imagem
plates = plate_cascade.detectMultiScale(img_gray, 1.1, 4)

# Para cada placa detectada
for (x, y, w, h) in plates:
    area = w * h
    if area >= min_area:  # Verificar se a área é grande o suficiente
        # Desenhar um retângulo ao redor da placa detectada
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(img, "Number Plate", (x, y - 5), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255, 0, 255), 2)

        # Recortar a imagem da placa
        img_roi = img[y:y + h, x:x + w]

        # Salvar a imagem recortada da placa
        cv2.imwrite(f"{output_dir}/scaned_img_{count}.jpg", img_roi)
        print(f"Placa salva: {output_dir}/scaned_img_{count}.jpg")

        # Mostrar a região da imagem (placa detectada)
        cv2.imshow("ROI", img_roi)

        # Incrementar o contador para o nome da imagem
        count += 1

# Exibir a imagem com as caixas desenhadas
cv2.imshow("Result", img)

# Aguardar até que qualquer tecla seja pressionada
cv2.waitKey(0)
cv2.destroyAllWindows()
