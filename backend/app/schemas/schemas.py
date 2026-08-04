"""
Pydantic schemas for API request/response validation.

These schemas define the contract for all REST API endpoints,
including input validation, serialization, and OpenAPI documentation.
"""

import uuid
from datetime import date, datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator


# =============================================================================
# Auth Schemas
# =============================================================================


class UserCreate(BaseModel):
    """Register a new user account."""

    email: EmailStr = Field(description="User's email address (must be unique)")
    password: str = Field(min_length=8, description="Password, minimum 8 characters")
    full_name: Optional[str] = Field(None, description="User's display name")


class LoginRequest(BaseModel):
    """Credentials for user authentication."""

    email: EmailStr = Field(description="Registered email address")
    password: str = Field(description="Account password")


class UserResponse(BaseModel):
    """Public user profile information."""

    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID = Field(description="Unique user identifier")
    email: str = Field(description="Email address")
    full_name: Optional[str] = Field(description="Display name")
    role: str = Field(description="User role: viewer, editor, or admin")
    is_active: bool = Field(description="Whether the account is active")
    render_credits: int = Field(description="Remaining AI render credits")
    created_at: datetime = Field(description="Account creation timestamp")


class TokenResponse(BaseModel):
    """JWT authentication tokens returned after login."""

    access_token: str = Field(description="Short-lived access token (30 min)")
    refresh_token: str = Field(description="Long-lived refresh token (7 days)")
    token_type: str = "bearer"
    user: UserResponse


class RefreshRequest(BaseModel):
    """Request to exchange a refresh token for a new access token."""

    refresh_token: str = Field(description="Valid refresh token")


class ChangePasswordRequest(BaseModel):
    """Change password for an authenticated user."""

    current_password: str = Field(description="Current account password")
    new_password: str = Field(min_length=8, description="New password, minimum 8 characters")


class ForgotPasswordRequest(BaseModel):
    """Request a password reset email."""

    email: EmailStr = Field(description="Email address to send reset link to")


class ResetPasswordRequest(BaseModel):
    """Reset password using a token from a reset email."""

    token: str = Field(description="Password reset JWT token")
    new_password: str = Field(min_length=8, description="New password, minimum 8 characters")


class MessageResponse(BaseModel):
    """Generic message response."""

    message: str = Field(description="Response message")


# =============================================================================
# Location Schemas
# =============================================================================


class LocationInput(BaseModel):
    """Geographic location with optional address."""

    latitude: float = Field(ge=-90, le=90, description="Latitude in decimal degrees (-90 to 90)")
    longitude: float = Field(ge=-180, le=180, description="Longitude in decimal degrees (-180 to 180)")
    address: Optional[str] = Field(None, description="Human-readable address (geocoded)")


class LocationResponse(BaseModel):
    """Geographic location returned in API responses."""

    latitude: float = Field(description="Latitude in decimal degrees")
    longitude: float = Field(description="Longitude in decimal degrees")
    address: Optional[str] = Field(None, description="Human-readable address")


# =============================================================================
# Project Schemas
# =============================================================================


class ConstructionPhaseInput(BaseModel):
    """Define a construction phase for timeline visualization."""

    phase_number: int = Field(ge=1, description="Phase sequence number (1-based)")
    name: str = Field(max_length=100, description="Phase name, e.g. 'Foundation' or 'Phase 2'")
    start_date: Optional[date] = Field(None, description="Phase start date")
    end_date: Optional[date] = Field(None, description="Phase end date")
    color: Optional[str] = Field(None, description="Hex color for 3D viewer, e.g. '#3b82f6'")


