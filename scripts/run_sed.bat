
setlocal 
set PATH=C:\Program Files\Git\usr\bin;%PATH%

chcp 65001


cd "c:\dev\QGIS-testing\data\Santa Cruz de Tenerife\PGO\"
dir
dir fip_test.json
goto :eof
rem sed 's/",\s?GEOMETRIA": ".*"//' "fip_short.json" > fip_test.json
rem sed -zE 's/,[[:space:]]*"GEOMETRIA"[[:space:]]*:[[:space:]]*"([^"\\]|\\.)*"//g' fip_short.json > fip_test.json
sed  's/,\s*"GEOMETRIA"\s*:\s*".*"//g' fip_short.json > fip_test.json
dir fip_test.json


endlocal