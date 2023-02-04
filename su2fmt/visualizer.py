from su2fmt.parser import Mesh
from su2fmt.utils import generate_color_legend_html, generate_rgb_values, to_rgb_str
import pythreejs
from IPython.display import display
from IPython.core.display import HTML

def visualize_mesh(mesh: Mesh, view_width=800, view_height=600):
        # Legend Colors
        zone_colors = generate_rgb_values(mesh.nzone, is_grayscale=True)
        marker_colors = generate_rgb_values(sum([zone.nmark for zone in mesh.zones]))

        # Legend Color Labels
        marker_color_labels = {}
        zone_color_labels = {}


        zone_line_segements = []
        for i, zone in enumerate(mesh.zones):
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
                    
                    marker_point_inds = line_point_inds if line_point_inds in zone.markers else line_point_inds[::-1]
                    if marker_point_inds in zone.markers:
                        marker_name = zone.markers[marker_point_inds]
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


        camera = pythreejs.PerspectiveCamera(position=[0, 0, 1], far=1000, near=0.001, aspect=view_width/view_height)
        scene = pythreejs.Scene(children=zone_line_segements, background="black")

        renderer = pythreejs.Renderer(
            camera=camera, 
            scene=scene, 
            controls=[pythreejs.OrbitControls(controlling=camera)],
            width=view_width,
            height=view_height
        )
       
        # Plot renderer
        display(renderer)

        # Plot legend
        marker_legend_html = generate_color_legend_html("Markers", marker_color_labels)
        zone_legend_html = generate_color_legend_html("Zones", zone_color_labels)
        display(HTML(marker_legend_html+zone_legend_html))
