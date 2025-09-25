import os
import sys
import math
from pathlib import Path
from typing import Optional

import pandas as pd
import numpy as np

#util: impresión separadores 
def banner(titulo: str):
    print("\n" + "="*80)
    print(titulo)
    print("="*80)

# 1) Serie con 5 asignaturas (índice = nombre asignatura), estadísticas y orden
def ejercicio_serie_asignaturas():
    banner("1) Serie de asignaturas, estadísticas y orden")
    asignaturas = pd.Series(
        [4.2, 3.8, 2.9, 4.5, 3.2],
        index=["Mate", "Lengua", "Historia", "Ciencias", "Arte"],
        name="promedio_final"
    )
    print("Serie:\n", asignaturas, sep="")
    print("Media:", asignaturas.mean())
    print("Máximo:", asignaturas.max())
    print("Mínimo:", asignaturas.min())
    print("Ordenado (desc):\n", asignaturas.sort_values(ascending=False), sep="")

    explicacion = (
        "El índice permite etiquetar filas/columnas con nombres significativos y no solo posiciones.\n"
        "Facilita accesos directos (por etiqueta), uniones/merge por claves y filtrados expresivos.\n"
        "También mejora la claridad del código al referirnos a 'Mate' o 'Ciencias' en lugar de [0] o [3]."
    )
    print("\nExplicación (índices):\n" + explicacion)

# 2) DataFrame con riesgo (promedio<3.0 o inasistencias>10)
def ejercicio_dataframe_riesgo():
    banner("2) DataFrame estudiantes + columna de riesgo y filtro ordenado")
    df_est = pd.DataFrame({
        "id_estudiante": [1,2,3,4,5],
        "grado": [10,10,11,11,9],
        "promedio": [2.5, 3.6, 4.1, 2.9, 3.0],
        "inasistencias": [12, 4, 6, 15, 2]
    })
    df_est["riesgo"] = (df_est["promedio"] < 3.0) | (df_est["inasistencias"] > 10)
    en_riesgo = df_est[df_est["riesgo"]].sort_values("promedio")
    print("Todos:\n", df_est, sep="")
    print("\nEn riesgo (ordenado por promedio asc):\n", en_riesgo, sep="")
    return df_est, en_riesgo

# 3) CSV ficticio ventas: filtro y groupby
def ejercicio_csv_ventas():
    banner("3) CSV ficticio ventas: filtro y groupby")
    ventas = pd.DataFrame({
        "id":[1,2,3,4,5],
        "producto":["A","B","C","D","E"],
        "categoria":["Tech","Tech","Hogar","Hogar","Moda"],
        "precio":[12000,8000,15000,20000,9000],
        "cantidad":[6,2,7,8,4]
    })
    print("Ventas:\n", ventas, sep="")

    filtrado = ventas[(ventas["precio"]>10000) & (ventas["cantidad"]>5)]
    print("\nFiltrado (precio>10000 & cantidad>5):\n", filtrado, sep="")

    agrupado = ventas.groupby("categoria", as_index=False).agg(
        cantidad_total=("cantidad","sum"),
        precio_total=("precio","sum")
    )
    print("\nGroupBy por categoría (sumas):\n", agrupado, sep="")

    explicacion = (
        "groupby permite resumir datos por categorías (agregaciones como suma, media).\n"
        "Transforma registros detallados en indicadores por grupo, facilitando análisis y comparaciones."
    )
    print("\nExplicación (groupby):\n" + explicacion)

# 4) Importar archivos reales y generar reporte de clientes
#     - clientes.xlsx (openpyxl)
#     - pedidos.csv  (latin-1, sep=';')
#     - facturas.pdf (tabula)
def ejercicio_importaciones_y_reporte(base_dir: Optional[Path] = None):
    banner("4) Importar clientes.xlsx, pedidos.csv, facturas.pdf y REPORTE clientes")
    if base_dir is None:
        base_dir = Path("/mnt/data")  # ajustar si se ejecuta en otra ruta

    clientes_path = base_dir / "clientes.xlsx"
    pedidos_path  = base_dir / "pedidos.csv"
    facturas_path = base_dir / "facturas.pdf"

    # Leer clientes.xlsx
    if not clientes_path.exists():
        print(f"ADVERTENCIA: No se encontró {clientes_path}.")
        clientes = pd.DataFrame(columns=["id_cliente","nombre","email"])
    else:
        clientes = pd.read_excel(clientes_path, engine="openpyxl")
    print("\nClientes (head 3):\n", clientes.head(3), sep="")

    # Leer pedidos.csv
    if not pedidos_path.exists():
        print(f"ADVERTENCIA: No se encontró {pedidos_path}.")
        pedidos = pd.DataFrame(columns=["id_pedido","id_cliente","valor"])
    else:
        pedidos = pd.read_csv(pedidos_path, sep=";", encoding="latin-1")
    print("\nPedidos (head 3):\n", pedidos.head(3), sep="")

    # Leer facturas.pdf con tabula (si falla por Java, el script continúa)
    try:
        if facturas_path.exists():
            import tabula
            facturas_list = tabula.read_pdf(str(facturas_path), pages="all")
            facturas = facturas_list[0] if facturas_list else pd.DataFrame()
            print("\nFacturas (head 3):\n", facturas.head(3), sep="")
        else:
            print(f"\nADVERTENCIA: No se encontró {facturas_path}.")
    except Exception as e:
        print("\nAviso: No se pudo leer facturas.pdf con tabula. Detalle:", e)

    # Merge clientes + pedidos
    if not clientes.empty and not pedidos.empty:
        clientes_pedidos = clientes.merge(pedidos, on="id_cliente", how="left")
        total_pedidos = clientes_pedidos.groupby("id_cliente", as_index=False).agg(
            num_pedidos=("id_pedido","count"),
            valor_total=("valor","sum")
        ).fillna(0)

        reporte = clientes.merge(total_pedidos, on="id_cliente", how="left").fillna(0)

        # Categoría de cliente
        reporte["categoria_cliente"] = reporte["valor_total"].apply(
            lambda x: "VIP" if x > 500000 else "Regular"
        )

        cols = [c for c in ["nombre","num_pedidos","valor_total","categoria_cliente"] if c in reporte.columns]
        print("\nREPORTE CLIENTES:\n", reporte[cols], sep="")

        # Guardar a CSV
        out_path = base_dir / "reporte_clientes.csv"
        reporte.to_csv(out_path, index=False)
        print(f"\nReporte guardado en: {out_path}")
    else:
        print("\nNo se pudo crear el reporte de clientes (faltan datos de clientes o pedidos).")

