from typing import Dict, List
from models.appointmentModel import AppointmentModel
from repositories.appointmentRepository import AppointmentRepository
from repositories.serviceRepository import ServiceRepository
from repositories.workerRepository import WorkerRepository
from repositories.personRepository import PersonRepository
from services.workerService import WorkerService

class AppointmentService:

    @staticmethod
    def create_appointment(client_id: str, worker_id: str, service_id: str,
                           date: str, start_time: str) -> Dict:
        try:
            service = ServiceRepository.find_by_id(service_id)
            if not service:
                return {"success": False, "message": "Servicio no encontrado"}
            worker = WorkerRepository.find_by_id(worker_id)
            if not worker or not worker.is_active:
                return {"success": False, "message": "Trabajadora no disponible"}

            # Calcular end_time
            from services.workerService import _time_to_minutes, _minutes_to_time
            start_mins = _time_to_minutes(start_time)
            end_mins   = start_mins + service.duration_minutes
            end_time   = _minutes_to_time(end_mins)

            # Verificar conflicto
            if AppointmentRepository.has_conflict(worker_id, date, start_time, end_time):
                return {"success": False, "message": "La trabajadora ya tiene una cita en ese horario"}

            appointment = AppointmentModel(
                client_id=client_id,
                worker_id=worker_id,
                service_id=service_id,
                date=date,
                start_time=start_time,
                end_time=end_time,
                total_price=service.price
            )
            appt_id = AppointmentRepository.create(appointment)
            return {"success": True, "message": "Cita creada exitosamente", "appointment_id": appt_id}
        except Exception as e:
            return {"success": False, "message": f"Error al crear cita: {e}"}

    @staticmethod
    def cancel_appointment(appointment_id: str, client_id: str) -> Dict:
        """Cancela una cita (solo el cliente propietario o admin)."""
        try:
            appt = AppointmentRepository.find_by_id(appointment_id)
            if not appt:
                return {"success": False, "message": "Cita no encontrada"}
            if appt.client_id != client_id:
                return {"success": False, "message": "No tienes permiso para cancelar esta cita"}
            if appt.status == "cancelada":
                return {"success": False, "message": "La cita ya está cancelada"}
            AppointmentRepository.update_status(appointment_id, "cancelada")
            return {"success": True, "message": "Cita cancelada. No se realizan devoluciones."}
        except Exception as e:
            return {"success": False, "message": f"Error al cancelar cita: {e}"}

    @staticmethod
    def complete_appointment(appointment_id: str) -> Dict:
        """Marca una cita como completada (trabajadora o admin)."""
        try:
            appt = AppointmentRepository.find_by_id(appointment_id)
            if not appt:
                return {"success": False, "message": "Cita no encontrada"}
            AppointmentRepository.update_status(appointment_id, "completada")
            return {"success": True, "message": "Cita marcada como completada"}
        except Exception as e:
            return {"success": False, "message": f"Error al completar cita: {e}"}

    @staticmethod
    def get_client_appointments(client_id: str) -> Dict:
        try:
            appointments = AppointmentRepository.find_by_client(client_id)
            result = []
            for a in appointments:
                service = ServiceRepository.find_by_id(a.service_id)
                worker  = WorkerRepository.find_by_id(a.worker_id)
                worker_person = PersonRepository.find_by_user_id(worker.user_id) if worker else None
                result.append({
                    "appointment_id": a.id,
                    "date":           a.date,
                    "start_time":     a.start_time,
                    "end_time":       a.end_time,
                    "service_name":   service.name if service else "N/A",
                    "service_category": service.category if service else "N/A",
                    "worker_name":    f"{worker_person.first_name} {worker_person.last_name}" if worker_person else "N/A",
                    "total_price":    a.total_price,
                    "status":         a.status,
                    "notes":          a.notes
                })
            return {"success": True, "appointments": result}
        except Exception as e:
            return {"success": False, "appointments": [], "message": f"Error: {e}"}

    @staticmethod
    def get_all_appointments() -> Dict:
        """Para el administrador."""
        try:
            appointments = AppointmentRepository.find_all()
            result = []
            for a in appointments:
                service = ServiceRepository.find_by_id(a.service_id)
                worker  = WorkerRepository.find_by_id(a.worker_id)
                worker_person = PersonRepository.find_by_user_id(worker.user_id) if worker else None
                client_person = PersonRepository.find_by_user_id(a.client_id)
                result.append({
                    "appointment_id": a.id,
                    "date":           a.date,
                    "start_time":     a.start_time,
                    "end_time":       a.end_time,
                    "service_name":   service.name if service else "N/A",
                    "client_name":    f"{client_person.first_name} {client_person.last_name}" if client_person else "N/A",
                    "worker_name":    f"{worker_person.first_name} {worker_person.last_name}" if worker_person else "N/A",
                    "total_price":    a.total_price,
                    "status":         a.status
                })
            return {"success": True, "appointments": result}
        except Exception as e:
            return {"success": False, "appointments": [], "message": f"Error: {e}"}
