-- ============================================================================
-- ESQUEMA DE BASE DE DATOS SIMPLIFICADO PARA NARRADORWEB
-- ============================================================================
-- Versión: 2.0
-- Fecha: Noviembre 13, 2025
-- Autor: Jorge Jesús Lee Soto
-- Propósito: Esquema minimalista alineado con métricas del seminario
-- ============================================================================

-- NOTA: Ejecutar este script en SQL Server Management Studio (SSMS)
--       o desde sqlcmd con la base de datos SeminarioNarrador seleccionada

USE SeminarioNarrador;
GO

-- ============================================================================
-- PASO 1: Eliminar tablas antiguas si existen (CUIDADO: Esto borra datos)
-- ============================================================================

-- Comentar estas líneas si quieres mantener datos antiguos
/*
IF OBJECT_ID('snw.audio_files', 'U') IS NOT NULL DROP TABLE snw.audio_files;
IF OBJECT_ID('snw.runs', 'U') IS NOT NULL DROP TABLE snw.runs;
IF OBJECT_ID('snw.pages', 'U') IS NOT NULL DROP TABLE snw.pages;
IF OBJECT_ID('snw.audio_assets', 'U') IS NOT NULL DROP TABLE snw.audio_assets;
IF OBJECT_ID('snw.metrics', 'U') IS NOT NULL DROP TABLE snw.metrics;
IF OBJECT_ID('snw.extracts', 'U') IS NOT NULL DROP TABLE snw.extracts;
IF OBJECT_ID('snw.software_versions', 'U') IS NOT NULL DROP TABLE snw.software_versions;
IF OBJECT_ID('snw.voices', 'U') IS NOT NULL DROP TABLE snw.voices;
IF OBJECT_ID('snw.systems', 'U') IS NOT NULL DROP TABLE snw.systems;
*/

-- ============================================================================
-- PASO 2: Crear esquema snw si no existe
-- ============================================================================

IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'snw')
BEGIN
    EXEC('CREATE SCHEMA snw');
    PRINT 'Schema snw creado exitosamente';
END
ELSE
BEGIN
    PRINT 'Schema snw ya existe';
END
GO

-- ============================================================================
-- TABLA 1: pages (Registro de URLs procesadas)
-- ============================================================================
-- Propósito: Mantener catálogo de páginas únicas procesadas
-- Cardinalidad esperada: 30-100 registros (dataset de evaluación)
-- ============================================================================

IF OBJECT_ID('snw.pages', 'U') IS NULL
BEGIN
    CREATE TABLE snw.pages (
        page_id INT IDENTITY(1,1) PRIMARY KEY,
        
        -- Información básica de la página
        url NVARCHAR(2048) NOT NULL UNIQUE,  -- URL completa (índice unique para evitar duplicados)
        domain NVARCHAR(255) NOT NULL,        -- Dominio extraído (ej: "wikipedia.org")
        title NVARCHAR(500) NULL,             -- Título de la página (opcional)
        
        -- Metadata
        created_at DATETIME DEFAULT GETDATE() NOT NULL
    );
    
    -- Índice para búsquedas por dominio
    CREATE INDEX idx_pages_domain ON snw.pages(domain);
    
    PRINT 'Tabla snw.pages creada exitosamente';
END
ELSE
BEGIN
    PRINT 'Tabla snw.pages ya existe';
END
GO

-- ============================================================================
-- TABLA 2: runs (Ejecuciones del sistema)
-- ============================================================================
-- Propósito: Registrar cada vez que se procesa una página con sus métricas
-- Cardinalidad esperada: 100-500 registros (múltiples runs por página)
-- ============================================================================

IF OBJECT_ID('snw.runs', 'U') IS NULL
BEGIN
    CREATE TABLE snw.runs (
        run_id CHAR(32) PRIMARY KEY,  -- UUID en formato hex (sin guiones)
        
        -- Relación con página
        page_id INT NOT NULL FOREIGN KEY REFERENCES snw.pages(page_id),
        url NVARCHAR(2048) NULL,  -- URL redundante para consultas rápidas
        
        -- ========== MÉTRICAS DEL SEMINARIO (CRÍTICAS) ==========
        -- VD1: Tiempo Hasta Contenido Útil (TTCU)
        ttcu_seconds FLOAT NOT NULL,
        -- Fórmula: (tiempo_extracción + tiempo_tts) / 1000.0
        -- Rango esperado: 0.5 - 5.0 segundos
        
        -- VD2: Proporción de Texto No-Informativo Narrado (PTNN)
        ptnn_percent FLOAT NOT NULL,
        -- Fórmula: ((chars_original - chars_extracted) / chars_original) * 100
        -- Rango esperado: 0 - 95%
        -- ======================================================
        
        -- Métricas técnicas complementarias
        total_time_ms INT NOT NULL,           -- Tiempo total del backend (ms)
        audio_duration_ms INT NULL,           -- Duración del audio generado (ms)
        chars_original INT NOT NULL,          -- Caracteres en HTML original
        chars_extracted INT NOT NULL,         -- Caracteres extraídos (contenido principal)
        
        -- Estado de la ejecución
        ok BIT DEFAULT 1 NOT NULL,            -- 1 = éxito, 0 = error
        err_msg NVARCHAR(500) NULL,           -- Mensaje de error si ok=0
        
        -- Metadata
        created_at DATETIME DEFAULT GETDATE() NOT NULL
    );
    
    -- Índices para análisis estadístico
    CREATE INDEX idx_runs_created ON snw.runs(created_at DESC);
    CREATE INDEX idx_runs_ttcu ON snw.runs(ttcu_seconds);
    CREATE INDEX idx_runs_ptnn ON snw.runs(ptnn_percent);
    CREATE INDEX idx_runs_page ON snw.runs(page_id);
    
    PRINT 'Tabla snw.runs creada exitosamente';
