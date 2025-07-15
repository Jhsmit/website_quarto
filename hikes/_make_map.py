# %%
from pathlib import Path
from typing import Iterable, Optional

import gpxpy
from ipyleaflet import Map, Marker, MarkerCluster, Polyline, FullScreenControl
from ipywidgets import HTML, Layout
from datetime import datetime
from itertools import cycle

AMS = (2.377956, 4.897070)

# !! moretehan is overlapping with another hike,
# adjust colors?

# %%


def valid(p: Path) -> bool:
    if p.stem.startswith("."):
        return False
    if p.is_dir():
        return True
    return False


def parse_gpx(file_path: Path) -> list[tuple[float, float]]:
    gpx = gpxpy.parse(file_path.read_text())

    # Extract the first track in the GPX file
    track = gpx.tracks[0]
    segment = track.segments[0]

    # Extract coordinates from the segment
    coordinates = [(point.latitude, point.longitude) for point in segment.points]
    return coordinates


def load_coords(dir_path: Path) -> list[tuple[float, float]]:
    coords = []
    for file_path in sorted(dir_path.glob("*.gpx")):
        coords.extend(parse_gpx(file_path))
    return coords


def make_tracks(segment_coords: Iterable[list[tuple[float, float]]]) -> list[Polyline]:
    tracks = []
    for i, segment in enumerate(segment_coords):
        gpx_track = Polyline(
            locations=segment,
            color="blue" if i % 2 == 0 else "green",
            fill=False,
            opacity=0.7,
            scaling=False,
            rotations=False,
        )
        tracks.append(gpx_track)
    return tracks


# %%
def extract_date_from_path(fpath: Path) -> Optional[datetime]:
    try:
        date_part = fpath.stem.split("_")[0]
        dt_from_date = datetime.strptime(date_part, "%Y-%m-%d")
        return dt_from_date
    except ValueError:
        return None


# %%
m = Map(center=AMS, zoom=2, scroll_wheel_zoom=True, layout=Layout(height="600px"))
m.add(FullScreenControl())

dirs = [d for d in Path("hikes-gpx").iterdir() if valid(d)]
markers = []
for dpath in dirs:
    location = None
    previous_date = None

    colors = cycle(["green", "blue"])
    color = next(colors)

    for i, fpath in enumerate(sorted(dpath.glob("*.gpx"))):
        date = extract_date_from_path(fpath)

        if date != previous_date:
            color = next(colors)

        segment = parse_gpx(fpath)
        track = Polyline(
            locations=segment,
            color=color,
            fill=False,
            opacity=0.7,
            scaling=False,
            rotations=False,
        )
        m.add(track)
        if i == 0:
            location = segment[0]

        previous_date = date

    gpx_marker = Marker(location=location, draggable=False)
    if (Path("posts") / (dpath.stem + ".qmd")).exists():
        hike_name = dpath.stem.replace("-", " ").title()
        popup_html = f"""
        <h3>{hike_name}</h3>
        <a href="/hikes/posts/{dpath.stem}.html">View Details</a>
        """
        gpx_marker.popup = HTML(popup_html)

    markers.append(gpx_marker)

m.add(MarkerCluster(markers=markers))

m

# %%
