"""Document visualization functionality using PyVista."""

import pyvista as pv
from .base import Document

def visualize_document(document: Document) -> None:
    """Visualize the parts in a document using PyVista.
    
    Creates a 3D visualization window showing all parts in the document
    with different colors for distinction. The window remains open until
    closed by the user.
    
    Args:
        document: The Document instance to visualize.
        
    Note:
        This is a blocking operation - code execution will pause until
        the visualization window is closed.
    """
    try:
        # Create a plotter instance
        plotter = pv.Plotter()
        
        # Color map for different parts
        colors = ['red', 'blue', 'green', 'yellow', 'cyan', 'magenta']
        
        for i, part in enumerate(document.parts):
            try:
                # Convert the part's geometry to a PyVista mesh
                mesh = part.geometry.to_pyvista()
                # Add mesh to plotter with a unique color
                plotter.add_mesh(mesh, color=colors[i % len(colors)],
                               label=f"{part.name or f'Part {i+1}'}")
            except Exception as e:
                print(f"Warning: Failed to visualize {part.name or f'part {i+1}'}: {str(e)}")
        
        # Add legend showing part names/numbers
        plotter.add_legend()
        
        # Show the plot (blocks until window is closed)
        plotter.show()
        
    except Exception as e:
        print(f"Error during visualization: {str(e)}")
