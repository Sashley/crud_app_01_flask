table PlantDetail {
    id Int [pk, increment]
    name String
    description String
    smu Int
    smu_last_update DateTime
    parent_id PlantDetail
    maintenance_group MaintenanceGroup
    createdAt DateTime
    updatedAt DateTime
    m2m [
      operator
      tradesman
    ]
    o2m [
      history
      work_order
      production
      smu_history
      scheduled_maintenance
    ]
}