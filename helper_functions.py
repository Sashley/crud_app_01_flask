import random

def get_commodity_data():
    commodities = {
        "Electronics": [
            ("Smartphones", "Mobile phones and accessories for retail distribution"),
            ("Laptops", "Personal computers and related equipment"),
            ("Consumer Electronics", "Home entertainment and personal electronic devices"),
            ("Computer Parts", "Components and peripherals for computer assembly"),
            ("Industrial Electronics", "Electronic components for manufacturing"),
            ("Network Equipment", "Networking and telecommunications hardware"),
            ("Display Panels", "LCD, LED, and OLED display components"),
            ("Audio Equipment", "Professional and consumer audio devices"),
            ("Gaming Hardware", "Video game consoles and accessories"),
            ("Smart Devices", "IoT and connected devices"),
            ("Memory Chips", "RAM and storage components"),
            ("Power Supplies", "Power adapters and UPS systems"),
            ("Cameras", "Digital cameras and photography equipment"),
            ("Printers", "Printing and scanning devices"),
            ("Security Systems", "Electronic security and surveillance equipment")
        ],
        "Automotive": [
            ("Auto Parts", "Replacement parts for vehicle maintenance and repair"),
            ("Vehicle Components", "OEM components for vehicle assembly"),
            ("Tires & Wheels", "Vehicle tires and wheel assemblies"),
            ("Engine Parts", "Engine components and assemblies"),
            ("Car Accessories", "Aftermarket vehicle accessories"),
            ("Electrical Systems", "Vehicle electrical and electronic systems"),
            ("Transmission Parts", "Transmission and drivetrain components"),
            ("Brake Systems", "Brake components and assemblies"),
            ("Interior Parts", "Vehicle interior components and trim"),
            ("Body Parts", "Vehicle body and structural components"),
            ("Suspension Systems", "Shock absorbers and suspension components"),
            ("Exhaust Systems", "Mufflers and exhaust components"),
            ("Lighting Systems", "Vehicle lighting and signaling equipment"),
            ("Fuel Systems", "Fuel delivery and injection components"),
            ("Safety Equipment", "Vehicle safety and restraint systems")
        ],
        "Textiles": [
            ("Raw Cotton", "Unprocessed cotton for textile manufacturing"),
            ("Finished Garments", "Ready-to-wear clothing for retail"),
            ("Synthetic Fabrics", "Man-made textile materials"),
            ("Wool Products", "Processed wool and wool-based products"),
            ("Industrial Textiles", "Technical and industrial fabric materials"),
            ("Leather Goods", "Processed leather and leather products"),
            ("Denim Products", "Denim fabrics and finished goods"),
            ("Sports Apparel", "Athletic and performance wear"),
            ("Home Textiles", "Household textile products"),
            ("Fashion Accessories", "Textile-based fashion accessories"),
            ("Silk Products", "Natural silk fabrics and garments"),
            ("Linen Products", "Linen fabrics and finished goods"),
            ("Protective Wear", "Safety and protective clothing"),
            ("Upholstery Fabrics", "Furniture and automotive textiles"),
            ("Specialty Fibers", "High-performance synthetic fibers")
        ],
        "Chemicals": [
            ("Industrial Chemicals", "Chemicals for manufacturing processes"),
            ("Pharmaceutical Ingredients", "Raw materials for medicine production"),
            ("Agricultural Chemicals", "Fertilizers and crop protection products"),
            ("Plastic Resins", "Raw materials for plastic manufacturing"),
            ("Specialty Chemicals", "High-purity chemicals for specific applications"),
            ("Cleaning Agents", "Industrial and commercial cleaning products"),
            ("Paint Products", "Industrial and decorative coatings"),
            ("Adhesives", "Industrial and commercial adhesive products"),
            ("Food Additives", "Chemical additives for food processing"),
            ("Water Treatment", "Water purification and treatment chemicals"),
            ("Petrochemicals", "Petroleum-derived chemical products"),
            ("Polymer Products", "Synthetic polymer materials"),
            ("Laboratory Reagents", "Chemicals for laboratory use"),
            ("Textile Chemicals", "Chemicals for textile processing"),
            ("Construction Chemicals", "Chemicals for construction applications")
        ]
    }
    
    # Generate all possible combinations first
    all_combinations = []
    for category, items in commodities.items():
        for subcategory, description in items:
            all_combinations.append((f"{subcategory} ({category})", description))
    
    # Return a random combination
    return random.choice(all_combinations)

