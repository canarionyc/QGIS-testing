"""
QGIS Script: Generates an A4 Landscape Print Layout with Geolocated Photos and Leader Arrows.
Reads photos from a specified directory, extracts EXIF GPS coordinates, plots them on the map,
stacks them in a neat vertical column on the right side of the page, and draws non-crossing
leader arrows pointing from each photo to its exact geographical location on the map.

Compatible with:
- QGIS Desktop Python Console / Script Editor (opens Layout Designer automatically)
- Standalone / Headless execution via OSGeo4W python-qgis-ltr.bat
"""

import os
import glob
import re
import math
from osgeo import gdal

from qgis.core import (
    QgsApplication,
    QgsProject,
    QgsPrintLayout,
    QgsLayoutItemPage,
    QgsLayoutItemMap,
    QgsLayoutItemPicture,
    QgsLayoutItemLabel,
    QgsLayoutItemPolyline,
    QgsLayoutItemShape,
    QgsLayoutItemScaleBar,
    QgsLayoutPoint,
    QgsLayoutSize,
    QgsUnitTypes,
    QgsLayoutMeasurement,
    QgsPointXY,
    QgsRectangle,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsLineSymbol,
    QgsSimpleLineSymbolLayer,
    QgsMarkerLineSymbolLayer,
    QgsSimpleMarkerSymbolLayer,
    QgsMarkerSymbol,
    QgsVectorLayer,
    QgsFeature,
    QgsGeometry,
    QgsField,
    QgsSingleSymbolRenderer,
    QgsPalLayerSettings,
    QgsVectorLayerSimpleLabeling,
    QgsTextFormat,
    QgsLayoutExporter,
    Qgis
)
from PyQt5.QtGui import QPolygonF, QColor, QFont
from PyQt5.QtCore import QPointF, QVariant

# Optional iface import when running inside QGIS GUI
try:
    from qgis.utils import iface
except ImportError:
    iface = None


# ==============================================================================
# CONFIGURATION
# ==============================================================================
DEFAULT_PHOTOS_DIR = r"C:\dev\QGIS-testing\QGIS_projects\Santa Cruz de Tenerife\Photos-1-001"
DEFAULT_PROJECT_PATH = r"C:\dev\QGIS-testing\QGIS_projects\Santa Cruz de Tenerife\Santa Cruz de Tenerife.qgz"
DEFAULT_OUTPUT_PDF = r"C:\dev\QGIS-testing\QGIS_projects\Santa Cruz de Tenerife\Plano_Fotografias.pdf"
DEFAULT_OUTPUT_PNG = r"C:\dev\QGIS-testing\QGIS_projects\Santa Cruz de Tenerife\Plano_Fotografias.png"
DEFAULT_LAYOUT_NAME = "Reporte_Fotografias"
TARGET_POLYGON_CODE = "5874-821-SU-1-2-1_381_377"  # Highlighted SUNCO polygon


def parse_dms(dms_str, ref):
    """Parse degrees, minutes, seconds from EXIF string to decimal degrees."""
    if not dms_str:
        return None
    numbers = [float(x) for x in re.findall(r"[\d\.]+", dms_str)]
    if len(numbers) < 3:
        return None
    deg = numbers[0] + numbers[1] / 60.0 + numbers[2] / 3600.0
    if ref and ref.upper() in ["S", "W"]:
        deg = -deg
    return deg


