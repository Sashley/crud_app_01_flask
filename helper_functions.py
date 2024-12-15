def get_commodity_data():
    """Return realistic commodity data pairs (name, description)"""
    commodities = [
        ("Electronics", "Consumer electronics and components"),
        ("Textiles", "Clothing and fabric materials"),
        ("Automotive Parts", "Vehicle components and spare parts"),
        ("Machinery", "Industrial equipment and machinery"),
        ("Chemicals", "Industrial chemicals and compounds"),
        ("Food Products", "Processed and packaged food items"),
        ("Pharmaceuticals", "Medical supplies and medicines"),
        ("Furniture", "Home and office furniture"),
        ("Toys", "Children's toys and games"),
        ("Sports Equipment", "Athletic and recreational equipment"),
        ("Building Materials", "Construction supplies and materials"),
        ("Paper Products", "Paper goods and materials"),
        ("Metal Products", "Processed metal goods"),
        ("Plastics", "Raw and processed plastic materials"),
        ("Agricultural Products", "Farm produce and materials")
    ]
    return commodities[0]  # Return first pair for consistent data

def get_packtype_data():
    """Return realistic pack type data pairs (name, description)"""
    return [
        ("Pallet", "Standard wooden pallet"),
        ("Carton", "Cardboard box packaging"),
        ("Crate", "Wooden crate for heavy items"),
        ("Drum", "Metal or plastic drum container"),
        ("Bag", "Flexible bag packaging"),
        ("Bundle", "Bundled items"),
        ("Roll", "Rolled materials"),
        ("Case", "Protective case packaging"),
        ("Barrel", "Large cylindrical container"),
        ("Box", "Standard shipping box")
    ]