def get_packtype_data():
    """Get all pack type data"""
    return [
        # Containers
        ("20ft Standard Container", "20ft x 8ft x 8.5ft dry cargo container for general purpose shipping"),
        ("40ft Standard Container", "40ft x 8ft x 8.5ft dry cargo container for general purpose shipping"),
        ("40ft High Cube", "40ft x 8ft x 9.5ft high cube container for volume cargo"),
        ("20ft Reefer", "20ft refrigerated container for temperature-controlled cargo"),
        ("40ft Reefer", "40ft refrigerated container for temperature-controlled cargo"),
        ("20ft Open Top", "20ft container with removable top for oversized cargo"),
        ("40ft Open Top", "40ft container with removable top for oversized cargo"),
        ("20ft Flat Rack", "20ft platform with end walls for heavy and oversized cargo"),
        ("40ft Flat Rack", "40ft platform with end walls for heavy and oversized cargo"),
        ("20ft Tank", "20ft tank container for liquid bulk cargo"),
        ("40ft Tank", "40ft tank container for liquid bulk cargo"),
        ("20ft Ventilated", "20ft container with ventilation for perishable cargo"),
        ("40ft Ventilated", "40ft container with ventilation for perishable cargo"),
        ("20ft Insulated", "20ft insulated container for temperature-sensitive cargo"),
        ("40ft Insulated", "40ft insulated container for temperature-sensitive cargo"),
        ("20ft Hard Top", "20ft container with removable steel roof"),
        ("40ft Hard Top", "40ft container with removable steel roof"),
        ("20ft Platform", "20ft platform container for oversized cargo"),
        ("40ft Platform", "40ft platform container for oversized cargo"),
        ("45ft High Cube", "45ft x 8ft x 9.5ft high cube container for extra volume"),
        
        # Pallets and Crates
        ("Standard Wood Pallet", "48x40 inch wooden pallet for general cargo"),
        ("Euro Pallet", "1200x800mm European standard pallet"),
        ("Plastic Pallet", "Durable plastic pallet for repeated use"),
        ("Metal Pallet", "Steel pallet for heavy-duty applications"),
        ("Wooden Crate", "Custom wooden crate for fragile items"),
        ("Steel Crate", "Heavy-duty steel crate for industrial cargo"),
        
        # Drums and Tanks
        ("Steel Drum", "55-gallon steel drum for liquid cargo"),
        ("Plastic Drum", "55-gallon plastic drum for chemicals"),
        ("Fiber Drum", "Fiber drum for dry goods"),
        ("IBC Tank", "1000L intermediate bulk container"),
        ("ISO Tank", "Tank container for liquid bulk cargo"),
        
        # Bags and Sacks
        ("Bulk Bag", "Flexible intermediate bulk container (FIBC)"),
        ("Polypropylene Sack", "Woven PP sack for dry goods"),
        ("Paper Sack", "Multi-layer paper sack for powders"),
        ("Jute Bag", "Natural fiber bag for agricultural products"),
        
        # Specialized Units
        ("Refrigerated Box", "Insulated box with cooling unit"),
        ("Cargo Net", "Net container for irregular items"),
        ("Roll Cage", "Wheeled cage for retail distribution"),
        ("Collapsible Bin", "Foldable container for storage efficiency"),
        ("Air Cargo Unit", "Specialized container for air freight")
    ]

def get_random_packtype():
    """Get a random pack type"""
    return random.choice(get_packtype_data())