def extract_photos_metadata(photos_dir, target_crs, project_instance):
    """
    Scans directory for JPG/JPEG photos, extracts EXIF GPS and timestamp using GDAL,
    and converts coordinates to the target CRS.
    """
    extensions = ("*.jpg", "*.jpeg", "*.JPG", "*.JPEG")
    photo_paths = []
    for ext in extensions:
        photo_paths.extend(glob.glob(os.path.join(photos_dir, ext)))
    photo_paths = sorted(list(set(photo_paths)))

    if not photo_paths:
        raise FileNotFoundError(f"No photos found in directory: {photos_dir}")

    crs_4326 = QgsCoordinateReferenceSystem("EPSG:4326")
    transform = QgsCoordinateTransform(crs_4326, target_crs, project_instance)

    extracted = []
    for ppath in photo_paths:
        ds = gdal.Open(ppath)
        if not ds:
            continue
        meta = ds.GetMetadata()
        lat_str = meta.get("EXIF_GPSLatitude")
        lat_ref = meta.get("EXIF_GPSLatitudeRef", "N")
        lon_str = meta.get("EXIF_GPSLongitude")
        lon_ref = meta.get("EXIF_GPSLongitudeRef", "E")
        dt_str = meta.get("EXIF_DateTimeOriginal", meta.get("EXIF_DateTime", ""))

        lat = parse_dms(lat_str, lat_ref)
        lon = parse_dms(lon_str, lon_ref)

        if lat is not None and lon is not None:
            pt_proj = transform.transform(QgsPointXY(lon, lat))
            extracted.append({
                "name": os.path.basename(ppath),
                "path": ppath,
                "lat": lat,
                "lon": lon,
                "x": pt_proj.x(),
                "y": pt_proj.y(),
                "datetime": dt_str,
                "width_px": ds.RasterXSize,
                "height_px": ds.RasterYSize
            })

    # Sort North to South (highest latitude first) so leader arrows in the right column
    # do not cross each other as they connect to the map.
    extracted.sort(key=lambda p: p["lat"], reverse=True)
    for idx, item in enumerate(extracted, 1):
        item["id"] = idx

    return extracted


def create_or_update_points_layer(project_instance, photos_data, layer_name="Fotos_Geolocalizadas"):
    """
    Creates or updates a memory point vector layer in QGIS representing the photo locations,
    with custom circular badges and bold numbered labels matching the report.
    """
    # Remove existing layer if present
    for lyr in list(project_instance.mapLayers().values()):
        if lyr.name() == layer_name:
            project_instance.removeMapLayer(lyr.id())

    proj_crs = project_instance.crs()
    mem_layer = QgsVectorLayer(f"Point?crs={proj_crs.authid()}", layer_name, "memory")
    pr = mem_layer.dataProvider()
    pr.addAttributes([
        QgsField("id", QVariant.Int),
        QgsField("foto", QVariant.String),
        QgsField("lat", QVariant.Double),
        QgsField("lon", QVariant.Double)
    ])
    mem_layer.updateFields()

    for pd in photos_data:
        feat = QgsFeature(mem_layer.fields())
        feat.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(pd["x"], pd["y"])))
        feat.setAttribute("id", pd["id"])
        feat.setAttribute("foto", pd["name"])
        feat.setAttribute("lat", pd["lat"])
        feat.setAttribute("lon", pd["lon"])
        pr.addFeatures([feat])

    mem_layer.updateExtents()

    # Symbology: Vivid circular badge with magenta fill and clean white border
    marker_layer = QgsSimpleMarkerSymbolLayer.create({
        "name": "circle",
        "size": "7.0",
        "color": "#D81B60",
        "stroke_color": "#FFFFFF",
        "stroke_width": "0.7"
    })
    marker_sym = QgsMarkerSymbol()
    marker_sym.changeSymbolLayer(0, marker_layer)
    mem_layer.setRenderer(QgsSingleSymbolRenderer(marker_sym))

    # Centered white bold number
    pal = QgsPalLayerSettings()
    pal.fieldName = "id"
    pal.placement = Qgis.LabelPlacement.OverPoint
    txt_fmt = QgsTextFormat()
    txt_fmt.setFont(QFont("Arial", 8, QFont.Bold))
    txt_fmt.setColor(QColor("#FFFFFF"))
    pal.setFormat(txt_fmt)
    mem_layer.setLabeling(QgsVectorLayerSimpleLabeling(pal))
    mem_layer.setLabelsEnabled(True)

    # Insert on top of layer tree so it sits cleanly above orthophotos and polygons
    project_instance.addMapLayer(mem_layer, False)
    root = project_instance.layerTreeRoot()
    root.insertLayer(0, mem_layer)
    mem_layer.triggerRepaint()

    return mem_layer


def make_text_format(font_family="Arial", size_pt=9, bold=False, color_hex="#1a1a1a"):
    """Helper to build modern QgsTextFormat objects without deprecation warnings."""
    tf = QgsTextFormat()
    font = QFont(font_family, int(size_pt))
    font.setBold(bold)
    tf.setFont(font)
    tf.setColor(QColor(color_hex))
    return tf


