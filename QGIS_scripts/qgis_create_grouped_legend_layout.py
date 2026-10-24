"""
QGIS Script: Generates an A4 Print Layout with Grouped Legends.
Creates a professional print layout in A4 Landscape (or Portrait) where land
classification categories (Superclasses 1 to 5) are split into grouped legends:
- Supercategories 1 (Suelo Urbano) and 2 (Suelo Urbanizable) in the Upper Left
- Supercategories 3, 4 and 5 (Suelo Rústico) in the Lower Right

Compatible with:
- QGIS Desktop Python Console / Script Editor (opens Layout Designer automatically)
- Standalone / Headless execution via OSGeo4W python-qgis-ltr.bat
"""

import os
import sys

from qgis.core import (
    QgsApplication,
    QgsProject,
    QgsPrintLayout,
    QgsLayoutItemPage,
    QgsLayoutItemMap,
    QgsLayoutItemLegend,
    QgsLayoutItemLabel,
    QgsLayoutItemShape,
    QgsLayoutItemScaleBar,
    QgsLayoutItemPicture,
    QgsLegendRenderer,
    QgsLegendStyle,
    QgsMapLayerLegendUtils,
    QgsLayerTree,
    QgsLayoutSize,
    QgsLayoutPoint,
    QgsUnitTypes,
    QgsLayoutMeasurement,
    QgsLayoutItem,
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
DEFAULT_OUTPUT_PDF = os.path.join(OUTPUT_DIR, "Plano_Clasificacion_Suelo_A4.pdf")
DEFAULT_OUTPUT_PNG = os.path.join(OUTPUT_DIR, "Plano_Clasificacion_Suelo_A4.png")

LAYOUT_NAME = "Plano_Clasificacion_Suelo_A4"
TARGET_LAYER_NAME = "CLA"
MASK_LAYER_NAME = "Mask_Nucleo_SantaCruz"

# Layout Orientation: "Landscape" (297x210 mm) or "Portrait" (210x297 mm)
ORIENTATION = "Landscape"

# Titles
MAP_TITLE = "PLAN GENERAL DE ORDENACIÓN"
MAP_SUBTITLE = "Santa Cruz de Tenerife · Clasificación del Suelo"
LEGEND_1_TITLE = "SUELO URBANO Y URBANIZABLE"
LEGEND_2_TITLE = "SUELO RÚSTICO"

# Superclasses assigned to Legend 1 (Upper Left)
# All others automatically go to Legend 2 (Lower Right)
GROUP_1_PREFIXES = ("1.", "2.")

# Export DPI settings
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


def find_target_layer(project, layer_name):
    """Finds a layer by name in the given QgsProject instance."""
    layers = project.mapLayersByName(layer_name)
    if not layers:
        for lyr in project.mapLayers().values():
            if lyr.name().strip().lower() == layer_name.strip().lower():
                return lyr
        raise RuntimeError(f"Layer '{layer_name}' not found in active QGIS project.")
    return layers[0]


def partition_legend_node_indices(layer, group1_prefixes=GROUP_1_PREFIXES):
    """
    Dynamically inspects the rule-based renderer of the target layer
    and partitions the legend node indices into two groups based on
    the supercategory prefixes.

    Returns:
        tuple (group1_indices, group2_indices)
    """
    renderer = layer.renderer()
    group1_indices = []
    group2_indices = []

    if hasattr(renderer, "rootRule") and renderer.rootRule():
        node_idx = 0
        for rule in renderer.rootRule().children():
            label = rule.label().strip()
            is_group1 = any(label.startswith(p) for p in group1_prefixes)

            # Top-level group rule node
            if is_group1:
                group1_indices.append(node_idx)
            else:
                group2_indices.append(node_idx)
            node_idx += 1

            # Child symbol rules
            for _ in rule.children():
                if is_group1:
                    group1_indices.append(node_idx)
                else:
                    group2_indices.append(node_idx)
                node_idx += 1
    else:
        # Fallback for simple layers
        group1_indices = [0]
        group2_indices = []

    return group1_indices, group2_indices


def create_styled_legend(
    layout,
    map_item,
    layer,
    node_indices,
    title_text,
    column_count=1
):
    """
    Creates and configures a QgsLayoutItemLegend with a filtered subset of layer rules,
    hidden layer title, and a polished card aesthetic.
    """
    legend = QgsLayoutItemLegend(layout)
    legend.setLinkedMap(map_item)
    legend.setAutoUpdateModel(False)
    legend.setTitle(title_text)

    # Columns configuration
    legend.setColumnCount(column_count)
    if column_count > 1:
        legend.setSplitLayer(True)
        legend.setEqualColumnWidth(True)
        legend.setColumnSpace(3.0)

    # Card appearance
    legend.setBackgroundColor(QColor(255, 255, 255, 240))
    legend.setBackgroundEnabled(True)
    legend.setFrameEnabled(True)
    legend.setFrameStrokeWidth(QgsLayoutMeasurement(0.25, QgsUnitTypes.LayoutMillimeters))
    legend.setFrameStrokeColor(QColor("#b0bec5"))

    # Symbol and spacing metrics
    legend.setSymbolWidth(4.5)
    legend.setSymbolHeight(3.2)
    legend.setBoxSpace(3.0)

    # Clean typography
    legend.rstyle(QgsLegendStyle.Title).setTextFormat(make_text_format("Segoe UI", 8, bold=True, color_hex="#1a237e"))
    legend.rstyle(QgsLegendStyle.Group).setTextFormat(make_text_format("Segoe UI", 7, bold=True, color_hex="#263238"))
    legend.rstyle(QgsLegendStyle.Subgroup).setTextFormat(make_text_format("Segoe UI", 7, bold=True, color_hex="#263238"))
    legend.rstyle(QgsLegendStyle.SymbolLabel).setTextFormat(make_text_format("Segoe UI", 6, color_hex="#37474f"))

    legend.setStyleMargin(QgsLegendStyle.Title, QgsLegendStyle.Bottom, 1.5)
    legend.setStyleMargin(QgsLegendStyle.Group, QgsLegendStyle.Top, 2.0)
    legend.setStyleMargin(QgsLegendStyle.Group, QgsLegendStyle.Bottom, 1.0)

    # Use the legend model's existing root group to ensure solid C++ memory ownership
    root = legend.model().rootGroup()
    root.clear()
    layer_node = root.addLayer(layer)
    QgsLegendRenderer.setNodeLegendStyle(layer_node, QgsLegendStyle.Hidden)
    QgsMapLayerLegendUtils.setLegendNodeOrder(layer_node, node_indices)
    legend.model().refreshLayerLegend(layer_node)

    return legend


def build_grouped_legend_layout(
    project,
    canvas_extent=None,
    orientation=ORIENTATION,
    layout_name=LAYOUT_NAME
):
    """
    Builds the complete A4 Print Layout with grouped legends, title card,
    scale bar, and north arrow.
    """
    target_layer = find_target_layer(project, TARGET_LAYER_NAME)

    # Partition the superclasses dynamically
    group1_indices, group2_indices = partition_legend_node_indices(
        target_layer, GROUP_1_PREFIXES
    )

    # Reset or create layout
    layout_manager = project.layoutManager()
    old_layout = layout_manager.layoutByName(layout_name)
    if old_layout:
        layout_manager.removeLayout(old_layout)

    layout = QgsPrintLayout(project)
    layout.initializeDefaults()
    layout.setName(layout_name)
    layout_manager.addLayout(layout)

    # Page Dimensions
    page = layout.pageCollection().pages()[0]
    if orientation.lower() == "portrait":
        page_w, page_h = 210.0, 297.0
    else:
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

    # Determine extent: use current on-screen canvas extent if available, else mask or layer extent
    if canvas_extent and not canvas_extent.isEmpty():
        map_item.zoomToExtent(canvas_extent)
    else:
        # Check for Mask_Nucleo_SantaCruz to frame the urban nucleus
        mask_layers = project.mapLayersByName(MASK_LAYER_NAME)
        if mask_layers:
            mask_ext = mask_layers[0].extent()
            map_item.zoomToExtent(mask_ext.buffered(400))
        else:
            layer_extent = target_layer.extent()
            map_item.zoomToExtent(layer_extent.buffered(layer_extent.width() * 0.05))

    layout.addLayoutItem(map_item)

    # 2. Header Card with Title & Subtitle (Upper Left)
    header_x = margin + 4.0
    header_y = margin + 4.0
    header_w = 100.0
    header_h = 16.0

    header_box = QgsLayoutItemShape(layout)
    header_box.setShapeType(QgsLayoutItemShape.Rectangle)
    header_box.attemptMove(QgsLayoutPoint(header_x, header_y, QgsUnitTypes.LayoutMillimeters))
    header_box.attemptResize(QgsLayoutSize(header_w, header_h, QgsUnitTypes.LayoutMillimeters))
    header_box.setFrameEnabled(True)
    header_box.setFrameStrokeWidth(QgsLayoutMeasurement(0.25, QgsUnitTypes.LayoutMillimeters))
    header_box.setFrameStrokeColor(QColor("#b0bec5"))
    header_box.setBackgroundColor(QColor(255, 255, 255, 240))
    header_box.setBackgroundEnabled(True)
    layout.addLayoutItem(header_box)

    title_lbl = QgsLayoutItemLabel(layout)
    title_lbl.setText(MAP_TITLE)
    title_lbl.setTextFormat(make_text_format("Segoe UI", 9, bold=True, color_hex="#1a1a1a"))
    title_lbl.attemptMove(QgsLayoutPoint(header_x + 2.0, header_y + 1.5, QgsUnitTypes.LayoutMillimeters))
    title_lbl.attemptResize(QgsLayoutSize(header_w - 4.0, 5.5, QgsUnitTypes.LayoutMillimeters))
    layout.addLayoutItem(title_lbl)

    sub_lbl = QgsLayoutItemLabel(layout)
    sub_lbl.setText(MAP_SUBTITLE)
    sub_lbl.setTextFormat(make_text_format("Segoe UI", 7, italic=True, color_hex="#546e7a"))
    sub_lbl.attemptMove(QgsLayoutPoint(header_x + 2.0, header_y + 7.5, QgsUnitTypes.LayoutMillimeters))
    sub_lbl.attemptResize(QgsLayoutSize(header_w - 4.0, 5.0, QgsUnitTypes.LayoutMillimeters))
    layout.addLayoutItem(sub_lbl)

    # 3. Legend 1: Supercategories 1 & 2 (Upper Left, directly below Header Card)
    leg1 = create_styled_legend(
        layout,
        map_item,
        target_layer,
        group1_indices,
        LEGEND_1_TITLE,
        column_count=1
    )
    leg1_y = header_y + header_h + 3.0
    leg1.attemptMove(QgsLayoutPoint(header_x, leg1_y, QgsUnitTypes.LayoutMillimeters))
    layout.addLayoutItem(leg1)
    leg1.adjustBoxSize()

    # 4. Legend 2: Supercategories 3, 4 & 5 (Lower Right)
    leg2 = create_styled_legend(
        layout,
        map_item,
        target_layer,
        group2_indices,
        LEGEND_2_TITLE,
        column_count=1
    )
    # Position in the lower-right area inside map boundaries
    # Standard width ~60mm, height ~78mm.
    # Placed at (x=224, y=118) in Landscape A4 to ensure 6mm padding inside the map frame
    if orientation.lower() == "portrait":
        leg2_x = page_w - margin - 68.0
        leg2_y = page_h - margin - 90.0
    else:
        leg2_x = page_w - margin - 65.0
        leg2_y = page_h - margin - 88.0

    leg2.attemptMove(QgsLayoutPoint(leg2_x, leg2_y, QgsUnitTypes.LayoutMillimeters))
    layout.addLayoutItem(leg2)
    leg2.adjustBoxSize()

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
    scalebar_y = page_h - margin - 22.0
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
    north.setPicturePath("arrows/NorthArrow_02.svg")
    north_x = page_w - margin - 19.0
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
        print(f"[1/3] Building A4 {ORIENTATION} layout with grouped legends...")
        layout = build_grouped_legend_layout(
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
