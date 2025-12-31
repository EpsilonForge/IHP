"""BJT Transistor components for IHP PDK."""

import math

import gdsfactory as gf
from gdsfactory.typings import LayerSpec

from cni.tech import Tech

tech_name = "SG13_dev"
tech = Tech.get("SG13_dev").getTechParams()


@gf.cell
def npn13G2(
    STI: float = 0.44,
    baspolyx: float = 0.3,
    bipwinx: float = 0.07,
    bipwiny: float = 0.1,
    empolyx: float = 0.15,
    empolyy: float = 0.18,
    emitter_length: float = 0.9,
    emitter_width: float = 0.7,
    Nx: int = 1,
    Ny: int = 1,
    text: str = "npn13G2",
    CMetY1: float = 0,
    CMetY2: float = 0,
    extra_argument_for_naming: str | None = None,
) -> gf.Component:
    """Returns the IHP npn13G2 BJT transistor as a gdsfactory Component.

    Args:
        Nx: Number of emitter fingers in the x-direction.
        Ny: Number of emitter fingers in the y-direction.
        emitter_length: Length of the emitter region in microns.
        emitter_width: Width of the emitter region in microns.
        STI: Shallow Trench Isolation width in microns.
        baspolyx: Base poly extension in x-direction in microns.
        bipwinx: Bipolar window extension in x-direction in microns.
        bipwiny: Bipolar window extension in y-direction in microns.
        empolyx: Emitter poly extension in x-direction in microns.
        empolyy: Emitter poly extension in y-direction in microns.
        text: Text label for the transistor.
        CMetY1: Contact metal Y1 dimension in microns.
        CMetY2: Contact metal Y2 dimension in microns.

    Returns:
        gdsfactory.Component: The generated npn13G2 transistor layout.
    """

    c = gf.Component()

    layer_via1: LayerSpec = "Via1drawing"

    # ActivShift = 0.01
    # ActivShift = 0.0

    # for multiplied npn: le has to be bigger
    stepX = 1.85
    # stretchX = stepX * (Nx - 1)
    bipwinyoffset = (2 * (bipwiny - 0.1) - 0) / 2
    empolyyoffset = (2 * (empolyy - 0.18)) / 2

    # empolyxoffset = (2 * (empolyx - 0.15)) / 2
    # baspolyxoffset = (2 * (baspolyx - 0.3)) / 2
    # STIoffset = (2 * (STI - 0.44)) / 2

    # le = emitter_length
    # we = emitter_width

    # nSDBlockShift = (
    #     0.43 - le
    # )  # 23.07.09: needed to draw nSDBlock shorter in small pCell

    leoffset = 0  # ((le - 0.07) / 2)

    ##############
    # npn13G2_base

    pcStepY = 0.41
    yOffset = 0.20

    pcRepeatY = 4

    # if Nx > 1:
    #     CMetY1 = 1.01 + we / 2 + leoffset + bipwinyoffset + empolyyoffset
    #     CMetY2 = 0.57 + we / 2 + leoffset + bipwinyoffset + empolyyoffset
    # else:
    #     CMetY1 = 0.8 + we / 2 + leoffset + bipwinyoffset + empolyyoffset
    #     CMetY2 = 0.56 + we / 2 + leoffset + bipwinyoffset + empolyyoffset

    for pcIndexX in range(int(math.floor(Nx))):
        # loop for generate the given number of vias in variable pcRepeatY
        # two vias are generated per loop
        for pcIndexY in range(int(math.floor(pcRepeatY))):
            # Via on left side
            via1_size = 0.19
            left = (stepX * pcIndexX) - 0.3
            bottom = (
                -(
                    (-0.3 - yOffset - leoffset - bipwinyoffset - empolyyoffset)
                    + (pcIndexY * pcStepY)
                )
                + 0.2
                - via1_size
            )
            c.add_ref(
                gf.components.rectangle(
                    size=(
                        via1_size,
                        via1_size,
                    ),
                    layer=layer_via1,
                )
            ).move((left, bottom))

            left = (stepX * pcIndexX) + 0.11
            # Via on the right side
            c.add_ref(
                gf.components.rectangle(
                    size=(
                        via1_size,
                        via1_size,
                    ),
                    layer=layer_via1,
                )
            ).move((left, bottom))

    return c


if __name__ == "__main__":
    from gdsfactory.difftest import xor

    from ihp import PDK, cells2

    PDK.activate()
    c0 = cells2.npn13G2()
    c1 = npn13G2()
    c = xor(c0, c1)
    c.show()
    # gf.show(c)
