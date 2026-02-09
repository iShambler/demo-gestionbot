"""
Ejecutor de comandos interpretados
Coordina las llamadas a la API según el comando
"""
from datetime import datetime, timedelta
from api_client import DemoApiClient


def obtener_lunes(fecha=None):
    """Obtiene el lunes de la semana de una fecha"""
    if fecha is None:
        fecha = datetime.now()
    elif isinstance(fecha, str):
        fecha = datetime.fromisoformat(fecha)
    
    dias_desde_lunes = fecha.weekday()
    lunes = fecha - timedelta(days=dias_desde_lunes)
    return lunes


def dias_a_fechas(dias, fecha_base=None):
    """
    Convierte nombres de días a fechas concretas
    
    Args:
        dias: Lista de nombres ["lunes", "martes", ...]
        fecha_base: Fecha de referencia
        
    Returns:
        list: Lista de objetos datetime
    """
    if fecha_base is None:
        fecha_base = datetime.now()
    
    lunes = obtener_lunes(fecha_base)
    
    mapa_dias = {
        "lunes": 0,
        "martes": 1,
        "miercoles": 2,
        "jueves": 3,
        "viernes": 4
    }
    
    fechas = []
    for dia in dias:
        dia_lower = dia.lower()
        if dia_lower in mapa_dias:
            offset = mapa_dias[dia_lower]
            fecha = lunes + timedelta(days=offset)
            fechas.append(fecha)
    
    return fechas


def ejecutar_listar_proyectos(api_client):
    """Lista todos los proyectos del usuario"""
    proyectos = api_client.obtener_proyectos()
    
    if not proyectos:
        return "📋 No tienes proyectos creados aún.\n\nPuedes crear uno haciendo clic en el botón 'CREAR PROYECTO' en la tabla."
    
    respuesta = f"📋 **Tus proyectos ({len(proyectos)})**\n\n"
    
    for i, proyecto in enumerate(proyectos, 1):
        nombre = proyecto.get("nombre", "Sin nombre")
        respuesta += f"{i}. {nombre}\n"
    
    respuesta += "\n💡 Puedes imputar horas diciendo: 'Pon 8h en [nombre del proyecto]'"
    
    return respuesta


def ejecutar_consulta_semana(api_client, fecha):
    """Ejecuta una consulta semanal"""
    lunes = obtener_lunes(fecha)
    data = api_client.consultar_semana(lunes)
    
    if not data:
        return "❌ No he podido consultar la semana."
    
    proyectos = data.get("proyectos", [])
    
    if not proyectos:
        return f"📅 Semana del {lunes.strftime('%d/%m/%Y')}: No tienes horas imputadas."
    
    respuesta = f"📅 **Semana del {lunes.strftime('%d/%m/%Y')}**\n\n"
    total_semana = 0
    
    for proyecto in proyectos:
        nombre = proyecto.get("nombre", "Sin nombre")
        horas = proyecto.get("horas", {})
        total_proyecto = sum(horas.values())
        total_semana += total_proyecto
        
        respuesta += f"**{nombre}**: {total_proyecto}h\n"
        
        dias_con_horas = []
        for fecha_str, h in horas.items():
            if h > 0:
                fecha_obj = datetime.fromisoformat(fecha_str)
                dia_nombre = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"][fecha_obj.weekday()]
                dias_con_horas.append(f"{dia_nombre}: {h}h")
        
        if dias_con_horas:
            respuesta += "  " + ", ".join(dias_con_horas) + "\n"
        respuesta += "\n"
    
    respuesta += f"**TOTAL**: {total_semana}h"
    return respuesta


def ejecutar_imputacion(api_client, imputaciones):
    """Ejecuta una o varias imputaciones"""
    proyectos = api_client.obtener_proyectos()
    
    if not proyectos:
        return "❌ No tienes proyectos creados."
    
    mapa_proyectos = {}
    for p in proyectos:
        nombre_normalizado = p["nombre"].lower().strip()
        mapa_proyectos[nombre_normalizado] = p["id"]
    
    resultados = []
    errores = []
    
    for imp in imputaciones:
        nombre_proyecto = imp["proyecto"]
        horas = imp["horas"]
        dias = imp["dias"]
        
        nombre_normalizado = nombre_proyecto.lower().strip()
        project_id = mapa_proyectos.get(nombre_normalizado)
        
        if not project_id:
            errores.append(f"❌ Proyecto '{nombre_proyecto}' no encontrado")
            continue
        
        fechas = dias_a_fechas(dias)
        
        if not fechas:
            errores.append(f"❌ No se pudieron procesar los días")
            continue
        
        exitos = 0
        for fecha in fechas:
            if api_client.imputar_horas(project_id, fecha, horas):
                exitos += 1
        
        if exitos > 0:
            dias_texto = ", ".join(dias)
            resultados.append(f"✅ {nombre_proyecto}: {horas}h × {exitos} días ({dias_texto})")
    
    respuesta = ""
    if resultados:
        respuesta += "\n".join(resultados)
    if errores:
        if respuesta:
            respuesta += "\n\n"
        respuesta += "\n".join(errores)
    
    return respuesta if respuesta else "❌ No se pudo realizar ninguna imputación"


def ejecutar_comando(api_client, comando):
    """Ejecuta un comando interpretado"""
    tipo = comando.get("tipo")
    
    if tipo == "conversacion":
        # Conversación sin comando, devolver respuesta directamente
        return comando.get("respuesta", "Hola, ¿en qué puedo ayudarte?")
    
    elif tipo == "listar_proyectos":
        return ejecutar_listar_proyectos(api_client)
    
    elif tipo == "consulta_semana":
        fecha = comando.get("fecha")
        return ejecutar_consulta_semana(api_client, fecha)
    
    elif tipo == "imputar":
        imputaciones = comando.get("imputaciones", [])
        return ejecutar_imputacion(api_client, imputaciones)
    
    else:
        return f"❌ Tipo de comando desconocido: {tipo}"
