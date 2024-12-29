    table Manifest {
      id Int [pk, increment]
      bill_of_lading String
      shipper_id Int [ref: > Client.id]
      consignee_id Int [ref: > Client.id]
      vessel_id Int [ref: > Vessel.id]
      voyage_id Int [ref: > Voyage.id]
      port_of_loading_id Int [ref: > Port.id]
      port_of_discharge_id Int [ref: > Port.id]
      place_of_delivery String
      place_of_receipt String
      clauses String
      date_of_receipt DateTime
      line_items LineItem[] [relationship: "one-to-many", back_populates: "manifest"]
    }

    table LineItem {
      id Int [pk, increment]
      manifest_id Int [ref: > Manifest.id]
      description String
      quantity Int
      weight Int
      volume Int
      pack_type_id Int [ref: > PackType.id]
      commodity_id Int [ref: > Commodity.id]
      container_id Int [ref: > Container.id]
    }

    table Commodity {
      id Int [pk, increment]
      name String
      description String
      line_items LineItem[] [relationship: "one-to-many", back_populates: "commodity"]
    }

    table PackType {
      id Int [pk, increment]
      name String
      description String
      line_items LineItem[] [relationship: "one-to-many", back_populates: "pack_type"]
    }

    table Container {
      id Int [pk, increment]
      number String
      port_id Int [ref: > Port.id]
      updated DateTime
      line_items LineItem[] [relationship: "one-to-many", back_populates: "container"]
      container_histories ContainerHistory[] [relationship: "one-to-many", back_populates: "container"]
    }

    table ContainerHistory {
      id Int [pk, increment]
      container_id Int [ref: > Container.id]
      port_id Int [ref: > Port.id]
      client_id Int [ref: > Client.id]
      container_status_id Int [ref: > ContainerStatus.id]
      damage String
      updated DateTime
    }

    table ContainerStatus {
      id Int [pk, increment]
      name String
      description String
      container_histories ContainerHistory[] [relationship: "one-to-many", back_populates: "container_status"]
    }

    table ShippingCompany {
      id Int [pk, increment]
      name String
      vessels Vessel[] [relationship: "one-to-many", back_populates: "shipping_company"]
    }

    table Vessel {
      id Int [pk, increment]
      name String
      shipping_company_id Int [ref: > ShippingCompany.id]
      manifests Manifest[] [relationship: "one-to-many", back_populates: "vessel"]
    }

    table Voyage {
      id Int [pk, increment]
      name String
      vessel_id Int [ref: > Vessel.id]
      rotation_number Int
      legs Leg[] [relationship: "one-to-many", back_populates: "voyage"]
      manifests Manifest[] [relationship: "one-to-many", back_populates: "voyage"]
    }

    table Leg {
      id Int [pk, increment]
      voyage_id Int [ref: > Voyage.id]
      port_id Int [ref: > Port.id]
      leg_number Int
      eta DateTime
      etd DateTime
    }

    table Port {
      id Int [pk, increment]
      name String
      country String
      prefix String
      containers Container[] [relationship: "one-to-many", back_populates: "port"]
    }

    table PortPair {
      id Int [pk, increment]
      pol_id Int [ref: > Port.id]
      pod_id Int [ref: > Port.id]
      distance Int
    }

    table Country {
      id Int [pk, increment]
      name String
      ports Port[] [relationship: "one-to-many", back_populates: "country"]
    }

    table Client {
      id Int [pk, increment]
      name String
      address String
      town String
      country_id Int [ref: > Country.id]
      contact_person String
      email String
      phone String
      manifests Manifest[] [relationship: "one-to-many", back_populates: "client"]
      consigned_manifests Manifest[] [relationship: "one-to-many", back_populates: "client"]
    }

    table User {
      id Int [pk, increment]
      name String
      email String
      password_hash String
      line_items LineItem[] [relationship: "one-to-many", back_populates: "user"]
    }

    table Rate {
      id Int [pk, increment]
      distance Int
      commodity_id Int [ref: > Commodity.id]
      pack_type_id Int [ref: > PackType.id]
      client_id Int [ref: > Client.id]
      rate Float
      effective DateTime
    }