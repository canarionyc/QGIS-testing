"""
QGIS Script: Generates an A4 Landscape Print Layout for Planeamiento Vigente.
Uses the active WMS layers from Grafcan (IDECanarias):
- Ámbitos en suspensión (SUSP)
- Categoría y subcategoría del suelo (CLA)
Along with their official WMS GetLegendGraphic images embedded directly as layout picture cards,
guaranteeing high visual quality and 100% crash-free stability (no C++/SIP QgsLegendModel issues).

Compatible with:
- QGIS Desktop Python Console / MCP execution (opens Layout Designer automatically)
- Standalone / Headless execution via OSGeo4W python-qgis-ltr.bat
"""

import os
import sys
import urllib.request

from qgis.core import (
    QgsApplication,
    QgsProject,
    QgsPrintLayout,
    QgsLayoutItemPage,
    QgsLayoutItemMap,
    QgsLayoutItemLabel,
    QgsLayoutItemShape,
    QgsLayoutItemScaleBar,
    QgsLayoutItemPicture,
    QgsLayoutSize,
    QgsLayoutPoint,
    QgsUnitTypes,
    QgsLayoutMeasurement,
    QgsLayoutExporter,
    QgsTextFormat,
)
from PyQt5.QtGui import QColor, QFont

# Optional iface import when running inside QGIS GUI
try:
    from qgis.utils import iface
except ImportError:
    iface = None


# ==============================================================================
# CONFIGURATION
# ==============================================================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_PROJECT_PATH = os.path.join(
    BASE_DIR, "QGIS_projects", "Santa Cruz de Tenerife", "Santa Cruz de Tenerife.qgz"
)
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
DEFAULT_OUTPUT_PDF = os.path.join(OUTPUT_DIR, "Plano_Planeamiento_Vigente_A4.pdf")
DEFAULT_OUTPUT_PNG = os.path.join(OUTPUT_DIR, "Plano_Planeamiento_Vigente_A4.png")

LAYOUT_NAME = "Plano_Planeamiento_Vigente_A4"
MASK_LAYER_NAME = "Mask_Nucleo_SantaCruz"

# Legend Image URLs from Grafcan WMS GetLegendGraphic endpoint
WMS_BASE_URL = "https://idecan2.grafcan.es/ServicioWMS/Planeamiento"
LEGEND_URLS = {
    "SUSP": f"{WMS_BASE_URL}?SERVICE=WMS&REQUEST=GetLegendGraphic&VERSION=1.1.1&FORMAT=image/png&LAYER=SUSP",
    "CLA": f"{WMS_BASE_URL}?SERVICE=WMS&REQUEST=GetLegendGraphic&VERSION=1.1.1&FORMAT=image/png&LAYER=CLA"
}

ORIENTATION = "Landscape"
DPI_PNG = 150
DPI_PDF = 300


# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def make_text_format(font_family="Segoe UI", point_size=8, bold=False, italic=False, color_hex="#222222"):
    """Creates a QgsTextFormat with clean typography."""
    tf = QgsTextFormat()
    font = QFont(font_family, int(point_size))
    font.setBold(bold)
    font.setItalic(italic)
    tf.setFont(font)
    tf.setSize(point_size)
    tf.setColor(QColor(color_hex))
    return tf


def ensure_wms_legend_images(target_dir):
    """
    Downloads and caches the official WMS GetLegendGraphic images from Grafcan.
    Returns a dict with local file paths.
    """
    os.makedirs(target_dir, exist_ok=True)
    paths = {}
    for code, url in LEGEND_URLS.items():
        local_path = os.path.join(target_dir, f"legend_{code}.png")
        if not os.path.exists(local_path) or os.path.getsize(local_path) == 0:
            print(f"[INFO] Downloading WMS legend graphic for {code} from {url}...")
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
            with urllib.request.urlopen(req, timeout=20) as resp, open(local_path, "wb") as fh:
                fh.write(resp.read())
        paths[code] = local_path
    return paths


