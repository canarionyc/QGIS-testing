# Agent Instructions & Environment Reference (QGIS-testing)

This document defines the runtime environment, Python interpreters, CLI tool suites, and permissions for AI agents (Antigravity) operating in this workspace.

---

## 1. Python Interpreters & Environments

- **System Python**: `C:\Python312\python.exe`
- **OSGeo4W Python**: `C:\OSGeo4W\apps\Python312\python.exe`
- **QGIS LTR Python Launcher (PyQGIS)**: `C:\OSGeo4W\bin\python-qgis-ltr.bat`
  - Use `python-qgis-ltr.bat` for standalone execution of scripts importing `qgis.core`, `qgis.gui`, `PyQt5`, `osgeo`, etc.

---

## 2. QGIS Environment Variables (`qgis-ltr-bin.env`)

The standard OSGeo4W environment establishes:
```ini
PATH=C:\OSGeo4W\apps\qgis-ltr\bin;C:\OSGeo4W\apps\qt5\bin;C:\OSGeo4W\apps\Python312\Scripts;C:\OSGeo4W\bin;C:\WINDOWS\system32;C:\WINDOWS;C:\WINDOWS\system32\WBem
GDAL_DATA=C:\OSGeo4W\apps\gdal\share\gdal
GDAL_DRIVER_PATH=C:\OSGeo4W\apps\gdal\lib\gdalplugins
GDAL_FILENAME_IS_UTF8=YES
PDAL_DRIVER_PATH=C:\OSGeo4W\apps\pdal\plugins
OSGEO4W_ROOT=C:\OSGeo4W
PROJ_LIB=C:\Program Files\PostgreSQL\18\share\contrib\postgis-3.6\proj
PROJ_DATA=C:\OSGeo4W\share\proj
PYTHONHOME=C:\OSGeo4W\apps\Python312
PYTHONUTF8=1
QGIS_PREFIX_PATH=C:/OSGeo4W/apps/qgis-ltr
QT_PLUGIN_PATH=C:\OSGeo4W\apps\qgis-ltr\qtplugins;C:\OSGeo4W\apps\qt5\plugins
VSI_CACHE=TRUE
VSI_CACHE_SIZE=1000000
O4W_QT_PREFIX=C:/OSGeo4W/apps/Qt5
O4W_QT_BINARIES=C:/OSGeo4W/apps/Qt5/bin
O4W_QT_PLUGINS=C:/OSGeo4W/apps/Qt5/plugins
O4W_QT_LIBRARIES=C:/OSGeo4W/apps/Qt5/lib
O4W_QT_TRANSLATIONS=C:/OSGeo4W/apps/Qt5/translations
O4W_QT_HEADERS=C:/OSGeo4W/apps/Qt5/include
QGIS_WIN_APP_NAME=OSGeo4W\QGIS Desktop 3.44.8
SSL_CERT_DIR=C:\OSGeo4W\apps\openssl\certs
SSL_CERT_FILE=C:\OSGeo4W\bin\curl-ca-bundle.crt
CURL_CA_BUNDLE=C:\Program Files\PostgreSQL\18\ssl\certs\ca-bundle.crt
```
- **GDAL Version**: 3.12.3 ("Chicoutimi")

---

## 3. Permissions & Capabilities

- **QGIS MCP Plugin**: Antigravity is explicitly permissioned to use all calls in the QGIS MCP Plugin at all times.
- **Python Execution**: Antigravity is authorized to execute scripts using both System Python (`C:\Python312\python.exe`) and OSGeo4W Python (`C:\OSGeo4W\apps\Python312\python.exe` / `C:\OSGeo4W\bin\python-qgis-ltr.bat`).
- **OSGeo4W Shell Commands**: Antigravity is authorized to use the full OSGeo4W CLI tool suite.

---

## 4. OSGeo4W CLI Tool Suite

The following OSGeo4W tools are available for terminal execution:

### Geospatial Raster & Vector Processing (GDAL / OGR / PROJ)
- `gdalinfo`, `gdal_translate`, `gdalwarp`, `gdalbuildvrt`, `gdaldem`, `gdal_contour`, `gdal_rasterize`, `gdal_grid`, `gdal_footprint`, `gdal_viewshed`
- `ogrinfo`, `ogr2ogr`, `ogrtindex`, `ogrlineref`
- `proj`, `projinfo`, `projsync`, `cs2cs`, `cct`, `geod`, `invgeod`, `invproj`
- `geosop`, `geotifcp`, `nearblack`, `sozip`

### Point Clouds & Elevation (PDAL / LAS)
- `pdal`
- `lasinfo`, `las2las`, `las2txt`, `lasblock`, `txt2las`, `ts2las`

### Database & Network Analysis
- `psql`, `pg_dump`, `pg_dumpall`, `pg_restore` (PostgreSQL / PostGIS 18)
- `sqlite3`
- `gnmanalyse`, `gnmmanage`

### QGIS & GIS Engines
- `qgis_process-qgis-ltr` (QGIS standalone processing CLI)
- `python-qgis-ltr` (PyQGIS script runner)
- `grass84`, `python-grass84` (GRASS GIS 8.4)
- `gpsbabel`, `gs` (Ghostscript), `curl`, `iconv`, `xmllint`, `xsltproc`

---

## 5. Execution Strategy Guidelines

1. **GUI & Live Inspections**:
   - Use the **QGIS MCP Plugin** for interacting with active layers, inspecting selections, zooming canvas, or querying the open project.
2. **Heavy / Batch / Layout Exports**:
   - For generating print layouts, complex legend manipulation, or heavy geometry processing, prefer standalone execution via:
     ```powershell
     C:\OSGeo4W\bin\python-qgis-ltr.bat <script_path>
     ```
   - This prevents locking the QGIS desktop UI and avoids memory management issues with unparented Qt/SIP objects.
3. **Data Preprocessing & Transformations**:
   - Use OSGeo4W CLI utilities (`ogr2ogr`, `gdalwarp`, `pdal`) directly when converting or projecting spatial datasets.
