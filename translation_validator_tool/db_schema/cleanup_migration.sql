-- Script para limpiar el estado de la migración fallida
-- Ejecutar en PostgreSQL

-- Primero, verificar qué versiones están registradas
SELECT version_num FROM alembic_version;

-- Si hay una migración fallida incompleta, limpiarla
-- DELETE FROM alembic_version WHERE version_num = '20250101000000_add_multi_user_annotations';

-- Establecer a la última versión conocida que funcionaba
DELETE FROM alembic_version;
INSERT INTO alembic_version (version_num) VALUES ('20260324100000');

-- Verificar que quedó correcto
SELECT version_num FROM alembic_version;
