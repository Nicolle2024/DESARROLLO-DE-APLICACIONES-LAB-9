import reflex as rx

class EstadoKanban(rx.State):
    tareas: list[dict[str, str]] = [
        {"id": "1", "titulo": "Diseñar interfaz", "descripcion": "Crear prototipo UI inicial", "estado": "Pendiente"},
        {"id": "2", "titulo": "Configurar BD", "descripcion": "Definir esquemas en PostgreSQL", "estado": "Completada"},
        {"id": "3", "titulo": "Implementar API", "descripcion": "Endpoints con FastAPI", "estado": "En progreso"},
        {"id": "4", "titulo": "Pruebas unitarias", "descripcion": "Validar componentes del sistema", "estado": "Pendiente"},
        {"id": "5", "titulo": "Desplegar app", "descripcion": "Docker y servidor de pruebas", "estado": "Pendiente"},
        {"id": "6", "titulo": "Documentación", "descripcion": "Redactar manual técnico", "estado": "Completada"},
    ]
    
    mostrar_solo_pendientes: bool = False

    @rx.event
    def toggle_filtro(self):
        self.mostrar_solo_pendientes = not self.mostrar_solo_pendientes

    @rx.event
    def cambiar_estado(self, tarea_id: str):
        for tarea in self.tareas:
            if tarea["id"] == tarea_id:
                if tarea["estado"] == "Pendiente":
                    tarea["estado"] = "En progreso"
                elif tarea["estado"] == "En progreso":
                    tarea["estado"] = "Completada"
                else:
                    tarea["estado"] = "Pendiente"
                break

    @rx.var
    def tareas_visibles(self) -> list[dict[str, str]]:
        if self.mostrar_solo_pendientes:
            return [
                tarea for tarea in self.tareas
                if tarea["estado"] == "Pendiente"
            ]
        return self.tareas
def tarjeta_tarea(tarea: dict[str, str]) -> rx.Component:
    return rx.box(
        rx.heading(tarea["titulo"], size="4"),
        rx.text(tarea["descripcion"]),
        rx.text(f"Estado: {tarea['estado']}", font_weight="bold", color="blue"),
        rx.button(
            "Cambiar Estado", 
            on_click=lambda: EstadoKanban.cambiar_estado(tarea["id"]),
            size="2",  
            margin_top="8px"
        ),
        padding="15px",
        border="1px solid #cccccc",
        border_radius="8px",
        margin_bottom="10px",
        background_color="#ffffff",
    )
def index() -> rx.Component:
    return rx.vstack(
        rx.heading("Tablero Kanban de Tareas", size="7"),
        
        rx.button(
            rx.cond(
                EstadoKanban.mostrar_solo_pendientes,
                "Mostrar Todas las Tareas",
                "Filtrar Solo Pendientes"
            ),
            on_click=EstadoKanban.toggle_filtro,
        ),
        
        rx.divider(),
        
        rx.cond(
            EstadoKanban.tareas_visibles.length() > 0,
            rx.foreach(
                EstadoKanban.tareas_visibles,
                tarjeta_tarea
            ),
            rx.text("No existen tareas que cumplan con el filtro seleccionado.", color="gray", font_style="italic"),
        ),
        
        spacing="4",
        padding="30px",
        max_width="600px",
        margin="0 auto",
    )

app = rx.App()
app.add_page(index)