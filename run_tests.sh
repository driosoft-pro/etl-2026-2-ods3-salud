#!/bin/bash

echo "=========================================="
echo "  EJECUCIÓN DE TESTS - SALUD COLOMBIA"
echo "=========================================="

case "$1" in
    "unit")
        echo " Ejecutando tests unitarios..."
        python -m pytest tests/ -v -m "unit" --tb=short
        ;;
    "integration")
        echo " Ejecutando tests de integración..."
        python -m pytest tests/ -v -m "integration" --tb=short
        ;;
    "data")
        echo " Ejecutando tests de validación de datos..."
        python -m pytest tests/ -v -m "data" --tb=short
        ;;
    "all")
        echo " Ejecutando TODOS los tests..."
        python -m pytest tests/ -v --tb=short
        ;;
    *)
        echo ""
        echo "Uso: ./run_tests.sh [opción]"
        echo ""
        echo "Opciones:"
        echo "  unit         Ejecutar tests unitarios"
        echo "  integration  Ejecutar tests de integración"
        echo "  data         Ejecutar tests de validación de datos"
        echo "  all          Ejecutar todos los tests"
        echo ""
        echo "Ejemplo: ./run_tests.sh unit"
        ;;
esac

echo ""
echo "=========================================="
echo "  TESTS COMPLETADOS"
echo "=========================================="