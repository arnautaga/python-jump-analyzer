class Estadistica:
    def __init__(self):
        self.aux = None
    def porcentiles_altura(self, sexo, altura_salto):
        if sexo == "M":
            if altura_salto <= 24.52:
                return (5, 0, 24.52, 24.52 - altura_salto)
            elif altura_salto <= 26.78 and altura_salto > 24.52:
                return (5, 24.52, 26.78, 26.78 - altura_salto)
            elif altura_salto <= 29.96 and altura_salto > 26.78:
                return (25, 26.78, 29.96, 29.96 - altura_salto)
            elif altura_salto <= 33.24 and altura_salto > 29.96:
                return (50, 29.96, 33.24, 33.24 - altura_salto)
            elif altura_salto <= 36.90 and altura_salto > 33.24:
                return (75, 33.24, 36.90, 36.90 - altura_salto)
            elif altura_salto <= 41.19 and altura_salto > 36.9:
                return (90, 41.19, 36.9, 41.19 - altura_salto)
            elif altura_salto <=43.49 and altura_salto > 41.19:
                return (95, 43.49, 41.19, 43.49 - altura_salto)
            elif altura_salto <= 70 and altura_salto > 43.49:
                return 100
            else:
                raise Exception("Errno6. Altura invalida, revise unidades. Unidad esperada cm")
        elif sexo == "F":
            if altura_salto <= 18:
                return (5, 0, 18, 18 - altura_salto)
            elif altura_salto <= 20.11 and altura_salto > 18:
                return (5, 18, 20.11, 20.11 - altura_salto)
            elif altura_salto <= 21.79 and altura_salto > 20.11:
                return (25, 20.11, 21.79, 21.79 - altura_salto)
            elif altura_salto <= 24.62 and altura_salto > 21.79:
                return (50, 21.79, 24.62, 24.62 - altura_salto)
            elif altura_salto <= 26.89 and altura_salto > 24.62:
                return (75, 24.62, 26.89, 26.89 - altura_salto)
            elif altura_salto <= 30.35 and altura_salto > 26.89:
                return (90, 30.35, 26.89, 30.35 - altura_salto)
            elif altura_salto <= 32.78 and altura_salto > 30.35:
                return (95, 32.78, 30.35, 32.78 - altura_salto)
            elif altura_salto <= 65 and altura_salto > 32.78:
                return 100
            else:
                raise Exception("Errno6. Altura invalida, revise unidades. Unidad esperada cm")
        else:
            raise ValueError("Errno7. Sexo debe ser M para masculino o F para femenino")