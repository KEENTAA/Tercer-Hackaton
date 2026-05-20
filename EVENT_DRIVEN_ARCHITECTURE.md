# ARQUITECTURA EVENT-DRIVEN

## Flujo de Eventos en el Sistema

### 1. Event Bus (RabbitMQ)

El sistema utiliza **RabbitMQ Topic Exchange** llamado **`code-grading`** para toda la comunicación asíncrona entre microservicios.

### 2. Eventos Principales

#### 2.1 `submission.submissionCreated`

**Publicador**: Submission Service  
**Consumidores**: Execution Service, Audit Service  
**Cuándo**: Cuando un estudiante envía código

```json
{
  "event_id": "evt_abc123",
  "event_type": "submission.submissionCreated",
  "timestamp": "2024-05-19T10:30:00Z",
  "data": {
    "submission_id": "sub_456",
    "student_id": "usr_789",
    "assignment_id": "task_123",
    "code_content": "print('Hello')",
    "language": "python",
    "attempt_number": 1
  }
}
```

**Procesamiento**:
- **Execution Service**: Ejecuta el código inmediatamente
- **Audit Service**: Registra el evento en log de auditoría

---

#### 2.2 `execution.executionCompleted`

**Publicador**: Execution Service  
**Consumidores**: Grading Service, Plagiarism Service, Audit Service  
**Cuándo**: Después de ejecutar el código contra test cases

```json
{
  "event_id": "evt_def456",
  "event_type": "execution.executionCompleted",
  "timestamp": "2024-05-19T10:31:00Z",
  "data": {
    "execution_id": "exec_111",
    "submission_id": "sub_456",
    "status": "success",
    "test_results": {
      "tests_passed": 8,
      "tests_total": 10,
      "execution_time_ms": 245,
      "memory_used_mb": 15.2
    },
    "stdout": "Test 1 PASSED\nTest 2 PASSED\n...",
    "stderr": ""
  }
}
```

**Procesamiento**:
- **Grading Service**: Calcula score basado en tests
- **Plagiarism Service**: Comienza análisis de plagio
- **Audit Service**: Registra el evento

---

#### 2.3 `grading.gradingCompleted`

**Publicador**: Grading Service  
**Consumidores**: Plagiarism Service, Audit Service  
**Cuándo**: Después de calcular la calificación

```json
{
  "event_id": "evt_ghi789",
  "event_type": "grading.gradingCompleted",
  "timestamp": "2024-05-19T10:32:00Z",
  "data": {
    "grade_id": "grade_222",
    "submission_id": "sub_456",
    "student_id": "usr_789",
    "score": 85,
    "percentage": 85.0,
    "rubric_scores": {
      "functionality": 45,
      "code_quality": 25,
      "efficiency": 15
    }
  }
}
```

**Procesamiento**:
- **Plagiarism Service**: Comienza análisis si no está hecho
- **Audit Service**: Registra la calificación

---

#### 2.4 `plagiarism.plagiarismAnalyzed`

**Publicador**: Plagiarism Service  
**Consumidores**: Audit Service  
**Cuándo**: Después de analizar similitudes con otros envíos

```json
{
  "event_id": "evt_jkl012",
  "event_type": "plagiarism.plagiarismAnalyzed",
  "timestamp": "2024-05-19T10:33:00Z",
  "data": {
    "report_id": "plagiarism_333",
    "submission_id": "sub_456",
    "assignment_id": "task_123",
    "plagiarism_percentage": 5.2,
    "status": "completed",
    "matches": [
      {
        "submission_id_2": "sub_789",
        "student_id_2": "usr_101",
        "similarity": 12.5
      }
    ]
  }
}
```

**Procesamiento**:
- **Audit Service**: Registra el análisis
- Final del pipeline - envío completamente procesado

---

#### 2.5 `audit.eventLogged`

**Publicador**: Audit Service  
**Consumidores**: Ninguno (terminal)  
**Cuándo**: Después de registrar cada evento