def build_photo_layout(project_instance, photos_data, layout_name=DEFAULT_LAYOUT_NAME, canvas_extent=None):
    """
    Constructs an A4 Landscape Print Layout containing:
    - Main map view on the left/center.
    - Stacked photos column on the right with metadata captions.
    - Non-crossing leader lines with arrowheads pointing to each photo point.
    - Scale bar, North arrow, and header title card.
    """
    layout_manager = project_instance.layoutManager()
    existing_layout = layout_manager.layoutByName(layout_name)
    if existing_layout:
        layout_manager.removeLayout(existing_layout)

    layout = QgsPrintLayout(project_instance)
    layout.initializeDefaults()
    layout.setName(layout_name)
    layout_manager.addLayout(layout)

    # Page size: A4 Landscape = 297 mm x 210 mm
    page = layout.pageCollection().pages()[0]
    page.setPageSize(QgsLayoutSize(297, 210, QgsUnitTypes.LayoutMillimeters))

    # 1. Map Item (Left / Center)
    map_x = 10.0
    map_y = 10.0
    map_w = 195.0
    map_h = 190.0

    map_item = QgsLayoutItemMap(layout)
    map_item.attemptMove(QgsLayoutPoint(map_x, map_y, QgsUnitTypes.LayoutMillimeters))
    map_item.attemptResize(QgsLayoutSize(map_w, map_h, QgsUnitTypes.LayoutMillimeters))
    map_item.setFrameEnabled(True)
    map_item.setFrameStrokeWidth(QgsLayoutMeasurement(0.4, QgsUnitTypes.LayoutMillimeters))
    map_item.setFrameStrokeColor(QColor("#2b2b2b"))

    # Compute Map Extent:
    # If canvas_extent provided (from active GUI), check if it covers all photos.
    # Otherwise, frame the photos + target SUNCO polygon with generous buffer.
    extent_to_use = None
    if canvas_extent and not canvas_extent.isEmpty():
        covers_all = True
        for pd in photos_data:
            if not canvas_extent.contains(QgsPointXY(pd["x"], pd["y"])):
                covers_all = False
                break
        if covers_all:
            extent_to_use = canvas_extent

    if extent_to_use is None:
        map_box = None
        cla_layers = project_instance.mapLayersByName("CLA")
        if cla_layers:
            cla = cla_layers[0]
            for f in cla.getFeatures():
                if f["CODIGO"] == TARGET_POLYGON_CODE:
                    map_box = f.geometry().boundingBox()
                    break

        if map_box is None and photos_data:
            map_box = QgsRectangle(photos_data[0]["x"], photos_data[0]["y"], photos_data[0]["x"], photos_data[0]["y"])

        for pd in photos_data:
            map_box.combineExtentWith(QgsPointXY(pd["x"], pd["y"]))

        extent_to_use = map_box.buffered(160)

    map_item.setExtent(extent_to_use)
    layout.addLayoutItem(map_item)

    # 2. Scale Bar
    scalebar = QgsLayoutItemScaleBar(layout)
    scalebar.setStyle("Single Box")
    scalebar.setUnits(QgsUnitTypes.DistanceMeters)
    scalebar.setNumberOfSegments(2)
    scalebar.setNumberOfSegmentsLeft(0)
    scalebar.setUnitsPerSegment(50)
    scalebar.setLinkedMap(map_item)
    scalebar.setUnitLabel("m")
    scalebar.setTextFormat(make_text_format("Arial", 7, color_hex="#222222"))
    scalebar.attemptMove(QgsLayoutPoint(15, 190, QgsUnitTypes.LayoutMillimeters))
    layout.addLayoutItem(scalebar)

    # 3. North Arrow
    north_arrow = QgsLayoutItemPicture(layout)
    north_arrow.setPicturePath("arrows/NorthArrow_02.svg")
    north_arrow.attemptMove(QgsLayoutPoint(188, 175, QgsUnitTypes.LayoutMillimeters))
    north_arrow.attemptResize(QgsLayoutSize(12, 16, QgsUnitTypes.LayoutMillimeters))
    north_arrow.setLinkedMap(map_item)
    layout.addLayoutItem(north_arrow)

    # 4. Header Card with Title and Subtitle
    header_box = QgsLayoutItemShape(layout)
    header_box.setShapeType(QgsLayoutItemShape.Rectangle)
    header_box.attemptMove(QgsLayoutPoint(12, 12, QgsUnitTypes.LayoutMillimeters))
    header_box.attemptResize(QgsLayoutSize(160, 15, QgsUnitTypes.LayoutMillimeters))
    header_box.setFrameEnabled(True)
    header_box.setFrameStrokeWidth(QgsLayoutMeasurement(0.2, QgsUnitTypes.LayoutMillimeters))
    header_box.setFrameStrokeColor(QColor("#CCCCCC"))
    header_box.setBackgroundColor(QColor(255, 255, 255, 230))
    header_box.setBackgroundEnabled(True)
    layout.addLayoutItem(header_box)

    title_label = QgsLayoutItemLabel(layout)
    title_label.setText("LOCALIZACIÓN FOTOGRÁFICA DE PARCELA Y ENTORNO")
    title_label.setTextFormat(make_text_format("Arial", 10, bold=True, color_hex="#1a1a1a"))
    title_label.attemptMove(QgsLayoutPoint(14, 13.5, QgsUnitTypes.LayoutMillimeters))
    title_label.attemptResize(QgsLayoutSize(155, 6, QgsUnitTypes.LayoutMillimeters))
    layout.addLayoutItem(title_label)

    sub_label = QgsLayoutItemLabel(layout)
    sub_label.setText(f"Ámbito: SUNCO {TARGET_POLYGON_CODE} | Rambla de Santa Cruz | {project_instance.crs().authid()}")
    sub_label.setTextFormat(make_text_format("Arial", 7, color_hex="#555555"))
    sub_label.attemptMove(QgsLayoutPoint(14, 19.5, QgsUnitTypes.LayoutMillimeters))
    sub_label.attemptResize(QgsLayoutSize(155, 5, QgsUnitTypes.LayoutMillimeters))
    layout.addLayoutItem(sub_label)

    # 5. Right Photos Column & Connecting Arrows
    col_x = 214.0
    photo_w = 73.0
    start_y = 12.0
    spacing_y = 66.0

    for idx, pd in enumerate(photos_data):
        cur_y = start_y + idx * spacing_y

        # Compute height based on image aspect ratio (default ~ 34.5 mm for 21:9 panoramas)
        aspect = pd["width_px"] / pd["height_px"] if pd["height_px"] > 0 else (16.0 / 9.0)
        photo_h = min(photo_w / aspect, 48.0)

        # Photo Frame
        pic = QgsLayoutItemPicture(layout)
        pic.setPicturePath(pd["path"])
        pic.attemptMove(QgsLayoutPoint(col_x, cur_y, QgsUnitTypes.LayoutMillimeters))
        pic.attemptResize(QgsLayoutSize(photo_w, photo_h, QgsUnitTypes.LayoutMillimeters))
        pic.setResizeMode(QgsLayoutItemPicture.Zoom)
        pic.setFrameEnabled(True)
        pic.setFrameStrokeWidth(QgsLayoutMeasurement(0.4, QgsUnitTypes.LayoutMillimeters))
        pic.setFrameStrokeColor(QColor("#333333"))
        layout.addLayoutItem(pic)

        # Caption Underneath
        lbl = QgsLayoutItemLabel(layout)
        dt_str = pd["datetime"] if pd["datetime"] else "Sin fecha"
        lbl.setText(f"Foto [{pd['id']}]: {pd['name']}\nCoord: {pd['lat']:.5f}°N, {abs(pd['lon']):.5f}°W  |  {dt_str}")
        lbl.setTextFormat(make_text_format("Arial", 6, color_hex="#222222"))
        lbl.attemptMove(QgsLayoutPoint(col_x, cur_y + photo_h + 1.5, QgsUnitTypes.LayoutMillimeters))
        lbl.attemptResize(QgsLayoutSize(photo_w, 9, QgsUnitTypes.LayoutMillimeters))
        layout.addLayoutItem(lbl)

        # Leader Line (Arrow)
        photo_mid_y = cur_y + photo_h / 2.0
        pt_start = QPointF(col_x, photo_mid_y)

        # Geographic target on map canvas transformed to layout paper coords
        pt_map_item = map_item.mapToItemCoords(QPointF(pd["x"], pd["y"]))
        target_paper_x = map_item.pos().x() + pt_map_item.x()
        target_paper_y = map_item.pos().y() + pt_map_item.y()

        # Stop arrowhead exactly at the perimeter of the circular badge (radius = 4.0 mm)
        bend_x = col_x - 6.0  # 6mm horizontal stub entering the map
        dx = target_paper_x - bend_x
        dy = target_paper_y - photo_mid_y
        dist = math.hypot(dx, dy)
        marker_radius = 4.0
        if dist > marker_radius:
            arrow_tip_x = target_paper_x - (dx / dist) * marker_radius
            arrow_tip_y = target_paper_y - (dy / dist) * marker_radius
        else:
            arrow_tip_x = target_paper_x
            arrow_tip_y = target_paper_y

        pt_end = QPointF(arrow_tip_x, arrow_tip_y)

        # Construct dogleg polyline: photo left edge -> stub bend -> marker perimeter
        poly = QPolygonF()
        poly.append(pt_start)
        poly.append(QPointF(bend_x, photo_mid_y))
        poly.append(pt_end)

        arrow_item = QgsLayoutItemPolyline(poly, layout)

        # Arrow styling: Vivid magenta line with directional arrowhead at the last vertex
        line_sym = QgsLineSymbol.createSimple({
            "color": "#D81B60",
            "width": "0.7",
            "joinstyle": "round",
            "capstyle": "round"
        })

        arrowhead_marker = QgsSimpleMarkerSymbolLayer.create({
            "name": "arrowhead",
            "size": "4.0",
            "color": "#D81B60",
            "stroke_color": "#FFFFFF",
            "stroke_width": "0.4",
            "angle": "0"
        })
        marker_sym = QgsMarkerSymbol()
        marker_sym.changeSymbolLayer(0, arrowhead_marker)

        marker_line = QgsMarkerLineSymbolLayer()
        marker_line.setSubSymbol(marker_sym)
        marker_line.setPlacements(QgsMarkerLineSymbolLayer.LastVertex)
        line_sym.appendSymbolLayer(marker_line)

        arrow_item.setSymbol(line_sym)
        layout.addLayoutItem(arrow_item)

    return layout


