"""
Editor Tools for Unreal MCP.

This module provides tools for controlling the Unreal Editor viewport and other editor functionality.
"""

import logging
from typing import Dict, List, Any, Optional
from mcp.server.fastmcp import FastMCP, Context

# Get logger
logger = logging.getLogger("UnrealMCP")

def register_editor_tools(mcp: FastMCP):
    """Register editor tools with the MCP server."""
    
    @mcp.tool()
    def get_actors_in_level(ctx: Context) -> List[Dict[str, Any]]:
        """Get a list of all actors in the current level."""
        from unreal_mcp_server import get_unreal_connection
        
        try:
            unreal = get_unreal_connection()
            if not unreal:
                logger.warning("Failed to connect to Unreal Engine")
                return []
                
            response = unreal.send_command("get_actors_in_level", {})
            
            if not response:
                logger.warning("No response from Unreal Engine")
                return []
                
            # Log the complete response for debugging
            logger.info(f"Complete response from Unreal: {response}")
            
            # Check response format
            if "result" in response and "actors" in response["result"]:
                actors = response["result"]["actors"]
                logger.info(f"Found {len(actors)} actors in level")
                return actors
            elif "actors" in response:
                actors = response["actors"]
                logger.info(f"Found {len(actors)} actors in level")
                return actors
                
            logger.warning(f"Unexpected response format: {response}")
            return []
            
        except Exception as e:
            logger.error(f"Error getting actors: {e}")
            return []

    @mcp.tool()
    def find_actors_by_name(ctx: Context, pattern: str) -> List[str]:
        """Find actors by name pattern."""
        from unreal_mcp_server import get_unreal_connection
        
        try:
            unreal = get_unreal_connection()
            if not unreal:
                logger.warning("Failed to connect to Unreal Engine")
                return []
                
            response = unreal.send_command("find_actors_by_name", {
                "pattern": pattern
            })
            
            if not response:
                return []
                
            return response.get("actors", [])
            
        except Exception as e:
            logger.error(f"Error finding actors: {e}")
            return []
    
    @mcp.tool()
    def spawn_actor(
        ctx: Context,
        name: str,
        type: str,
        location: Optional[List[float]] = None,
        rotation: Optional[List[float]] = None,
        scale: Optional[List[float]] = None,
        static_mesh: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new actor in the current level.

        Args:
            ctx: The MCP context
            name: The name to give the new actor (must be unique)
            type: The type of actor to create (e.g. StaticMeshActor, PointLight)
            location: The [x, y, z] world location to spawn at
            rotation: The [pitch, yaw, roll] rotation in degrees
            scale: The [x, y, z] scale (default [1,1,1])
            static_mesh: Optional mesh asset path (e.g. /Engine/BasicShapes/Cube)

        Returns:
            Dict containing the created actor's properties
        """
        from unreal_mcp_server import get_unreal_connection

        try:
            unreal = get_unreal_connection()
            if not unreal:
                logger.error("Failed to connect to Unreal Engine")
                return {"success": False, "message": "Failed to connect to Unreal Engine"}

            location = location or [0.0, 0.0, 0.0]
            rotation = rotation or [0.0, 0.0, 0.0]

            # Ensure all parameters are properly formatted
            params = {
                "name": name,
                "type": type,
                "location": location,
                "rotation": rotation
            }
            if scale is not None:
                params["scale"] = [float(val) for val in scale]
            if static_mesh is not None:
                params["static_mesh"] = static_mesh

            # Validate location and rotation formats
            for param_name in ["location", "rotation"]:
                param_value = params[param_name]
                if not isinstance(param_value, list) or len(param_value) != 3:
                    logger.error(f"Invalid {param_name} format: {param_value}. Must be a list of 3 float values.")
                    return {"success": False, "message": f"Invalid {param_name} format. Must be a list of 3 float values."}
                # Ensure all values are float
                params[param_name] = [float(val) for val in param_value]
            
            logger.info(f"Creating actor '{name}' of type '{type}' with params: {params}")
            response = unreal.send_command("spawn_actor", params)
            
            if not response:
                logger.error("No response from Unreal Engine")
                return {"success": False, "message": "No response from Unreal Engine"}
            
            # Log the complete response for debugging
            logger.info(f"Actor creation response: {response}")
            
            # Handle error responses correctly
            if response.get("status") == "error":
                error_message = response.get("error", "Unknown error")
                logger.error(f"Error creating actor: {error_message}")
                return {"success": False, "message": error_message}
            
            return response
            
        except Exception as e:
            error_msg = f"Error creating actor: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}
    
    @mcp.tool()
    def delete_actor(ctx: Context, name: str) -> Dict[str, Any]:
        """Delete an actor by name."""
        from unreal_mcp_server import get_unreal_connection
        
        try:
            unreal = get_unreal_connection()
            if not unreal:
                logger.error("Failed to connect to Unreal Engine")
                return {"success": False, "message": "Failed to connect to Unreal Engine"}
                
            response = unreal.send_command("delete_actor", {
                "name": name
            })
            return response or {}
            
        except Exception as e:
            logger.error(f"Error deleting actor: {e}")
            return {}
    
    @mcp.tool()
    def set_actor_transform(
        ctx: Context,
        name: str,
        location: List[float]  = None,
        rotation: List[float]  = None,
        scale: List[float] = None
    ) -> Dict[str, Any]:
        """Set the transform of an actor."""
        from unreal_mcp_server import get_unreal_connection
        
        try:
            unreal = get_unreal_connection()
            if not unreal:
                logger.error("Failed to connect to Unreal Engine")
                return {"success": False, "message": "Failed to connect to Unreal Engine"}
                
            params = {"name": name}
            if location is not None:
                params["location"] = location
            if rotation is not None:
                params["rotation"] = rotation
            if scale is not None:
                params["scale"] = scale
                
            response = unreal.send_command("set_actor_transform", params)
            return response or {}
            
        except Exception as e:
            logger.error(f"Error setting transform: {e}")
            return {}
    
    @mcp.tool()
    def get_actor_properties(ctx: Context, name: str) -> Dict[str, Any]:
        """Get all properties of an actor."""
        from unreal_mcp_server import get_unreal_connection
        
        try:
            unreal = get_unreal_connection()
            if not unreal:
                logger.error("Failed to connect to Unreal Engine")
                return {"success": False, "message": "Failed to connect to Unreal Engine"}
                
            response = unreal.send_command("get_actor_properties", {
                "name": name
            })
            return response or {}
            
        except Exception as e:
            logger.error(f"Error getting properties: {e}")
            return {}

    @mcp.tool()
    def set_actor_property(
        ctx: Context,
        name: str,
        property_name: str,
        property_value,
    ) -> Dict[str, Any]:
        """
        Set a property on an actor.
        
        Args:
            name: Name of the actor
            property_name: Name of the property to set
            property_value: Value to set the property to
            
        Returns:
            Dict containing response from Unreal with operation status
        """
        from unreal_mcp_server import get_unreal_connection
        
        try:
            unreal = get_unreal_connection()
            if not unreal:
                logger.error("Failed to connect to Unreal Engine")
                return {"success": False, "message": "Failed to connect to Unreal Engine"}
                
            response = unreal.send_command("set_actor_property", {
                "name": name,
                "property_name": property_name,
                "property_value": property_value
            })
            
            if not response:
                logger.error("No response from Unreal Engine")
                return {"success": False, "message": "No response from Unreal Engine"}
            
            logger.info(f"Set actor property response: {response}")
            return response
            
        except Exception as e:
            error_msg = f"Error setting actor property: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    # @mcp.tool() commented out because it's buggy
    def focus_viewport(
        ctx: Context,
        target: str = None,
        location: List[float] = None,
        distance: float = 1000.0,
        orientation: List[float] = None
    ) -> Dict[str, Any]:
        """
        Focus the viewport on a specific actor or location.
        
        Args:
            target: Name of the actor to focus on (if provided, location is ignored)
            location: [X, Y, Z] coordinates to focus on (used if target is None)
            distance: Distance from the target/location
            orientation: Optional [Pitch, Yaw, Roll] for the viewport camera
            
        Returns:
            Response from Unreal Engine
        """
        from unreal_mcp_server import get_unreal_connection
        
        try:
            unreal = get_unreal_connection()
            if not unreal:
                logger.error("Failed to connect to Unreal Engine")
                return {"success": False, "message": "Failed to connect to Unreal Engine"}
                
            params = {}
            if target:
                params["target"] = target
            elif location:
                params["location"] = location
            
            if distance:
                params["distance"] = distance
                
            if orientation:
                params["orientation"] = orientation
                
            response = unreal.send_command("focus_viewport", params)
            return response or {}
            
        except Exception as e:
            logger.error(f"Error focusing viewport: {e}")
            return {"status": "error", "message": str(e)}

    @mcp.tool()
    def spawn_blueprint_actor(
        ctx: Context,
        blueprint_name: str,
        actor_name: str,
        location: Optional[List[float]] = None,
        rotation: Optional[List[float]] = None,
        scale: Optional[List[float]] = None
    ) -> Dict[str, Any]:
        """Spawn an actor from a Blueprint.

        Args:
            ctx: The MCP context
            blueprint_name: Name of the Blueprint to spawn from
            actor_name: Name to give the spawned actor
            location: The [x, y, z] world location to spawn at
            rotation: The [pitch, yaw, roll] rotation in degrees
            scale: The [x, y, z] scale (default [1,1,1])

        Returns:
            Dict containing the spawned actor's properties
        """
        from unreal_mcp_server import get_unreal_connection

        try:
            unreal = get_unreal_connection()
            if not unreal:
                logger.error("Failed to connect to Unreal Engine")
                return {"success": False, "message": "Failed to connect to Unreal Engine"}

            # Ensure all parameters are properly formatted
            params = {
                "blueprint_name": blueprint_name,
                "actor_name": actor_name,
                "location": location or [0.0, 0.0, 0.0],
                "rotation": rotation or [0.0, 0.0, 0.0]
            }
            if scale is not None:
                params["scale"] = [float(val) for val in scale]
            
            # Validate location and rotation formats
            for param_name in ["location", "rotation"]:
                param_value = params[param_name]
                if not isinstance(param_value, list) or len(param_value) != 3:
                    logger.error(f"Invalid {param_name} format: {param_value}. Must be a list of 3 float values.")
                    return {"success": False, "message": f"Invalid {param_name} format. Must be a list of 3 float values."}
                # Ensure all values are float
                params[param_name] = [float(val) for val in param_value]
            
            logger.info(f"Spawning blueprint actor with params: {params}")
            response = unreal.send_command("spawn_blueprint_actor", params)
            
            if not response:
                logger.error("No response from Unreal Engine")
                return {"success": False, "message": "No response from Unreal Engine"}
            
            logger.info(f"Spawn blueprint actor response: {response}")
            return response
            
        except Exception as e:
            error_msg = f"Error spawning blueprint actor: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def import_asset(
        ctx: Context,
        file_path: str = "",
        file_paths: Optional[List[str]] = None,
        destination_path: str = "/Game/Buildings"
    ) -> Dict[str, Any]:
        """Import asset files (FBX, OBJ, etc.) into the Unreal Engine Content Browser.

        Args:
            ctx: The MCP context
            file_path: Single file path to import (absolute path)
            file_paths: List of file paths to import (absolute paths)
            destination_path: Content Browser destination (e.g. /Game/Buildings)

        Returns:
            Dict with imported asset names and paths
        """
        from unreal_mcp_server import get_unreal_connection

        try:
            unreal = get_unreal_connection()
            if not unreal:
                return {"success": False, "message": "Failed to connect to Unreal Engine"}

            params = {"destination_path": destination_path}
            if file_path:
                params["file_path"] = file_path
            if file_paths:
                params["file_paths"] = file_paths

            response = unreal.send_command("import_asset", params)

            if not response:
                return {"success": False, "message": "No response from Unreal Engine"}

            return response

        except Exception as e:
            logger.error(f"Error importing asset: {e}")
            return {"success": False, "message": str(e)}

    @mcp.tool()
    def spawn_forest(
        ctx: Context,
        json_path: str = ""
    ) -> Dict[str, Any]:
        """Spawn forest from genplan JSON using HISM instanced trees.

        Reads tree positions from kaskad_terrain.json, computes Z heights from DEM,
        and places trees as HierarchicalInstancedStaticMesh instances.

        Args:
            ctx: The MCP context
            json_path: Optional path to terrain JSON (default uses actor's TreesJsonPath)

        Returns:
            Dict with spawner name and total instance count
        """
        from unreal_mcp_server import get_unreal_connection

        try:
            unreal = get_unreal_connection()
            if not unreal:
                return {"success": False, "message": "Failed to connect to Unreal Engine"}

            params = {}
            if json_path:
                params["json_path"] = json_path

            response = unreal.send_command("spawn_forest", params)

            if not response:
                return {"success": False, "message": "No response from Unreal Engine"}

            return response

        except Exception as e:
            logger.error(f"Error spawning forest: {e}")
            return {"success": False, "message": str(e)}

    @mcp.tool()
    def snap_to_ground(
        ctx: Context,
        pattern: str = "",
        z_offset: float = 0.0
    ) -> Dict[str, Any]:
        """Snap StaticMeshActors to the ground using line trace.

        Performs a vertical line trace from above each actor to find the ground
        (Landscape or other geometry), then moves the actor so its bottom sits
        on the ground surface.

        Args:
            ctx: The MCP context
            pattern: Optional name filter — only actors containing this string will be snapped
            z_offset: Additional Z offset after snapping (positive = above ground)

        Returns:
            Dict with snapped_count and list of actors with old/new Z values
        """
        from unreal_mcp_server import get_unreal_connection

        try:
            unreal = get_unreal_connection()
            if not unreal:
                return {"success": False, "message": "Failed to connect to Unreal Engine"}

            params = {"z_offset": z_offset}
            if pattern:
                params["pattern"] = pattern

            response = unreal.send_command("snap_to_ground", params)

            if not response:
                return {"success": False, "message": "No response from Unreal Engine"}

            return response

        except Exception as e:
            logger.error(f"Error snapping to ground: {e}")
            return {"success": False, "message": str(e)}

    @mcp.tool()
    def flatten_landscape(
        ctx: Context,
        pattern: str = "",
        padding: float = 200.0,
        blend_radius: float = 500.0
    ) -> Dict[str, Any]:
        """Flatten landscape under buildings to create level building pads.

        For each StaticMeshActor, flattens the landscape to the height at the
        building center, with smooth blending at edges.

        Args:
            ctx: The MCP context
            pattern: Optional name filter — only flatten under actors containing this string
            padding: Extra padding around building footprint in cm (default 200)
            blend_radius: Blend distance from flat area to original terrain in cm (default 500)

        Returns:
            Dict with flattened_count and list of affected areas
        """
        from unreal_mcp_server import get_unreal_connection

        try:
            unreal = get_unreal_connection()
            if not unreal:
                return {"success": False, "message": "Failed to connect to Unreal Engine"}

            params = {"padding": padding, "blend_radius": blend_radius}
            if pattern:
                params["pattern"] = pattern

            response = unreal.send_command("flatten_landscape", params)

            if not response:
                return {"success": False, "message": "No response from Unreal Engine"}

            return response

        except Exception as e:
            logger.error(f"Error flattening landscape: {e}")
            return {"success": False, "message": str(e)}

    @mcp.tool()
    def take_screenshot(
        ctx: Context,
        filename: str = "screenshot.png"
    ) -> Dict[str, Any]:
        """Capture a screenshot of the active editor viewport.

        Args:
            ctx: The MCP context
            filename: Output filename (saved to project Saved/Screenshots/)

        Returns:
            Dict with file path of saved screenshot
        """
        from unreal_mcp_server import get_unreal_connection

        try:
            unreal = get_unreal_connection()
            if not unreal:
                return {"success": False, "message": "Failed to connect to Unreal Engine"}

            response = unreal.send_command("take_screenshot", {"filename": filename})

            if not response:
                return {"success": False, "message": "No response from Unreal Engine"}

            return response

        except Exception as e:
            logger.error(f"Error taking screenshot: {e}")
            return {"success": False, "message": str(e)}

    @mcp.tool()
    def create_landscape(
        ctx: Context,
        heightmap_path: str,
        size: int = 1009,
        scale_x: float = 100.0,
        scale_y: float = 100.0,
        scale_z: float = 100.0,
        location_x: float = 0.0,
        location_y: float = 0.0,
        location_z: float = 0.0
    ) -> Dict[str, Any]:
        """Create a UE Landscape from a R16 heightmap file.

        Args:
            ctx: The MCP context
            heightmap_path: Absolute path to R16 heightmap file
            size: Heightmap resolution (e.g. 1009, 505, 253)
            scale_x: X scale per quad
            scale_y: Y scale per quad
            scale_z: Z scale (height multiplier)
            location_x: World X position
            location_y: World Y position
            location_z: World Z position

        Returns:
            Dict with landscape info
        """
        from unreal_mcp_server import get_unreal_connection

        try:
            unreal = get_unreal_connection()
            if not unreal:
                return {"success": False, "message": "Failed to connect to Unreal Engine"}

            params = {
                "heightmap_path": heightmap_path,
                "size": size,
                "scale_x": scale_x,
                "scale_y": scale_y,
                "scale_z": scale_z,
                "location_x": location_x,
                "location_y": location_y,
                "location_z": location_z
            }

            response = unreal.send_command("create_landscape", params)

            if not response:
                return {"success": False, "message": "No response from Unreal Engine"}

            return response

        except Exception as e:
            logger.error(f"Error creating landscape: {e}")
            return {"success": False, "message": str(e)}

    @mcp.tool()
    def load_terrain_dem(
        ctx: Context,
        json_path: str
    ) -> Dict[str, Any]:
        """Load DEM elevation data from JSON into a procedural terrain actor.

        Args:
            ctx: The MCP context
            json_path: Absolute path to DEM JSON file

        Returns:
            Dict with terrain info
        """
        from unreal_mcp_server import get_unreal_connection

        try:
            unreal = get_unreal_connection()
            if not unreal:
                return {"success": False, "message": "Failed to connect to Unreal Engine"}

            response = unreal.send_command("load_terrain_dem", {"json_path": json_path})

            if not response:
                return {"success": False, "message": "No response from Unreal Engine"}

            return response

        except Exception as e:
            logger.error(f"Error loading terrain DEM: {e}")
            return {"success": False, "message": str(e)}

    @mcp.tool()
    def get_available_materials(
        ctx: Context,
        search_path: str = "/Game",
        name_filter: str = "",
        max_results: int = 50
    ) -> Dict[str, Any]:
        """Search for available materials in the project.

        Args:
            ctx: The MCP context
            search_path: Content path to search in (e.g. /Game, /Game/Materials)
            name_filter: Optional name filter (case-insensitive substring match)
            max_results: Maximum number of results to return (default 50)

        Returns:
            Dict with list of materials (name, path, class)
        """
        from unreal_mcp_server import get_unreal_connection

        try:
            unreal = get_unreal_connection()
            if not unreal:
                return {"success": False, "message": "Failed to connect to Unreal Engine"}

            params = {"search_path": search_path, "max_results": max_results}
            if name_filter:
                params["name_filter"] = name_filter

            response = unreal.send_command("get_available_materials", params)

            if not response:
                return {"success": False, "message": "No response from Unreal Engine"}

            return response

        except Exception as e:
            logger.error(f"Error getting materials: {e}")
            return {"success": False, "message": str(e)}

    @mcp.tool()
    def apply_material_to_actor(
        ctx: Context,
        actor_name: str,
        material_path: str,
        slot_index: int = 0
    ) -> Dict[str, Any]:
        """Apply a material to an actor's mesh component.

        Args:
            ctx: The MCP context
            actor_name: Name of the target actor
            material_path: Full path to the material (e.g. /Game/Materials/M_Wood)
            slot_index: Material slot index (default 0)

        Returns:
            Dict with applied material info
        """
        from unreal_mcp_server import get_unreal_connection

        try:
            unreal = get_unreal_connection()
            if not unreal:
                return {"success": False, "message": "Failed to connect to Unreal Engine"}

            params = {
                "actor_name": actor_name,
                "material_path": material_path,
                "slot_index": slot_index
            }

            response = unreal.send_command("apply_material_to_actor", params)

            if not response:
                return {"success": False, "message": "No response from Unreal Engine"}

            return response

        except Exception as e:
            logger.error(f"Error applying material: {e}")
            return {"success": False, "message": str(e)}

    @mcp.tool()
    def get_actor_material_info(
        ctx: Context,
        actor_name: str
    ) -> Dict[str, Any]:
        """Get material information for all mesh components of an actor.

        Args:
            ctx: The MCP context
            actor_name: Name of the actor to inspect

        Returns:
            Dict with material slots info (component, slot_index, material_name, material_path)
        """
        from unreal_mcp_server import get_unreal_connection

        try:
            unreal = get_unreal_connection()
            if not unreal:
                return {"success": False, "message": "Failed to connect to Unreal Engine"}

            response = unreal.send_command("get_actor_material_info", {"actor_name": actor_name})

            if not response:
                return {"success": False, "message": "No response from Unreal Engine"}

            return response

        except Exception as e:
            logger.error(f"Error getting material info: {e}")
            return {"success": False, "message": str(e)}

    @mcp.tool()
    def set_mesh_material_color(
        ctx: Context,
        actor_name: str,
        color: List[float],
        slot_index: int = 0,
        param_name: str = "BaseColor"
    ) -> Dict[str, Any]:
        """Set the color of an actor's material using a dynamic material instance.

        Creates a MaterialInstanceDynamic from the current material and sets
        a vector parameter (default "BaseColor") to the specified color.

        Args:
            ctx: The MCP context
            actor_name: Name of the target actor
            color: [R, G, B] or [R, G, B, A] with values 0.0-1.0
            slot_index: Material slot index (default 0)
            param_name: Vector parameter name to set (default "BaseColor")

        Returns:
            Dict with applied color info
        """
        from unreal_mcp_server import get_unreal_connection

        try:
            unreal = get_unreal_connection()
            if not unreal:
                return {"success": False, "message": "Failed to connect to Unreal Engine"}

            params = {
                "actor_name": actor_name,
                "color": color,
                "slot_index": slot_index,
                "param_name": param_name
            }

            response = unreal.send_command("set_mesh_material_color", params)

            if not response:
                return {"success": False, "message": "No response from Unreal Engine"}

            return response

        except Exception as e:
            logger.error(f"Error setting material color: {e}")
            return {"success": False, "message": str(e)}

    @mcp.tool()
    def get_mesh_asset_materials(
        ctx: Context,
        mesh_path: str
    ) -> Dict[str, Any]:
        """Get material slots and their assigned materials from a Static Mesh asset.

        Args:
            ctx: The MCP context
            mesh_path: Content path to the Static Mesh (e.g. '/Game/Buildings/Villa_180/Villa_180_UE')

        Returns:
            Dict with mesh name, num_slots, and material_slots array
        """
        from unreal_mcp_server import get_unreal_connection

        try:
            unreal = get_unreal_connection()
            if not unreal:
                return {"success": False, "message": "Failed to connect to Unreal Engine"}

            response = unreal.send_command("get_mesh_asset_materials", {
                "mesh_path": mesh_path
            })

            if not response:
                return {"success": False, "message": "No response from Unreal Engine"}

            return response

        except Exception as e:
            logger.error(f"Error getting mesh asset materials: {e}")
            return {"success": False, "message": str(e)}

    @mcp.tool()
    def set_mesh_asset_material(
        ctx: Context,
        mesh_path: str,
        material_path: str,
        slot_index: int = 0,
        slot_indices: Optional[List[int]] = None,
        all_slots: bool = False
    ) -> Dict[str, Any]:
        """Set material on a Static Mesh asset's material slot(s).

        Args:
            ctx: The MCP context
            mesh_path: Content path to the Static Mesh (e.g. '/Game/Buildings/Villa_180/Villa_180_UE')
            material_path: Content path to the Material or Material Instance
            slot_index: Single slot index to set (default 0)
            slot_indices: List of slot indices to set (overrides slot_index)
            all_slots: If True, apply material to all slots

        Returns:
            Dict with updated slot info
        """
        from unreal_mcp_server import get_unreal_connection

        try:
            unreal = get_unreal_connection()
            if not unreal:
                return {"success": False, "message": "Failed to connect to Unreal Engine"}

            params: Dict[str, Any] = {
                "mesh_path": mesh_path,
                "material_path": material_path,
            }

            if all_slots:
                params["all_slots"] = True
            elif slot_indices is not None:
                params["slot_indices"] = slot_indices
            else:
                params["slot_index"] = slot_index

            response = unreal.send_command("set_mesh_asset_material", params)

            if not response:
                return {"success": False, "message": "No response from Unreal Engine"}

            return response

        except Exception as e:
            logger.error(f"Error setting mesh asset material: {e}")
            return {"success": False, "message": str(e)}

    @mcp.tool()
    def wp_list_all(
        ctx: Context,
        pattern: str = ""
    ) -> Dict[str, Any]:
        """List ALL actors in a World Partition level — including unloaded cells.

        Unlike get_actors_in_level (which only sees loaded cells), this enumerates
        actor descriptors directly from the World Partition database, returning
        metadata (name, class, location) for every actor regardless of streaming state.

        Args:
            ctx: The MCP context
            pattern: Optional name filter (case-insensitive substring match)

        Returns:
            Dict with actors array (name, class, x, y, z, loaded), total count,
            and has_world_partition flag
        """
        from unreal_mcp_server import get_unreal_connection

        try:
            unreal = get_unreal_connection()
            if not unreal:
                return {"success": False, "message": "Failed to connect to Unreal Engine"}

            params = {}
            if pattern:
                params["pattern"] = pattern

            response = unreal.send_command("wp_list_all", params)

            if not response:
                return {"success": False, "message": "No response from Unreal Engine"}

            return response

        except Exception as e:
            logger.error(f"Error listing WP actors: {e}")
            return {"success": False, "message": str(e)}

    @mcp.tool()
    def wp_load_all(ctx: Context) -> Dict[str, Any]:
        """Force-load all World Partition cells into editor memory.

        After this call, get_actors_in_level and find_actors_by_name will see
        all actors in the level. Required before delete_actors_by_pattern can
        reach unloaded actors.

        Returns:
            Dict with loaded_actors count and success status
        """
        from unreal_mcp_server import get_unreal_connection

        try:
            unreal = get_unreal_connection()
            if not unreal:
                return {"success": False, "message": "Failed to connect to Unreal Engine"}

            response = unreal.send_command("wp_load_all", {})

            if not response:
                return {"success": False, "message": "No response from Unreal Engine"}

            return response

        except Exception as e:
            logger.error(f"Error loading WP cells: {e}")
            return {"success": False, "message": str(e)}

    @mcp.tool()
    def delete_actors_by_pattern(
        ctx: Context,
        pattern: str
    ) -> Dict[str, Any]:
        """Delete all actors whose name contains the given pattern.

        Deletes all currently loaded actors matching the pattern and marks
        the level dirty. If actors are in unloaded World Partition cells,
        call wp_load_all first, then retry.

        Args:
            ctx: The MCP context
            pattern: Name substring to match (e.g. 'VillaS', 'Rectangle', 'Shape')

        Returns:
            Dict with deleted_count and list of deleted actor names/classes
        """
        from unreal_mcp_server import get_unreal_connection

        try:
            unreal = get_unreal_connection()
            if not unreal:
                return {"success": False, "message": "Failed to connect to Unreal Engine"}

            response = unreal.send_command("delete_actors_by_pattern", {"pattern": pattern})

            if not response:
                return {"success": False, "message": "No response from Unreal Engine"}

            return response

        except Exception as e:
            logger.error(f"Error deleting actors by pattern: {e}")
            return {"success": False, "message": str(e)}

    logger.info("Editor tools registered successfully")
