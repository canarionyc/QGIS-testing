setlocal enableextensions enabledelayedexpansion

REM Script para identificar parcelas en abandono prolongado
call "C:\OSGeo4W\bin\o4w_env.bat"

cd c:\dev\QGIS-testing

goto CULTIVOS_FILTERING
goto INFO_PARCELAS_ABANDONO_PROLONGADO

:CULTIVOS_INFO
ogrinfo -al -so data\GC_MCultivos_2013\GC_MCultivos_2013.shp

:CULTIVOS_FILTERING
REM Using -a_srs to assign the CRS since the source coordinates are already in UTM Zone 28N
REM Fixed SQL syntax: using AND instead of &
ogr2ogr -f "ESRI Shapefile" -overwrite -a_srs EPSG:32628 --config SHAPE_ENCODING UTF-8 -lco ENCODING=UTF-8 -where "Cultivo = 'Abandono Prolongado' AND Area_m2 >= 8000 AND Area_m2 <= 8500" output\parcelas_abandono_prolongado data\GC_MCultivos_2013\GC_MCultivos_2013.shp

REM Check if the previous command failed, and exit if it did
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] ogr2ogr failed. Exiting script.
    exit /b %ERRORLEVEL%
)

:INFO_PARCELAS_ABANDONO_PROLONGADO
ogrinfo -al -so parcelas_abandono_prolongado\GC_MCultivos_2013.shp

:CAPA1_ZIP
REM Compress the resulting shapefile into a ZIP file
rem powershell -Command "Compress-Archive -Path 'parcelas_abandono_prolongado\*' -DestinationPath 'parcelas_abandono_prolongado.zip'"

tar cvf capa1_1.zip parcelas_abandono_prolongado
tar -tf capa1_1.zip

goto END

:NUCLEOS_URBANOS_INFO
ogrinfo -al -so "data\gobcan_nucleos\gobcan_unidades-estadisticas_nucleos.shp"

:NUCLEOS_URBANOS_FILTERING
REM Using -a_srs to assign the CRS since the source coordinates are already in UTM Zone 28N

endlocal