import re


LETRAS_NIF = "TRWAGMYFPDXBNJZSQVHLCKE"


def limpiar_documento_fiscal(valor: str) -> str:
    if not valor:
        return ""

    return (
        valor
        .upper()
        .replace(" ", "")
        .replace("-", "")
        .replace(".", "")
    )


def validar_nif_nie(valor: str) -> bool:
    doc = limpiar_documento_fiscal(valor)

    # DNI/NIF: 8 números + letra
    if re.fullmatch(r"\d{8}[A-Z]", doc):
        numero = int(doc[:8])
        letra = doc[-1]
        return letra == LETRAS_NIF[numero % 23]

    # NIE: X/Y/Z + 7 números + letra
    if re.fullmatch(r"[XYZ]\d{7}[A-Z]", doc):
        conversion = {
            "X": "0",
            "Y": "1",
            "Z": "2"
        }

        numero = int(
            conversion[doc[0]] + doc[1:8]
        )

        letra = doc[-1]
        return letra == LETRAS_NIF[numero % 23]

    # CIF empresa/sociedad: validación básica de formato
    if re.fullmatch(r"[ABCDEFGHJKLMNPQRSUVW]\d{7}[0-9A-J]", doc):
        return True

    return False