def create_legend_card(layout, x, y, width, height, title, subtitle, image_path, img_w, img_h, accent_color="#1a237e"):
    """
    Creates a styled card containing a title header, optional subtitle, and an embedded WMS legend image.
    Uses native QgsLayoutItemPicture to ensure 100% crash-free stability.
    """
    # 1. Background Box Card
    box = QgsLayoutItemShape(layout)
    box.setShapeType(QgsLayoutItemShape.Rectangle)
    box.attemptMove(QgsLayoutPoint(x, y, QgsUnitTypes.LayoutMillimeters))
    box.attemptResize(QgsLayoutSize(width, height, QgsUnitTypes.LayoutMillimeters))
    box.setFrameEnabled(True)
    box.setFrameStrokeWidth(QgsLayoutMeasurement(0.25, QgsUnitTypes.LayoutMillimeters))
    box.setFrameStrokeColor(QColor("#b0bec5"))
    box.setBackgroundColor(QColor(255, 255, 255, 245))
    box.setBackgroundEnabled(True)
    layout.addLayoutItem(box)

    # 2. Card Title
    title_lbl = QgsLayoutItemLabel(layout)
    title_lbl.setText(title)
    title_lbl.setTextFormat(make_text_format("Segoe UI", 7.5, bold=True, color_hex=accent_color))
    title_lbl.attemptMove(QgsLayoutPoint(x + 3.0, y + 2.0, QgsUnitTypes.LayoutMillimeters))
    title_lbl.attemptResize(QgsLayoutSize(width - 6.0, 5.0, QgsUnitTypes.LayoutMillimeters))
    layout.addLayoutItem(title_lbl)

    current_y = y + 7.0

    # 3. Optional Subtitle
    if subtitle:
        sub_lbl = QgsLayoutItemLabel(layout)
        sub_lbl.setText(subtitle)
        sub_lbl.setTextFormat(make_text_format("Segoe UI", 6.0, italic=True, color_hex="#546e7a"))
        sub_lbl.attemptMove(QgsLayoutPoint(x + 3.0, current_y, QgsUnitTypes.LayoutMillimeters))
        sub_lbl.attemptResize(QgsLayoutSize(width - 6.0, 4.0, QgsUnitTypes.LayoutMillimeters))
        layout.addLayoutItem(sub_lbl)
        current_y += 4.5

    # 4. Legend Picture Item
    pic = QgsLayoutItemPicture(layout)
    pic.setPicturePath(image_path)
    pic.setResizeMode(QgsLayoutItemPicture.Zoom)
    pic.attemptMove(QgsLayoutPoint(x + (width - img_w) / 2.0, current_y, QgsUnitTypes.LayoutMillimeters))
    pic.attemptResize(QgsLayoutSize(img_w, img_h, QgsUnitTypes.LayoutMillimeters))
    layout.addLayoutItem(pic)

    return box


