from __future__ import annotations

import argparse
import io
import re
from pathlib import Path

from PIL import Image, ImageColor, ImageOps
from rembg import new_session, remove


EXTENSIONES = {".jpg", ".jpeg", ".png", ".webp"}


def clave_nombre(archivo: Path) -> list[object]:
    """Ordena nombres con numeros de forma natural: foto (2) antes de foto (10)."""
    partes = re.split(r"(\d+)", archivo.stem.casefold())
    return [int(parte) if parte.isdigit() else parte for parte in partes]


def quitar_fondo(imagen: Image.Image, sesion) -> Image.Image:
    """Devuelve la imagen recortada con canal alfa."""
    imagen = ImageOps.exif_transpose(imagen).convert("RGBA")
    resultado = remove(imagen, session=sesion)
    if isinstance(resultado, Image.Image):
        return resultado.convert("RGBA")
    return Image.open(io.BytesIO(resultado)).convert("RGBA")


def colocar_en_lienzo(producto: Image.Image, tamano: int, margen: float) -> Image.Image:
    """Centra el producto y deja un margen uniforme para una foto de catálogo."""
    caja = producto.getbbox()
    if caja is None:
        raise ValueError("no se detecto ningun objeto")

    producto = producto.crop(caja)
    limite = max(1, int(tamano * (1 - margen * 2)))
    escala = min(limite / producto.width, limite / producto.height)
    nuevo_tamano = (
        max(1, round(producto.width * escala)),
        max(1, round(producto.height * escala)),
    )
    producto = producto.resize(nuevo_tamano, Image.Resampling.LANCZOS)

    lienzo = Image.new("RGBA", (tamano, tamano), (255, 255, 255, 0))
    posicion = (
        (tamano - producto.width) // 2,
        (tamano - producto.height) // 2,
    )
    lienzo.alpha_composite(producto, posicion)
    return lienzo


def guardar(imagen: Image.Image, destino: Path, fondo: str) -> None:
    extension = ".png" if fondo == "transparente" else ".jpg"
    archivo_salida = destino.parent / f"{destino.name}{extension}"
    if fondo != "transparente":
        colores = {"blanco": "white", "gris": "#D9D9D9"}
        color = ImageColor.getrgb(colores.get(fondo, fondo))
        lienzo = Image.new("RGB", imagen.size, color)
        lienzo.paste(imagen, mask=imagen.getchannel("A"))
        lienzo.save(archivo_salida, quality=95, optimize=True)
    else:
        imagen.save(archivo_salida, optimize=True)


def procesar_carpeta(
    entrada: Path,
    salida: Path,
    tamano: int,
    margen: float,
    fondo: str,
    forzar: bool,
) -> None:
    entrada.mkdir(parents=True, exist_ok=True)
    archivos = sorted(
        (
            archivo for archivo in entrada.iterdir()
            if archivo.is_file() and archivo.suffix.lower() in EXTENSIONES
        ),
        key=clave_nombre,
    )
    if not archivos:
        print(f"No hay imagenes compatibles en: {entrada}")
        return

    salida.mkdir(parents=True, exist_ok=True)
    sesion = new_session("u2net")
    total = len(archivos)

    for indice, archivo in enumerate(archivos, start=1):
        try:
            extension_salida = ".png" if fondo == "transparente" else ".jpg"
            destino = salida / archivo.stem
            archivo_salida = destino.parent / f"{destino.name}{extension_salida}"
            if not forzar and archivo_salida.exists():
                print(f"[{indice}/{total}] OMITIDA: ya existe {archivo.name}")
                continue
            with Image.open(archivo) as original:
                sin_fondo = quitar_fondo(original, sesion)
            final = colocar_en_lienzo(sin_fondo, tamano, margen)
            guardar(final, destino, fondo)
            print(f"[{indice}/{total}] OK: {archivo.name} -> {destino.name}{extension_salida}")
        except Exception as error:
            print(f"[{indice}/{total}] ERROR: {archivo.name} -> {error}")


def argumentos() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Quita fondos y prepara fotos de producto para e-commerce."
    )
    parser.add_argument("--entrada", type=Path, default=Path("fotos_entrada"))
    parser.add_argument("--salida", type=Path, default=Path("fotos_salida"))
    parser.add_argument("--tamano", type=int, default=1200, help="Lado del lienzo final en pixeles.")
    parser.add_argument(
        "--margen",
        type=float,
        default=0.08,
        help="Margen alrededor del producto, entre 0 y 0.45 (por defecto: 0.08).",
    )
    parser.add_argument(
        "--fondo",
        choices=("blanco", "gris", "transparente"),
        default="blanco",
        help="Fondo final: blanco, gris o transparente.",
    )
    parser.add_argument(
        "--color-fondo",
        metavar="HEX",
        help="Color hexadecimal personalizado, por ejemplo #F5F5F5. Reemplaza --fondo.",
    )
    parser.add_argument(
        "--forzar",
        action="store_true",
        help="Vuelve a procesar archivos aunque el resultado ya exista.",
    )
    args = parser.parse_args()
    if not 0 <= args.margen < 0.5:
        parser.error("--margen debe estar entre 0 y 0.5")
    if args.tamano < 100:
        parser.error("--tamano debe ser como minimo 100")
    if args.color_fondo:
        try:
            ImageColor.getrgb(args.color_fondo)
        except ValueError:
            parser.error("--color-fondo debe ser un color hexadecimal valido, por ejemplo #F5F5F5")
        args.fondo = args.color_fondo
    return args


if __name__ == "__main__":
    opciones = argumentos()
    procesar_carpeta(
        opciones.entrada,
        opciones.salida,
        opciones.tamano,
        opciones.margen,
        opciones.fondo,
        opciones.forzar,
    )