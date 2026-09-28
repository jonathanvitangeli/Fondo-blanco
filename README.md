# Procesador de fotos de producto

## Instalacion

Abre PowerShell en esta carpeta y ejecuta:

```powershell
python -m pip install -r requirements.txt
```

La primera imagen descarga automaticamente el modelo de eliminacion de fondo y puede tardar un poco.

## Uso rapido

1. Crea la carpeta `fotos_entrada` (el script tambien la crea automaticamente si no existe).
2. Pon dentro tus fotos `.jpg`, `.jpeg`, `.png` o `.webp`.
3. Ejecuta:

```powershell
python procesar_productos.py
```

Las fotos terminadas apareceran en `fotos_salida` como JPG de 1200 x 1200 px con fondo blanco.
La orientacion EXIF de las fotos se corrige automaticamente.
Se conserva el nombre completo de cada archivo, incluidos numeros como `(2)` o `(3)` y puntos en nombres como `10.24.43`; se ordenan de forma natural.

## Opciones

```powershell
python procesar_productos.py --entrada originales --salida listas --tamano 1600 --margen 0.1
python procesar_productos.py --fondo transparente
python procesar_productos.py --fondo gris
python procesar_productos.py --color-fondo "#F5F5F5"
python procesar_productos.py --forzar
```

`--margen` controla el espacio alrededor del producto. Por ejemplo, `--margen 0.1` deja un 10% de margen.

Con `--fondo transparente`, el resultado se guarda como PNG para conservar el fondo transparente.
Con `--color-fondo` puedes usar cualquier color hexadecimal; el resultado se guarda como JPG.
Por defecto, los archivos que ya tienen resultado se omiten. Usa `--forzar` para procesarlos de nuevo.