def main():
    """Main execution entry point."""
    photos_dir = DEFAULT_PHOTOS_DIR
    pdf_path = DEFAULT_OUTPUT_PDF
    png_path = DEFAULT_OUTPUT_PNG

    standalone_app = None
    if iface is None:
        # Running outside QGIS Desktop GUI
        standalone_app = QgsApplication([], False)
        standalone_app.initQgis()
        project = QgsProject.instance()
        project.read(DEFAULT_PROJECT_PATH)
        canvas_extent = None
    else:
        # Running inside QGIS Desktop GUI
        project = QgsProject.instance()
        canvas_extent = iface.mapCanvas().extent()

    try:
        print(f"[1/4] Extracting geolocated photos from: {photos_dir}")
        photos_data = extract_photos_metadata(photos_dir, project.crs(), project)
        print(f"      Found {len(photos_data)} photos. Order (North -> South):")
        for p in photos_data:
            print(f"      [{p['id']}] {p['name']} -> Lat: {p['lat']:.5f}°N, Lon: {p['lon']:.5f}°W")

        print("[2/4] Creating photo pin markers on map layer 'Fotos_Geolocalizadas'...")
        create_or_update_points_layer(project, photos_data)

        if iface:
            iface.mapCanvas().refresh()

        print("[3/4] Building A4 Landscape Print Layout with leader arrows...")
        layout = build_photo_layout(project, photos_data, canvas_extent=canvas_extent)

        print(f"[4/4] Exporting layout...")
        exporter = QgsLayoutExporter(layout)

        # Export PNG
        img_settings = QgsLayoutExporter.ImageExportSettings()
        img_settings.dpi = 150
        if os.path.exists(png_path):
            try:
                os.remove(png_path)
            except OSError:
                pass
        res_png = exporter.exportToImage(png_path, img_settings)
        if res_png == QgsLayoutExporter.Success:
            print(f"      [OK] Image exported: {png_path}")
        else:
            print(f"      [WARN] Image export returned status: {res_png}")

        # Export PDF
        pdf_settings = QgsLayoutExporter.PdfExportSettings()
        pdf_settings.dpi = 300
        res_pdf = exporter.exportToPdf(pdf_path, pdf_settings)
        if res_pdf == QgsLayoutExporter.Success:
            print(f"      [OK] PDF exported: {pdf_path}")
        else:
            print(f"      [WARN] PDF export returned status: {res_pdf}")

        # If inside QGIS GUI, open the interactive designer window
        if iface:
            iface.openLayoutDesigner(layout)
            print("      [OK] Layout Designer opened in QGIS.")

        print("[SUCCESS] Photo map report generation completed successfully.")

    finally:
        if standalone_app:
            standalone_app.exitQgis()


if __name__ == "__main__" or __name__ == "builtins":
    main()
