class Carro:
    ruedas = 4
    def __init__(self,color,aceleración):
        self.color = color
        self.aceleración = aceleración
        self.velocidad = 0

    """
    Métodos con las funciones de clase
    """
    def acelerar(self):
        self.velocidad = self.velocidad + self.aceleración

    def frenar(self,frenos):
        velocidad = self.velocidad - frenos
        if velocidad < 0:
            velocidad = 0
        self.velocidad = velocidad
carro01 = Carro("Negro",50)
carro01.acelerar()
print("La velocidad inicial es de: {}".format(carro01.velocidad),"Km/H")
carro01.frenar(30)
print("Al frenar, la velocidad del auto es: {}".format(carro01.velocidad),"Km/H")
carro01.frenar(50)
print("Al frenar, la velocidad del auto es: {}".format(carro01.velocidad),"Km/H")