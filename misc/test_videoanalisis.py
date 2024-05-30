import cv2
import numpy as np

class VideoAnalyzer:
    def __init__(self, video_file):
        self.video_file = video_file
        self.cap = cv2.VideoCapture(video_file)
        self.markers = []
        self.scale = None

    def _mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.markers.append((x, y))
            if len(self.markers) >= 2:
                cv2.setMouseCallback('Video', lambda *args: None)  # Deshabilitar el manejo del mouse

    def select_markers(self):
        cv2.namedWindow('Video')
        cv2.setMouseCallback('Video', self._mouse_callback)

        ret, frame = self.cap.read()
        if not ret:
            print("No se pudo cargar el vídeo.")
            return

        while len(self.markers) < 2:
            frame_copy = frame.copy()
            for marker in self.markers:
                cv2.circle(frame_copy, marker, 5, (0, 255, 0), -1)

            cv2.imshow('Video', frame_copy)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cv2.destroyAllWindows()

    def calculate_scale(self):
        if len(self.markers) < 2:
            print("Se necesitan dos marcadores para calcular la escala.")
            return

        start_marker, end_marker = self.markers

        # Calcular la distancia vertical entre los dos marcadores
        height_px = abs(end_marker[1] - start_marker[1])

        # Solicitar al usuario la altura entre los dos puntos en centímetros
        height_cm = float(input("Por favor, introduce la altura entre los dos puntos en centímetros: "))
        self.scale = height_px / height_cm

        print("La escala (píxeles por centímetro) es:", self.scale)

    def track_movement(self):
        if self.scale is None:
            print("Se necesita establecer la escala antes de realizar el seguimiento.")
            return

        start_marker, end_marker = self.markers
        max_height_px = None  # Almacenar la altura máxima del marcador

        while True:
            ret, frame = self.cap.read()
            if not ret:
                break

            # Dibujar una línea entre los dos marcadores
            cv2.line(frame, start_marker, end_marker, (0, 0, 255), 2)

            # Calcular la posición del marcador
            marker_pos = (start_marker[0], end_marker[1])  # Mantener la misma coordenada x que el marcador inicial

            # Dibujar el marcador en el frame
            cv2.circle(frame, marker_pos, 5, (0, 255, 0), -1)

            # Actualizar la altura máxima del marcador si es necesario
            if max_height_px is None or marker_pos[1] < max_height_px:
                max_height_px = marker_pos[1]

            # Mostrar el frame con el marcador
            cv2.imshow('Video', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Calcular la altura del salto en centímetros utilizando la escala
        jump_height_cm = (start_marker[1] - max_height_px) / self.scale
        print("La altura del salto es:", jump_height_cm, "centímetros")

if __name__ == "__main__":
    analyzer = VideoAnalyzer('video.mp4')
    analyzer.select_markers()
    analyzer.calculate_scale()
    analyzer.track_movement()
