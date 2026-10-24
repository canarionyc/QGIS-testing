 CD 'C:\DEV\QGIS-testing\data\Santa Cruz de Tenerife\PGO\'

(Get-Content fip_short.json -Raw) -replace ',\s*"GEOMETRIA"\s*:\s*"([^"\\]|\\.)*"', '' | Set-Content fip_test.json