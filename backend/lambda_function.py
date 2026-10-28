import json
import os
import uuid
from datetime import datetime
import boto3
from boto3.dynamodb.conditions import Key, Attr

# Inicializar DynamoDB
TABLE_NAME = os.environ.get("TABLE_NAME", "Contactos")
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization,X-Api-Key",
    "Access-Control-Allow-Methods": "OPTIONS,GET,POST,PUT,DELETE",
    "Content-Type": "application/json"
}

def build_response(status_code, body):
    """Genera una respuesta HTTP compatible con API Gateway."""
    return {
        "statusCode": status_code,
        "headers": CORS_HEADERS,
        "body": json.dumps(body, ensure_ascii=False)
    }

def lambda_handler(event, context):
    """
    Router CRUD completo compatible tanto con REST API como con HTTP API (v2).
    """
    print("Evento recibido:", json.dumps(event))

    # Identificar método HTTP y ruta (soporta formato v1 y v2 de API Gateway)
    http_method = event.get("httpMethod")
    if not http_method and "requestContext" in event:
        http_method = event["requestContext"].get("http", {}).get("method")

    # Manejar preflight CORS
    if http_method == "OPTIONS":
        return build_response(200, {"message": "OK"})

    path_params = event.get("pathParameters") or {}
    query_params = event.get("queryStringParameters") or {}
    contact_id = path_params.get("id")

    try:
        if http_method == "GET":
            if contact_id:
                # Obtener un contacto por ID
                res = table.get_item(Key={"id": contact_id})
                item = res.get("Item")
                if not item:
                    return build_response(404, {"error": "Contacto no encontrado"})
                return build_response(200, item)
            else:
                # Listar contactos con soporte de búsqueda
                search_query = query_params.get("q", "").strip().lower()
                response = table.scan()
                items = response.get("Items", [])

                if search_query:
                    items = [
                        item for item in items
                        if search_query in item.get("nombre", "").lower()
                        or search_query in item.get("email", "").lower()
                        or search_query in item.get("telefono", "").lower()
                        or search_query in item.get("empresa", "").lower()
                    ]

                # Ordenar por fecha de creación descendente
                items.sort(key=lambda x: x.get("created_at", ""), reverse=True)
                return build_response(200, {"total": len(items), "contacts": items})

        elif http_method == "POST":
            # Crear nuevo contacto
            body = json.loads(event.get("body", "{}"))
            if not body.get("nombre") or not body.get("telefono"):
                return build_response(400, {"error": "Nombre y teléfono son obligatorios"})

            new_id = str(uuid.uuid4())
            now = datetime.utcnow().isoformat()

            new_contact = {
                "id": new_id,
                "nombre": body["nombre"].strip(),
                "telefono": body["telefono"].strip(),
                "email": body.get("email", "").strip().lower(),
                "empresa": body.get("empresa", "").strip(),
                "categoria": body.get("categoria", "Personal"),  # Trabajo, Familia, VIP, etc.
                "favorito": bool(body.get("favorito", False)),
                "avatar_url": body.get("avatar_url", f"https://api.dicebear.com/7.x/bottts/svg?seed={new_id}"),
                "notas": body.get("notas", ""),
                "created_at": now,
                "updated_at": now
            }

            table.put_item(Item=new_contact)
            return build_response(201, {"message": "Contacto creado", "contact": new_contact})

        elif http_method == "PUT":
            # Actualizar contacto existente
            if not contact_id:
                return build_response(400, {"error": "Se requiere el ID en la ruta"})

            body = json.loads(event.get("body", "{}"))
            res = table.get_item(Key={"id": contact_id})
            existing_item = res.get("Item")

            if not existing_item:
                return build_response(404, {"error": "Contacto no encontrado"})

            now = datetime.utcnow().isoformat()
            updated_contact = {
                **existing_item,
                "nombre": body.get("nombre", existing_item.get("nombre")),
                "telefono": body.get("telefono", existing_item.get("telefono")),
                "email": body.get("email", existing_item.get("email")),
                "empresa": body.get("empresa", existing_item.get("empresa")),
                "categoria": body.get("categoria", existing_item.get("categoria")),
                "favorito": body.get("favorito", existing_item.get("favorito", False)),
                "notas": body.get("notas", existing_item.get("notas", "")),
                "updated_at": now
            }

            table.put_item(Item=updated_contact)
            return build_response(200, {"message": "Contacto actualizado", "contact": updated_contact})

        elif http_method == "DELETE":
            # Eliminar contacto
            if not contact_id:
                return build_response(400, {"error": "Se requiere el ID en la ruta"})

            table.delete_item(Key={"id": contact_id})
            return build_response(200, {"message": "Contacto eliminado correctamente", "id": contact_id})

        else:
            return build_response(405, {"error": f"Método {http_method} no permitido"})

    except Exception as e:
        print("Error en Lambda:", str(e))
        return build_response(500, {"error": "Error interno del servidor", "details": str(e)})
