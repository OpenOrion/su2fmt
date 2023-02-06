from typing import List, Union
from su2fmt.parser import Mesh, combine_meshes
from su2fmt.utils import generate_color_legend_html, generate_rgb_values, to_rgb_str
import pythreejs
from IPython.display import display
from IPython.core.display import HTML
import ipywidgets as widgets
import numpy as np



def visualize_mesh(meshes: Union[Mesh, List[Mesh]], view_width=800, view_height=600):
    coord_html = widgets.HTML("Coords: ()")
    def on_surf_mousemove(change):
        # write coordinates to html container
        if change.new is None:
            coord_html.value = "Coords: ()"
        else:
            coord_html.value = "Coords: (%f, %f, %f)" % change.owner.point

    combined_mesh = combine_meshes(meshes) if isinstance(meshes, list) else meshes

    # Legend Colors
    zone_colors = generate_rgb_values(combined_mesh.nzone, is_grayscale=True)
    marker_colors = generate_rgb_values(sum([zone.nmark for zone in combined_mesh.zones]))

    # Legend Color Labels
    marker_color_labels = {}
    zone_color_labels = {}

    zone_line_segements = []
    zone_meshes = []
    for i, zone in enumerate(combined_mesh.zones):
        zone_color = zone_colors[i]
        zone_color_labels[f"Zone {zone.izone}"] = zone_color

        # Marker line segment points and colors
        marker_line_points = []
        marker_segment_colors = []

        # Non-marker line segment points
        non_marker_line_points = []

        for point_inds in zone.elements:
            for i in range(len(point_inds)):
                if i + 1 < len(point_inds):
                    line_point_inds = (point_inds[i+1], point_inds[i])
                else:
                    line_point_inds = (point_inds[0], point_inds[i])
                line_points = [zone.points[line_point_inds[0]].tolist(), zone.points[line_point_inds[1]].tolist()]

                marker_point_inds = line_point_inds if line_point_inds in zone.marker_elements_to_tag else line_point_inds[::-1]
                if marker_point_inds in zone.marker_elements_to_tag:
                    marker_name = zone.marker_elements_to_tag[marker_point_inds]
                    if marker_name not in marker_color_labels:
                        marker_color_labels[marker_name] = marker_colors[len(marker_color_labels)]
                    marker_color = marker_color_labels[marker_name]
                    marker_segment_colors.append([marker_color, marker_color])
                    marker_line_points.append(line_points)
                else:
                    non_marker_line_points.append(line_points)

        non_marker_lines = pythreejs.LineSegments2(
            pythreejs.LineSegmentsGeometry(positions=non_marker_line_points),
            pythreejs.LineMaterial(linewidth=1, color=to_rgb_str(zone_color))
        )
        marker_lines = pythreejs.LineSegments2(
            pythreejs.LineSegmentsGeometry(positions=marker_line_points, colors=marker_segment_colors),
            pythreejs.LineMaterial(linewidth=2, vertexColors='VertexColors')
        )

        zone_line_segements.append(non_marker_lines)
        zone_line_segements.append(marker_lines)

        zone_mesh_geom = pythreejs.BufferGeometry(attributes=dict(
            position=pythreejs.BufferAttribute(zone.points, normalized=False),
            index=pythreejs.BufferAttribute(np.concatenate(zone.elements), normalized=False),
        ))

        zone_mesh = pythreejs.Mesh(
            geometry=zone_mesh_geom,
            material=pythreejs.MeshLambertMaterial(color='white', side='DoubleSide'),
        )
        zone_meshes.append(zone_mesh)


    camera = pythreejs.PerspectiveCamera(position=[0, 0, 1], far=1000, near=0.001, aspect=view_width/view_height)
    scene = pythreejs.Scene(children=zone_line_segements+zone_meshes, background="black")

    orbit_controls = pythreejs.OrbitControls(controlling=camera)
    
    pickable_objects = pythreejs.Group()
    for zone_mesh in zone_meshes:
        pickable_objects.add(zone_mesh)

    mousemove_picker = pythreejs.Picker(
        controlling = pickable_objects,
        event = 'mousemove'
    )
    mousemove_picker.observe(on_surf_mousemove, names=['faceIndex'])

    renderer = pythreejs.Renderer(
        camera=camera,
        scene=scene,
        controls=[orbit_controls, mousemove_picker],
        width=view_width,
        height=view_height
    )

    # Plot renderer
    display(coord_html, renderer)
    
    # Plot legend
    marker_legend_html = generate_color_legend_html("Markers", marker_color_labels)
    zone_legend_html = generate_color_legend_html("Zones", zone_color_labels)
    display(HTML(marker_legend_html+zone_legend_html))
