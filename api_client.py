"""
Cliente HTTP para interactuar con la API de demo-gestion-horas
Usa el token JWT del usuario ya logueado
"""
import requests
import os


class DemoApiClient:
    def __init__(self, base_url=None):
        self.base_url = base_url or os.getenv("DEMO_API_URL", "http://localhost:8000")
        self.token = None
    
    def set_token(self, token):
        """
        Establece el token JWT del usuario
        
        Args:
            token: Token JWT del localStorage del frontend
        """
        self.token = token
        print(f"✅ Token establecido")
    
    def consultar_semana(self, fecha):
        """
        Consulta las horas de una semana específica
        
        Args:
            fecha: datetime object del lunes de la semana
            
        Returns:
            dict: Datos de la semana o None si falla
        """
        if not self.token:
            print("❌ No hay token")
            return None
        
        try:
            fecha_str = fecha.strftime("%Y-%m-%d")
            
            response = requests.get(
                f"{self.base_url}/api/imputaciones/semana/{fecha_str}",
                headers={"Authorization": f"Bearer {self.token}"}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Error consultando semana: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error consultando semana: {e}")
            return None
    
    def imputar_horas(self, project_id, fecha, horas):
        """
        Imputa horas en un proyecto para una fecha específica
        
        Args:
            project_id: ID del proyecto
            fecha: datetime object
            horas: cantidad de horas (float)
            
        Returns:
            bool: True si éxito, False si falla
        """
        if not self.token:
            print("❌ No hay token")
            return False
        
        try:
            fecha_str = fecha.strftime("%Y-%m-%d")
            
            response = requests.post(
                f"{self.base_url}/api/imputaciones",
                headers={"Authorization": f"Bearer {self.token}"},
                json={
                    "project_id": project_id,
                    "fecha": fecha_str,
                    "horas": horas
                }
            )
            
            if response.status_code == 200:
                return True
            else:
                print(f"❌ Error imputando horas: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error imputando horas: {e}")
            return False
    
    def obtener_proyectos(self):
        """
        Obtiene la lista de proyectos del usuario
        
        Returns:
            list: Lista de proyectos o None si falla
        """
        if not self.token:
            print("❌ No hay token")
            return None
        
        try:
            response = requests.get(
                f"{self.base_url}/api/projects",
                headers={"Authorization": f"Bearer {self.token}"}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Error obteniendo proyectos: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error obteniendo proyectos: {e}")
            return None
