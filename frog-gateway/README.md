# GestorMedic - API Gateway Central

Este módulo actúa como el único punto de entrada público (Reverse Proxy) para la infraestructura de microservicios de GestorMedic. Está construido sobre Nginx y se encarga de interceptar, enrutar y gestionar todo el tráfico HTTP entrante hacia los servicios internos correspondientes.

Al utilizar este Gateway, la red interna de contenedores queda aislada del exterior, garantizando que los clientes web (como la interfaz en Angular) interactúen con una única dirección IP y un solo puerto, resolviendo problemas de CORS y unificando el dominio.

## Enrutamiento

El servidor expone el puerto `80` internamente (mapeado al `8000` en el host local) y distribuye el tráfico basándose en los prefijos de la URI.

| Ruta de Entrada | Microservicio Destino | Puerto Interno | Propósito Principal |
| :--- | :--- | :--- | :--- |
| `/` | `gm-backend` | `8000` | Gestión central (Auth, Usuarios, Clínicas, Roles) |
| `/citas/` | `gm-citas` | `8000` | Agendas, validación de solapamientos y reservas |
| `/notificaciones/` | `gm-notifications-api` | `8000` | Envío de correos, alertas y tareas en segundo plano |

## Documentación (Swagger)

Una vez que la infraestructura esté en ejecución, puedes acceder a la documentación Swagger en los siguientes enlaces:

* **Módulo Central (Core):** [http://localhost:8000/docs](http://localhost:8000/docs)
* **Módulo de Citas:** [http://localhost:8000/citas/docs](http://localhost:8000/citas/docs)
* **Módulo de Notificaciones:** [http://localhost:8000/notificaciones/docs](http://localhost:8000/notificaciones/docs)
