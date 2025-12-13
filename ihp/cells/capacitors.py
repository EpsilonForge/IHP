"""Capacitor components for IHP PDK."""

import gdsfactory as gf
from gdsfactory import Component
from gdsfactory.typings import LayerSpec, LayerSpecs

import math

def add_rect(component, size: tuple[float, float], layer: LayerSpec, origin: tuple[float, float], centered: bool = False):
    """Create rectangle, add ref to component and move to origin, return ref."""
    rect = gf.components.rectangle(size=size, layer=layer, centered=centered)
    ref = component.add_ref(rect)
    ref.move(origin)
    return ref


@gf.cell
def cmim(
    width: float = 6.99,
    length: float = 6.99,
    capacitance: float | None = None,
    model: str = "cmim",
    layer_metal5: LayerSpec = "Metal5drawing",
    layer_mim: LayerSpec = "MIMdrawing",
    layer_topmetal1: LayerSpec = "TopMetal1drawing",
    layer_vmim: LayerSpec = "Vmimdrawing",
) -> Component:
    """Create an MIM (Metal-Insulator-Metal) capacitor.

    Args:
        width: MIM plate X-size (um). Scales the MIM/top-plate in X.
        length: MIM plate Y-size (um). Scales the MIM/top-plate in Y.
        capacitance: Optional (kept for compatibility; not used for geometry).
        model: Device model name stored in metadata.
        layer_metal5: Metal5 drawing layer.
        layer_mim: MIM dielectric layer.
        layer_topmetal1: TopMetal1 drawing layer.
        layer_vmim: Vmimdrawing (small tile) layer.

    Returns:
        MIM capacitor component.
    """
    c = Component()

    # Geometrical constants
    METAL_5_MIM_MARGIN = 0.6
    METAL_1_MIM_MARGIN = 0.34
    metal_1_mim_margin_x = -0.004 * width + 0.625
    VMIM_TILE_LENGTH = 0.42
    VMIM_TILE_GAP = 0.84
    GRID_STEP = 0.005

    # Grid snapping
    length = round(length / GRID_STEP) * GRID_STEP
    width = round(width / GRID_STEP) * GRID_STEP

    # Calculate capacitance
    if capacitance is None:
        CAP_DENSITY = 1.54
        area = width * length
        capacitance = area * CAP_DENSITY

    # Draw MIM layer (X = width, Y = length)
    add_rect(c, size=(width, length), layer=layer_mim, origin=(0.0, 0.0))

    # Draw Metal5 layers (bottom plate, margin around MIM)
    metal_5_size_x = width + 2 * METAL_5_MIM_MARGIN
    metal_5_size_y = length + 2 * METAL_5_MIM_MARGIN
    add_rect(
        c,
        size=(metal_5_size_x, metal_5_size_y),
        layer=layer_metal5,
        origin=(-METAL_5_MIM_MARGIN, -METAL_5_MIM_MARGIN),
    )

    # Draw TopMetal1 layers (top plate, inset from MIM)
    metal_1_size_x = width - 2 * metal_1_mim_margin_x
    metal_1_size_y = length - 2 * METAL_1_MIM_MARGIN
    add_rect(
        c,
        size=(metal_1_size_x, metal_1_size_y),
        layer=layer_topmetal1,
        origin=(metal_1_mim_margin_x, METAL_1_MIM_MARGIN),
    )

    # Draw VMIM tiles inside the top plate
    metal_1_vmim_margin = VMIM_TILE_LENGTH
    tile_pitch = VMIM_TILE_LENGTH + VMIM_TILE_GAP
    usable_x = width - 2 * metal_1_vmim_margin
    usable_y = length - 2 * metal_1_vmim_margin

    # Calculate number of tiles
    n_tiles_x = max(int(math.floor((usable_x + VMIM_TILE_GAP) / tile_pitch)), 0)
    n_tiles_y = max(int(math.floor((usable_y + VMIM_TILE_GAP) / tile_pitch)), 0)

    for ix in range(n_tiles_x):
        for iy in range(n_tiles_y):
            x = METAL_1_MIM_MARGIN + metal_1_vmim_margin + ix * tile_pitch
            y = METAL_1_MIM_MARGIN + metal_1_vmim_margin + iy * tile_pitch
            add_rect(
                c,
                size=(VMIM_TILE_LENGTH, VMIM_TILE_LENGTH),
                layer=layer_vmim,
                origin=(x, y),
            )

    # Add Metal5 port (P1) at plate center
    c.add_port(
        name="P1",
        center=(
            -METAL_5_MIM_MARGIN + metal_5_size_x / 2.0,
            -METAL_5_MIM_MARGIN + metal_5_size_y / 2.0,
        ),
        width=min(metal_5_size_x, metal_5_size_y),
        orientation=180,
        layer=layer_metal5,
        port_type="electrical",
    )

    # Add TopMetal1 port (P2) at plate center
    c.add_port(
        name="P2",
        center=(
            METAL_1_MIM_MARGIN + metal_1_size_x / 2.0,
            METAL_1_MIM_MARGIN + metal_1_size_y / 2.0,
        ),
        width=min(metal_1_size_x, metal_1_size_y),
        orientation=0,
        layer=layer_topmetal1,
        port_type="electrical",
    )

    # Metadata
    c.info.update(
        {
            "model": model,
            "capacitance": capacitance,
            "mim_length": length,
            "mim_width": width,
            "vmim_tile_length": VMIM_TILE_LENGTH,
            "n_vmim_tiles": (n_tiles_x, n_tiles_y),
        }
    )

    return c


