Set-Location -Path "C:\Program Files\QGIS 3.40.15\apps\Python312\Lib\site-packages\pywin32_system32"
# $env:PATH += ";C:\Program Files\QGIS 3.40.15\apps\Python312\Lib\site-packages\pywin32_system32"
Get-ChildItem -Path "C:\Program Files\QGIS 3.40.15\apps\Python312\Lib\site-packages\pywin32_system32" -Filter "python*.dll"

Set-Location -Path "C:\Program Files\QGIS 3.40.15\apps\Python312\Lib\site-packages\win32"
Get-ChildItem -Path "C:\Program Files\QGIS 3.40.15\apps\Python312\Lib\site-packages\win32" -Filter "python*.dll"

Set-Location -Path "C:\OSGeo4W\apps\"
Get-ChildItem -Path "C:\OSGeo4W\apps\"  -Recurse

Set-Location -Path "C:\OSGeo4W\apps\grass-8.4.0\lib"