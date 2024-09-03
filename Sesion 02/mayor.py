def numero_mayor_al_cubo():
    numeros = []

    # Pedir 4 números al usuario
    for i in range(4):
        num = float(input(f"Ingrese el número {i + 1}: "))
        numeros.append(num)

    # Encontrar el número mayor
    numero_mayor = max(numeros)

    # Elevar el número mayor al cubo
    resultado = numero_mayor ** 3

    # Mostrar el número mayor
    print(f"El número mayor fue: {numero_mayor}")

    return resultado


# Llamar a la función y mostrar el resultado
print("El número mayor elevado al cubo es:", numero_mayor_al_cubo())