END
ELSE
BEGIN
    PRINT 'Tabla snw.runs ya existe';
END
GO

-- ============================================================================
-- TABLA 3: audio_files (Registro de archivos generados) - OPCIONAL
-- ============================================================================
-- Propósito: Llevar registro de archivos .wav generados (útil para análisis)
-- Cardinalidad esperada: 100-500 registros (1:1 con runs)
-- ============================================================================

IF OBJECT_ID('snw.audio_files', 'U') IS NULL
BEGIN
    CREATE TABLE snw.audio_files (
        audio_id INT IDENTITY(1,1) PRIMARY KEY,
        
        -- Relación con ejecución
        run_id CHAR(32) NOT NULL FOREIGN KEY REFERENCES snw.runs(run_id),
        
        -- Información del archivo
        file_path NVARCHAR(500) NOT NULL,     -- Ruta relativa o absoluta del .wav
        size_bytes BIGINT NULL,               -- Tamaño del archivo (opcional)
        
        -- Metadata
        created_at DATETIME DEFAULT GETDATE() NOT NULL
    );
    
    CREATE INDEX idx_audio_run ON snw.audio_files(run_id);
    
    PRINT 'Tabla snw.audio_files creada exitosamente';
END
ELSE
BEGIN
    PRINT 'Tabla snw.audio_files ya existe';
END
GO

-- ============================================================================
-- PASO 3: Verificar integridad del esquema
-- ============================================================================

PRINT '';
PRINT '============================================================';
PRINT 'VERIFICACIÓN DE ESQUEMA';
PRINT '============================================================';

-- Contar tablas creadas
DECLARE @table_count INT;
SELECT @table_count = COUNT(*)
FROM sys.tables t
JOIN sys.schemas s ON t.schema_id = s.schema_id
WHERE s.name = 'snw';

PRINT 'Total de tablas en esquema snw: ' + CAST(@table_count AS VARCHAR(10));

-- Listar tablas
SELECT 
    SCHEMA_NAME(schema_id) AS [Schema],
    name AS [Table],
    create_date AS [Created]
FROM sys.tables
WHERE SCHEMA_NAME(schema_id) = 'snw'
ORDER BY name;

-- Contar campos totales
DECLARE @column_count INT;
SELECT @column_count = COUNT(*)
FROM sys.columns c
JOIN sys.tables t ON c.object_id = t.object_id
JOIN sys.schemas s ON t.schema_id = s.schema_id
WHERE s.name = 'snw';

PRINT 'Total de campos en esquema snw: ' + CAST(@column_count AS VARCHAR(10));

PRINT '';
PRINT '✅ Esquema simplificado creado exitosamente';
PRINT '============================================================';
PRINT '';

-- ============================================================================
-- PASO 4: Datos de prueba (opcional, comentar si no deseas)
-- ============================================================================

/*
-- Insertar página de prueba
INSERT INTO snw.pages (url, domain, title)
VALUES 
    ('https://es.wikipedia.org/wiki/Python', 'es.wikipedia.org', 'Python - Wikipedia'),
    ('https://www.inegi.org.mx/', 'www.inegi.org.mx', 'INEGI - Inicio');

-- Insertar run de prueba
INSERT INTO snw.runs (
    run_id, page_id, url, ttcu_seconds, ptnn_percent, 
    total_time_ms, audio_duration_ms, chars_original, chars_extracted, ok
)
VALUES 
    ('a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6', 1, 'https://es.wikipedia.org/wiki/Python',
     1.234, 85.5, 1500, 12000, 5000, 725, 1);

PRINT 'Datos de prueba insertados';
*/

-- ============================================================================
-- CONSULTAS ÚTILES PARA ANÁLISIS (Copiar y usar en SSMS)
-- ============================================================================

PRINT '';
PRINT '============================================================';
PRINT 'CONSULTAS ÚTILES PARA ANÁLISIS';
PRINT '============================================================';
PRINT '';
PRINT '-- Estadísticas generales:';
PRINT 'SELECT COUNT(*) as total_runs, AVG(ttcu_seconds) as avg_ttcu, AVG(ptnn_percent) as avg_ptnn FROM snw.runs WHERE ok = 1;';
PRINT '';
PRINT '-- Métricas por dominio:';
PRINT 'SELECT p.domain, COUNT(*) as runs, AVG(r.ttcu_seconds) as avg_ttcu FROM snw.runs r JOIN snw.pages p ON r.page_id = p.page_id WHERE r.ok = 1 GROUP BY p.domain;';
PRINT '';
PRINT '-- Top 10 páginas más lentas:';
PRINT 'SELECT TOP 10 p.title, r.ttcu_seconds FROM snw.runs r JOIN snw.pages p ON r.page_id = p.page_id WHERE r.ok = 1 ORDER BY r.ttcu_seconds DESC;';
PRINT '';
PRINT '============================================================';

GO
