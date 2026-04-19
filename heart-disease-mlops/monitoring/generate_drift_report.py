# monitoring/generate_drift_report.py
import pandas as pd
import os
import sys

# Intentar importar evidently - SI FALLA, EL SCRIPT TERMINA CON ERROR
try:
    from evidently.report import Report
    from evidently.metric_preset import DataDriftPreset
except ImportError:
    print("❌ ERROR: Evidently no está instalado.")
    print("   Ejecuta: pip install evidently")
    sys.exit(1)

# Rutas
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
TRAIN_PATH = os.path.join(DATA_DIR, "X_train.csv")
TEST_PATH = os.path.join(DATA_DIR, "X_test.csv")

# 1. CARGAR LOS DATOS
print("📂 Cargando datos...")
if not os.path.exists(TRAIN_PATH):
    print(f"❌ No se encontró {TRAIN_PATH}")
    print("   Ejecuta primero el notebook para generar los archivos")
    sys.exit(1)

if not os.path.exists(TEST_PATH):
    print(f"❌ No se encontró {TEST_PATH}")
    print("   Ejecuta primero el notebook para generar los archivos")
    sys.exit(1)

X_train = pd.read_csv(TRAIN_PATH)
X_test = pd.read_csv(TEST_PATH)
print(f"   X_train: {X_train.shape}")
print(f"   X_test:  {X_test.shape}")

# 2. Generar reporte con Evidently
print("🔍 Generando reporte de deriva de datos con Evidently...")
report = Report(metrics=[DataDriftPreset()])
report.run(reference_data=X_train, current_data=X_test)

# 3. Guardar reporte
output_path = os.path.join(BASE_DIR, "drift_report.html")
report.save_html(output_path)
print(f"✅ Reporte guardado: {output_path}")

# 4. Mostrar resumen en terminal
print("\n📊 Resumen de Deriva:")
try:
    drift_summary = report.as_dict()["metrics"][0]["result"]
    print(f"   Características con deriva: {drift_summary['number_of_drifted_columns']}")
    print(f"   Proporción: {drift_summary['share_of_drifted_columns']:.2%}")
except:
    print("   (Abre el archivo HTML para ver detalles completos)")