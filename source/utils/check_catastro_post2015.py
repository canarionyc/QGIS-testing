import sqlite3
import os

# We can use ogrinfo/ogr2ogr or inspect via python with sqlite3/spatialite or osgeo
# Let's check with ogrinfo summary on CONSTRU.ZIP to see how many buildings were built after 2015!
# ogrinfo supports SQL queries: SELECT COUNT(*) FROM CONSTRU WHERE FECHAALTA >= 20150101
cmd = r'C:\OSGeo4W\bin\ogrinfo.exe /vsizip/"c:\dev\QGIS-testing\data\Santa Cruz de Tenerife\Catastro - 38900uA 38015 SANTA CRUZ DE TENERIFE\38900uA_38015_23012026_CONSTRU.ZIP" -dialect SQLite -sql "SELECT COUNT(*), MIN(FECHAALTA), MAX(FECHAALTA) FROM CONSTRU WHERE FECHAALTA >= 20150101"'
os.system(cmd)