```json
{
  "event_id": "evt_mno345",
  "event_type": "audit.eventLogged",
  "timestamp": "2024-05-19T10:33:00Z",
  "data": {
    "user_id": "usr_789",
    "action": "submission.submissionCreated",
    "resource_type": "submission",
    "resource_id": "sub_456",
    "status": "success",
    "ip_address": "192.168.1.100",
    "details": {...}
  }
}
```

---

### 3. Flujo Completo: Envío hasta Calificación

```
┌─────────────────────┐
│    Estudiante       │
│  Envía Código       │
└──────────┬──────────┘
           │
           ▼
┌──────────────────────────────┐
│   Submission Service         │
│  - Valida deadline           │
│  - Guarda en BD              │
│  - Publica evento            │
└──────────┬───────────────────┘
           │
    ┌──────*──────┐
    │             │
    ▼             ▼
 ┌─────────┐  ┌─────────────┐
 │ Execution │  │   Audit    │
 │ Service   │  │  Service   │
 └──────┬────┘  └─────────────┘
        │
        │ (ejecuta tests)
        │
        ▼
 ┌──────────────────┐
 │ Publica evento:  │
 │ executionCompleted
 └─────┬────────────┘
       │
   ┌───*────┬───────────┐
   │        │           │
   ▼        ▼           ▼
┌──────┐ ┌────────┐ ┌────────┐
│Grading│ │Plagiarism│ │Audit│
│Service│ │Service   │ │     │
└──┬───┘ └────┬───┘ └────────┘
   │          │
   │ (calcula score)
   │          │
   ▼          │
┌──────────────┐
│gradingCompleted
└─────┬────────┘
      │
  ┌───*────┐
  │        │
  ▼        ▼
┌─────┐  ┌────────┐
│Plagia│ │Audit   │
│rism  │ │Service │
└──┬───┘ └────────┘
   │
   │ (detecta similitudes)
   │
   ▼
┌──────────────┐
│plagiarismAnalyzed
└────┬─────────┘
     │
     ▼
  ┌────────┐
  │ Audit  │
  │Service │
  └────────┘
            │
            ▼
      ✅ ENVÍO COMPLETAMENTE PROCESADO
```

---

### 4. Configuración de RabbitMQ

#### 4.1 Exchange

```
Name: code-grading
Type: topic
Durable: true
```

#### 4.2 Queues

```
submission.queue
  ├─ Binding: submission.*
  └─ Consumer: Execution Service, Audit Service

execution.queue
  ├─ Binding: execution.*
  └─ Consumer: Grading Service, Plagiarism Service, Audit Service

grading.queue
  ├─ Binding: grading.*
  └─ Consumer: Plagiarism Service, Audit Service

plagiarism.queue
  ├─ Binding: plagiarism.*
  └─ Consumer: Audit Service

audit.queue
  ├─ Binding: audit.*
  └─ Consumer: none
```

---

### 5. Implementación en Python (FastAPI)

#### 5.1 Publicar Evento

```python
import pika
import json
from schemas import SubmissionCreatedEvent

def publish_event(event: SubmissionCreatedEvent):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='rabbitmq')
    )
    channel = connection.channel()
    
    # Declarar exchange
    channel.exchange_declare(
        exchange='code-grading',
        exchange_type='topic',
        durable=True
    )
    
    # Publicar evento
    channel.basic_publish(
        exchange='code-grading',
        routing_key='submission.submissionCreated',
        body=json.dumps(event.dict()),
        properties=pika.BasicProperties(
            delivery_mode=2  # persistent
        )
    )
    
    connection.close()
```

#### 5.2 Consumir Evento

