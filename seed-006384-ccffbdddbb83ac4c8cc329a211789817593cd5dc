/**
 * enrichArchetypes.cjs
 *
 * Generates renderPrompt, facadeDetail, and roofDetail for all 45 archetypes
 * in buildingArchetypes.json based on their id, title, aestheticCategory,
 * and styleProfile.
 */

const fs = require('fs');
const path = require('path');

const INPUT = path.resolve(__dirname, '../src/data/buildingArchetypes.json');
const OUTPUT = INPUT; // overwrite in place

const data = JSON.parse(fs.readFileSync(INPUT, 'utf-8'));

// ─── ARCHETYPE METADATA DEFINITIONS ─────────────────────────────────────────
// Each key is the archetype ID. Values are { renderPrompt, facadeDetail, roofDetail }

const METADATA = {
  brownstone_rowhouse_frontage: {
    renderPrompt: {
      mapOverlay: "Replace the colored building block with a photorealistic brownstone rowhouse frontage. Keep the exact same building footprint and height. The building has warm brown sandstone facades with carved entry stoops, tall double-hung windows with stone lintels, decorative cornices, and wrought-iron railings. 3-4 storey townhouse rhythm with stoop entries and planted tree pits. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
      roofView: "Replace the colored block viewed from above with a flat or low-slope brownstone roof with brick chimneys, dark membrane roofing, and occasional roof gardens. Low stone parapet walls. Keep surrounding context exactly as-is.",
      negative: "cartoon, illustration, sketch, low quality, blurry, text, watermark, neon, unrealistic colors, modern glass"
    },
    facadeDetail: {
      primaryMaterial: "warm brown sandstone, smooth-cut ashlar, traditional mortar joints",
      secondaryMaterial: "carved brownstone door surrounds and window lintels",
      accentMaterial: "wrought-iron railings, cast-iron stoop balustrades",
      groundFloor: "elevated stoop entry with carved stone steps, arched doorway with fanlight transom, under-stoop garden level with iron gate",
      upperFloors: "tall double-hung windows with stone lintels and sills, 2-over-2 or 4-over-4 divided lites, shallow stone string courses between floors",
      cornice: "projecting carved stone cornice with brackets and dentil molding, 200mm projection",
      colorScheme: "warm brown sandstone body, dark brown or black ironwork, cream window sashes, dark green shutters"
    },
    roofDetail: {
      form: "flat with low stone parapet or shallow mansard with slate",
      material: "dark membrane roof or slate shingles on mansard",
      features: "brick chimneys, occasional rooftop skylight, planted containers",
      aerialAppearance: "dark flat surface with occasional brick chimneys and stone parapet walls, some rooftop planting"
    }
  },

  classic_brownstone_streetwall: {
    renderPrompt: {
      mapOverlay: "Replace the colored building block with a photorealistic classic brownstone streetwall. Keep the exact same building footprint and height. Continuous row of 3-4 storey brownstone townhouses with consistent cornice line, carved stone detailing, rhythmic stoop entries, and mature street trees. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
      roofView: "Replace the colored block viewed from above with continuous flat rooftops with brick parapets, chimneys, and occasional roof decks. Uniform brownstone streetwall rhythm from above. Keep surrounding context exactly as-is.",
      negative: "cartoon, illustration, sketch, low quality, blurry, text, watermark, neon, unrealistic colors"
    },
    facadeDetail: {
      primaryMaterial: "brown sandstone ashlar blocks, hand-dressed with subtle texture variation",
      secondaryMaterial: "carved brownstone ornamental details, egg-and-dart moldings",
      accentMaterial: "wrought-iron stoop railings, cast-iron window guards, brass door hardware",
      groundFloor: "high stoop with carved brownstone steps, double entry doors with arched transom, sub-grade English basement with iron grating",
      upperFloors: "regular rhythm of tall narrow windows with carved stone surrounds, stone belt courses, Italianate brackets at upper floors",
      cornice: "heavy projecting cornice with carved brackets, dentil course, and metal flashing",
      colorScheme: "rich brown sandstone varying from chocolate to amber, dark ironwork, cream or white window sashes"
    },
    roofDetail: {
      form: "flat with continuous brick/stone parapet",
      material: "dark membrane or built-up tar roof",
      features: "brick chimneys at party walls, occasional roof hatch, planted containers",
      aerialAppearance: "regular dark rectangles with shared party walls visible as narrow lines, brick chimneys at intervals"
    }
  },

  historical_brick_main_street: {
    renderPrompt: {
      mapOverlay: "Replace the colored building block with a photorealistic historical brick main street building. Keep the exact same building footprint and height. Red-orange brick facades with decorative corbelling, arched windows, cast-iron storefront columns, and painted signage. 3-5 storey mixed-use with ground-floor retail. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
      roofView: "Replace the colored block viewed from above with flat roofs with brick parapets, some with decorative false fronts. Dark membrane roofing with mechanical units. Keep surrounding context exactly as-is.",
      negative: "cartoon, illustration, sketch, low quality, blurry, text, watermark, neon, unrealistic colors"
    },
    facadeDetail: {
      primaryMaterial: "red-orange pressed brick, common bond pattern, cream mortar",
      secondaryMaterial: "cast-iron columns and storefront frames at ground floor",
      accentMaterial: "limestone or sandstone keystones, carved date stones, painted wood signage",
      groundFloor: "large display windows with cast-iron framing, recessed entries with tile vestibules, canvas awnings, painted signage boards",
      upperFloors: "arched or flat-head windows with brick voussoirs, stone sills, decorative brick corbelling at floor lines",
      cornice: "elaborate brick corbel cornice with stone cap, sometimes with pressed metal ornamental panels",
      colorScheme: "red-orange brick body, cream/limestone trim, dark green or black cast-iron, painted wood signage in traditional colors"
    },
    roofDetail: {
      form: "flat with decorative parapet, sometimes stepped false front",
      material: "built-up tar or membrane roof",
      features: "brick chimneys, decorative parapet with date stone or name plaque, fire escapes at rear",
      aerialAppearance: "dark flat roof with decorative front parapet rising above, some mechanical equipment, occasional skylight"
    }
  },

  victorian_heritage_avenue: {
    renderPrompt: {
      mapOverlay: "Replace the colored building block with a photorealistic Victorian heritage avenue building. Keep the exact same building footprint and height. Ornate Victorian facades with bay windows, decorative gables, turned wood or cast-iron porch elements, multi-colored paint scheme, and intricate millwork. 2-3 storey residential. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
      roofView: "Replace the colored block viewed from above with complex pitched roof forms with cross-gables, slate or shingle roofing, decorative ridge cresting, and brick chimneys. Keep surrounding context exactly as-is.",
      negative: "cartoon, illustration, sketch, low quality, blurry, text, watermark, neon, unrealistic colors, modern materials"
    },
    facadeDetail: {
      primaryMaterial: "painted wood clapboard siding or decorative shingles",
      secondaryMaterial: "ornamental millwork, turned wood porch columns and balustrades",
      accentMaterial: "cast-iron cresting, stained glass transoms, decorative brackets and vergeboard",
      groundFloor: "wraparound porch with turned columns, entry door with sidelights and transom, bay window",
      upperFloors: "projecting bay windows, decorative shingle patterns in gable ends, tall narrow double-hung windows with ornamental hoods",
      cornice: "deep eaves with decorative brackets, ornamental bargeboard on gable ends",
      colorScheme: "multi-toned painted scheme: body in muted tone, trim in cream, accent in deep burgundy or forest green"
    },
    roofDetail: {
      form: "steeply pitched cross-gable with turret or tower element",
      material: "slate shingles or wood shingles in decorative patterns",
      features: "ornamental ridge cresting, finials at gable peaks, brick chimneys with corbelled caps, dormer windows",
      aerialAppearance: "complex dark roof geometry with multiple gables, dormers, and possible turret, brick chimneys"
    }
  },

  contemporary_midrise_residential: {
    renderPrompt: {
      mapOverlay: "Replace the colored building block with a photorealistic contemporary mid-rise residential building. Keep the exact same building footprint and height. Clean modern facades with mix of white render, timber cladding, and large glazed balconies. 5-8 storey residential with ground-floor lobby and landscaping. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
      roofView: "Replace the colored block viewed from above with a flat green roof or rooftop amenity deck with planters, seating, and solar panels. Keep surrounding context exactly as-is.",
      negative: "cartoon, illustration, sketch, low quality, blurry, text, watermark, neon, unrealistic colors"
    },
    facadeDetail: {
      primaryMaterial: "smooth white or light grey render/stucco finish",
      secondaryMaterial: "natural timber cladding panels (cedar or larch), warm tone",
      accentMaterial: "dark metal balcony frames, powder-coated aluminium window frames",
      groundFloor: "glazed lobby entrance with cantilevered canopy, landscaped setback with low planting, bike storage",
      upperFloors: "regular rhythm of floor-to-ceiling glazed doors opening to private balconies, alternating render and timber-clad bays",
      cornice: "clean parapet edge with concealed metal coping, slight setback at top floor",
      colorScheme: "white/light grey render, warm timber accent panels, charcoal balcony frames, green planting accents"
    },
    roofDetail: {
      form: "flat with parapet, possible penthouse setback",
      material: "extensive green roof with sedum, or light-colored membrane with solar panels",
      features: "rooftop amenity terrace, planters, solar panel arrays, mechanical penthouse screened by louvres",
      aerialAppearance: "green vegetated surface or grey membrane with solar panels, penthouse volume, rooftop garden areas"
    }
  },

  contemporary_townhouse_courtyard: {
    renderPrompt: {
      mapOverlay: "Replace the colored building block with photorealistic contemporary townhouses arranged around a courtyard. Keep the exact same building footprint. Modern 3-storey townhouses with flat roofs, large windows, timber and render facades, private entries, and central landscaped courtyard. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
      roofView: "Replace the colored block viewed from above with flat roof townhouses around a green landscaped courtyard with paths and mature trees. Keep surrounding context exactly as-is.",
      negative: "cartoon, illustration, sketch, low quality, blurry, text, watermark, neon, unrealistic colors"
    },
    facadeDetail: {
      primaryMaterial: "smooth light render with crisp edges",
      secondaryMaterial: "vertical timber cladding in natural or stained finish",
      accentMaterial: "dark powder-coated aluminium frames, corten steel planters",
      groundFloor: "individual entry doors with recessed porch, full-height glazing to living spaces, integrated garage doors",
      upperFloors: "large picture windows and glazed corner elements, Juliet balconies, timber-clad accent bays",
      cornice: "clean flat parapet with minimal metal coping",
      colorScheme: "white render, warm timber cladding, charcoal window frames, green courtyard planting"
    },
    roofDetail: {
      form: "flat with concealed parapet",
      material: "light membrane roof with green roof patches",
      features: "roof terraces on select units, photovoltaic panels, skylights",
      aerialAppearance: "regular flat-roofed townhouse units around central green courtyard, paths crossing through planting"
    }
  },

  detached_contemporary_infill: {
    renderPrompt: {
      mapOverlay: "Replace the colored building block with a photorealistic detached contemporary infill house. Keep the exact same building footprint. Modern 2-3 storey single-family home with asymmetric massing, large glazed openings, mix of render and wood cladding, and landscaped yard. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
      roofView: "Replace the colored block viewed from above with a flat or low-slope contemporary roof with green roof sections, skylights, and rooftop terrace. Keep surrounding context exactly as-is.",
      negative: "cartoon, illustration, sketch, low quality, blurry, text, watermark, neon, unrealistic colors"
    },
    facadeDetail: {
      primaryMaterial: "smooth white render or fibre cement panels",
      secondaryMaterial: "charcoal-stained timber cladding, vertical board",
      accentMaterial: "black powder-coated steel framing, corten steel accents",
      groundFloor: "large sliding glass doors to garden, flush threshold entry, integrated carport or garage",
      upperFloors: "asymmetric window placement, cantilevered volume over ground floor, private balcony",
      cornice: "clean parapet edge, no traditional cornice",
      colorScheme: "white and charcoal with natural timber accent, black framing, green landscaping"
    },
    roofDetail: {
      form: "flat or butterfly roof with clean lines",
      material: "membrane roof with green roof sections, photovoltaic panels",
      features: "skylights, rooftop terrace, concealed drainage",
      aerialAppearance: "modern flat-roofed footprint with mix of green roof, terrace deck, and solar panels"
    }
  },

  courtyard_family_housing: {
    renderPrompt: {
      mapOverlay: "Replace the colored building block with photorealistic courtyard family housing. Keep the exact same building footprint. 3-4 storey residential buildings arranged around shared landscaped courtyards with brick and render facades, generous balconies, and pedestrian paths. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
      roofView: "Replace the colored block viewed from above with flat roofs surrounding green communal courtyards with play areas, paths, and mature trees. Keep surrounding context exactly as-is.",
      negative: "cartoon, illustration, sketch, low quality, blurry, text, watermark, neon, unrealistic colors"
    },
    facadeDetail: {
      primaryMaterial: "light-toned brick in running bond, warm buff or cream",
      secondaryMaterial: "smooth render panels in contrasting white",
      accentMaterial: "powder-coated metal balcony railings, timber privacy screens",
      groundFloor: "individual entries facing courtyard, generous glazing, planted threshold zones with low hedges",
      upperFloors: "deep balconies with solid balustrade and planter boxes, regular window rhythm, recessed loggias",
      cornice: "flat parapet with subtle brick soldier course",
      colorScheme: "warm buff brick, white render panels, grey-green balcony frames, abundant courtyard planting"
    },
    roofDetail: {
      form: "flat with low parapet",
      material: "green roof or membrane with solar panels",
      features: "communal roof terrace on select blocks, photovoltaics, skylights to corridors",
      aerialAppearance: "flat-roofed residential blocks around green courtyards with trees, paths, and play areas"
    }
  },

  modern_glass_office_institutional: {
    renderPrompt: {
      mapOverlay: "Replace the colored building block with a photorealistic modern glass office/institutional building. Keep the exact same building footprint and height. Curtain wall glass facades with expressed structural grid, stone or metal base, dramatic entrance canopy, and landscaped plaza. 6-12 storey. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
      roofView: "Replace the colored block viewed from above with a flat roof with mechanical penthouse, cooling towers, and possible green roof sections. Keep surrounding context exactly as-is.",
      negative: "cartoon, illustration, sketch, low quality, blurry, text, watermark, neon, unrealistic colors"
    },
    facadeDetail: {
      primaryMaterial: "unitized curtain wall glazing with low-E coated glass, clear or tinted grey-blue",
      secondaryMaterial: "brushed stainless steel or anodized aluminium mullions and transoms",
      accentMaterial: "polished granite or limestone base cladding, stainless steel entrance canopy",
      groundFloor: "double-height glazed lobby with revolving doors, stone-clad base, landscaped entry plaza",
      upperFloors: "continuous curtain wall with expressed floor slabs as horizontal shadow lines, operable ventilation panels",
      cornice: "minimal parapet with aluminium coping, mechanical penthouse set back from edge",
      colorScheme: "silver-grey aluminium frame, blue-grey glass, dark granite base, polished metal accents"
    },
    roofDetail: {
      form: "flat with mechanical penthouse",
      material: "light-coloured membrane roof, possible green roof at setback levels",
      features: "mechanical penthouse with cooling towers and louvred screens, satellite dishes, lightning protection",
      aerialAppearance: "light grey flat roof with central mechanical penthouse, equipment arrays, and possible green roof patches"
    }
  },

  modernist_civic_block: {
    renderPrompt: {
      mapOverlay: "Replace the colored building block with a photorealistic modernist civic block. Keep the exact same building footprint and height. Bold geometric concrete forms with expressed structural grid, deep window reveals, and civic plaza. Brutalist or late-modern expression with board-formed concrete and strategic glazing. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
      roofView: "Replace the colored block viewed from above with a flat concrete roof with mechanical penthouse, sculptural rooftop elements, and possible public terrace. Keep surrounding context exactly as-is.",
      negative: "cartoon, illustration, sketch, low quality, blurry, text, watermark, neon, unrealistic colors"
    },
    facadeDetail: {
      primaryMaterial: "board-formed exposed concrete, bush-hammered or smooth finish",
      secondaryMaterial: "dark anodized aluminium window frames and curtain wall sections",
      accentMaterial: "corten steel accent panels, polished concrete at entry",
      groundFloor: "deep colonnade or pilotis supporting upper mass, public lobby with civic presence, generous entry plaza",
      upperFloors: "deep concrete reveals creating strong shadow patterns, horizontal ribbon windows, expressed structural columns",
      cornice: "expressed concrete roof slab edge, possibly cantilevered",
      colorScheme: "raw concrete grey, dark aluminium frames, occasional warm wood or corten accent"
    },
    roofDetail: {
      form: "flat with expressed concrete edges, possible mechanical tower",
      material: "concrete deck with membrane waterproofing",
      features: "sculptural mechanical penthouse, possible rooftop sculpture or antenna, public observation terrace",
      aerialAppearance: "bold concrete geometry with flat roof, expressed grid pattern, mechanical penthouse"
    }
  },

  mid_century_modern_pavilion_block: {
    renderPrompt: {
      mapOverlay: "Replace the colored building block with a photorealistic mid-century modern pavilion block. Keep the exact same building footprint and height. Elegant horizontal massing with expressed steel frame, curtain wall glazing, floating roof plane, and landscaped setting. 3-5 storey with pilotis or cantilevered elements. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
      roofView: "Replace the colored block viewed from above with a flat roof with clean edges, minimal mechanical equipment, and possible courtyard or atrium below. Keep surrounding context exactly as-is.",
      negative: "cartoon, illustration, sketch, low quality, blurry, text, watermark, neon, unrealistic colors"
    },
    facadeDetail: {
      primaryMaterial: "painted steel structural frame, white or black",
      secondaryMaterial: "floor-to-ceiling glass curtain wall with thin mullions",
      accentMaterial: "travertine or marble base panels, polished brass entry hardware",
      groundFloor: "pilotis or transparent ground floor with lobby, reflecting pool or landscaped forecourt",
      upperFloors: "continuous glass curtain wall with expressed steel columns, sun shading fins or overhangs",
      cornice: "floating roof plane extending beyond glass line, thin edge profile",
      colorScheme: "white or black steel frame, clear glass, warm stone base, green landscape setting"
    },
    roofDetail: {
      form: "flat with dramatic overhanging edges",
      material: "white membrane or gravel roof",
      features: "minimal mechanical equipment hidden by parapet, possible central atrium opening",
      aerialAppearance: "clean flat white or gravel roof with crisp rectangular edges, possible central courtyard or atrium"
    }
  },

  civic_classical_building: {
    renderPrompt: {
      mapOverlay: "Replace the colored building block with a photorealistic civic classical building. Keep the exact same building footprint and height. Limestone or marble facade with classical columns, pediment, symmetrical composition, and formal entry staircase. Institutional presence with civic gravitas. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
      roofView: "Replace the colored block viewed from above with a flat or hipped roof behind a classical balustrade parapet, with copper or lead roofing and mechanical equipment hidden from view. Keep surrounding context exactly as-is.",
      negative: "cartoon, illustration, sketch, low quality, blurry, text, watermark, neon, unrealistic colors"
    },
    facadeDetail: {
      primaryMaterial: "smooth-cut limestone or marble ashlar, fine-dressed",
      secondaryMaterial: "fluted columns with Corinthian or Ionic capitals, carved entablature",
      accentMaterial: "bronze entry doors and window frames, carved stone cartouches and keystones",
      groundFloor: "formal entry with grand staircase, columned portico, bronze doors with fanlight transom",
      upperFloors: "regular fenestration with classical proportions, stone architraves, carved swags between windows",
      cornice: "full classical entablature with architrave, frieze, and cornice, possibly with balustrade above",
      colorScheme: "warm cream or white limestone, bronze door and window details, grey lead or copper roof elements"
    },
    roofDetail: {
      form: "flat or shallow hipped behind stone balustrade parapet",
      material: "copper or lead sheet roofing, concealed behind parapet",
      features: "stone balustrade, central dome or cupola on some examples, hidden mechanical",
      aerialAppearance: "copper-green or dark lead roof behind stone balustrade, possible central dome or skylight"
    }
  },

  monumental_courthouse_axis: {
    renderPrompt: {
      mapOverlay: "Replace the colored building block with a photorealistic monumental courthouse. Keep the exact same building footprint and height. Grand Beaux-Arts or Neoclassical courthouse with colossal columned portico, domed rotunda, symmetrical wings, and formal approach steps. Stone facades with carved allegorical sculpture. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
      roofView: "Replace the colored block viewed from above with a large central dome or rotunda with copper/lead cladding, flanked by flat-roofed wings with stone parapets. Keep surrounding context exactly as-is.",
      negative: "cartoon, illustration, sketch, low quality, blurry, text, watermark, neon, unrealistic colors"
    },
    facadeDetail: {
      primaryMaterial: "grey granite base, white marble or limestone upper facades",
      secondaryMaterial: "colossal Corinthian columns, carved marble entablature and pediment with allegorical sculpture",
      accentMaterial: "bronze entry doors, carved stone balustrades, gilded details",
      groundFloor: "monumental entry stairs spanning full width, rusticated stone base, heavy bronze doors",
      upperFloors: "tall arched windows with carved stone surrounds, pilastered bays, carved frieze panels",
      cornice: "massive entablature with full cornice, carved modillions, and stone balustrade with acroteria",
      colorScheme: "white marble or cream limestone, dark granite base, bronze and gilt accents, copper dome patina"
    },
    roofDetail: {
      form: "central dome or rotunda with flanking flat wings",
      material: "copper or lead dome cladding, membrane on flat sections",
      features: "lantern atop dome, sculptural acroteria at corners, concealed mechanical",
      aerialAppearance: "prominent copper-green dome as central element, flanking flat roof wings with stone parapets"
    }
  },

  adaptive_reuse_warehouse_lofts: {
    renderPrompt: {
      mapOverlay: "Replace the colored building block with a photorealistic adaptive reuse warehouse loft building. Keep the exact same building footprint and height. Converted industrial warehouse with exposed brick, oversized steel-framed windows, modern penthouse additions in glass and steel, and ground-floor creative retail. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
      roofView: "Replace the colored block viewed from above with a flat warehouse roof with modern penthouse addition, rooftop deck with planters, and industrial skylights. Keep surrounding context exactly as-is.",
      negative: "cartoon, illustration, sketch, low quality, blurry, text, watermark, neon, unrealistic colors"
    },
    facadeDetail: {
      primaryMaterial: "original exposed brick, cleaned and repointed, varying red-brown tones",
      secondaryMaterial: "new steel-and-glass penthouse addition with dark frames",
      accentMaterial: "preserved cast-iron loading bay details, new corten steel balconies",
      groundFloor: "original loading bay openings converted to large storefront windows, creative retail/cafe spaces",
      upperFloors: "oversized original warehouse windows with new steel frames, fire escape retained as balcony access, exposed structural timber or steel",
      cornice: "original brick parapet with painted ghost signage, modern glass penthouse set back above",
      colorScheme: "warm aged brick, black steel new insertions, timber and corten accents, industrial character"
    },
    roofDetail: {
      form: "flat original roof with modern penthouse setback addition",
      material: "membrane roof with timber deck terraces",
      features: "original skylights restored, rooftop terrace with planters and string lights, modern penthouse volume",
      aerialAppearance: "dark flat roof with modern glass penthouse addition, timber deck areas, industrial skylight monitors"
    }
  },

  scandinavian_urban_residential: {
    renderPrompt: {
      mapOverlay: "Replace the colored building block with a photorealistic Scandinavian urban residential building. Keep the exact same building footprint and height. Clean-lined Nordic mid-rise with warm-toned brick or painted render, generous balconies, and human-scaled detailing. 4-6 storey with landscaped courtyard. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
      roofView: "Replace the colored block viewed from above with a flat or gently pitched green roof with communal terrace, solar panels, and birch tree courtyard. Keep surrounding context exactly as-is.",
      negative: "cartoon, illustration, sketch, low quality, blurry, text, watermark, neon, unrealistic colors"
    },
    facadeDetail: {
      primaryMaterial: "warm buff or yellow brick, smooth-pressed, running bond",
      secondaryMaterial: "light render panels or painted concrete elements",
      accentMaterial: "natural oak or pine timber balcony screens, anodized aluminium frames",
      groundFloor: "generous glazed lobby with timber door, bike storage, individual entries to ground-floor units, low planting beds",
      upperFloors: "deep balconies with timber and metal railings, floor-to-ceiling windows, subtle brick pattern variations between floors",
      cornice: "clean brick parapet with metal coping, subtle step-back at top floor",
      colorScheme: "warm buff brick, white/cream render, natural timber balconies, muted green planting"
    },
    roofDetail: {
      form: "flat or very low pitch with clean parapet",
      material: "sedum green roof or light membrane with solar panels",
      features: "communal roof terrace, photovoltaic arrays, rainwater collection",
      aerialAppearance: "green vegetated roof or light surface with solar panels, possible communal terrace with timber decking"
    }
  },

  nordic_timber_midrise: {
    renderPrompt: {
      mapOverlay: "Replace the colored building block with a photorealistic Nordic timber mid-rise building. Keep the exact same building footprint and height. Cross-laminated timber (CLT) structure with exposed wood facades, deep balconies, and warm natural material expression. 4-7 storey sustainable residential. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
      roofView: "Replace the colored block viewed from above with a green roof with solar panels, timber-clad mechanical screening, and communal roof garden. Keep surrounding context exactly as-is.",
      negative: "cartoon, illustration, sketch, low quality, blurry, text, watermark, neon, unrealistic colors"
    },
    facadeDetail: {
      primaryMaterial: "charred timber (shou sugi ban) or natural larch cladding, vertical board-on-board",
      secondaryMaterial: "exposed CLT structural elements at balconies and reveals",
      accentMaterial: "dark metal flashings, natural stone base plinth",
      groundFloor: "timber-framed lobby entrance, ground-floor units with private garden patios, natural stone base",
      upperFloors: "deep timber balconies with solid wood balustrades, tall windows with wood frames, varied timber cladding patterns",
      cornice: "timber parapet with metal coping, expressed timber beam ends",
      colorScheme: "natural silver-grey or warm amber timber tones, dark metal accents, green landscape elements"
    },
    roofDetail: {
      form: "flat or shallow mono-pitch with clean timber edge",
      material: "extensive green roof with wildflower meadow or sedum, integrated photovoltaics",
      features: "communal roof garden, timber-clad mechanical housing, rainwater harvesting",
      aerialAppearance: "lush green roof surface with solar panels, timber-screened mechanical area, possible communal garden"
    }
  },

  mediterranean_villa_estate: {
    renderPrompt: {
      mapOverlay: "Replace the colored building block with a photorealistic Mediterranean villa estate. Keep the exact same building footprint. Terracotta-roofed villa with cream stucco walls, arched openings, courtyard with fountain, mature cypress and olive trees. 2-3 storey low-density residential. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
      roofView: "Replace the colored block viewed from above with warm terracotta clay tile roofs in varied hip and gable forms, with interior courtyard, swimming pool, and Mediterranean garden. Keep surrounding context exactly as-is.",
      negative: "cartoon, illustration, sketch, low quality, blurry, text, watermark, neon, unrealistic colors"
    },
    facadeDetail: {
      primaryMaterial: "smooth cream or warm white lime stucco over masonry",
      secondaryMaterial: "natural stone quoins, window and door surrounds in travertine or limestone",
      accentMaterial: "wrought-iron balcony railings and window grilles, terracotta pot details, wood shutters",
      groundFloor: "arched entry portal with heavy timber doors, loggia or covered arcade, courtyard access",
      upperFloors: "Juliet balconies with wrought-iron railings, wood shuttered windows, arched window heads",
      cornice: "deep terracotta roof overhang with exposed rafter tails or decorative brackets",
      colorScheme: "warm cream stucco, terracotta roof, dark green shutters, wrought-iron black, stone trim"
    },
    roofDetail: {
      form: "hip and cross-gable with varied ridge heights",
      material: "barrel terracotta clay tiles, aged to warm orange-brown",
      features: "chimney pots, terracotta ridge tiles, cupola or tower element on larger villas",
      aerialAppearance: "warm terracotta tile roofs in varied forms around central courtyard, blue pool, cypress trees"
    }
  },

  mediterranean_arcade_mixed_use: {
    renderPrompt: {
      mapOverlay: "Replace the colored building block with a photorealistic Mediterranean arcade mixed-use building. Keep the exact same building footprint and height. Stucco-and-stone facades with ground-floor arcaded walkway, wrought-iron balconies, terracotta tile roof, and retail shopfronts under arches. 3-5 storey. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
      roofView: "Replace the colored block viewed from above with terracotta clay tile roofs at varied levels, rooftop terraces with pergolas, and planted courtyards. Keep surrounding context exactly as-is.",
      negative: "cartoon, illustration, sketch, low quality, blurry, text, watermark, neon, unrealistic colors"
    },
    facadeDetail: {
      primaryMaterial: "warm-toned stucco over masonry, ochre or terracotta wash",
      secondaryMaterial: "stone arcade columns and archivolts at ground floor",
      accentMaterial: "wrought-iron balcony railings, painted wood shutters, ceramic tile accents",
      groundFloor: "continuous arcade with stone columns, retail shopfronts within arched bays, shaded walkway",
      upperFloors: "wrought-iron Juliet balconies, louvred wood shutters, stucco with subtle quoin details",
      cornice: "deep roof overhang with decorative bracket or exposed timber rafters",
      colorScheme: "warm ochre or terracotta stucco, cream stone arches, dark green shutters, terracotta roof"
    },
    roofDetail: {
      form: "hipped or flat with terracotta parapet",
      material: "barrel terracotta tiles on pitched sections, membrane with terracotta pavers on terraces",
      features: "rooftop terraces with timber pergolas, planted containers, occasional tower or belvedere",
      aerialAppearance: "warm terracotta roof tiles, rooftop terraces with pergola shadows, interior courtyard planting"
    }
  },

  parametric_future_hub: {
    renderPrompt: {
      mapOverlay: "Replace the colored building block with a photorealistic parametric future hub building. Keep the exact same building footprint and height. Flowing parametric forms with ETFE or glass envelope, diagrid structure, dynamic curves, and integrated green terraces. 8-15 storey innovation district landmark. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
      roofView: "Replace the colored block viewed from above with a flowing organic roof form with ETFE cushions, integrated photovoltaics, and green terraces cascading down. Keep surrounding context exactly as-is.",
      negative: "cartoon, illustration, sketch, low quality, blurry, text, watermark, neon, unrealistic colors"
    },
    facadeDetail: {
      primaryMaterial: "unitized double-skin glass facade with parametric mullion geometry",
      secondaryMaterial: "white-painted steel diagrid or tubular structure",
      accentMaterial: "ETFE cushion panels with variable opacity, LED-integrated facade panels",
      groundFloor: "dramatic flowing canopy over public plaza, fully transparent ground floor, landscaped bio-swales",
      upperFloors: "parametric facade panels that twist and rotate, integrated planters at terrace levels, operable ventilation",
      cornice: "sculptural roof edge dissolving into sky, no traditional cornice",
      colorScheme: "white structural frame, clear and fritted glass, touches of green from integrated planting, subtle LED accents"
    },
    roofDetail: {
      form: "organic flowing form, possibly double-curved",
      material: "ETFE cushion roof with integrated thin-film photovoltaics",
      features: "green roof terraces at multiple levels, rainwater collection, dynamic shading system",
      aerialAppearance: "dramatic organic roof geometry with ETFE panels, green terraces, solar integration"
    }
  },

  autonomous_tech_campus: {
    renderPrompt: {
      mapOverlay: "Replace the colored building block with a photorealistic autonomous tech campus building. Keep the exact same building footprint and height. Sleek low-rise campus buildings with glass and white metal panel facades, covered walkways, autonomous vehicle drop-off zones, and extensive landscaping. 2-5 storey. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
      roofView: "Replace the colored block viewed from above with large photovoltaic canopy roofs, green courtyards, connected building clusters, and autonomous vehicle lanes. Keep surrounding context exactly as-is.",
      negative: "cartoon, illustration, sketch, low quality, blurry, text, watermark, neon, unrealistic colors"
    },
    facadeDetail: {
      primaryMaterial: "smooth white composite metal panels or fibre-reinforced polymer",
      secondaryMaterial: "floor-to-ceiling high-performance glazing with electrochromic tinting",
      accentMaterial: "anodized aluminium fins, integrated LED wayfinding strips",
      groundFloor: "transparent ground floor with lobby, autonomous vehicle arrival zone, covered colonnade connecting buildings",
      upperFloors: "continuous glass and white panel envelope, automated exterior shading fins, operable panels",
      cornice: "floating photovoltaic canopy extending beyond building edge",
      colorScheme: "white panels, clear glass, silver aluminium structure, green landscape dominates"
    },
    roofDetail: {
      form: "flat with extended photovoltaic canopy structure",
      material: "building-integrated photovoltaic canopy, green roof on building sections",
      features: "massive solar arrays, drone landing pads, rainwater collection, mechanical equipment hidden below canopy",
      aerialAppearance: "large solar canopy structures connecting building clusters, green courtyards, autonomous vehicle paths"
    }
  },

  art_deco_setback_tower: {
    renderPrompt: {
      mapOverlay: "Replace the colored building block with a photorealistic Art Deco setback tower. Keep the exact same building footprint and height. Stepped limestone tower with geometric ornamentation, vertical emphasis, decorative spandrel panels, and illuminated crown. 10-20 storey mixed-use. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
      roofView: "Replace the colored block viewed from above with a stepped tower crown with Art Deco geometric ornament, copper or metal decorative cap, and setback terraces. Keep surrounding context exactly as-is.",
      negative: "cartoon, illustration, sketch, low quality, blurry, text, watermark, neon, unrealistic colors"
    },
    facadeDetail: {
      primaryMaterial: "smooth cream or buff limestone cladding, precision-cut ashlar",
      secondaryMaterial: "polished black granite base, cast aluminium or bronze spandrel panels",
      accentMaterial: "gilded geometric ornament, stainless steel window surrounds, decorative metalwork",
      groundFloor: "dramatic double-height entry lobby with polished stone, brass revolving doors, chevron floor pattern",
      upperFloors: "vertical window bands between limestone piers, geometric spandrel panels, progressive setbacks creating terraces",
      cornice: "stepped tower crown with geometric ornament, possible illuminated cap or finial",
      colorScheme: "cream limestone, polished black granite base, gold/brass ornamental accents, dark bronze windows"
    },
    roofDetail: {
      form: "stepped tower crown with decorative cap",
      material: "copper or stainless steel decorative crown, membrane on setback terraces",
      features: "Art Deco geometric finial or antenna mount, illuminated at night, setback terraces with balustrades",
      aerialAppearance: "distinctive stepped tower crown tapering upward, geometric metal cap, setback terraces at multiple levels"
    }
  },

  deco_theater_mainstreet: {
    renderPrompt: {
      mapOverlay: "Replace the colored building block with a photorealistic Art Deco theater on a main street. Keep the exact same building footprint and height. Ornate Deco facade with vertical sign tower, geometric terra cotta ornament, marquee canopy, and polychrome detailing. 2-4 storey entertainment venue. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
      roofView: "Replace the colored block viewed from above with a flat roof with Art Deco vertical sign tower, decorative parapet, and large auditorium volume behind the facade. Keep surrounding context exactly as-is.",
      negative: "cartoon, illustration, sketch, low quality, blurry, text, watermark, neon, unrealistic colors"
    },
    facadeDetail: {
      primaryMaterial: "polychrome glazed terra cotta panels in geometric patterns",
      secondaryMaterial: "cream stucco or cast stone on side walls",
      accentMaterial: "neon signage, gilded sunburst motifs, stainless steel trim",
      groundFloor: "projecting marquee canopy with integrated lighting, ticket booth flanked by poster cases, terrazzo entry floor",
      upperFloors: "tall vertical sign tower with theater name, geometric terra cotta panels, decorative pilasters with chevron motifs",
      cornice: "stepped parapet with geometric finials and sunburst medallions",
      colorScheme: "cream and turquoise terra cotta, gold gilt accents, neon signage colors, polished stainless steel"
    },
    roofDetail: {
      form: "flat with tall decorative front parapet and sign tower",
      material: "membrane roof over auditorium volume, decorative terra cotta on parapet",
      features: "vertical neon sign tower, decorative parapet with geometric finials, fly tower if theater has stage",
      aerialAppearance: "large auditorium roof volume behind decorative front facade, prominent sign tower, flat membrane roof"
    }
  },

  traditional_vernacular_market_street: {
    renderPrompt: {
      mapOverlay: "Replace the colored building block with a photorealistic traditional vernacular market street building. Keep the exact same building footprint and height. Locally-rooted mixed-use with timber frame, brick or stone ground floor, varied gable rooflines, and market stall frontage. 2-4 storey. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
      roofView: "Replace the colored block viewed from above with steeply pitched roofs with clay or slate tiles, varied ridge heights along the street, and brick chimneys. Keep surrounding context exactly as-is.",
      negative: "cartoon, illustration, sketch, low quality, blurry, text, watermark, neon, unrealistic colors"
    },
    facadeDetail: {
      primaryMaterial: "local stone or brick at ground floor, timber-frame with render or clapboard above",
      secondaryMaterial: "heavy timber structural beams and posts, exposed at corners",
      accentMaterial: "wrought-iron shop signs, carved timber brackets, painted wood trim",
      groundFloor: "market stalls or shop fronts with large timber-framed display windows, deep thresholds, canvas awnings",
      upperFloors: "small-paned casement windows in timber frames, jettied upper floors on some buildings, render with decorative pargeting",
      cornice: "deep roof overhang with exposed rafter tails or decorative bargeboard",
      colorScheme: "natural stone grey or warm brick, cream render, dark timber framing, painted shop signage"
    },
    roofDetail: {
      form: "steeply pitched gable with varied ridge heights along street",
      material: "clay pantiles or natural slate, aged and weathered",
      features: "brick or stone chimneys, dormer windows, gable-end detail",
      aerialAppearance: "varied pitched rooflines creating irregular skyline, clay or slate tiles, brick chimneys"
    }
  },

  vernacular_courtyard_housing: {
    renderPrompt: {
      mapOverlay: "Replace the colored building block with photorealistic vernacular courtyard housing. Keep the exact same building footprint. Traditional courtyard houses with thick masonry walls, internal gardens, timber pergolas, and simple rendered facades with small windows. 1-3 storey. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
      roofView: "Replace the colored block viewed from above with clay tile roofs surrounding private courtyards with trees, gardens, and covered outdoor living spaces. Keep surrounding context exactly as-is.",
      negative: "cartoon, illustration, sketch, low quality, blurry, text, watermark, neon, unrealistic colors"
    },
    facadeDetail: {
      primaryMaterial: "thick lime-rendered masonry walls, whitewashed or earth-toned",
      secondaryMaterial: "natural stone thresholds, lintels, and base courses",
      accentMaterial: "timber shutters, wrought-iron window grilles, terracotta pots",
      groundFloor: "heavy timber or studded door in arched opening, minimal street-facing windows, inward-looking plan",
      upperFloors: "small shuttered windows, thick wall reveals creating deep shadows, occasional balcony or loggia facing courtyard",
      cornice: "simple parapet or deep roof overhang with exposed timber beams",
      colorScheme: "white or earth-toned lime wash, natural timber, terracotta tiles, green courtyard planting"
    },
    roofDetail: {
      form: "low-pitch hip or flat with parapet, surrounding courtyard",
      material: "clay barrel tiles or flat clay tiles, naturally weathered",
      features: "internal courtyard open to sky, timber pergola over outdoor living area, rainwater cistern",
      aerialAppearance: "terracotta roofs surrounding green courtyard gardens, pergola structures, possible water feature"
    }
  },

  minimalist_courtyard_block: {
    renderPrompt: {
      mapOverlay: "Replace the colored building block with a photorealistic minimalist courtyard block. Keep the exact same building footprint. Ultra-clean residential block with precise white facades, floor-to-ceiling glazing, and serene central courtyard with water feature. 4-6 storey. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
      roofView: "Replace the colored block viewed from above with a flat white roof surrounding a minimalist courtyard with reflecting pool, gravel, and specimen trees. Keep surrounding context exactly as-is.",
      negative: "cartoon, illustration, sketch, low quality, blurry, text, watermark, neon, unrealistic colors"
    },
    facadeDetail: {
      primaryMaterial: "smooth white render or white concrete panels, flawless finish",
      secondaryMaterial: "floor-to-ceiling frameless or minimal-frame glazing",
      accentMaterial: "concealed dark aluminium frames, natural stone threshold at entry",
      groundFloor: "flush frameless glass entry, minimal signage, gravel and stone landscape, seamless indoor-outdoor threshold",
      upperFloors: "continuous glass and white panel rhythm, no visible joints or fixings, deep recessed balconies",
      cornice: "razor-thin parapet edge, no visible coping or flashing",
      colorScheme: "pure white facades, clear glass, grey stone base, minimal palette with green planting as only color"
    },
    roofDetail: {
      form: "perfectly flat with concealed parapet",
      material: "white membrane or gravel roof, photovoltaics hidden from view",
      features: "minimalist rooftop with concealed equipment, possible reflective water plane",
      aerialAppearance: "white flat roof surrounding dark reflecting pool or gravel courtyard, specimen trees, extreme precision"
    }
  },

  minimalist_infill_townhouse: {
    renderPrompt: {
      mapOverlay: "Replace the colored building block with a photorealistic minimalist infill townhouse. Keep the exact same building footprint. Precisely detailed narrow townhouse with clean facades, one statement material, large glazed opening, and roof terrace. 3-4 storey. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
      roofView: "Replace the colored block viewed from above with a flat roof with private terrace, frameless glass railing, and minimal planting. Keep surrounding context exactly as-is.",
      negative: "cartoon, illustration, sketch, low quality, blurry, text, watermark, neon, unrealistic colors"
    },
    facadeDetail: {
      primaryMaterial: "dark brick in stack bond or smooth render in single tone",
      secondaryMaterial: "large frameless or minimal-frame fixed glazing panel",
      accentMaterial: "concealed aluminium frames, flush pivot door, hidden gutters",
      groundFloor: "flush pivot entry door (same material as facade), full-height glazed panel revealing interior stair",
      upperFloors: "one or two precisely placed openings, material continuity wall-to-sky, deep window reveals",
      cornice: "knife-edge parapet, invisible from street level",
      colorScheme: "monochromatic — either all dark brick, all white render, or all grey concrete"
    },
    roofDetail: {
      form: "flat with invisible parapet",
      material: "membrane roof with timber deck or gravel",
      features: "private roof terrace with frameless glass balustrade, minimal planting, concealed drainage",
      aerialAppearance: "small flat roof with timber deck terrace, frameless glass edge, minimal and precise"
    }
  },

  parisian_midrise_block: {
    renderPrompt: {
      mapOverlay: "Replace the colored building block with a photorealistic Parisian mid-rise block. Keep the exact same building footprint and height. Haussmann-style limestone facade with wrought-iron balconies at second and fifth floors, zinc mansard roof with dormers, and ground-floor brasserie. 6-7 storey. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
      roofView: "Replace the colored block viewed from above with a zinc mansard roof with dormer windows, terracotta chimney pots, and zinc ridge caps. Keep surrounding context exactly as-is.",
      negative: "cartoon, illustration, sketch, low quality, blurry, text, watermark, neon, unrealistic colors"
    },
    facadeDetail: {
      primaryMaterial: "cream Lutetian limestone, smooth-dressed ashlar blocks",
      secondaryMaterial: "carved stone balcony supports, window surrounds, and cartouches",
      accentMaterial: "wrought-iron balcony railings with scrollwork, zinc mansard cladding, brass door hardware",
      groundFloor: "tall ground floor with large windows, brasserie or shop with canvas awning, stone-framed entry with double doors",
      upperFloors: "continuous wrought-iron balcony at 2nd floor (piano nobile), individual balconies at 5th floor, tall narrow windows with stone surrounds",
      cornice: "heavy stone cornice at 5th floor with modillions, mansard begins above",
      colorScheme: "warm cream limestone, dark grey zinc mansard, black wrought-iron, cream window frames"
    },
    roofDetail: {
      form: "zinc mansard with dormers, steeply pitched lower face",
      material: "standing-seam zinc panels, aged to dark grey patina",
      features: "mansard dormer windows with zinc cheeks, terracotta chimney pots in rows, zinc ridge caps",
      aerialAppearance: "dark grey zinc mansard roof with rows of dormers, chimney pots, occasional rooftop terrace"
    }
  },

  parisian_boulevard_corner: {
    renderPrompt: {
      mapOverlay: "Replace the colored building block with a photorealistic Parisian boulevard corner building. Keep the exact same building footprint and height. Grand Haussmann corner building with curved facade, wrought-iron balconies, decorative stone carving, zinc dome at corner, and ground-floor commercial. 7-8 storey. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
      roofView: "Replace the colored block viewed from above with a zinc mansard roof with prominent corner dome or turret, dormer windows, and chimney stacks. Keep surrounding context exactly as-is.",
      negative: "cartoon, illustration, sketch, low quality, blurry, text, watermark, neon, unrealistic colors"
    },
    facadeDetail: {
      primaryMaterial: "cream limestone ashlar with rustication at base",
      secondaryMaterial: "elaborate carved stone ornament: caryatids, garlands, masks at keystones",
      accentMaterial: "wrought-iron balconies with gilded highlights, copper or zinc dome at corner",
      groundFloor: "double-height commercial ground floor with stone pilasters, large display windows, corner entry",
      upperFloors: "continuous balconies at 2nd and 5th floors, tall arched windows at piano nobile, curved corner facade following street geometry",
      cornice: "massive stone cornice with carved modillions, mansard with dome above corner",
      colorScheme: "cream limestone, grey zinc mansard, black-and-gold ironwork, copper dome patina"
    },
    roofDetail: {
      form: "mansard with prominent corner dome or tourelle",
      material: "zinc mansard panels, copper dome cap, slate on lower pitch",
      features: "corner dome with finial, dormer windows, chimney stacks, zinc ornamental cresting",
      aerialAppearance: "distinctive corner dome element in copper/zinc, surrounding mansard roof, chimneys and dormers"
    }
  },

  mountain_alpine_chalet: {
    renderPrompt: {
      mapOverlay: "Replace the colored building block with a photorealistic mountain alpine chalet. Keep the exact same building footprint. Heavy timber-and-stone lodge with broad overhanging pitched roof, covered balconies with carved wood railings, stone chimney, and mountain-adapted massing. 2-3 storey. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
      roofView: "Replace the colored block viewed from above with a broad steep pitched roof with wood shingles or metal standing seam, deep overhangs, stone chimney, and snow guards. Keep surrounding context exactly as-is.",
      negative: "cartoon, illustration, sketch, low quality, blurry, text, watermark, neon, unrealistic colors"
    },
    facadeDetail: {
      primaryMaterial: "massive local stone base (granite or fieldstone), heavy timber construction above",
      secondaryMaterial: "dark-stained timber cladding and structural beams, hand-hewn or aged",
      accentMaterial: "carved timber balcony railings and brackets, wrought-iron hardware",
      groundFloor: "stone base with heavy timber entry door, small deep-set windows, covered porch, woodpile",
      upperFloors: "broad wraparound timber balcony with carved railings, timber-framed windows with shutters, exposed structural timber",
      cornice: "deep roof overhang (1-2m) with exposed decorative rafter tails and carved bargeboard",
      colorScheme: "grey stone base, dark brown timber, cream window frames, green shutters, warm interior glow"
    },
    roofDetail: {
      form: "steeply pitched gable or hip with broad overhangs",
      material: "wood shingles, natural slate, or standing-seam metal in dark tone",
      features: "large stone chimney, snow guards, deep overhangs protecting walls, dormer windows",
      aerialAppearance: "large steep dark roof with prominent stone chimney, deep overhangs casting shadows, possible dormer"
    }
  },

  alpine_mixed_use_lodge: {
    renderPrompt: {
      mapOverlay: "Replace the colored building block with a photorealistic alpine mixed-use lodge. Keep the exact same building footprint and height. Mountain village mixed-use building with stone-and-timber construction, pitched roof with dormers, ground-floor shops, and upper residential. 3-5 storey. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
      roofView: "Replace the colored block viewed from above with a pitched roof with standing-seam metal or slate, dormer windows, stone chimneys, and snow guards. Keep surrounding context exactly as-is.",
      negative: "cartoon, illustration, sketch, low quality, blurry, text, watermark, neon, unrealistic colors"
    },
    facadeDetail: {
      primaryMaterial: "coursed local stone at base and first floor, timber-frame above",
      secondaryMaterial: "dark-stained timber balconies and window frames, board-and-batten cladding",
      accentMaterial: "wrought-iron shop signs, carved timber brackets, copper downpipes",
      groundFloor: "stone-walled ground floor with shop windows, timber-framed display cases, deep entry porches",
      upperFloors: "covered timber balconies running full width, small-paned windows with timber shutters, flower boxes",
      cornice: "deep pitched roof overhang with exposed timber structure",
      colorScheme: "grey stone, dark timber, cream or pastel render panels, warm window glow, flower-box colors"
    },
    roofDetail: {
      form: "steep pitch with multiple dormers and cross-gables",
      material: "standing-seam metal or natural slate, dark tone",
      features: "stone chimneys, dormer windows, snow guards and snow fences, deep overhangs",
      aerialAppearance: "large dark pitched roof with dormers, stone chimneys, surrounding mountain landscape"
    }
  },

  transit_oriented_station_block: {
    renderPrompt: {
      mapOverlay: "Replace the colored building block with a photorealistic transit-oriented station block. Keep the exact same building footprint and height. Dense mixed-use development above transit station with active ground floor, glass-and-panel tower with podium, and covered transit plaza. 8-15 storey. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
      roofView: "Replace the colored block viewed from above with flat roofs at different levels, green roof on podium, rooftop amenities on tower, and transit canopy structure below. Keep surrounding context exactly as-is.",
      negative: "cartoon, illustration, sketch, low quality, blurry, text, watermark, neon, unrealistic colors"
    },
    facadeDetail: {
      primaryMaterial: "curtain wall glazing with insulated panels on tower, masonry or stone on podium",
      secondaryMaterial: "perforated metal panel rain screen, anodized aluminium framing",
      accentMaterial: "digital signage, wayfinding elements, stainless steel transit canopy columns",
      groundFloor: "fully activated ground floor with retail, transit entrance, bike facilities, covered public space",
      upperFloors: "tower rising from podium with glass-and-panel facade, balconies on residential levels, expressed floor plates",
      cornice: "clean parapet with subtle setback at top floors, no traditional cornice",
      colorScheme: "warm grey and silver panels, clear glass, bright wayfinding accents, green roof podium"
    },
    roofDetail: {
      form: "flat at multiple levels — podium and tower",
      material: "green roof on podium, membrane with solar on tower roof",
      features: "rooftop amenity space, solar arrays, mechanical penthouse, transit canopy structure at ground level",
      aerialAppearance: "tower rising from green-roofed podium, solar panels on tower roof, transit infrastructure below"
    }
  },

  transit_podium_residential: {
    renderPrompt: {
      mapOverlay: "Replace the colored building block with a photorealistic transit podium residential building. Keep the exact same building footprint and height. Mid-rise residential tower on a retail podium near transit, with warm cladding, generous balconies, and landscaped podium roof. 6-12 storey. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
      roofView: "Replace the colored block viewed from above with flat roof on residential tower and landscaped podium roof garden with pool, play area, and communal terrace. Keep surrounding context exactly as-is.",
      negative: "cartoon, illustration, sketch, low quality, blurry, text, watermark, neon, unrealistic colors"
    },
    facadeDetail: {
      primaryMaterial: "warm-toned brick or composite panels on tower, stone or precast on podium",
      secondaryMaterial: "aluminium-framed curtain wall on podium retail frontage",
      accentMaterial: "metal balcony frames, timber screening, integrated planter boxes",
      groundFloor: "active retail frontage with tall glazing, transit-adjacent entry, covered walkway, bike parking",
      upperFloors: "generous private balconies with metal frames, mix of solid and glazed panels, timber privacy screens",
      cornice: "stepped parapet with clean profile, top floor setback creating terrace",
      colorScheme: "warm brick or terracotta panels, grey metal balconies, green from podium landscaping"
    },
    roofDetail: {
      form: "flat tower roof with landscaped podium terrace",
      material: "membrane on tower, extensive green roof and hard landscape on podium",
      features: "podium garden with pool, play areas, communal BBQ; tower roof has solar panels and mechanical",
      aerialAppearance: "tower rising from lush podium garden with pool and terraces, solar panels on tower roof"
    }
  },

  glass_tower_podium_modern: {
    renderPrompt: {
      mapOverlay: "Replace the colored building block with a photorealistic modern glass tower with podium. Keep the exact same building footprint and height. Sleek glass curtain wall tower rising from a stone/concrete podium with retail and lobby. 15-40 storey high-rise. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
      roofView: "Replace the colored block viewed from above with a flat roof with mechanical penthouse and helipad on tower, and green roof terrace on podium. Keep surrounding context exactly as-is.",
      negative: "cartoon, illustration, sketch, low quality, blurry, text, watermark, neon, unrealistic colors"
    },
    facadeDetail: {
      primaryMaterial: "high-performance unitized curtain wall with blue-grey or clear low-E glass",
      secondaryMaterial: "anodized aluminium mullions and spandrel panels",
      accentMaterial: "polished stone or metal at podium, stainless steel entrance canopy",
      groundFloor: "double-height glazed lobby, polished stone podium cladding, dramatic entrance canopy, retail along street",
      upperFloors: "continuous glass curtain wall with subtle horizontal shadow lines at each floor, setback at top creating crown",
      cornice: "illuminated crown or subtle parapet, no traditional cornice",
      colorScheme: "blue-grey glass, silver aluminium frame, dark granite podium, stainless steel accents"
    },
    roofDetail: {
      form: "flat tower top with mechanical penthouse, stepped podium roof",
      material: "membrane roof with possible green sections on podium",
      features: "mechanical penthouse, possible helipad marking, lightning protection spire, green roof on podium",
      aerialAppearance: "glass tower top with mechanical penthouse, podium green roof terrace, distinctive floor plan visible through glass"
    }
  },

  skyline_glass_office_cluster: {
    renderPrompt: {
      mapOverlay: "Replace the colored building block with a photorealistic skyline glass office cluster. Keep the exact same building footprint and height. Cluster of glass office towers with varied heights, interconnected at podium level, with reflective curtain walls and landscaped plaza. 15-50 storey. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
      roofView: "Replace the colored block viewed from above with flat tower rooftops at varying heights with mechanical equipment, spires, and shared podium plaza below. Keep surrounding context exactly as-is.",
      negative: "cartoon, illustration, sketch, low quality, blurry, text, watermark, neon, unrealistic colors"
    },
    facadeDetail: {
      primaryMaterial: "reflective blue or silver-tinted curtain wall glass, high-performance coating",
      secondaryMaterial: "brushed stainless steel or white aluminium mullion system",
      accentMaterial: "polished granite at base, decorative lighting at crown",
      groundFloor: "interconnected lobby and retail at podium level, covered public plaza, water features",
      upperFloors: "all-glass curtain wall with varied tints between towers, sky bridges connecting towers, expressed floor plates",
      cornice: "varied tower crowns — flat-top, angled, or illuminated",
      colorScheme: "reflective glass in blue-silver tones, white structure, polished stone base"
    },
    roofDetail: {
      form: "multiple flat tower tops at different heights",
      material: "membrane roofs with mechanical equipment",
      features: "helicopter markings on tallest tower, mechanical penthouses, spires or antenna",
      aerialAppearance: "cluster of glass towers at varying heights, mechanical penthouses, shared podium/plaza visible between towers"
    }
  },

  civic_monumental_institution: {
    renderPrompt: {
      mapOverlay: "Replace the colored building block with a photorealistic civic monumental institution. Keep the exact same building footprint and height. Bold contemporary civic building with monumental stone or concrete forms, large-scale glazed entry hall, public forecourt, and institutional gravitas. 4-8 storey. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
      roofView: "Replace the colored block viewed from above with a sculptural roof form — possibly green roof, dramatic overhang, or copper-clad geometric volume. Keep surrounding context exactly as-is.",
      negative: "cartoon, illustration, sketch, low quality, blurry, text, watermark, neon, unrealistic colors"
    },
    facadeDetail: {
      primaryMaterial: "bush-hammered or honed limestone or concrete, large-format panels",
      secondaryMaterial: "structural glass curtain wall at main hall, expressed steel or concrete frame",
      accentMaterial: "bronze or corten steel entrance doors, public art integration",
      groundFloor: "monumental public entry with covered forecourt, fully glazed entrance hall, accessibility ramps",
      upperFloors: "expressed structural grid with stone infill panels, strategic glazing for daylight, deep reveals",
      cornice: "dramatic roof overhang or cantilever, sculptural roof form as architectural statement",
      colorScheme: "warm grey stone or concrete, clear glass main hall, bronze or corten accents"
    },
    roofDetail: {
      form: "sculptural — cantilever, fold, or dramatic overhang",
      material: "standing-seam metal, copper, or green roof on flat sections",
      features: "skylights to main hall, sculptural form visible from distance, concealed mechanical",
      aerialAppearance: "distinctive sculptural roof form, possible copper or green surface, dramatic geometry"
    }
  },

  monumental_museum_axis: {
    renderPrompt: {
      mapOverlay: "Replace the colored building block with a photorealistic monumental museum building. Keep the exact same building footprint and height. Grand cultural institution with stone facades, dramatic glazed atrium, sculpture forecourt, and axial approach. Mix of classical and contemporary elements. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
      roofView: "Replace the colored block viewed from above with a complex roof with glazed atrium skylight, green roof galleries, and sculpture terrace. Keep surrounding context exactly as-is.",
      negative: "cartoon, illustration, sketch, low quality, blurry, text, watermark, neon, unrealistic colors"
    },
    facadeDetail: {
      primaryMaterial: "smooth white or cream limestone, large-format ashlar panels",
      secondaryMaterial: "structural glass atrium with expressed steel or timber structure",
      accentMaterial: "bronze entrance doors, public sculpture, water features at entry",
      groundFloor: "grand entry sequence with water features, sculpture forecourt, fully glazed atrium lobby",
      upperFloors: "windowless gallery walls with stone cladding, strategic clerestory glazing, expressed joints",
      cornice: "clean roof edge or dramatic cantilever, glass atrium volume rising above roofline",
      colorScheme: "white/cream stone, clear glass atrium, bronze accents, green landscape setting"
    },
    roofDetail: {
      form: "complex with glazed atrium, flat gallery wings, possible sculptural element",
      material: "glass atrium roof with steel structure, green roof on gallery wings",
      features: "dramatic atrium skylight, sculpture terrace, concealed mechanical, skylights to galleries",
      aerialAppearance: "glazed atrium as centrepiece, flanking green-roofed gallery wings, sculpture terrace, formal landscaping"
    }
  },

  japanese_contemporary_lanehouse: {
    renderPrompt: {
      mapOverlay: "Replace the colored building block with a photorealistic Japanese contemporary lanehouse. Keep the exact same building footprint. Narrow urban house with precise timber-and-concrete construction, layered threshold entry, interior courtyard, and minimalist street presence. 2-3 storey. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
      roofView: "Replace the colored block viewed from above with a flat or very shallow-pitched roof with small interior courtyard open to sky, skylights, and minimal rooftop garden. Keep surrounding context exactly as-is.",
      negative: "cartoon, illustration, sketch, low quality, blurry, text, watermark, neon, unrealistic colors"
    },
    facadeDetail: {
      primaryMaterial: "smooth exposed concrete, board-formed or fair-faced",
      secondaryMaterial: "natural cedar timber cladding, horizontal or vertical battens",
      accentMaterial: "blackened steel entry gate, gravel garden at threshold, concealed lighting",
      groundFloor: "deep recessed entry through layered threshold, timber gate or sliding screen, planted gravel garden",
      upperFloors: "minimal openings, strategic clerestory or slot windows, timber-screened balcony",
      cornice: "razor-edge parapet, no traditional cornice expression",
      colorScheme: "grey concrete, natural cedar silver-aging, black steel, white gravel, green moss or bamboo"
    },
    roofDetail: {
      form: "flat or very shallow mono-pitch, precise edges",
      material: "membrane roof with gravel surface or minimal planting",
      features: "interior courtyard void open to sky, concealed drainage, skylight to interior rooms",
      aerialAppearance: "precise flat roof with small void or courtyard, minimal and clean, possible moss garden"
    }
  },

  japanese_machiya_mixed_use: {
    renderPrompt: {
      mapOverlay: "Replace the colored building block with a photorealistic Japanese machiya-inspired mixed-use building. Keep the exact same building footprint and height. Traditional Kyoto townhouse reinterpreted for mixed-use with timber lattice screens, narrow deep plan, shop at front, and garden at rear. 2-4 storey. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
      roofView: "Replace the colored block viewed from above with a gently pitched tile roof over narrow deep buildings, with interior light wells and rear gardens. Keep surrounding context exactly as-is.",
      negative: "cartoon, illustration, sketch, low quality, blurry, text, watermark, neon, unrealistic colors"
    },
    facadeDetail: {
      primaryMaterial: "dark-stained timber lattice (koshi) screens over deep timber structure",
      secondaryMaterial: "lime-plastered walls (shikkui), natural clay tiles",
      accentMaterial: "indigo-dyed noren curtains at entries, bamboo elements, stone threshold",
      groundFloor: "deep shop front (mise-no-ma) with sliding timber screens, noren curtain at entry, earthen or stone threshold",
      upperFloors: "timber lattice screens allowing filtered light, sliding shoji screens behind, deep eaves",
      cornice: "deep timber eaves with exposed beam structure, traditional tile edge",
      colorScheme: "dark-stained timber, white plaster, grey clay tiles, indigo fabric, green garden glimpses"
    },
    roofDetail: {
      form: "shallow pitch with deep eaves, running along narrow axis",
      material: "grey clay kawara tiles, traditional overlapping profile",
      features: "interior tsuboniwa (light-well garden), rear garden visible, deep timber eaves",
      aerialAppearance: "narrow deep roof forms with grey clay tiles, light-well gardens visible between buildings, rear gardens"
    }
  },

  eco_urban_bioclimatic_block: {
    renderPrompt: {
      mapOverlay: "Replace the colored building block with a photorealistic eco-urban bioclimatic block. Keep the exact same building footprint and height. Heavily planted mixed-use building with green facades, timber-and-glass construction, photovoltaic canopy, and natural ventilation chimneys. 5-8 storey. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
      roofView: "Replace the colored block viewed from above with an intensive green roof with urban farm plots, solar canopy, rainwater gardens, and biodiversity zones. Keep surrounding context exactly as-is.",
      negative: "cartoon, illustration, sketch, low quality, blurry, text, watermark, neon, unrealistic colors"
    },
    facadeDetail: {
      primaryMaterial: "CLT or glulam timber frame with timber cladding panels",
      secondaryMaterial: "planted facade modules with integrated irrigation, climbing plants on wire trellises",
      accentMaterial: "photovoltaic panels integrated into facade, natural stone base",
      groundFloor: "bio-swale landscaping at entry, community spaces, farm market or cafe, permeable paving",
      upperFloors: "deep balconies with planter boxes creating continuous green line, timber screens and operable louvres, natural ventilation",
      cornice: "green roof edge with cascading planting, solar canopy above",
      colorScheme: "natural timber, abundant green planting, earth tones, blue photovoltaic accents"
    },
    roofDetail: {
      form: "flat with intensive green roof and solar canopy",
      material: "intensive green roof with soil substrate, photovoltaic canopy structure above",
      features: "urban farm plots, pollinator gardens, rainwater collection, composting area, beehives",
      aerialAppearance: "lush green productive roof with farm plots, solar canopy structure, rainwater gardens, biodiversity areas"
    }
  },

  vertical_forest_residential: {
    renderPrompt: {
      mapOverlay: "Replace the colored building block with a photorealistic vertical forest residential tower. Keep the exact same building footprint and height. Residential tower with deep balconies supporting mature trees and shrubs at every level, creating a living green facade. 10-20 storey. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
      roofView: "Replace the colored block viewed from above with a green canopy of trees growing from balconies at the top, creating a forest-like appearance from above, with rooftop garden. Keep surrounding context exactly as-is.",
      negative: "cartoon, illustration, sketch, low quality, blurry, text, watermark, neon, unrealistic colors"
    },
    facadeDetail: {
      primaryMaterial: "white or light concrete structural frame, expressed at balcony edges",
      secondaryMaterial: "deep reinforced concrete balcony slabs supporting tree planters",
      accentMaterial: "stainless steel tree support cables, integrated irrigation systems",
      groundFloor: "public garden at base, community space, transparent lobby with green interior",
      upperFloors: "deep cantilevered balconies (3m+) with mature trees, large shrubs, and trailing plants at every level, floor-to-ceiling glazing behind",
      cornice: "trees and planting cascade over roof edge, no visible traditional cornice",
      colorScheme: "white concrete structure barely visible behind abundant green foliage, seasonal color variation"
    },
    roofDetail: {
      form: "flat with intensive rooftop garden and mature trees",
      material: "intensive green roof with deep soil, integrated irrigation",
      features: "mature trees and shrubs continuing the vertical forest upward, wind screening, photovoltaics where possible",
      aerialAppearance: "green canopy of trees and shrubs from above, resembling a forest patch, barely visible building structure"
    }
  },

  coastal_resort_terrace_block: {
    renderPrompt: {
      mapOverlay: "Replace the colored building block with a photorealistic coastal resort terrace block. Keep the exact same building footprint and height. Light-toned stepped residential building with generous terraces, ocean-facing orientation, louvred sun screens, and tropical landscaping. 4-8 storey. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
      roofView: "Replace the colored block viewed from above with stepped terraces with pools and gardens at multiple levels, white roof surfaces, and tropical planting. Keep surrounding context exactly as-is.",
      negative: "cartoon, illustration, sketch, low quality, blurry, text, watermark, neon, unrealistic colors"
    },
    facadeDetail: {
      primaryMaterial: "smooth white render or light limestone cladding",
      secondaryMaterial: "natural timber louvred sun screens, operable for shade control",
      accentMaterial: "brushed stainless steel railings, teak timber decking on terraces",
      groundFloor: "open-air lobby with cross-ventilation, resort reception, pool deck access, tropical garden",
      upperFloors: "deep terraces stepping back with each floor, plunge pools on select units, timber louvre screens, tropical planting",
      cornice: "no traditional cornice — building steps back creating organic profile",
      colorScheme: "white facades, natural timber screens, turquoise pool water, green tropical planting, blue sky"
    },
    roofDetail: {
      form: "stepped terraces creating cascading profile",
      material: "white membrane on flat areas, timber deck on terraces, pool surfaces",
      features: "private terrace pools, tropical planting at each step, solar panels on highest roof, cross-ventilation design",
      aerialAppearance: "cascading white terraces with pools and tropical gardens stepping down toward water, dramatic stepped profile"
    }
  },

  coastal_breezeway_mixed_use: {
    renderPrompt: {
      mapOverlay: "Replace the colored building block with a photorealistic coastal breezeway mixed-use building. Keep the exact same building footprint and height. Airy waterfront mixed-use with open breezeways, coral stone or light render, covered walkways, and ground-floor marina/retail. 3-5 storey. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
      roofView: "Replace the colored block viewed from above with a combination of pitched and flat roofs with terracotta or metal cladding, rooftop dining terraces, and shade structures. Keep surrounding context exactly as-is.",
      negative: "cartoon, illustration, sketch, low quality, blurry, text, watermark, neon, unrealistic colors"
    },
    facadeDetail: {
      primaryMaterial: "white lime render or coral stone cladding",
      secondaryMaterial: "natural timber shutters and breezeway screens, weathered to silver-grey",
      accentMaterial: "copper or bronze hardware, rope and nautical details, canvas shade sails",
      groundFloor: "open-air ground floor with retail and restaurants, breezeway passages to waterfront, marina views",
      upperFloors: "deep covered verandas with timber railings, operable timber shutters, cross-ventilation design",
      cornice: "deep roof overhang with exposed timber rafters, no enclosed attic",
      colorScheme: "white render, silver-grey weathered timber, turquoise sea accents, canvas cream, copper patina"
    },
    roofDetail: {
      form: "hip or gable with deep overhangs, some flat terrace sections",
      material: "standing-seam metal or terracotta tiles, light-colored to reflect heat",
      features: "rooftop dining terrace with shade sails, cupola ventilators, deep overhangs for shade",
      aerialAppearance: "light-colored roofs with shade structures, rooftop terraces, breezeway passages visible, waterfront connection"
    }
  },

  custom_prompt_ready_archetype: {
    renderPrompt: {
      mapOverlay: "Replace the colored building block with a photorealistic building matching the user's custom style description. Keep the exact same building footprint and height. Apply the specified materials, proportions, and architectural character. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
      roofView: "Replace the colored block viewed from above with a roof matching the user's custom style description. Keep surrounding context exactly as-is.",
      negative: "cartoon, illustration, sketch, low quality, blurry, text, watermark, neon, unrealistic colors"
    },
    facadeDetail: {
      primaryMaterial: "user-specified primary facade material",
      secondaryMaterial: "user-specified secondary material or contrast element",
      accentMaterial: "user-specified accent details",
      groundFloor: "user-specified ground floor treatment and frontage type",
      upperFloors: "user-specified upper floor composition and fenestration",
      cornice: "user-specified roof-to-wall transition",
      colorScheme: "user-specified color palette"
    },
    roofDetail: {
      form: "user-specified roof form",
      material: "user-specified roof material",
      features: "user-specified roof features",
      aerialAppearance: "user-specified aerial appearance"
    }
  },

  custom_contextual_experiment: {
    renderPrompt: {
      mapOverlay: "Replace the colored building block with a photorealistic experimental building matching the user's creative vision. Keep the exact same building footprint and height. Apply unconventional materials and forms as specified. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
      roofView: "Replace the colored block viewed from above with an experimental roof form matching the user's vision. Keep surrounding context exactly as-is.",
      negative: "cartoon, illustration, sketch, low quality, blurry, text, watermark, neon, unrealistic colors"
    },
    facadeDetail: {
      primaryMaterial: "user-specified experimental primary material",
      secondaryMaterial: "user-specified experimental secondary material",
      accentMaterial: "user-specified experimental accent elements",
      groundFloor: "user-specified experimental ground floor treatment",
      upperFloors: "user-specified experimental upper floor composition",
      cornice: "user-specified experimental roof edge treatment",
      colorScheme: "user-specified experimental color palette"
    },
    roofDetail: {
      form: "user-specified experimental roof form",
      material: "user-specified experimental roof material",
      features: "user-specified experimental roof features",
      aerialAppearance: "user-specified experimental aerial appearance"
    }
  }
};

// ─── APPLY METADATA ──────────────────────────────────────────────────────────

let enriched = 0;
let skipped = 0;

for (const archetype of data.archetypes) {
  const meta = METADATA[archetype.id];
  if (meta) {
    // Don't overwrite if already has renderPrompt (e.g., industrial_brick_mixed_use)
    if (!archetype.renderPrompt) {
      archetype.renderPrompt = meta.renderPrompt;
      enriched++;
    } else {
      skipped++;
    }
    if (!archetype.facadeDetail) {
      archetype.facadeDetail = meta.facadeDetail;
    }
    if (!archetype.roofDetail) {
      archetype.roofDetail = meta.roofDetail;
    }
  } else {
    console.warn(`No metadata defined for archetype: ${archetype.id}`);
  }
}

fs.writeFileSync(OUTPUT, JSON.stringify(data, null, 2) + '\n', 'utf-8');
console.log(`Done! Enriched ${enriched} archetypes, skipped ${skipped} (already had metadata).`);
console.log(`Total archetypes: ${data.archetypes.length}`);
