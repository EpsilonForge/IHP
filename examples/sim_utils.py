# this will be in the next version of gdsfactoryplus
import zipfile
from pathlib import Path

import meshio
import pyvista as pv
from gdsfactoryplus import sim
from IPython.display import Image, display


def upload_simulation_dir(
    input_dir: str | Path,
    job_definition: sim.JobDefinition,
) -> sim.PreJob:
    """Zip all files in a directory (recursively) and upload for simulation."""
    input_dir = Path(input_dir)
    zip_path = Path("simulation_zipfile.zip")

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_STORED) as zf:
        for file in input_dir.rglob("*"):
            if file.is_file():
                zf.write(file, arcname=file.relative_to(input_dir))

    pre_job = sim.upload_simulation(path=zip_path, job_definition=job_definition)
    zip_path.unlink()  # Delete the zip file
    return pre_job


def print_job_summary(job):
    """Print a concise summary of a simulation job."""
    if job.started_at and job.finished_at:
        delta = job.finished_at - job.started_at
        minutes, seconds = divmod(int(delta.total_seconds()), 60)
        duration = f"{minutes}m {seconds}s"
    else:
        duration = "N/A"

    size_kb = job.output_size_bytes / 1024
    size_str = f"{size_kb:.1f} KB" if size_kb < 1024 else f"{size_kb / 1024:.2f} MB"
    files = list(job.download_urls.keys()) if job.download_urls else []

    print(f"{'Job:':<12} {job.job_name}")
    print(f"{'Status:':<12} {job.status.value} (exit {job.exit_code})")
    print(f"{'Duration:':<12} {duration}")
    print(
        f"{'Resources:':<12} {job.requested_cpu} CPU / {job.requested_memory_mb // 1024} GB"
    )
    print(f"{'Output:':<12} {size_str}")
    print(f"{'Files:':<12} {len(files)} files")
    for f in files:
        print(f"             - {f}")


def plot_mesh_pv(msh_path, output="mesh.png", show_groups=None, interactive=True):
    """Plot mesh wireframe using PyVista.

    Args:
        msh_path: Path to .msh file
        output: Output PNG path (ignored if interactive=True)
        show_groups: List of group name patterns to show (None = all)
        interactive: If True, open interactive viewer
    """
    # Get group info
    mio = meshio.read(msh_path)
    group_map = {tag: name for name, (tag, dim) in mio.field_data.items()}

    mesh = pv.read(msh_path)

    if interactive:
        plotter = pv.Plotter(window_size=[1200, 900])
    else:
        plotter = pv.Plotter(off_screen=True, window_size=[1200, 900])

    plotter.set_background("white")

    if show_groups:
        ids = [
            tag
            for tag, name in group_map.items()
            if any(p in name for p in show_groups)
        ]
        colors = ["red", "blue", "green", "orange", "purple", "cyan"]
        for i, gid in enumerate(ids):
            subset = mesh.extract_cells(mesh.cell_data["gmsh:physical"] == gid)
            if subset.n_cells > 0:
                plotter.add_mesh(
                    subset,
                    style="wireframe",
                    color=colors[i % len(colors)],
                    line_width=1,
                    label=group_map.get(gid, str(gid)),
                )
        plotter.add_legend()
    else:
        plotter.add_mesh(mesh, style="wireframe", color="black", line_width=1)

    plotter.camera_position = "iso"

    if interactive:
        plotter.show()
    else:
        plotter.screenshot(output)
        plotter.close()
        display(Image(output))
