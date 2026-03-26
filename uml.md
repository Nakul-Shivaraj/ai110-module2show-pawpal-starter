classDiagram
    class Owner {
        +String name
        +String email
        +String available_hours
        +List pets
        +add_pet(pet)
        +remove_pet(pet)
        +get_pets()
    }

    class Pet {
        +String name
        +String species
        +int age
        +String health_notes
        +List tasks
        +add_task(task)
        +remove_task(task)
        +get_tasks()
    }

    class Task {
        +String name
        +String category
        +int duration_minutes
        +int priority
        +String recurrence
        +String preferred_time
        +is_due_today()
        +to_dict()
    }

    class Scheduler {
        +Pet pet
        +int available_minutes
        +List scheduled_tasks
        +generate_plan()
        +sort_by_priority()
        +check_conflicts()
        +explain_plan()
    }

    Owner "1" --> "many" Pet : owns
    Pet "1" --> "many" Task : has
    Scheduler "1" --> "1" Pet : schedules for