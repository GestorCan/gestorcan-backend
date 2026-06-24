LETRAS_DNI = "TRWAGMYFPDXBNJZSQVHLCKE"

def generar_dni(numero):
    numero = str(numero).zfill(8)
    letra = LETRAS_DNI[int(numero) % 23]
    return f"{numero}{letra}"

print(generar_dni("65255874"
                
                  ""))
