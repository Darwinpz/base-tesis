from typing import Dict, List
from models.serviceModel import ServiceModel
from repositories.serviceRepository import ServiceRepository
import os
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

def _allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

class ServiceService:

    @staticmethod
    def create_service(name: str, description: str, category: str,
                       price: str, duration_minutes: str,
                       image_file=None, upload_folder: str = None) -> Dict:
        errors = []
        if not name or len(name.strip()) < 2:
            errors.append("El nombre del servicio debe tener al menos 2 caracteres")
        if not category:
            errors.append("La categoría es obligatoria")
        try:
            p = float(price)
            if p <= 0:
                errors.append("El precio debe ser mayor a 0")
        except (TypeError, ValueError):
            errors.append("El precio debe ser un número válido")
        try:
            d = int(duration_minutes)
            if d <= 0:
                errors.append("La duración debe ser mayor a 0 minutos")
        except (TypeError, ValueError):
            errors.append("La duración debe ser un número entero válido")

        if errors:
            return {"success": False, "message": ", ".join(errors)}

        image_url = None
        if image_file and image_file.filename:
            if not _allowed_file(image_file.filename):
                return {"success": False, "message": "Formato de imagen no permitido (jpg, png, webp)"}
            filename = secure_filename(image_file.filename)
            # Guardamos con un nombre único
            import uuid
            ext = filename.rsplit(".", 1)[1].lower()
            unique_name = f"{uuid.uuid4().hex}.{ext}"
            if upload_folder:
                image_file.save(os.path.join(upload_folder, unique_name))
            image_url = f"/img/services/{unique_name}"

        try:
            service = ServiceModel(
                name=name.strip(),
                description=description.strip() if description else "",
                category=category.strip(),
                price=float(price),
                duration_minutes=int(duration_minutes),
                image_url=image_url
            )
            service_id = ServiceRepository.create(service)
            return {"success": True, "message": "Servicio creado exitosamente", "service_id": service_id}
        except Exception as e:
            return {"success": False, "message": f"Error al crear servicio: {e}"}

    @staticmethod
    def update_service(service_id: str, name: str, description: str, category: str,
                       price: str, duration_minutes: str, is_active: bool,
                       image_file=None, upload_folder: str = None) -> Dict:
        try:
            service = ServiceRepository.find_by_id(service_id)
            if not service:
                return {"success": False, "message": "Servicio no encontrado"}

            data = {
                "name": name.strip(),
                "description": description.strip() if description else "",
                "category": category.strip(),
                "price": float(price),
                "duration_minutes": int(duration_minutes),
                "is_active": is_active
            }

            if image_file and image_file.filename:
                if not _allowed_file(image_file.filename):
                    return {"success": False, "message": "Formato de imagen no permitido"}
                import uuid
                filename = secure_filename(image_file.filename)
                ext = filename.rsplit(".", 1)[1].lower()
                unique_name = f"{uuid.uuid4().hex}.{ext}"
                if upload_folder:
                    image_file.save(os.path.join(upload_folder, unique_name))
                data["image_url"] = f"/img/services/{unique_name}"

            ServiceRepository.update(service_id, data)
            return {"success": True, "message": "Servicio actualizado exitosamente"}
        except Exception as e:
            return {"success": False, "message": f"Error al actualizar servicio: {e}"}

    @staticmethod
    def delete_service(service_id: str) -> Dict:
        try:
            ServiceRepository.delete_by_id(service_id)
            return {"success": True, "message": "Servicio eliminado exitosamente"}
        except Exception as e:
            return {"success": False, "message": f"Error al eliminar servicio: {e}"}

    @staticmethod
    def get_all_services(only_active=False) -> Dict:
        try:
            services = ServiceRepository.find_all(only_active=only_active)
            return {"success": True, "services": [s.__dict__ for s in services]}
        except Exception as e:
            return {"success": False, "message": f"Error al obtener servicios: {e}", "services": []}

    @staticmethod
    def get_service_by_id(service_id: str) -> Dict:
        try:
            service = ServiceRepository.find_by_id(service_id)
            if not service:
                return {"success": False, "message": "Servicio no encontrado"}
            return {"success": True, "service": service.__dict__}
        except Exception as e:
            return {"success": False, "message": f"Error al obtener servicio: {e}"}

    @staticmethod
    def get_categories() -> List[str]:
        try:
            return ServiceRepository.get_categories()
        except Exception:
            return []