# 5) (Opcional) Reporte académico por estudiante si existen los CSV:
#    estudiantes.csv: id, grado, sexo, estrato, promedio, ausencias, club, fecha_ingreso, estado
#    sesiones.csv   : id_sesion, id_estudiante, fecha, tema, duracion_min, modalidad, asistencia (0/1)
#    notas.csv      : id_estudiante, area, periodo, nota
#    - total sesiones asistidas
#    - minutos totales
#    - promedio de notas por área (pivot)
#    - bandera de riesgo (ausencias>10 o promedio<3.0)
#    - índice de participación = sesiones asistidas / sesiones totales del grupo (grado, periodo)
def ejercicio_reporte_academico(base_dir: Optional[Path] = None):
    banner("5) Reporte académico (opcional si existen CSV)")
    if base_dir is None:
        base_dir = Path("/mnt/data")

    est_path = base_dir / "estudiantes.csv"
    ses_path = base_dir / "sesiones.csv"
    not_path = base_dir / "notas.csv"

    if not (est_path.exists() and ses_path.exists() and not_path.exists()):
        print("Saltando: no se encontraron los tres archivos estudiantes.csv, sesiones.csv y notas.csv en", base_dir)
        return

    # Cargar
    est = pd.read_csv(est_path)
    ses = pd.read_csv(ses_path, parse_dates=["fecha"])
    notas = pd.read_csv(not_path)

    # Total sesiones asistidas y minutos por estudiante
    asis = ses[ses["asistencia"]==1].groupby("id_estudiante", as_index=False).agg(
        sesiones_asistidas=("id_sesion","count"),
        minutos_totales=("duracion_min","sum")
    )

    # Promedio de notas por área (pivot)
    notas_prom = notas.groupby(["id_estudiante","area"], as_index=False)["nota"].mean()
    pivot_notas = notas_prom.pivot(index="id_estudiante", columns="area", values="nota").reset_index()

    # Riesgo por ausencias o promedio<3.0
    # - Promedio global por estudiante (media entre áreas disponibles)
    prom_global = notas.groupby("id_estudiante", as_index=False)["nota"].mean().rename(columns={"nota":"promedio_global"})
    est2 = est.merge(prom_global, on="id_estudiante", how="left")
    est2["ausencias"] = est2.get("ausencias", pd.Series([0]*len(est2)))
    est2["riesgo"] = (est2["ausencias"] > 10) | (est2["promedio_global"] < 3.0)

    # Periodo desde fecha (por ejemplo, trimestre: Q1/Q2/Q3/Q4)
    ses["periodo"] = ses["fecha"].dt.to_period("Q").astype(str)

    # Sesiones totales por grupo (grado, periodo)
    sesiones_tot_grupo = (
        ses.groupby(["grado","periodo"], as_index=False)["id_sesion"]
          .nunique()
          .rename(columns={"id_sesion":"sesiones_totales_grupo"})
    )

    # Sesiones asistidas por estudiante + join con grado/periodo de sus sesiones
    # (Si un estudiante tiene sesiones en varios periodos, se considera el más reciente)
    ses_est = ses.groupby("id_estudiante", as_index=False).agg(
        grado=("grado","max"),
        periodo=("periodo","max")
    )

    report = (
        est2.merge(asis, on="id_estudiante", how="left")
            .merge(pivot_notas, on="id_estudiante", how="left")
            .merge(ses_est, on="id_estudiante", how="left")
            .merge(sesiones_tot_grupo, on=["grado","periodo"], how="left")
    )

    # Índice de participación
    report["sesiones_asistidas"] = report["sesiones_asistidas"].fillna(0)
    report["sesiones_totales_grupo"] = report["sesiones_totales_grupo"].replace(0, np.nan)
    report["indice_participacion"] = report["sesiones_asistidas"] / report["sesiones_totales_grupo"]

    # Orden columnas amigable
    cols_first = [
        "id_estudiante","grado","periodo","sesiones_asistidas","minutos_totales",
        "promedio_global","riesgo","indice_participacion"
    ]
    other_cols = [c for c in report.columns if c not in cols_first]
    report = report[cols_first + other_cols]

    print("REPORTE ACADÉMICO (preview):\n", report.head(10), sep="")

    out_path = base_dir / "reporte_academico.csv"
    report.to_csv(out_path, index=False)
    print(f"\nReporte académico guardado en: {out_path}")

# MAIN
if __name__ == "__main__":
    ejercicio_serie_asignaturas()
    ejercicio_dataframe_riesgo()
    ejercicio_csv_ventas()
    ejercicio_importaciones_y_reporte()
    ejercicio_reporte_academico()
