echo off

setlocal enableextensions enabledelayedexpansion

REM Setup environment
call "C:\OSGeo4W\bin\o4w_env.bat"

cd c:\dev\QGIS-testing
echo on
rem goto CAPA3

rem goto NUCLEOS_URBANOS

:PARCELAS_ABANDONO_PROLONGADO
:: #region Cultivos Filtering Task
@echo ==============================================================================
@echo TASK 1: Parcelas en abandono prolongado -> Writes directly to capa1.zip
@echo ==============================================================================
set SOURCE_SHP=data\GC_MCultivos_2013\GC_MCultivos_2013.shp
set OUTPUT_ZIP=output\capa1.zip
set TMP_DIR=tmp_parcela_abandono

ogr2ogr -f "ESRI Shapefile" -overwrite -a_srs EPSG:32628 --config SHAPE_ENCODING UTF-8 -lco ENCODING=UTF-8 -where "Cultivo = 'Abandono Prolongado' AND Area_m2 >= 8000 AND Area_m2 <= 8500" %TMP_DIR% %SOURCE_SHP%

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Task 1 failed.
    exit /b %ERRORLEVEL%
)
@rem dir %TMP_DIR%
tar -a -c -C %TMP_DIR% -f %OUTPUT_ZIP% *
tar -tf %OUTPUT_ZIP%
rem rmdir /s /q %TMP_DIR%
rem goto :EOF

:: #endregion

:NUCLEOS_URBANOS

:: #region Nucleos Urbanos Task

@echo ==============================================================================
@echo TASK 2: Nucleos urbanos en Telde (>500 hab)
@echo ==============================================================================

set "SOURCE_SHP=data\gobcan_nucleos\gobcan_unidades-estadisticas_nucleos.shp"
set "TMP_DIR=tmp_telde"
set OUTPUT_ZIP=output\capa2.zip
REM 1. Print total records in the source dataset
@echo ---------------------------------------------------
@echo [INFO] Analyzing source dataset...
for /f "tokens=*" %%a in ('ogrinfo -al -so "%SOURCE_SHP%" ^| findstr /C:"Feature Count"') do (
    echo [INFO] Original %%a
)

@echo ---------------------------------------------------

REM 2. Extract and Filter to a temporary folder
@echo [INFO] Filtering for NMUN = 'TELDE' AND POB_TOT ^> 500...
ogr2ogr -f "ESRI Shapefile" -overwrite -a_srs EPSG:32628 --config SHAPE_ENCODING UTF-8 -lco ENCODING=UTF-8 -where "POB_TOT > 500 AND NMUN = 'TELDE'" %TMP_DIR% "%SOURCE_SHP%"

if %ERRORLEVEL% NEQ 0 (
    @echo [ERROR] ogr2ogr failed.
    exit /b %ERRORLEVEL%
)

REM 3. Print filtered records in the new dataset
REM Note: ogr2ogr keeps the original filename when outputting to a directory
for /f "tokens=*" %%a in ('ogrinfo -al -so "%TMP_DIR%\gobcan_unidades-estadisticas_nucleos.shp" ^| findstr /C:"Feature Count"') do (
    @echo [INFO] Filtered %%a
)
@echo ---------------------------------------------------

REM 4. Compress the folder into capa2.zip, then delete the temp folder
@echo [INFO] Compressing to capa2.zip...
tar -a -c -C %TMP_DIR% -f %OUTPUT_ZIP% *
rem rmdir /s /q %TMP_DIR%

@echo [SUCCESS] Telde layer filtered, zipped, and cleaned up!
rem goto :EOF
:: #endregion

:: #region CAPA3 Task
:CAPA3

@echo ==============================================================================
@echo TASK 3 & 4: Parcelas afectadas por viario (Spatial Join)
@echo ==============================================================================

REM We use forward slashes for the UG path because SQLite handles them better in queries
set "UG_SHP=data/UG.shp"
set "CATASTRO_SHP=data\catastroSC.shp"
set "TMP_DIR=tmp_capa3"
set OUTPUT_SHP=%TMP_DIR%\parcelas_afectadas.shp
set OUTPUT_ZIP=output\capa3.zip

@echo ---------------------------------------------------
@echo [INFO] Analyzing source dataset (catastroSC)...
for /f "tokens=*" %%a in ('ogrinfo -al -so "%CATASTRO_SHP%" ^| findstr /C:"Feature Count"') do (
    @echo [INFO] catastroSC: %%a
)
@echo ---------------------------------------------------

@echo [INFO] Executing spatial join (ETIPLAN = 'V' AND ST_Intersects)...

REM -nln names the output files "parcelas_afectadas" inside the capa3 folder
ogr2ogr -f "ESRI Shapefile" -overwrite %TMP_DIR% "%CATASTRO_SHP%" -nln parcelas_afectadas -dialect sqlite ^
    -sql "SELECT * FROM catastroSC c WHERE EXISTS (SELECT 1 FROM '%UG_SHP%'.'UG' u WHERE u.ETIPLAN = 'V' AND ST_Intersects(c.geometry, u.geometry))"
rem dir /B %TMP_DIR%

if %ERRORLEVEL% NEQ 0 (
    @echo [ERROR] Spatial join ogr2ogr failed.
    exit /b %ERRORLEVEL%
)

REM Print the final count of affected parcels
for /f "tokens=*" %%a in ('ogrinfo -al -so "%OUTPUT_SHP%" ^| findstr /C:"Feature Count"') do (
    @echo [INFO] Parcelas afectadas %%a
)
@echo ---------------------------------------------------

@echo [INFO] Compressing to %OUTPUT_ZIP%...
tar -a -c -C %TMP_DIR% -f %OUTPUT_ZIP% *
tar -tf %OUTPUT_ZIP%

REM rmdir /s /q %TMP_DIR%

@echo [SUCCESS] Parcelas afectadas spatial join completed and zipped!
:: #endregion

:: region Comprobacion de resultados (opcional)
@echo [INFO] Launching QGIS to inspect the results...
start "" C:\OSGeo4W\bin\qgis-ltr-bin.exe output\capa1.zip output\capa2.zip output\capa3.zip
:: endregion

endlocal