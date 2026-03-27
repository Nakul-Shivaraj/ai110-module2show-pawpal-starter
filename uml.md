classDiagram
    class Task {
        +String name
        +String category
        +int duration_minutes
        +int priority
        +String recurrence
        +String preferred_time
        +bool completed
        +String task_id
        +date due_date
        +is_due_today() bool
        +next_occurrence() Task
        +to_dict() dict
    }

    class Pet {
        +String name
        +String species
        +int age
        +String health_notes
        +List tasks
        +add_task(task)
        +remove_task(task_name)
        +get_tasks() List
        +get_tasks_due_today() List
        +mark_task_complete(task_name) Task
    }

    class Owner {
        +String name
        +String email
        +String available_hours
        +List pets
        +add_pet(pet)
        +remove_pet(pet_name)
        +get_pets() List
        +get_all_tasks() List
        +available_minutes() int
    }

    class Scheduler {
        +Owner owner
        +List scheduled_tasks
        +List conflict_warnings
        +generate_plan() List
        +sort_by_priority(tasks) List
        +sort_by_time(tasks) List
        +check_conflicts(tasks) List
        +detect_conflicts(tasks) List
        +filter_tasks(pet_name, category, completed) List
        +explain_plan() str
        -_get_due_tasks() List
        -_to_minutes(time_str) int
    }

    Owner "1" --> "many" Pet : owns
    Pet "1" --> "many" Task : has
    Scheduler "1" --> "1" Owner : schedules for
    Task ..> Task : next_occurrence() creates