```python
import pika
import json
from datetime import datetime

def consume_execution_events():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='rabbitmq')
    )
    channel = connection.channel()
    
    # Declarar exchange y queue
    channel.exchange_declare(
        exchange='code-grading',
        exchange_type='topic',
        durable=True
    )
    
    channel.queue_declare(
        queue='execution.queue',
        durable=True
    )
    
    # Binding
    channel.queue_bind(
        exchange='code-grading',
        queue='execution.queue',
        routing_key='submission.*'
    )
    
    def callback(ch, method, properties, body):
        event = json.loads(body)
        
        if event['event_type'] == 'submission.submissionCreated':
            handle_submission_created(event)
        
        ch.basic_ack(delivery_tag=method.delivery_tag)
    
    channel.basic_consume(
        queue='execution.queue',
        on_message_callback=callback
    )
    
    print('Execution Service escuchando eventos...')
    channel.start_consuming()

def handle_submission_created(event):
    """Procesar nuevo envío - ejecutar tests"""
    submission_id = event['data']['submission_id']
    code_content = event['data']['code_content']
    language = event['data']['language']
    
    # Ejecutar código
    result = execute_code(code_content, language)
    
    # Guardar resultados
    save_execution_log(submission_id, result)
    
    # Publicar evento siguiente
    publish_event(ExecutionCompletedEvent(
        submission_id=submission_id,
        status='success',
        test_results=result
    ))
```

---

### 6. Garantías de Entrega

#### 6.1 At-Least-Once Delivery

```python
# Configurar ACK manual
channel.basic_consume(queue='queue', on_message_callback=callback)

def callback(ch, method, properties, body):
    try:
        process_message(body)
        ch.basic_ack(delivery_tag=method.delivery_tag)  # Confirmar
    except Exception as e:
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)  # Reintento
```

#### 6.2 Dead Letter Queue (para errores)

```python
# Declarar DLQ
channel.exchange_declare(
    exchange='dlx',
    exchange_type='direct'
)

channel.queue_declare(
    queue='dead-letter-queue',
    durable=True
)

# Configurar queue con DLX
channel.queue_declare(
    queue='submission.queue',
    durable=True,
    arguments={
        'x-dead-letter-exchange': 'dlx',
        'x-dead-letter-routing-key': 'dead-letter',
        'x-message-ttl': 86400000  # 24 horas
    }
)
```

---

### 7. Monitoreo de Eventos

#### 7.1 RabbitMQ Management UI

Acceder a: `http://localhost:15672`

Ver:
- Cantidad de eventos publicados/consumidos
- Queues pendientes
- Tasa de consumo
- Conexiones activas

#### 7.2 Logging de Eventos

```python
import logging

logger = logging.getLogger(__name__)

def handle_submission_created(event):
    logger.info(f"Procesando envío: {event['data']['submission_id']}")
    
    try:
        result = execute_code(...)
        logger.info(f"Envío procesado exitosamente: {event['data']['submission_id']}")
    except Exception as e:
        logger.error(f"Error procesando envío: {e}")
```

---

### 8. Resiliencia y Recuperación

#### 8.1 Reintentos

```python
import time

def retry_publish_event(event, max_retries=3):
    for attempt in range(max_retries):
        try:
            publish_event(event)
            return True
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                logger.error(f"Falló envío después de {max_retries} intentos")
                raise
```

#### 8.2 Circuit Breaker

```python
from pybreaker import CircuitBreaker

cb = CircuitBreaker(
    fail_max=5,
    reset_timeout=60,
    listeners=[logger]
)

@cb
def publish_event_with_breaker(event):
    publish_event(event)
```

---

### 9. Ventajas de Event-Driven

✅ **Desacoplamiento**: Servicios no dependen directamente  
✅ **Escalabilidad**: Fácil agregar nuevos consumidores  
✅ **Resiliencia**: Un servicio caído no detiene otros  
✅ **Auditoría**: Registro completo de eventos  
✅ **Replayable**: Posibilidad de reenviar eventos  
✅ **Eventual Consistency**: Consistencia eventual en datos

---

### 10. Próximos Pasos

1. Implementar Circuit Breaker completo
2. Agregar Event Sourcing para auditoría completa
3. Implementar CQRS para reads separados
4. Agregar Saga pattern para transacciones distribuidas
5. Metricas con Prometheus de eventos

