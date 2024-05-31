workspace {
    name "Сайт Заказа Услуг"
    description "Платформа для заказа различных услуг"

    !identifiers hierarchical

    model {
        user = person "Пользователь сайта заказа услуг"
        serviceOrdering = softwareSystem "Сайт заказа услуг" {
            description "Сайт для поиска и заказа услуг"

            api_gateway = container "API Gateway" {
                description "Входной API для обращения к сервисам приложения"
            }

            services_service = container "Services Service" {
                description "API для получения и управления услугами"
            }
            
            users_service = container "Users Service" {
                description "API для получения и управления пользователями"
            }

            orders_service = container "Orders Service" {
                description "API для управления заказами"
            }

            group "Слой хранения данных" {
                user_database = container "User Database" {
                    description "База данных для хранения информации о пользователях"
                    technology "containerized PostgreSQL"
                    tags "database"
                }
                
                services_database = container "Services Database" {
                    description "База данных для хранения информации об услугах"
                    technology "containerized MongoDB"
                    tags "database"
                }

                orders_database = container "Orders Database" {
                    description "База данных для хранения информации о заказах"
                    technology "containerized MongoDB"
                    tags "database"
                }
            }

            user -> api_gateway "API команды на управление и получение данных о пользователях, услугах и заказах"
            api_gateway -> services_service "Внутренние API команды на управление и получение данных об услугах"
            api_gateway -> users_service "Внутренние API команды на управление и получение данных о пользователях"
            api_gateway -> orders_service "Внутренние API команды на управление заказами"

            services_service -> services_database "Получение/обновление данных об услугах" "TCP 3306"
            users_service -> user_database "Получение/обновление данных о пользователях" "TCP 5432"
            orders_service -> orders_database "Получение/обновление данных о заказах" "TCP 27017"
        }

        user -> serviceOrdering "Управление и получение данных о пользователях, услугах и заказах услуг"

        deploymentEnvironment "Production" {
            deploymentNode "Service Ordering Server" {
                containerInstance serviceOrdering.services_service
                containerInstance serviceOrdering.users_service
                containerInstance serviceOrdering.orders_service
                instances 1
                properties {
                    "cpu" "4"
                    "ram" "4Gb"
                }
            }

            deploymentNode "Databases" {
                deploymentNode "User Database Server" {
                    containerInstance serviceOrdering.user_database
                    instances 1
                }

                deploymentNode "Services Database Server" {
                    containerInstance serviceOrdering.services_database
                    instances 1
                }

                deploymentNode "Orders Database Server" {
                    containerInstance serviceOrdering.orders_database
                    instances 1
                }
            }
        }
    }

    views {
        themes default

        properties { 
            structurizr.tooltips true
        }

        !script groovy {
            workspace.views.createDefaultViews()
            workspace.views.views.findAll { it instanceof com.structurizr.view.ModelView }.each { it.enableAutomaticLayout() }
        }

        dynamic serviceOrdering "UC01" "Создание нового пользователя" {
            autoLayout
            user -> serviceOrdering.api_gateway "Создать нового пользователя (POST /users)"
            serviceOrdering.api_gateway -> serviceOrdering.users_service "Создать нового пользователя (POST /users)"
            serviceOrdering.users_service -> serviceOrdering.user_database "Сохранить данные о пользователе" 
        }

        dynamic serviceOrdering "UC02" "Поиск пользователя по логину" {
            autoLayout
            user -> serviceOrdering.api_gateway "Получить пользователя по логину (GET /users/{login})"
            serviceOrdering.api_gateway -> serviceOrdering.users_service "Получить пользователя по логину (GET /users/{login})"
            serviceOrdering.users_service -> serviceOrdering.user_database "Поиск пользователя в базе данных" 
        }

        dynamic serviceOrdering "UC03" "Поиск пользователя по маске имя и фамилии" {
            autoLayout
            user -> serviceOrdering.api_gateway "Получить пользователя по имени и фамилии (GET /users/{name})"
            serviceOrdering.api_gateway -> serviceOrdering.users_service "Получить пользователя по имени и фамилии (GET /users/{name})"
            serviceOrdering.users_service -> serviceOrdering.user_database "Поиск пользователя в базе данных" 
        }

        dynamic serviceOrdering "UC04" "Создание услуги" {
            autoLayout
            user -> serviceOrdering.api_gateway "Создать услугу (POST /services)"
            serviceOrdering.api_gateway -> serviceOrdering.services_service "Создать услугу (POST /services)"
            serviceOrdering.services_service -> serviceOrdering.services_database "Сохранить данные об услуге" 
        }

        dynamic serviceOrdering "UC05" "Получение списка услуг" {
            autoLayout
            user -> serviceOrdering.api_gateway "Получить список услуг (GET /services)"
            serviceOrdering.api_gateway -> serviceOrdering.services_service "Получить список услуг (GET /services)"
            serviceOrdering.services_service -> serviceOrdering.services_database "Получение данных об услугах" 
        }

        dynamic serviceOrdering "UC06" "Добавление услуг в заказ" {
            autoLayout
            user -> serviceOrdering.api_gateway "Добавить услугу в заказ (POST /orders/{orderId}/services)"
            serviceOrdering.api_gateway -> serviceOrdering.orders_service "Добавить услугу в заказ (POST /orders/{orderId}/services)"
            serviceOrdering.orders_service -> serviceOrdering.orders_database "Обновить заказ с новой услугой" 
        }

        dynamic serviceOrdering "UC07" "Получение заказа для пользователя" {
            autoLayout
            user -> serviceOrdering.api_gateway "Получить заказ пользователя (GET /orders/{userId})"
            serviceOrdering.api_gateway -> serviceOrdering.orders_service "Получить заказ пользователя (GET /orders/{userId})"
            serviceOrdering.orders_service -> serviceOrdering.orders_database "Получение данных о заказе пользователя" 
        }

    }

}
