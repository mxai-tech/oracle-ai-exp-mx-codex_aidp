#!/usr/bin/env python3
"""Verifica el CSV de referencia del taller sin acceder a OCI ni AIDP."""

import argparse
import csv
import sys
from collections import Counter, defaultdict
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path


COLUMNAS = [
    "Código",
    "Nombre del cliente",
    "Empresa",
    "Correo electrónico",
    "Teléfono",
    "Estado",
    "Tiempo en negociación (días, ficticio)",
    "Cantidad de contactos realizados (ficticio)",
    "Días desde el último contacto (ficticio)",
    "Valor de la propuesta (BRL, ficticio)",
    "Se volvió activo en 30 días (ficticio)",
]

STATUS = {
    "activo": "Activo",
    "inactivo": "Inactivo",
    "inactvo": "Inactivo",
    "en negociación": "En negociación",
    "en negociacion": "En negociación",
    "": "No informado",
    "n/a": "No informado",
}


def comprobar(descripcion, obtenido, esperado):
    """También falla cuando Python se ejecuta con -O, que deshabilita assert."""
    if obtenido != esperado:
        raise ValueError(
            f"{descripcion}: se esperaba {esperado!r}, se encontró {obtenido!r}."
        )


def moneda(valor):
    partes = f"{valor:,.2f}".split(".")
    return "BRL " + partes[0] + "." + partes[1]


def verificar(ruta):
    with ruta.open(encoding="utf-8-sig", newline="") as archivo:
        lector = csv.reader(archivo, delimiter=",")
        encabezado = next(lector, None)
        comprobar("Nombres y orden de las 11 columnas", encabezado, COLUMNAS)
        filas = []
        for numero, valores in enumerate(lector, start=2):
            comprobar(f"Número de campos en el registro {numero}", len(valores), 11)
            # csv.reader conserva todos los campos como texto, incluidos "001" y "".
            filas.append(tuple(valores))

    comprobar("Registros de origen", len(filas), 100)
    frecuencias = Counter(filas)
    distintos = list(frecuencias)
    comprobar("Contenidos distintos en los 11 campos originales", len(distintos), 95)
    excedentes = sum(cantidad - 1 for cantidad in frecuencias.values())
    comprobar("Copias idénticas excedentes", excedentes, 5)
    registros = [dict(zip(COLUMNAS, valores)) for valores in distintos]

    por_codigo = defaultdict(list)
    for registro in registros:
        codigo = registro["Código"]
        if codigo.strip():
            por_codigo[codigo].append(registro)
    colisiones = {codigo: grupo for codigo, grupo in por_codigo.items() if len(grupo) > 1}
    comprobar("Códigos en colisión", sorted(colisiones), ["018", "037", "094"])
    comprobar("Registros distintos en las colisiones", sum(map(len, colisiones.values())), 6)

    por_estado = Counter()
    por_resultado = Counter()
    por_empresa = defaultdict(Decimal)
    for registro in registros:
        estado_original = registro["Estado"].strip().lower()
        if estado_original not in STATUS:
            raise ValueError(f"Estado sin regla de normalización: {registro['Estado']!r}.")
        por_estado[STATUS[estado_original]] += 1
        por_resultado[registro[COLUMNAS[-1]].strip()] += 1
        empresa = registro["Empresa"].strip() or "No informado"
        valor = Decimal(registro[COLUMNAS[-2]].strip())
        if not valor.is_finite():
            raise ValueError("El valor de la propuesta debe ser un número finito.")
        por_empresa[empresa] += valor

    comprobar(
        "Estado después de normalizar",
        dict(por_estado),
        {"Activo": 38, "Inactivo": 24, "En negociación": 20, "No informado": 13},
    )
    comprobar(
        "Resultados a 30 días",
        dict(por_resultado),
        {"Sí": 27, "No": 30, "No aplica": 38},
    )
    numerador = por_resultado["Sí"]
    denominador = numerador + por_resultado["No"]
    comprobar("Numerador de conversión", numerador, 27)
    comprobar("Denominador de conversión", denominador, 57)
    porcentaje = (Decimal(numerador) / Decimal(denominador) * 100).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    comprobar("Conversión redondeada (%)", porcentaje, Decimal("47.37"))
    total = sum(por_empresa.values(), Decimal(0))
    comprobar("Importe total ficticio de propuestas", total, Decimal("3132500"))
    mayor_importe = max(por_empresa.values())
    lideres = sorted(empresa for empresa, valor in por_empresa.items() if valor == mayor_importe)
    comprobar("Empresa con mayor importe ficticio de propuestas", lideres, ["Sol Nascente"])
    comprobar("Importe ficticio de propuestas de la empresa líder", mayor_importe, Decimal("362000"))

    print(f"Archivo: {ruta.resolve()}")
    print("VALIDACIÓN LOCAL COMPLETADA")
    print("Origen: 100 registros, 11 columnas y 95 contenidos distintos.")
    print("Deduplicación: 5 copias idénticas excedentes; referencia de plata: 95 registros.")
    print("Colisiones: 018, 037 y 094; 6 registros distintos conservados.")
    print("Estado: Activo 38; Inactivo 24; En negociación 20; No informado 13.")
    print("Resultado: Sí 27; No 30; No aplica 38.")
    print("Conversión: 27 / 57 = 47.37%.")
    print(f"Propuestas ficticias: total {moneda(total)}.")
    print(f"Mayor importe ficticio por empresa: Sol Nascente, {moneda(mayor_importe)}.")
    print("Esta verificación solo lee el CSV local. No comprueba la ejecución en AIDP.")


def main():
    raiz = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(
        description="Valida los resultados de referencia del CSV del taller sin dependencias externas."
    )
    parser.add_argument(
        "csv", nargs="?", type=Path, default=raiz / "clientes.csv",
        help="CSV opcional. El valor predeterminado es clientes.csv en la raíz del repositorio.",
    )
    argumentos = parser.parse_args()
    try:
        verificar(argumentos.csv)
    except (OSError, UnicodeError, csv.Error, ValueError, InvalidOperation) as error:
        print(f"ERROR DE VALIDACIÓN: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