def build_planeamiento_vigente_layout(
    project,
    canvas_extent=None,
    orientation=ORIENTATION,
    layout_name=LAYOUT_NAME
):
    """
    Builds the complete A4 Print Layout for Planeamiento Vigente with official WMS legend cards.
    """
    legends_dir = os.path.join(BASE_DIR, "img", "legends")
    legend_paths = ensure_wms_legend_images(legends_dir)

    # Reset or create layout
    layout_manager = project.layoutManager()
    old_layout = layout_manager.layoutByName(layout_name)
    if old_layout:
        layout_manager.removeLayout(old_layout)

    layout = QgsPrintLayout(project)
    layout.initializeDefaults()
    layout.setName(layout_name)
    layout_manager.addLayout(layout)

    # Page Dimensions: A4 Landscape (297 x 210 mm)
    page = layout.pageCollection().pages()[0]
    page_w, page_h = 297.0, 210.0
    page.setPageSize(QgsLayoutSize(page_w, page_h, QgsUnitTypes.LayoutMillimeters))

    # Margin around the map
    margin = 8.0
    map_w = page_w - (2 * margin)
    map_h = page_h - (2 * margin)

    # 1. Main Map Item
    map_item = QgsLayoutItemMap(layout)
    map_item.attemptMove(QgsLayoutPoint(margin, margin, QgsUnitTypes.LayoutMillimeters))
    map_item.attemptResize(QgsLayoutSize(map_w, map_h, QgsUnitTypes.LayoutMillimeters))
    map_item.setFrameEnabled(True)
    map_item.setFrameStrokeWidth(QgsLayoutMeasurement(0.35, QgsUnitTypes.LayoutMillimeters))
    map_item.setFrameStrokeColor(QColor("#2b2b2b"))

    # Determine extent: use current on-screen canvas extent if available, else mask layer extent
    if canvas_extent and not canvas_extent.isEmpty():
        map_item.zoomToExtent(canvas_extent)
    else:
        mask_layers = project.mapLayersByName(MASK_LAYER_NAME)
        if mask_layers:
            mask_ext = mask_layers[0].extent()
            map_item.zoomToExtent(mask_ext.buffered(400))
        else:
            map_item.zoomToExtent(project.viewExtent())

    layout.addLayoutItem(map_item)

    # 2. Header Card with Title & Subtitle (Upper Left)
    header_x = margin + 4.0
    header_y = margin + 4.0
    header_w = 110.0
    header_h = 20.0

    header_box = QgsLayoutItemShape(layout)
    header_box.setShapeType(QgsLayoutItemShape.Rectangle)
    header_box.attemptMove(QgsLayoutPoint(header_x, header_y, QgsUnitTypes.LayoutMillimeters))
    header_box.attemptResize(QgsLayoutSize(header_w, header_h, QgsUnitTypes.LayoutMillimeters))
    header_box.setFrameEnabled(True)
    header_box.setFrameStrokeWidth(QgsLayoutMeasurement(0.25, QgsUnitTypes.LayoutMillimeters))
    header_box.setFrameStrokeColor(QColor("#b0bec5"))
    header_box.setBackgroundColor(QColor(255, 255, 255, 245))
    header_box.setBackgroundEnabled(True)
    layout.addLayoutItem(header_box)

    title_lbl = QgsLayoutItemLabel(layout)
    title_lbl.setText("PLANEAMIENTO VIGENTE")
    title_lbl.setTextFormat(make_text_format("Segoe UI", 9.5, bold=True, color_hex="#1a1a1a"))
    title_lbl.attemptMove(QgsLayoutPoint(header_x + 3.0, header_y + 2.0, QgsUnitTypes.LayoutMillimeters))
    title_lbl.attemptResize(QgsLayoutSize(header_w - 6.0, 5.5, QgsUnitTypes.LayoutMillimeters))
    layout.addLayoutItem(title_lbl)

    sub_lbl = QgsLayoutItemLabel(layout)
    sub_lbl.setText("Santa Cruz de Tenerife · Clasificación y Ámbitos en Suspensión")
    sub_lbl.setTextFormat(make_text_format("Segoe UI", 7.0, italic=True, color_hex="#37474f"))
    sub_lbl.attemptMove(QgsLayoutPoint(header_x + 3.0, header_y + 8.0, QgsUnitTypes.LayoutMillimeters))
    sub_lbl.attemptResize(QgsLayoutSize(header_w - 6.0, 4.5, QgsUnitTypes.LayoutMillimeters))
    layout.addLayoutItem(sub_lbl)

    meta_lbl = QgsLayoutItemLabel(layout)
    meta_lbl.setText("Servicio WMS IDECanarias (GRAFCAN) · CRS: EPSG:4083 (REGCAN95 / UTM 28N)")
    meta_lbl.setTextFormat(make_text_format("Segoe UI", 5.5, italic=False, color_hex="#78909c"))
    meta_lbl.attemptMove(QgsLayoutPoint(header_x + 3.0, header_y + 13.5, QgsUnitTypes.LayoutMillimeters))
    meta_lbl.attemptResize(QgsLayoutSize(header_w - 6.0, 4.0, QgsUnitTypes.LayoutMillimeters))
    layout.addLayoutItem(meta_lbl)

    # 3. Card 1: Ámbitos en Suspensión Legend (Upper Left, placed directly below header)
    # Original image is 655 x 125 px (aspect ratio: 5.24 : 1).
    # Width = 84 mm -> Height = 84 / 5.24 = 16.0 mm. Total card h = 28 mm.
    susp_card_w = 90.0
    susp_card_h = 28.0
    susp_card_y = header_y + header_h + 3.0
    create_legend_card(
        layout,
        x=header_x,
        y=susp_card_y,
        width=susp_card_w,
        height=susp_card_h,
        title="ÁMBITOS EN SUSPENSIÓN (TSJC)",
        subtitle="Áreas con ordenación suspendida por resolución judicial",
        image_path=legend_paths["SUSP"],
        img_w=84.0,
        img_h=16.0,
        accent_color="#b71c1c"  # Red accent to match suspension styling
    )

    # 4. Card 2: Categoría y Subcategoría del Suelo Legend (Lower Right, in open ocean margin)
    # Original image is 361 x 625 px (aspect ratio: 0.5776 : 1, h/w = 1.731).
    # Width = 56 mm -> Height = 56 * 1.731 = 96.9 mm. Total card h = 112 mm.
    cla_card_w = 64.0
    cla_card_h = 112.0
    cla_card_x = page_w - margin - cla_card_w - 4.0   # ~221 mm
    cla_card_y = page_h - margin - cla_card_h - 4.0   # ~86 mm
    create_legend_card(
        layout,
        x=cla_card_x,
        y=cla_card_y,
        width=cla_card_w,
        height=cla_card_h,
        title="CLASIFICACIÓN DEL SUELO",
        subtitle="Categoría y subcategoría del suelo",
        image_path=legend_paths["CLA"],
        img_w=56.0,
        img_h=97.0,
        accent_color="#1a237e"  # Deep blue accent
    )

    # 5. Scale Bar (Bottom Left)
    scalebar = QgsLayoutItemScaleBar(layout)
    scalebar.setStyle("Single Box")
    scalebar.setUnits(QgsUnitTypes.DistanceKilometers)
    scalebar.setNumberOfSegments(2)
    scalebar.setNumberOfSegmentsLeft(0)
    scalebar.setUnitsPerSegment(1)
    scalebar.setUnitLabel("km")
    scalebar.setTextFormat(make_text_format("Segoe UI", 7, color_hex="#263238"))
    scalebar.setLinkedMap(map_item)
    scalebar_y = page_h - margin - 20.0
    scalebar.attemptMove(QgsLayoutPoint(header_x, scalebar_y, QgsUnitTypes.LayoutMillimeters))
    scalebar.setBoxContentSpace(2.0)
    scalebar.setBackgroundColor(QColor(255, 255, 255, 220))
    scalebar.setBackgroundEnabled(True)
    scalebar.setFrameEnabled(True)
    scalebar.setFrameStrokeWidth(QgsLayoutMeasurement(0.2, QgsUnitTypes.LayoutMillimeters))
    scalebar.setFrameStrokeColor(QColor("#cccccc"))
    layout.addLayoutItem(scalebar)

    # 6. North Arrow (Top Right)
    north = QgsLayoutItemPicture(layout)
    north_svg_candidates = [
        r"C:\OSGeo4W\apps\qgis-ltr\svg\arrows\NorthArrow_02.svg",
        r"C:\OSGeo4W\apps\qgis-ltr\svg\arrows\NorthArrow_01.svg",
        "arrows/NorthArrow_02.svg"
    ]
    for candidate in north_svg_candidates:
        if os.path.exists(candidate):
            north.setPicturePath(candidate)
            break
    else:
        north.setPicturePath("arrows/NorthArrow_02.svg")

    north_x = page_w - margin - 18.0
    north_y = margin + 4.0
    north.attemptMove(QgsLayoutPoint(north_x, north_y, QgsUnitTypes.LayoutMillimeters))
    north.attemptResize(QgsLayoutSize(12.0, 16.0, QgsUnitTypes.LayoutMillimeters))
    north.setLinkedMap(map_item)
    layout.addLayoutItem(north)

    return layout