class ProjectCreate(BaseModel):
    """Create a new development project."""

    name: str = Field(max_length=255, description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    location: Optional[LocationInput] = Field(None, description="Project site location")
    construction_phases: Optional[list[ConstructionPhaseInput]] = Field(
        None, description="Ordered list of construction phases"
    )
    default_style: Optional[str] = Field(None, description="Default architectural style for buildings in this project")


class ProjectUpdate(BaseModel):
    """Update an existing project. All fields are optional."""

    name: Optional[str] = Field(None, max_length=255, description="Updated project name")
    description: Optional[str] = Field(None, description="Updated description")
    location: Optional[LocationInput] = Field(None, description="Updated location")
    status: Optional[str] = Field(None, description="Project status: draft, processing, ready, archived")
    construction_phases: Optional[list[ConstructionPhaseInput]] = Field(None, description="Updated construction phases")
    default_style: Optional[str] = Field(None, description="Default architectural style for new buildings")


class ProjectResponse(BaseModel):
    """Full project details including buildings and documents."""

    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID = Field(description="Unique project identifier")
    name: str = Field(description="Project name")
    description: Optional[str] = Field(description="Project description")
    status: str = Field(description="Current status: draft, processing, ready, archived")
    location: Optional[LocationResponse] = Field(None, description="Project site location")
    construction_phases: Optional[list[dict[str, Any]]] = Field(None, description="Construction phase definitions")
    default_style: Optional[str] = Field(None, description="Default architectural style for buildings")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")
    owner_id: uuid.UUID = Field(description="Owner user ID")
    buildings: list["BuildingResponse"] = Field(default=[], description="Buildings in this project")
    documents: list["DocumentResponse"] = Field(default=[], description="Uploaded documents")


class ProjectListResponse(BaseModel):
    """Summarized project for list views."""

    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID = Field(description="Unique project identifier")
    name: str = Field(description="Project name")
    description: Optional[str] = Field(description="Project description")
    status: str = Field(description="Current status")
    location: Optional[LocationResponse] = Field(None, description="Project site location")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")
    owner_email: Optional[str] = Field(None, description="Owner email (admin view only)")


# =============================================================================
# Building Schemas
# =============================================================================


class BuildingCreate(BaseModel):
    """Create a building within a project."""

    name: Optional[str] = Field(None, description="Building name, e.g. 'Tower A'")
    height_meters: Optional[float] = Field(None, gt=0, description="Total building height in meters")
    floor_count: Optional[int] = Field(None, gt=0, description="Number of floors/stories")
    floor_height_meters: Optional[float] = Field(None, gt=0, description="Height per floor in meters")
    roof_type: Optional[str] = Field(None, description="Roof type: flat, gabled, or hipped")
    construction_phase: Optional[int] = Field(None, description="Construction phase number this building belongs to")
    footprint_coordinates: Optional[list[list[float]]] = Field(
        None, description="Building footprint as [[x,y], ...] polygon coordinates"
    )
    specifications: Optional[dict[str, Any]] = Field(
        None, description="Additional specs: facade_material, total_area_sqm, etc."
    )
    architectural_style: Optional[str] = Field(
        None, description="Architectural style ID (e.g., 'modern', 'classical', 'brutalist')"
    )


class BuildingUpdate(BaseModel):
    """Update building properties. All fields are optional."""

    name: Optional[str] = Field(None, description="Updated building name")
    height_meters: Optional[float] = Field(None, gt=0, description="Updated height in meters")
    floor_count: Optional[int] = Field(None, gt=0, description="Updated floor count")
    floor_height_meters: Optional[float] = Field(None, gt=0, description="Updated floor height")
    roof_type: Optional[str] = Field(None, description="Updated roof type: flat, gabled, or hipped")
    construction_phase: Optional[int] = Field(None, description="Updated construction phase")
    specifications: Optional[dict[str, Any]] = Field(None, description="Updated specifications")
    footprint_coordinates: Optional[list[list[float]]] = Field(
        None, description="Updated footprint as [[lng, lat], ...] polygon coordinates"
    )
    rotation_degrees: Optional[float] = Field(None, description="Y-axis rotation in degrees (0-360)")
    architectural_style: Optional[str] = Field(None, description="Architectural style ID")


class BuildingResponse(BaseModel):
    """Building details including 3D model URLs."""

    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID = Field(description="Unique building identifier")
    project_id: uuid.UUID = Field(description="Parent project ID")
    name: Optional[str] = Field(description="Building name")
    height_meters: Optional[float] = Field(description="Total height in meters")
    floor_count: Optional[int] = Field(description="Number of floors")
    floor_height_meters: Optional[float] = Field(description="Height per floor in meters")
    roof_type: Optional[str] = Field(description="Roof type: flat, gabled, or hipped")
    construction_phase: Optional[int] = Field(description="Construction phase number")
    model_url: Optional[str] = Field(description="URL to the generated GLB 3D model")
    lod_urls: Optional[dict[str, str]] = Field(None, description="LOD variant URLs: {'0': full, '1': simplified, ...}")
    specifications: Optional[dict[str, Any]] = Field(
        description="Additional specifications (materials, area, AI confidence, etc.)"
    )
    generation_status: Optional[str] = Field(
        None, description="AI generation status: idle, generating, completed, failed"
    )
    generation_prompt: Optional[str] = Field(None, description="Text prompt used for AI generation")
    meshy_task_id: Optional[str] = Field(None, description="Meshy.ai task ID for tracking")
    footprint_coordinates: Optional[list[list[float]]] = Field(
        None, description="Footprint polygon as [[lng, lat], ...] coordinate pairs"
    )
    rotation_degrees: Optional[float] = Field(None, description="Y-axis rotation in degrees (0-360)")
    architectural_style: Optional[str] = Field(None, description="Architectural style ID")
    preview_url: Optional[str] = Field(None, description="URL to the latest AI render preview image")
    preview_status: Optional[str] = Field(
        None, description="Render preview status: idle, generating, completed, failed"
    )
    generation_engine: Optional[str] = Field(None, description="3D generation engine used: meshy, tripo, procedural")
    created_at: datetime = Field(description="Creation timestamp")


# =============================================================================
# Document Schemas
# =============================================================================


class DocumentResponse(BaseModel):
    """Uploaded document with processing status."""

    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID = Field(description="Unique document identifier")
    project_id: uuid.UUID = Field(description="Parent project ID")
    filename: str = Field(description="Original filename")
    file_type: str = Field(description="File extension: pdf, jpg, png, dxf, xlsx, csv, geojson")
    file_size_bytes: int = Field(description="File size in bytes")
    processing_status: str = Field(description="Processing status: pending, processing, completed, failed")
    uploaded_at: datetime = Field(description="Upload timestamp")
    processed_at: Optional[datetime] = Field(description="Processing completion timestamp")


class ProcessingStatusResponse(BaseModel):
    """Real-time status of a Celery processing task."""

    job_id: str = Field(description="Celery task ID")
    status: str = Field(description="Task state: PENDING, PROCESSING, GENERATING, SUCCESS, FAILURE")
    progress: Optional[float] = Field(None, description="Progress percentage (0.0 to 1.0)")
    message: Optional[str] = Field(None, description="Current processing step description")
    result: Optional[dict[str, Any]] = Field(None, description="Task result when completed")


# =============================================================================
# Project Sharing Schemas
# =============================================================================


class ShareProjectRequest(BaseModel):
    email: EmailStr
    permission: str = Field("viewer", pattern="^(viewer|editor)$")


class ShareResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    project_id: uuid.UUID
    user_id: Optional[uuid.UUID]
    email: Optional[str]
    permission: str
    is_public_link: bool
    invite_token: Optional[str] = None
    created_at: datetime


class PublicLinkResponse(BaseModel):
    token: str
    url: str


# =============================================================================
# Annotation Schemas
# =============================================================================


class AnnotationCreate(BaseModel):
    text: str = Field(min_length=1, max_length=2000)
    building_id: Optional[uuid.UUID] = None
    position_x: float
    position_y: float
    position_z: float


class AnnotationUpdate(BaseModel):
    text: Optional[str] = Field(None, min_length=1, max_length=2000)
    resolved: Optional[bool] = None


class AnnotationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    project_id: uuid.UUID
    building_id: Optional[uuid.UUID]
    author_id: uuid.UUID
    text: str
    position_x: float
    position_y: float
    position_z: float
    resolved: bool
    created_at: datetime


# =============================================================================
# Site Zone Schemas
# =============================================================================


SiteZoneType = Literal[
    "site_boundary",
    "building",
    "residential",
    "road",
    "green_space",
    "parking",
    "water",
    "development_area",
]


class SiteZoneCreate(BaseModel):
    """Create a site zone within a project."""

    name: Optional[str] = Field(None, description="Zone label")
    zone_type: SiteZoneType = Field(
        description=(
            "Zone type: site_boundary, building, residential, road, green_space, parking, water, "
            "development_area. Paths and trails use road with road_type metadata."
        )
    )
    coordinates: list[list[float]] = Field(description="Polygon vertices as [[lng, lat], ...]")
    color: str = Field(default="#9b59b6", description="Hex color for the zone")
    properties: Optional[dict[str, Any]] = Field(
        None, description="Type-specific properties (height, floors, tree_density, etc.)"
    )
    sort_order: int = Field(default=0, description="Display order")


class SiteZoneUpdate(BaseModel):
    """Update a site zone. All fields are optional."""

    name: Optional[str] = Field(None, description="Updated zone label")
    zone_type: Optional[SiteZoneType] = Field(
        None, description="Updated zone type; paths and trails use road with road_type metadata"
    )
    coordinates: Optional[list[list[float]]] = Field(None, description="Updated polygon vertices")
    color: Optional[str] = Field(None, description="Updated hex color")
    properties: Optional[dict[str, Any]] = Field(None, description="Updated type-specific properties")
    sort_order: Optional[int] = Field(None, description="Updated display order")


class SiteZoneResponse(BaseModel):
    """Site zone details with polygon coordinates."""

    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    project_id: uuid.UUID
    name: Optional[str]
    zone_type: str
    coordinates: list[list[float]] = Field(default=[], description="Polygon vertices as [[lng, lat], ...]")
    color: str
    properties: Optional[dict[str, Any]]
    is_active_boundary: bool = False
    sort_order: int
    building_id: Optional[uuid.UUID] = None
    building_ids: Optional[list[uuid.UUID]] = None
    created_at: datetime
    updated_at: datetime


# =============================================================================
# Zone History Schemas
# =============================================================================


class ZoneHistoryResponse(BaseModel):
    """A single zone history entry."""

    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    zone_id: uuid.UUID
    project_id: uuid.UUID
    action: str  # 'create' | 'update' | 'delete'
    snapshot: dict[str, Any]
    previous_snapshot: Optional[dict[str, Any]] = None
    user_id: Optional[uuid.UUID] = None
    user_email: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime


class ZoneHistoryListResponse(BaseModel):
    """Paginated zone history."""

    items: list[ZoneHistoryResponse]
    total: int
    has_more: bool


class ZoneSnapshotRestoreRequest(BaseModel):
    """Restore a zone working state without creating a history entry."""

    zone_id: uuid.UUID
    snapshot: Optional[dict[str, Any]] = None


class ZoneSnapshotRestoreResponse(BaseModel):
    """Result from silently restoring or deleting a zone working snapshot."""

    zone_id: uuid.UUID
    deleted: bool = False
    zone: Optional[SiteZoneResponse] = None


# =============================================================================
# AI Layout Generation Schemas
# =============================================================================


class LayoutBuilding(BaseModel):
    """A single building placement in an AI-generated site layout."""

    center_x: float = Field(description="X offset from zone centroid in degrees longitude")
    center_y: float = Field(description="Y offset from zone centroid in degrees latitude")
    width_m: float = Field(description="Building footprint width in meters")
    depth_m: float = Field(description="Building footprint depth in meters")
    rotation_deg: float = Field(default=0, description="Rotation in degrees (0=north-facing)")
    height_m: Optional[float] = Field(None, description="Building height override in meters")
    floors: Optional[int] = Field(None, description="Number of floors override")
    building_type: str = Field(
        default="residential",
        description="Building type: residential, commercial, mixed_use, retail, civic, institutional",
    )
    building_typology: Optional[str] = Field(
        None,
        description="Building typology: townhouse_row, mid_rise_apartment, apartment_block, mixed_use_podium, retail_liner, office_block",
    )
    block_id: Optional[int] = Field(None, description="Block ID grouping buildings that share a street frontage")
    setback_front_m: float = Field(default=3.0, description="Front setback in meters")
    setback_side_m: float = Field(default=1.5, description="Side setback in meters")
    name: Optional[str] = Field(None, description="Custom building name")
    description: Optional[str] = Field(None, description="Building description for 3D generation prompt")
    style: Optional[str] = Field(None, description="Architectural style override")


class LayoutRoad(BaseModel):
    """An internal road in the AI-generated layout."""

    centerline: list[list[float]] = Field(description="Road centerline as [[x_offset, y_offset], ...] in degrees")
    width_m: float = Field(default=6.0, description="Road width in meters")
    road_type: str = Field(default="local", description="Road type: local, collector, cul_de_sac, loop")


class LayoutGreenSpace(BaseModel):
    """A green/open space in the AI-generated layout."""

    polygon: list[list[float]] = Field(description="Polygon as [[x_offset, y_offset], ...] in degrees")
    space_type: str = Field(
        default="buffer",
        description="Space type: buffer, park, setback, courtyard, civic_green, entry_plaza, planted_verge, pocket_park",
    )


class SiteLayoutResponse(BaseModel):
    """Complete AI-generated site layout response."""

    buildings: list[LayoutBuilding] = Field(description="Building placements")
    roads: list[LayoutRoad] = Field(default=[], description="Internal roads")
    green_spaces: list[LayoutGreenSpace] = Field(default=[], description="Green/open spaces")
    layout_strategy: str = Field(
        default="grid", description="Layout strategy used: cul_de_sac, loop_road, grid_collector, perimeter, etc."
    )
    reasoning: str = Field(default="", description="AI reasoning for the layout decisions")
    density_achieved: Optional[float] = Field(None, description="Achieved density in units per hectare")


class SiteLayoutOption(SiteLayoutResponse):
    """A single layout option in a multi-option preview response."""

    option_index: int = Field(description="Index of this option (0-based)")
    option_label: str = Field(default="", description="Human-readable label, e.g. 'Cul-de-sac', 'Loop Road'")
    orientation_deg: Optional[float] = Field(
        None, description="Primary site orientation angle in degrees (for orientation explorer options)"
    )
    orientation_mode: Optional[str] = Field(None, description="Option family identifier, e.g. 'site_orientation'")


class LayoutPreviewResponse(BaseModel):
    """Response containing multiple layout options for user to choose from."""

    options: list[SiteLayoutOption] = Field(description="Layout options to choose from")
    zone_id: str = Field(description="Zone ID these options are for")


class ApplyLayoutRequest(BaseModel):
    """Request to apply a chosen layout option to a zone."""

    option_index: int = Field(description="Index of the chosen layout option")
    layout: SiteLayoutResponse = Field(description="The full layout data to apply")


# =============================================================================
# Site-Wide Massing Schemas
# =============================================================================


class SiteMassingZone(BaseModel):
    """Layout data for a single zone within a site-wide massing option."""

    zone_id: str = Field(description="ID of the source site zone")
    zone_type: str = Field(description="Zone type: building, residential, green_space, road, parking, etc.")
    zone_label: str = Field(default="", description="Human-readable zone label")
    buildings: list[LayoutBuilding] = Field(default=[], description="Building placements for this zone")
    roads: list[LayoutRoad] = Field(default=[], description="Internal roads for this zone")
    green_spaces: list[LayoutGreenSpace] = Field(default=[], description="Green/open spaces for this zone")


class SiteMassingOption(BaseModel):
    """A single holistic site massing configuration."""

    option_index: int = Field(description="Index of this option (0-based)")
    option_label: str = Field(description="Human-readable label, e.g. 'High Density Cluster'")
    zones: list[SiteMassingZone] = Field(description="Layout data for each zone in this option")
    reasoning: str = Field(default="", description="AI reasoning for this configuration")
    total_building_count: int = Field(default=0, description="Total buildings across all zones")
    total_floor_area_m2: Optional[float] = Field(None, description="Estimated total gross floor area")
    density_achieved: Optional[float] = Field(None, description="Achieved density in units per hectare")


class SiteMassingResponse(BaseModel):
    """Response containing 3 site-wide massing options."""

    project_id: str = Field(description="Project ID")
    options: list[SiteMassingOption] = Field(description="3 massing options to choose from")


# =============================================================================
# OSM Context Schemas
# =============================================================================


class OSMContextBuilding(BaseModel):
    """A building from OSM context data."""

    osm_id: int = Field(description="OpenStreetMap way ID")
    coordinates: list[list[float]] = Field(description="Polygon as [[lon, lat], ...]")
    height_m: Optional[float] = Field(None, description="Estimated height in meters")
    building_type: str = Field(default="yes", description="OSM building tag value")
    name: Optional[str] = Field(None, description="Building name if tagged")
    levels: Optional[str] = Field(None, description="Number of levels")


class OSMContextRoad(BaseModel):
    """A road from OSM context data."""

    osm_id: int = Field(description="OpenStreetMap way ID")
    coordinates: list[list[float]] = Field(description="Linestring as [[lon, lat], ...]")
    width_m: float = Field(default=6.0, description="Estimated width in meters")
    road_type: str = Field(default="residential", description="OSM highway tag value")
    name: Optional[str] = Field(None, description="Road name if tagged")
    surface: Optional[str] = Field(None, description="Road surface material")
    lanes: Optional[str] = Field(None, description="Number of lanes")


class OSMContextFeature(BaseModel):
    """A water or park feature from OSM context data."""

    osm_id: int = Field(description="OpenStreetMap way ID")
    coordinates: list[list[float]] = Field(description="Geometry as [[lon, lat], ...]")
    feature_type: str = Field(description="Feature type: water, park, grass, etc.")
    name: Optional[str] = Field(None, description="Feature name if tagged")


class OSMContextResponse(BaseModel):
    """Complete OSM context for a site boundary."""

    buildings: list[OSMContextBuilding] = Field(default=[], description="Nearby buildings")
    roads: list[OSMContextRoad] = Field(default=[], description="Nearby roads")
    water: list[OSMContextFeature] = Field(default=[], description="Water features")
    parks: list[OSMContextFeature] = Field(default=[], description="Parks and green spaces")
    fetched_at: str = Field(description="ISO timestamp of when context was fetched")
    buffer_m: float = Field(default=50, description="Buffer distance used in meters")


class RegenerateLayoutRequest(BaseModel):
    """Request to regenerate layout with locked layers preserved."""

    locked_roads: list[int] = Field(default=[], description="Indices of roads to keep locked")
    locked_buildings: list[int] = Field(default=[], description="Indices of buildings to keep locked")
    locked_green_spaces: list[int] = Field(default=[], description="Indices of green spaces to keep locked")


class MasterPlan2DReferenceMetadata(BaseModel):
    """Structured reference metadata passed into the 2D generator."""

    reference_id: Optional[str] = Field(None, description="Stable client-side reference identifier")
    zone_id: str = Field(description="Source zone ID")
    zone_name: Optional[str] = Field(None, description="Source zone name")
    zone_type: str = Field(description="Source zone type")
    domain: Optional[str] = Field(None, description="Semantic domain such as building, parks, plazas, or streets_paths")
    category: Optional[str] = Field(None, description="Selected category")
    subcategory: Optional[str] = Field(None, description="Selected subcategory or typology")
    archetype_name: Optional[str] = Field(None, description="Selected archetype or hero image name")
    asset_id: Optional[str] = Field(None, description="Image asset identifier when available")
    image_url: str = Field(description="Resolved image URL")
    image_path: Optional[str] = Field(None, description="Internal image path when available")
    source: str = Field(description="Reference source: zone_prompt, archetype, or reference_image")
    source_label: str = Field(description="Human-readable source label")
    prompt_text: Optional[str] = Field(None, description="Prompt or caption text attached to the reference")
    caption: Optional[str] = Field(None, description="Reference caption")
    tags: Optional[list[str]] = Field(None, description="Generation tags or keywords")
    selection_order: Optional[int] = Field(None, description="Client-side selection order")
    style_profile: Optional[dict[str, Any]] = Field(None, description="Saved style profile for the selected reference")
    generation_style: Optional[dict[str, Any]] = Field(
        None, description="Saved generation style input for the selected reference"
    )


RenderStylePreset = Literal[
    "photorealistic_aerial",
    "photoreal_orthographic_aerial",
    "digital_watercolor_map",
    "watercolor_wash",
    "ink_line_drawing",
    "marker_render",
    "cinematic_dusk",
    "collage_mixed_media",
    "lush_landscape",
    "white_massing_model",
    "flat_diagrammatic",
]
LightingAtmospherePreset = Literal["crisp_summer_day", "golden_hour", "overcast_soft", "winter_snow"]
MasterPlanImageProvider = Literal["vertex", "stability", "gemini"]
MasterPlan2DRenderMode = Literal["orthographic_aerial_site_insert", "legacy_prompt_first"]


class MasterPlanMapBounds(BaseModel):
    """Viewport bounds associated with a captured map screenshot."""

    west: float = Field(ge=-180, le=180, description="Western longitude bound")
    south: float = Field(ge=-90, le=90, description="Southern latitude bound")
    east: float = Field(ge=-180, le=180, description="Eastern longitude bound")
    north: float = Field(ge=-90, le=90, description="Northern latitude bound")


class MasterPlan2DGenerateRequest(BaseModel):
    """Request to generate 2D aerial master-plan options."""

    render_mode: MasterPlan2DRenderMode = Field(
        default="orthographic_aerial_site_insert",
        description="Primary 2D render mode. orthographic_aerial_site_insert is the deterministic site-insert path.",
    )
    prompt: Optional[str] = Field(
        None,
        max_length=2000,
        description="Legacy free-text style direction. Prefer render_style_preset + lighting_atmosphere_preset + specific_overrides.",
    )
    render_style_preset: RenderStylePreset = Field(
        "photoreal_orthographic_aerial",
        description="High-level visual style preset for hidden prompt matrix compilation",
    )
    lighting_atmosphere_preset: LightingAtmospherePreset = Field(
        "crisp_summer_day", description="Lighting and atmosphere preset for hidden prompt matrix compilation"
    )
    specific_overrides: Optional[str] = Field(
        None, max_length=500, description="Optional specific directive appended to internal prompt matrix output"
    )
    option_count: int = Field(default=3, ge=1, le=6, description="Number of options to generate")
    style_preset: Optional[str] = Field(
        None,
        pattern="^(auto|rendered_sales_plan|hybrid_annotated_master_plan|illustrative_landscape_plan)$",
        description="Optional style preset selection",
    )
    quality_level: Optional[str] = Field(
        "presentation",
        pattern="^(draft|presentation|board_ready)$",
        description="Renderer quality level",
    )
    show_legend: Optional[bool] = Field(None, description="Override legend visibility")
    show_north_arrow: Optional[bool] = Field(None, description="Override north-arrow visibility")
    show_scale_bar: Optional[bool] = Field(None, description="Override scale-bar visibility")
    show_callout_markers: Optional[bool] = Field(None, description="Override callout marker visibility")
    show_surrounding_context: Optional[bool] = Field(None, description="Override muted context visibility")
    export_width: int = Field(default=4200, ge=3000, le=5000, description="High-resolution export width in pixels")
    map_screenshot_satellite: Optional[str] = Field(
        None,
        description="Optional satellite basemap screenshot data URI used as a real-context underlay for 2D renders",
    )
    map_screenshot_bounds: Optional[MasterPlanMapBounds] = Field(
        None, description="Optional map bounds for the screenshot underlay"
    )
    reference_images: Optional[list[str]] = Field(
        None, description="Structured reference image URLs selected for the 2D generator"
    )
    reference_metadata: Optional[list[MasterPlan2DReferenceMetadata]] = Field(
        None, description="Structured reference metadata bundle"
    )
    selected_image_urls: Optional[list[str]] = Field(
        None, description="Deprecated alias for selected reference image URLs"
    )
    ai_style_pass_enabled: Optional[bool] = Field(
        False, description="Run an optional AI texture pass on top of the geometry-locked 2D render"
    )
    ai_style_pass_provider: Optional[str] = Field(
        "gemini",
        pattern="^(auto|gemini|stability)$",
        description="AI style-pass provider preference. Gemini/Nano Banana is the default image finish path.",
    )
    compose_board: Optional[bool] = Field(
        True, description="Compose a deterministic presentation board in code after plan imagery generation"
    )
    board_template: Optional[str] = Field("master_plan_board_v1", description="Deterministic board template key")
    include_photo_strip: Optional[bool] = Field(
        True, description="Whether to include a deterministic reference/photo strip panel"
    )
    debug: Optional[bool] = Field(False, description="Whether to emit QA debug overlays alongside the final outputs")


class MasterPlan2DOptionResponse(BaseModel):
    """Saved 2D master-plan option."""

    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID = Field(description="Unique option ID")
    project_id: uuid.UUID = Field(description="Parent project ID")
    label: str = Field(description="Version label, e.g. Version A")
    style_preset: str = Field(description="Preset slug")
    style_name: str = Field(description="Preset display name")
    variant_index: int = Field(description="0-based index inside the generated set")
    preview_url: str = Field(description="Preview image URL/data URI")
    preview_png_url: str = Field(description="Preview PNG URL")
    full_png_url: Optional[str] = Field(None, description="Full-resolution PNG URL")
    svg_url: Optional[str] = Field(None, description="Downloadable SVG URL")
    plan_preview_png_url: Optional[str] = Field(None, description="Plan-layer preview PNG URL (imagery pass output)")
    plan_full_png_url: Optional[str] = Field(None, description="Plan-layer full PNG URL (imagery pass output)")
    plan_svg_url: Optional[str] = Field(None, description="Plan-layer SVG URL (imagery pass output)")
    debug_png_url: Optional[str] = Field(None, description="Optional debug overlay PNG URL")
    is_selected: bool = Field(description="Whether this option is selected")
    metadata: Optional[dict[str, Any]] = Field(None, description="Render metadata")
    created_at: datetime = Field(description="Creation timestamp")


class MasterPlan2DGenerateResponse(BaseModel):
    """Response for generation/regeneration of 2D options."""

    project_id: str = Field(description="Project ID")
    options: list[MasterPlan2DOptionResponse] = Field(description="Generated options")


class MasterPlan2DSelectResponse(BaseModel):
    """Response after selecting the preferred 2D option."""

    status: str = Field(description="Operation status")
    project_id: str = Field(description="Project ID")
    selected_option_id: str = Field(description="Selected option ID")


class MasterPlan2DExportResponse(BaseModel):
    """High-resolution export payload for a generated 2D option."""

    option_id: str = Field(description="Option ID")
    project_id: str = Field(description="Project ID")
    label: str = Field(description="Option label")
    style_preset: str = Field(description="Preset slug")
    style_name: str = Field(description="Preset display name")
    width: int = Field(description="Export width in pixels")
    height: int = Field(description="Export height in pixels")
    svg: str = Field(description="High-resolution SVG markup")
    preview_png_url: Optional[str] = Field(None, description="Preview PNG URL")
    full_png_url: Optional[str] = Field(None, description="Full-resolution PNG URL")
    svg_url: Optional[str] = Field(None, description="Downloadable SVG URL")
    plan_preview_png_url: Optional[str] = Field(None, description="Plan-layer preview PNG URL (imagery pass output)")
    plan_full_png_url: Optional[str] = Field(None, description="Plan-layer full PNG URL (imagery pass output)")
    plan_svg_url: Optional[str] = Field(None, description="Plan-layer SVG URL (imagery pass output)")
    debug_png_url: Optional[str] = Field(None, description="Optional debug overlay PNG URL")


BoardZoneKind = Literal[
    "site_boundary", "building", "residential", "road", "green_space", "parking", "water", "development_area"
]


class MasterPlanBoardLegendItem(BaseModel):
    chip_id: str = Field(description="Legend chip identifier")
    label: str = Field(description="Legend label")
    color: str = Field(description="Legend color")


class MasterPlanBoardCopyItem(BaseModel):
    chip_id: str = Field(description="Chip identifier for right panel copy")
    title: str = Field(description="Right panel item title")
    body: str = Field(description="Right panel item body copy")


class MasterPlanBoardZone(BaseModel):
    zone_id: str = Field(description="Stable zone identifier")
    zone_label: str = Field(description="Human readable zone label")
    chip_id: str = Field(description="Board chip ID such as A1 or R2")
    zone_kind: BoardZoneKind = Field(description="Normalized zone kind")
    color: str = Field(description="Zone color")
    polygon: list[list[float]] = Field(default_factory=list, description="Zone polygon coordinates [lng, lat]")
    label_anchor: Optional[list[float]] = Field(None, description="Optional label anchor [lng, lat]")
    height_m: Optional[float] = Field(None, ge=0, description="Optional zone height in meters")
    floor_count: Optional[int] = Field(None, ge=0, description="Optional floor count")
    archetype_title: Optional[str] = Field(None, description="Optional archetype title")
    archetype_metadata: Optional[dict[str, Any]] = Field(None, description="Optional archetype metadata")
    user_notes: Optional[str] = Field(None, description="Optional user notes")

    @field_validator("polygon")
    @classmethod
    def _validate_polygon(cls, value: list[list[float]]) -> list[list[float]]:
        for point in value:
            if not isinstance(point, list) or len(point) != 2:
                raise ValueError("polygon points must be [lng, lat] pairs")
        return value

    @field_validator("label_anchor")
    @classmethod
    def _validate_label_anchor(cls, value: Optional[list[float]]) -> Optional[list[float]]:
        if value is None:
            return value
        if len(value) != 2:
            raise ValueError("label_anchor must be [lng, lat]")
        return value


class MasterPlanBoardExportSettings(BaseModel):
    width: int = Field(default=4200, ge=1200, le=10000, description="Board export width in pixels")
    height: int = Field(default=2800, ge=900, le=10000, description="Board export height in pixels")


class MasterPlanBoardSpec(BaseModel):
    site_id: str = Field(description="Site identifier")
    project_title: str = Field(description="Board title")
    subtitle: Optional[str] = Field(None, description="Board subtitle")
    board_variant: str = Field(default="master_plan_board_v1", description="Board template key")
    zones: list[MasterPlanBoardZone] = Field(default_factory=list, description="Board zones")
    legend_items: list[MasterPlanBoardLegendItem] = Field(default_factory=list, description="Legend items")
    right_panel_copy: list[MasterPlanBoardCopyItem] = Field(default_factory=list, description="Right panel copy items")
    annotation_items: list[dict[str, Any]] = Field(default_factory=list, description="Optional annotation items")
    export_settings: MasterPlanBoardExportSettings = Field(
        default_factory=MasterPlanBoardExportSettings, description="Export settings"
    )

    @model_validator(mode="after")
    def _validate_chip_consistency(self) -> "MasterPlanBoardSpec":
        zone_chips = [zone.chip_id for zone in self.zones]
        if len(zone_chips) != len(set(zone_chips)):
            raise ValueError("zones must use unique chip_id values")
        legend_chips = [item.chip_id for item in self.legend_items]
        if len(legend_chips) != len(set(legend_chips)):
            raise ValueError("legend_items must use unique chip_id values")
        return self


# =============================================================================
# 2D to 3D Master Plan Schemas
# =============================================================================


class MasterPlan3DZoneSnapshot(BaseModel):
    """Client-side zone snapshot carried with the Generate-to-3D request for unsaved canvas state."""

    zone_id: str = Field(description="Client or persisted zone identifier")
    zone_label: Optional[str] = Field(None, description="Display label for the zone")
    zone_type: str = Field(description="Zone type")
    color: Optional[str] = Field(None, description="Zone display color")
    polygon: list[list[float]] = Field(
        default_factory=list, description="Authoritative polygon in WGS84 [lng, lat] pairs"
    )
    height_m: Optional[float] = Field(None, ge=0, description="Optional override height in meters")
    floor_count: Optional[int] = Field(None, ge=0, description="Optional override floor count")
    archetype_title: Optional[str] = Field(None, description="Optional archetype title")
    archetype_metadata: Optional[dict[str, Any]] = Field(None, description="Optional archetype metadata")
    user_notes: Optional[str] = Field(None, description="Optional user note for this zone")

    @field_validator("polygon")
    @classmethod
    def _validate_polygon(cls, value: list[list[float]]) -> list[list[float]]:
        if not value or len(value) < 4:
            raise ValueError("polygon must include at least 4 coordinate pairs")
        for point in value:
            if not isinstance(point, list) or len(point) != 2:
                raise ValueError("polygon points must be [lng, lat] pairs")
        return value


class MasterPlan3DGenerateRequest(BaseModel):
    """Request to convert a generated 2D master plan into structured 3D render packages."""

    render_style_preset: RenderStylePreset = Field(
        default="photoreal_orthographic_aerial",
        description="High-level render style preset resolved through hidden prompt matrix",
    )
    lighting_atmosphere_preset: LightingAtmospherePreset = Field(
        default="crisp_summer_day",
        description="Lighting and atmosphere preset resolved through hidden prompt matrix",
    )
    specific_overrides: Optional[str] = Field(
        None, max_length=500, description="Optional specific directive appended after preset matrix payload"
    )
    selected_perspective: Literal[
        "aerial_oblique", "street_level_eye_height", "corner_perspective", "promenade_view"
    ] = Field(
        default="aerial_oblique",
        description="Preferred camera framing for downstream 3D renders",
    )
    lighting_variant: Literal["golden_hour", "clear_daylight", "overcast_soft_light", "blue_hour_dusk"] = Field(
        default="clear_daylight",
        description="Lighting mood to apply to the 3D scene prompts",
    )
    scope: Literal["full_site", "selected_zones", "focused_frontage"] = Field(
        default="full_site",
        description="Whether to package the full site, selected zones only, or a focused frontage study",
    )
    selected_zone_ids: list[str] = Field(
        default_factory=list, description="Explicit zone IDs to include for selected or focused scope"
    )
    zones: list[MasterPlan3DZoneSnapshot] = Field(
        default_factory=list, description="Optional active-canvas zone snapshot for unsaved geometry state"
    )
    global_style_notes: Optional[str] = Field(
        None,
        max_length=2000,
        description="Legacy global notes. Retained for compatibility and merged into compiled style payload.",
    )

    @field_validator("selected_zone_ids", mode="before")
    @classmethod
    def _normalize_selected_zone_ids(cls, value: Any) -> list[str]:
        if value is None:
            return []
        values = value if isinstance(value, list) else [value]
        normalized: list[str] = []
        seen: set[str] = set()
        for item in values:
            token = str(item or "").strip()
            if not token or token in seen:
                continue
            seen.add(token)
            normalized.append(token)
        return normalized

    @model_validator(mode="after")
    def _validate_scope_selection(self) -> "MasterPlan3DGenerateRequest":
        if self.scope in {"selected_zones", "focused_frontage"} and not self.selected_zone_ids:
            raise ValueError(
                "selected_zone_ids must include at least one zone for selected_zones or focused_frontage scope"
            )
        return self


class MasterPlan3DFootprintReference(BaseModel):
    """Reference back to the authoritative 2D source geometry."""

    source_zone_label: str = Field(description="Original zone label")
    geometry_type: str = Field(description="Authoritative geometry type")


class MasterPlan3DFootprintGeometry(BaseModel):
    """Serializable authoritative footprint geometry for downstream renderers."""

    type: Literal["Polygon"] = Field(description="GeoJSON geometry type")
    coordinates: list[list[list[float]]] = Field(description="Polygon coordinates in WGS84 lon/lat order")


class MasterPlan3DRendererNotes(BaseModel):
    """Structured guidance for the downstream image renderer."""

    keep_footprint_alignment: bool = Field(description="Whether footprint alignment is mandatory")
    recommended_condition_strength: float = Field(description="Recommended geometry conditioning strength")
    geometry_priority: Literal["high"] = Field(description="Priority of geometry fidelity")
    style_override_applied: bool = Field(description="Whether user or global style overrides were applied")
    avoid: list[str] = Field(description="Negative constraints for the renderer")


class MasterPlan3DConditioningAssets(BaseModel):
    """Optional control images/maps for conditioned downstream inference."""

    structure_image_url: Optional[str] = Field(None, description="Orthographic structure-control image URL")
    depth_map_url: Optional[str] = Field(None, description="Orthographic depth-map image URL")
    segmentation_map_url: Optional[str] = Field(None, description="Orthographic segmentation-map image URL")
    massing_image_url: Optional[str] = Field(None, description="Orthographic clay/massing image URL")
    perspective_structure_image_url: Optional[str] = Field(None, description="Perspective structure-control image URL")
    perspective_depth_map_url: Optional[str] = Field(None, description="Perspective depth-map image URL")
    perspective_segmentation_map_url: Optional[str] = Field(None, description="Perspective segmentation-map image URL")
    perspective_massing_image_url: Optional[str] = Field(None, description="Perspective clay/massing image URL")
    camera_perspective: Optional[str] = Field(
        None, description="Perspective preset used to derive the camera-aware control images"
    )
    control_mode: Optional[str] = Field(None, description="Conditioning mode for the target renderer")
    control_strength: Optional[float] = Field(None, description="Recommended conditioning strength")


class MasterPlan3DRenderPackage(BaseModel):
    """A single renderer-ready 3D prompt package derived from a 2D zone."""

    scene_id: str = Field(description="Stable scene/package identifier")
    zone_id: str = Field(description="Source zone ID")
    zone_label: str = Field(description="Source zone label")
    zone_type: str = Field(description="Source zone type")
    archetype_title: str = Field(description="Resolved archetype or precinct title")
    height_m: float = Field(description="Resolved massing height in meters")
    floor_count: int = Field(description="Resolved floor count")
    footprint_reference: MasterPlan3DFootprintReference = Field(
        description="Link back to the authoritative 2D footprint"
    )
    footprint_geometry: MasterPlan3DFootprintGeometry = Field(description="Authoritative polygon geometry")
    archetype_metadata: dict[str, Any] = Field(
        default_factory=dict, description="Resolved archetype/style metadata for the zone"
    )
    user_notes: Optional[str] = Field(None, description="High-priority descriptive note from the user")
    render_prompt: str = Field(description="Downstream image-render prompt")
    renderer_notes: MasterPlan3DRendererNotes = Field(description="Renderer guardrails and conditioning hints")
    source_concept_image_url: Optional[str] = Field(
        None, description="Selected 2D concept image used as structural control source"
    )
    source_concept_asset_id: Optional[str] = Field(None, description="Stable source image asset id when available")
    conditioning_assets: Optional[MasterPlan3DConditioningAssets] = Field(
        None, description="Optional control images/maps for conditioned inference"
    )
    provider: MasterPlanImageProvider = Field(description="Provider routed for this render package")
    model: str = Field(description="Model identifier used for this package")
    prompt_type: str = Field(description="Prompt compiler type for this package")
    job_type: Literal["3d"] = Field(description="Render job type")
    render_image_url: Optional[str] = Field(
        None, description="Optional generated 3D render image URL when renderer execution is enabled"
    )


class MasterPlan3DPackageWarning(BaseModel):
    """Skipped-zone warning during 2D to 3D package generation."""

    zone_id: Optional[str] = Field(None, description="Zone ID when available")
    zone_label: Optional[str] = Field(None, description="Zone label when available")
    reason: str = Field(description="Why the zone was skipped or defaulted")


class MasterPlan3DRendererAdapter(BaseModel):
    """Future-facing adapter metadata for downstream renderer integration."""

    status: str = Field(description="Adapter status")
    provider: str = Field(description="Target downstream renderer provider")
    integration_status: str = Field(description="Implementation state for the adapter")
    notes: str = Field(description="Next-step note for renderer integration")


class MasterPlanProviderRouting(BaseModel):
    """Provider routing metadata for the hybrid 2D->3D pipeline."""

    two_d_image_provider: MasterPlanImageProvider = Field(description="Provider used for 2D site-image generation")
    three_d_image_provider: MasterPlanImageProvider = Field(description="Provider used for 3D-from-2D rendering")


class MasterPlan3DGenerateResponse(BaseModel):
    """Structured 3D render packages prepared from a generated 2D master plan option."""

    site_id: str = Field(description="Project/site ID")
    option_id: str = Field(description="Source 2D option ID")
    source_option_label: str = Field(description="Source 2D option label")
    selected_perspective: str = Field(description="Perspective used for package generation")
    lighting_variant: str = Field(description="Lighting variant used for package generation")
    scope: str = Field(description="Generation scope")
    selected_zone_ids: list[str] = Field(
        default_factory=list, description="Zone IDs explicitly selected for this package run"
    )
    global_style_notes: Optional[str] = Field(None, description="Legacy global notes applied to every package")
    render_style_preset: RenderStylePreset = Field(description="Resolved render style preset")
    lighting_atmosphere_preset: LightingAtmospherePreset = Field(description="Resolved lighting and atmosphere preset")
    specific_overrides: Optional[str] = Field(None, description="Optional specific overrides passed by the user")
    global_style_payload: Optional[str] = Field(
        None, description="Compiled hidden style matrix payload used across prompts"
    )
    source_concept_image_url: Optional[str] = Field(
        None, description="Selected approved 2D image used as concept/control source"
    )
    provider_routing: MasterPlanProviderRouting = Field(
        description="Configured image provider routing for 2D and 3D stages"
    )
    render_packages: list[MasterPlan3DRenderPackage] = Field(description="Structured render packages")
    skipped_zones: list[MasterPlan3DPackageWarning] = Field(
        default_factory=list, description="Skipped or defaulted zones"
    )
    renderer_adapter: MasterPlan3DRendererAdapter = Field(description="Downstream renderer integration metadata")
    created_at: datetime = Field(description="Creation timestamp")


# =============================================================================
# 3D Generation Schemas
# =============================================================================


class BuildingData(BaseModel):
    """Normalized building data for 3D generation."""

    id: str
    footprint: list[list[float]]  # [[x,y], [x,y], ...]
    height: float
    floors: int
    floor_height: float = 3.0
    roof_type: str = "flat"
    materials: dict[str, str] = Field(default_factory=lambda: {"facade": "concrete", "roof": "flat"})
    features: dict[str, Any] = Field(default_factory=dict)


class ProjectData(BaseModel):
    """Full normalized project data for 3D scene generation."""

    project_name: str
    location: LocationInput
    buildings: list[BuildingData]
    site_features: list[dict[str, Any]] = Field(default_factory=list)


# =============================================================================
# AI Generation Schemas
# =============================================================================


class GenerateRequest(BaseModel):
    """Request to generate a 3D model from a text prompt."""

    prompt: str = Field(min_length=3, max_length=500, description="Text description of the 3D model to generate")
    art_style: str = Field(default="realistic", description="Art style: realistic, cartoon, low-poly, sculpture")
    negative_prompt: Optional[str] = Field(None, max_length=500, description="What to avoid in generation")
    style: Optional[str] = Field(None, description="Architectural style ID for prompt enrichment")
    engine: Optional[str] = Field(
        None, description="Generation engine: 'meshy' or 'tripo' (defaults to system setting)"
    )


class GenerateFromImageRequest(BaseModel):
    """Request to generate a 3D model from an image."""

    image_url: str = Field(description="URL of the source image")


class GenerationStatusResponse(BaseModel):
    """Status of an AI 3D generation task."""

    status: str = Field(description="Generation status: idle, generating, completed, failed")
    progress: Optional[float] = Field(None, description="Progress percentage (0-100)")
    step: Optional[str] = Field(
        None, description="Current generation step: calling_meshy, polling, refining, downloading, etc."
    )
    model_url: Optional[str] = Field(None, description="URL to the generated GLB model when completed")
    preview_model_url: Optional[str] = Field(None, description="URL to preview model available during refinement")
    error: Optional[str] = Field(None, description="Error message if generation failed")
    meshy_task_id: Optional[str] = Field(None, description="Meshy task ID for external tracking")


class AITemplate(BaseModel):
    """Pre-built template for AI 3D model generation."""

    id: str = Field(description="Unique template identifier")
    name: str = Field(description="Display name")
    category: str = Field(description="Category: commercial, residential, infrastructure, landscaping")
    prompt: str = Field(description="Text prompt for generation")
    thumbnail_url: Optional[str] = Field(None, description="Preview thumbnail URL")


# =============================================================================
# Architectural Style Schemas
# =============================================================================


class ArchitecturalStyleResponse(BaseModel):
    """Architectural style definition for the frontend."""

    id: str = Field(description="Unique style identifier")
    name: str = Field(description="Display name")
    description: str = Field(description="Style description")
    facade_material: str = Field(description="Primary facade material")
    secondary_material: str = Field(description="Secondary material")
    roof_material: str = Field(description="Roof material")
    preferred_roof_types: list[str] = Field(description="Suitable roof types for this style")
    prompt_prefix: str = Field(description="AI prompt prefix for this style")
    meshy_art_style: str = Field(description="Meshy.ai art style mapping")
    thumbnail_url: Optional[str] = Field(None, description="Preview thumbnail URL")
    tags: list[str] = Field(default=[], description="Searchable tags")


# =============================================================================
# Render Preview Schemas
# =============================================================================


class RenderPreviewRequest(BaseModel):
    """Request to generate an AI render preview image."""

    prompt: str = Field(min_length=3, max_length=500, description="Prompt for the render")
    style: Optional[str] = Field(None, description="Architectural style ID")
    source_type: str = Field(default="text", description="Source type: text, sketch, floor_plan")
    source_image_url: Optional[str] = Field(None, description="Source image URL for sketch-to-render")


class RenderPreviewResponse(BaseModel):
    """Render preview result."""

    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID = Field(description="Preview ID")
    building_id: uuid.UUID = Field(description="Building ID")
    image_url: str = Field(description="URL to the generated preview image")
    prompt: Optional[str] = Field(description="Prompt used")
    style: Optional[str] = Field(description="Style used")
    source_type: str = Field(description="Source type")
    source_image_url: Optional[str] = Field(None, description="Source image URL")
    created_at: datetime = Field(description="Creation timestamp")


# =============================================================================
# Generation Engine Schemas
# =============================================================================


class GenerationEngineInfo(BaseModel):
    """Information about an available 3D generation engine."""

    id: str = Field(description="Engine identifier: meshy, tripo, procedural")
    name: str = Field(description="Display name")
    description: str = Field(description="Engine description")
    available: bool = Field(description="Whether the engine is configured and available")
    features: list[str] = Field(default=[], description="Engine capabilities")


# =============================================================================
# Model Library Schemas
# =============================================================================


class ModelLibrarySaveRequest(BaseModel):
    """Save a building's 3D model to the reusable model library."""

    name: str = Field(max_length=255, description="Display name for the library entry")
    description: Optional[str] = Field(None, description="Optional description")
    category: str = Field(
        default="other", description="Category: commercial, residential, infrastructure, landscaping, other"
    )
    tags: list[str] = Field(default=[], description="Searchable tags")


class ModelLibraryApplyRequest(BaseModel):
    """Apply a library model to a target building."""

    building_id: str = Field(description="Target building ID to apply the model to")


class ModelLibraryResponse(BaseModel):
    """A saved model in the library."""

    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    owner_id: uuid.UUID
    source_building_id: Optional[uuid.UUID] = None
    source_project_id: Optional[uuid.UUID] = None
    name: str
    description: Optional[str] = None
    category: str
    tags: Optional[list[str]] = None
    model_url: str
    lod_urls: Optional[dict[str, str]] = None
    thumbnail_url: Optional[str] = None
    generation_prompt: Optional[str] = None
    generation_engine: Optional[str] = None
    architectural_style: Optional[str] = None
    is_public: bool = False
    use_count: int = 0
    created_at: datetime


# =============================================================================
# Admin Schemas
# =============================================================================


class AdminDashboardStats(BaseModel):
    """Platform-wide statistics for the admin dashboard."""

    total_users: int
    active_users: int
    total_projects: int
    total_buildings: int
    total_documents: int
    users_by_role: dict[str, int]
    projects_by_status: dict[str, int]


class AdminUserListResponse(BaseModel):
    """User info for admin user management."""

    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    email: str
    full_name: Optional[str]
    role: str
    is_active: bool
    created_at: datetime
    last_login_at: Optional[datetime] = None
    project_count: int
    render_credits: int = 1000


class AdminUserUpdate(BaseModel):
    """Update a user's role, active status, or name (admin only)."""

    role: Optional[str] = Field(None, pattern="^(viewer|editor|admin|cofounder)$")
    is_active: Optional[bool] = None
    full_name: Optional[str] = None


class ConfirmRoleChangeRequest(BaseModel):
    """Confirm a pending admin role change via email token."""

    token: str = Field(description="Confirmation token from the email link")


class PendingRoleChangeResponse(BaseModel):
    """Response when an admin demotion requires email confirmation."""

    detail: str = Field(description="Message about the confirmation email")
    requires_confirmation: bool = Field(default=True)


class AdminProjectListResponse(BaseModel):
    """Project info for admin project oversight."""

    id: uuid.UUID
    name: str
    description: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime
    owner_id: uuid.UUID
    owner_email: str
    owner_name: Optional[str]
    building_count: int


class AdminBuildingListResponse(BaseModel):
    """Building info for admin buildings overview."""

    id: uuid.UUID
    name: Optional[str]
    project_id: uuid.UUID
    project_name: str
    owner_email: str
    generation_status: Optional[str]
    generation_engine: Optional[str]
    architectural_style: Optional[str]
    model_url: Optional[str]
    preview_url: Optional[str]
    generation_prompt: Optional[str]
    created_at: datetime


# =============================================================================
# Cofounder Analytics Schemas
# =============================================================================


class TimeSeriesPoint(BaseModel):
    """A single data point in a time series."""

    period: datetime
    count: int


class TimeSeriesResponse(BaseModel):
    """Generic time series response with metadata."""

    data: list[TimeSeriesPoint]
    total_in_range: int
    range: str
    granularity: str


class CreationTrendsResponse(BaseModel):
    """Dual time series for project and building creation trends."""

    projects: list[TimeSeriesPoint]
    buildings: list[TimeSeriesPoint]
    range: str
    granularity: str


class GenerationStatsResponse(BaseModel):
    """3D generation statistics by engine with overall success rate."""

    by_engine: dict[str, dict[str, int]]
    total_generations: int
    success_rate: float
    range: str


class PlatformHealthResponse(BaseModel):
    """Platform health metrics: API, queue, and document pipeline."""

    api: dict[str, Any]
    queue: dict[str, Any]
    documents: dict[str, Any]


class TopUserEntry(BaseModel):
    """A single user entry in the top users ranking."""

    id: str
    email: str
    full_name: Optional[str]
    role: str
    project_count: int
    building_count: int
    document_count: int
    total_activity: int


class TopUsersResponse(BaseModel):
    """Top users ranked by total platform activity."""

    users: list[TopUserEntry]
    range: str


# =============================================================================
# API Usage & Balance Schemas
# =============================================================================


class ProviderBalance(BaseModel):
    """Balance information for a single API provider."""

    provider: str
    balance: Optional[float] = None
    frozen: Optional[float] = None
    unit: str = "credits"
    configured: bool = True
    error: Optional[str] = None


class AnthropicTokenUsage(BaseModel):
    """Aggregated Anthropic token usage from usage logs."""

    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_calls: int = 0
    configured: bool = True


class GeminiTokenUsage(BaseModel):
    """Aggregated Gemini token usage from usage logs."""

    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_calls: int = 0
    configured: bool = True


class ServiceStatus(BaseModel):
    """Status for a non-metered service (e.g. Mapbox, Google OAuth)."""

    provider: str
    configured: bool = False
    description: str = ""


class ApiBalanceResponse(BaseModel):
    """Combined balance response for all API providers."""

    meshy: ProviderBalance
    tripo: ProviderBalance
    stability: ProviderBalance
    anthropic: AnthropicTokenUsage
    gemini: GeminiTokenUsage
    services: list[ServiceStatus] = []


class OperationBreakdown(BaseModel):
    """Usage breakdown for a single operation within a provider."""

    operation: str
    total_credits: float
    call_count: int
    success_rate: float


class ApiUsageByProvider(BaseModel):
    """Aggregated API usage for a single provider."""

    provider: str
    total_credits: float
    total_calls: int
    success_rate: float
    by_operation: list[OperationBreakdown]


class DailyUsage(BaseModel):
    """Daily usage data point for charting."""

    date: str
    provider: str
    credits: float
    calls: int


class ApiUsageResponse(BaseModel):
    """Full API usage analytics response."""

    providers: list[ApiUsageByProvider]
    daily: list[DailyUsage]
    range: str