@gf.cell
def rfcmim(
    width: float = 7.0,
    length: float = 7.0,
    capacitance: float | None = None,
    model: str = "rfcmim",
    layer_activ: LayerSpec = "Activdrawing",
    layer_mim: LayerSpec = "MIMdrawing",
    layer_metal1: LayerSpec = "Metal1drawing",
    layer_metal1_pin: LayerSpec = "Metal1pin",
    layer_metal5: LayerSpec = "Metal5drawing",
    layer_metal5_pin: LayerSpec = "Metal5pin",
    layer_topmetal1: LayerSpec = "TopMetal1drawing",
    layer_topmetal1_pin: LayerSpec = "TopMetal1pin",
    layer_vmim: LayerSpec = "Vmimdrawing",
    layer_cont: LayerSpec = "Contdrawing",
    layer_psd: LayerSpec = "pSDdrawing",
    layer_pwellblock: LayerSpec = "PWellblock",
    layers_no_qrc: LayerSpecs = (
        "Activnoqrc",
        "TopMetal1noqrc",
        "Metal1noqrc",
        "Metal2noqrc",
        "Metal3noqrc",
        "Metal4noqrc",
        "Metal5noqrc",
    ),
) -> Component:
    """
    Create an RF MIM capacitor (empty scaffold).

    Args:
        width: Capacitor width in micrometers.
        length: Capacitor length in micrometers.
        capacitance: Target capacitance in fF (optional).
        model: Model name for metadata.
        layer_activ: Active diffusion drawing layer.
        layer_mim: MIM dielectric layer.
        layer_metal1: Metal1 drawing layer.
        layer_metal1_pin: Metal1 pin layer.
        layer_metal5: Metal5 drawing layer.
        layer_metal5_pin: Metal5 pin layer.
        layer_topmetal1: TopMetal1 drawing layer.
        layer_topmetal1_pin: TopMetal1 pin layer.
        layer_vmim: Vmim tile layer.
        layer_cont: Contact drawing layer.
        layer_psd: P-sub diffusion drawing layer.
        layer_pwellblock: P-well block mask.
        layers_no_qrc: No quantitative RC extraction layers

    Returns:
        Model of RF MIM capacitor
    """
    c = Component()

    # Geometrical constants
    MIM_METAL_5_MARGIN = 0.6
    MIM_PWELL_MARGIN = 3
    NO_QRC_PWELL_MARGIN = 2.6

    # Grid snapping
    length = round(length / 0.005) * 0.005
    width = round(width / 0.005) * 0.005

    # Calculate capacitance
    if capacitance is None:
        CAP_DENSITY = 1.54
        area = width * length
        capacitance = area * CAP_DENSITY

    # MIM layer
    add_rect(c, (length, width), layer_mim, origin=(0, 0))

    # PWell block layer
    p_well_length = 2 * MIM_PWELL_MARGIN + length
    p_well_width = 2 * MIM_PWELL_MARGIN + width
    p_well_corner = (-MIM_PWELL_MARGIN, -MIM_PWELL_MARGIN)
    add_rect(c, (p_well_length, p_well_width), layer_pwellblock, origin=p_well_corner)

    # No QRC layers
    no_qrc_length = 2 * (MIM_PWELL_MARGIN + NO_QRC_PWELL_MARGIN) + length
    no_qrc_width = 2 * (MIM_PWELL_MARGIN + NO_QRC_PWELL_MARGIN) + width
    no_qrc_corner = (-MIM_PWELL_MARGIN - NO_QRC_PWELL_MARGIN, -MIM_PWELL_MARGIN - NO_QRC_PWELL_MARGIN)
    for layer in layers_no_qrc:
        add_rect(c, (no_qrc_length, no_qrc_width), layer, origin=no_qrc_corner)

    # Metal5 layer
    metal_5_length = 2 * MIM_METAL_5_MARGIN + length
    metal_5_width = 2 * MIM_METAL_5_MARGIN + width
    metal_5_corner = (-MIM_METAL_5_MARGIN, -MIM_METAL_5_MARGIN)
    add_rect(c, (metal_5_length, metal_5_width), layer_metal5, origin=metal_5_corner)


    return c


if __name__ == "__main__":
    from gdsfactory.difftest import xor

    from ihp import PDK, cells2

    PDK.activate()

    # Test the components
    c0 = cells2.cmim(width=10, length=10)  # original

    c1 = cmim(width=10, length=4)  # New
    # c = gf.grid([c0, c1], spacing=100)
    c = xor(c0, c1)
    c.show()

    # c0 = fixed.rfcmim()  # original
    # c1 = rfcmim()  # New
    # # c = gf.grid([c0, c1], spacing=100)
    # c = xor(c0, c1)
    # c.show()
