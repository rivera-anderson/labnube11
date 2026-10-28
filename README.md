# ⚡ Nexus Contacts - AWS Serverless Edition

Una aplicación moderna, ultra rápida y de costo $0 en la capa gratuita de AWS para gestión de contactos.

---

## 🏗️ Arquitectura Serverless

```
[ Frontend: Tailwind + Glassmorphism ]
                 │
                 ▼ (HTTPS / REST)
       [ Amazon API Gateway ]
                 │
                 ▼
          [ AWS Lambda ]  (Python 3.12 / boto3)
                 │
                 ▼
       [ Amazon DynamoDB ] (On-Demand NoSQL)
```

- **DynamoDB:** Facturación On-Demand (paga $0 cuando no hay peticiones).
- **AWS Lambda:** Ejecución ARM64 ultra rápida con enrutador CRUD completo y CORS habilitado.
- **Amazon API Gateway:** HTTP API v2 de baja latencia.
- **Frontend:** Single Page Application (SPA) con Tailwind CSS, Lucide Icons, avatars automáticos y búsqueda en tiempo real.

---

## 🚀 Inicio Rápido (En 10 segundos)

### 1. Probar el Frontend de inmediato
No necesitas instalar nada ni configurar Node.js:
1. Abre el archivo `frontend/index.html` en tu navegador favorito (Chrome, Edge, Firefox, Brave).
2. ¡Listo! Viene en **Modo Demo Local** con datos precargados y persistencia en `localStorage`.

---

## ☁️ Despliegue en AWS (1 solo comando)

Si tienes instalado [AWS SAM CLI](https://aws.amazon.com/serverless/sam/):

```bash
cd infra
sam build
sam deploy --guided
```

Al terminar, SAM te imprimirá en consola un `ApiEndpoint` parecido a este:
```
https://a1b2c3d4.execute-api.us-east-1.amazonaws.com
```

### Conectar tu Frontend con AWS:
1. Abre tu `index.html`.
2. Haz clic en la píldora superior **"Modo Demo Local"** o en el ícono de engranaje.
3. Pega la URL de tu `ApiEndpoint` y dale a **"Guardar y Conectar"**.
4. ¡A partir de ese momento tus contactos se guardan directamente en **DynamoDB**!

---

## 🛠️ Despliegue Manual desde la Consola de AWS

Si prefieres hacerlo a mano desde la consola web:

1. **DynamoDB:**
   - Crear tabla: `Contactos`
   - Clave de partición: `id` (String)
   - Capacidad: Bajo demanda (*On-Demand*)

2. **AWS Lambda:**
   - Crear función: `ContactsCrudFunction`
   - Runtime: `Python 3.12`
   - Copiar y pegar el código de `backend/lambda_function.py`.
   - En **Configuración > Permisos**, añadir permisos a la política de ejecución para DynamoDB (`AmazonDynamoDBFullAccess` o política de lectura/escritura en la tabla).

3. **API Gateway:**
   - Crear **HTTP API**.
   - Integración: AWS Lambda (`ContactsCrudFunction`).
   - Rutas:
     - `ANY /{proxy+}` o crear las rutas `/contacts` y `/contacts/{id}` para `GET`, `POST`, `PUT`, `DELETE`.
   - En **CORS**: Habilitar orígenes permitidos `*`, headers `*`, métodos `*`.