def export_layout(layout, png_path=DEFAULT_OUTPUT_PNG, pdf_path=DEFAULT_OUTPUT_PDF):
    """Exports the given layout to PNG and PDF formats."""
    exporter = QgsLayoutExporter(layout)

    # Export PNG
    if png_path:
        os.makedirs(os.path.dirname(png_path), exist_ok=True)
        if os.path.exists(png_path):
            try:
                os.remove(png_path)
            except OSError:
                pass
        img_settings = QgsLayoutExporter.ImageExportSettings()
        img_settings.dpi = DPI_PNG
        res_png = exporter.exportToImage(png_path, img_settings)
        if res_png == QgsLayoutExporter.Success:
            print(f"[OK] PNG image exported: {png_path} ({DPI_PNG} DPI)")
        else:
            print(f"[WARN] PNG export returned status: {res_png}")

    # Export PDF
    if pdf_path:
        os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
        if os.path.exists(pdf_path):
            try:
                os.remove(pdf_path)
            except OSError:
                pass
        pdf_settings = QgsLayoutExporter.PdfExportSettings()
        pdf_settings.dpi = DPI_PDF
        res_pdf = exporter.exportToPdf(pdf_path, pdf_settings)
        if res_pdf == QgsLayoutExporter.Success:
            print(f"[OK] PDF vector map exported: {pdf_path}")
        else:
            print(f"[WARN] PDF export returned status: {res_pdf}")


