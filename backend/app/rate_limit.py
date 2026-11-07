"""Presupuesto de consultas por proceso; compartido por las tres rutas del chat."""
from collections import deque
from math import ceil
from threading import Lock
from time import monotonic
from app.parametros import PARAMETROS


class LimiteConsultas:
    def __init__(self, max_solicitudes, ventana_segundos, reloj=monotonic):
        if type(max_solicitudes) is not int or max_solicitudes < 1 or ventana_segundos <= 0:
            raise ValueError('El límite y la ventana deben ser positivos')
        self.max_solicitudes = max_solicitudes
        self.ventana_segundos = ventana_segundos
        self.reloj = reloj
        self.eventos = deque()
        self.lock = Lock()

    def admitir(self):
        with self.lock:
            ahora = self.reloj()
            while self.eventos and self.eventos[0] <= ahora - self.ventana_segundos:
                self.eventos.popleft()
            if len(self.eventos) >= self.max_solicitudes:
                return max(1, ceil(self.eventos[0] + self.ventana_segundos - ahora))
            self.eventos.append(ahora)
            return None


limite_chat = LimiteConsultas(**PARAMETROS['chat_rate_limit'])