def main():
    """Main execution entry point."""
    standalone_app = None

    if iface is None:
        # Running outside QGIS GUI (Standalone / Headless)
        print("[INIT] Starting standalone QGIS application...")
        QgsApplication.setPrefixPath(r"C:\OSGeo4W\apps\qgis-ltr", True)
        standalone_app = QgsApplication([], False)
        standalone_app.initQgis()

        project = QgsProject.instance()
        if not project.read(DEFAULT_PROJECT_PATH):
            raise RuntimeError(f"Could not load project: {DEFAULT_PROJECT_PATH}")
        canvas_extent = None
    else:
        # Running inside QGIS Desktop GUI
        project = QgsProject.instance()
        canvas_extent = iface.mapCanvas().extent()

    try:
        print(f"[1/3] Building A4 {ORIENTATION} layout for Planeamiento Vigente...")
        layout = build_planeamiento_vigente_layout(
            project,
            canvas_extent=canvas_extent,
            orientation=ORIENTATION,
            layout_name=LAYOUT_NAME
        )

        # Persist layout to project file
        project.write()

        print("[2/3] Exporting print layout to PNG and PDF...")
        export_layout(layout, png_path=DEFAULT_OUTPUT_PNG, pdf_path=DEFAULT_OUTPUT_PDF)

        # In GUI mode, open Layout Designer for interactive viewing/editing
        if iface:
            print("[3/3] Opening Layout Designer in QGIS...")
            iface.openLayoutDesigner(layout)

        print(f"[SUCCESS] Layout '{LAYOUT_NAME}' successfully created, saved to project, and exported.")

    finally:
        if standalone_app:
            standalone_app.exitQgis()


if __name__ == "__main__" or __name__ == "builtins":
    main()
