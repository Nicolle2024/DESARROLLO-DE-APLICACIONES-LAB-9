import re
from typing import Any
import httpx
import reflex as rx

PALETA = {
    "fondo_app": "#FAF6F0",
    "fondo_panel": "#F3EDE2",
    "tarjeta": "#FFFDF9",
    "borde": "#E2D9C8",
    "texto_principal": "#3D352E",
    "texto_secundario": "#7A6F64",
    "acento_salvia": "#B8C9B9",
    "acento_salvia_texto": "#2C422E",
    "acento_terracota": "#E6B8A2",
    "acento_terracota_texto": "#5E301E",
    "acento_melocoton": "#F2D0A9",
    "acento_melocoton_texto": "#5C4018",
    "acento_lavanda": "#D8C8E0",
    "acento_lavanda_texto": "#432F4D",
}


class EstadoApp(rx.State):
    vista_activa: str = "ej1"
    mostrar_solo_pendientes: bool = False

    tareas: list[dict[str, str]] = [
        {
            "id": "ENC-01",
            "titulo": "Revelar rollos en blanco y negro",
            "descripcion": "Preparar los químicos en el cuarto oscuro para las fotos de arquitectura.",
            "estado": "Pendiente",
        },
        {
            "id": "ENC-02",
            "titulo": "Calibrar tostadora de café",
            "descripcion": "Ajustar la curva de temperatura para el lote nuevo de granos de Villa Rica.",
            "estado": "En progreso",
        },
        {
            "id": "ENC-03",
            "titulo": "Armar teclado mecánico a medida",
            "descripcion": "Lubricar los switches táctiles y soldar la placa antes de entregarlo.",
            "estado": "Pendiente",
        },
        {
            "id": "ENC-04",
            "titulo": "Restaurar tornamesa de los 80",
            "descripcion": "Cambiar la correa del motor y calibrar el peso de la aguja nueva.",
            "estado": "Completada",
        },
        {
            "id": "ENC-05",
            "titulo": "Automatizar riego de bonsáis",
            "descripcion": "Conectar los sensores de humedad de suelo al microcontrolador del balcón.",
            "estado": "En progreso",
        },
        {
            "id": "ENC-06",
            "titulo": "Digitalizar cintas de casete antiguas",
            "descripcion": "Pasar las grabaciones familiares a formato sin pérdida y limpiar el ruido.",
            "estado": "Completada",
        },
    ]

    solicitudes: list[dict[str, str]] = [
        {
            "id": "SOL-101",
            "nombre": "Mateo Santillán",
            "correo": "mateo.audio@estudio-sur.pe",
            "tipo": "Requerimiento",
            "descripcion": "Necesito un par de cables balanceados de 3 metros para conectar los monitores del estudio.",
        },
        {
            "id": "SOL-102",
            "nombre": "Valeria Lozada",
            "correo": "valeria@cafe-origen.com",
            "tipo": "Incidencia",
            "descripcion": "El molino principal está dejando el grano demasiado grueso para espresso desde esta mañana.",
        },
    ]
    contador_solicitudes: int = 103
    mensaje_solicitud: str = ""
    error_solicitud: bool = False

    usuarios: list[dict[str, str]] = []
    cargando_usuarios: bool = False
    error_usuarios: str = ""
    busqueda_usuario: str = ""

    @rx.event
    def cambiar_vista(self, nueva_vista: str):
        self.vista_activa = nueva_vista

    @rx.event
    def alternar_filtro(self):
        self.mostrar_solo_pendientes = not self.mostrar_solo_pendientes

    @rx.event
    def cambiar_estado_tarea(self, id_tarea: str, nuevo_estado: str):
        nuevas = []
        for t in self.tareas:
            if t["id"] == id_tarea:
                copia = dict(t)
                copia["estado"] = nuevo_estado
                nuevas.append(copia)
            else:
                nuevas.append(t)
        self.tareas = nuevas

    @rx.event
    def vaciar_o_restaurar_tareas(self):
        if len(self.tareas) > 0:
            self.tareas = []
        else:
            self.tareas = [
                {
                    "id": "ENC-01",
                    "titulo": "Revelar rollos en blanco y negro",
                    "descripcion": "Preparar los químicos en el cuarto oscuro para las fotos de arquitectura.",
                    "estado": "Pendiente",
                },
                {
                    "id": "ENC-02",
                    "titulo": "Calibrar tostadora de café",
                    "descripcion": "Ajustar la curva de temperatura para el lote nuevo de granos de Villa Rica.",
                    "estado": "En progreso",
                },
                {
                    "id": "ENC-03",
                    "titulo": "Armar teclado mecánico a medida",
                    "descripcion": "Lubricar los switches táctiles y soldar la placa antes de entregarlo.",
                    "estado": "Pendiente",
                },
                {
                    "id": "ENC-04",
                    "titulo": "Restaurar tornamesa de los 80",
                    "descripcion": "Cambiar la correa del motor y calibrar el peso de la aguja nueva.",
                    "estado": "Completada",
                },
                {
                    "id": "ENC-05",
                    "titulo": "Automatizar riego de bonsáis",
                    "descripcion": "Conectar los sensores de humedad de suelo al microcontrolador del balcón.",
                    "estado": "En progreso",
                },
                {
                    "id": "ENC-06",
                    "titulo": "Digitalizar cintas de casete antiguas",
                    "descripcion": "Pasar las grabaciones familiares a formato sin pérdida y limpiar el ruido.",
                    "estado": "Completada",
                },
            ]

    @rx.var
    def tareas_visibles(self) -> list[dict[str, str]]:
        if self.mostrar_solo_pendientes:
            return [t for t in self.tareas if t["estado"] == "Pendiente"]
        return self.tareas

    @rx.var
    def tareas_pendientes_lista(self) -> list[dict[str, str]]:
        return [t for t in self.tareas_visibles if t["estado"] == "Pendiente"]

    @rx.var
    def tareas_progreso_lista(self) -> list[dict[str, str]]:
        return [t for t in self.tareas_visibles if t["estado"] == "En progreso"]

    @rx.var
    def tareas_completadas_lista(self) -> list[dict[str, str]]:
        return [t for t in self.tareas_visibles if t["estado"] == "Completada"]

    @rx.var
    def total_tareas(self) -> int:
        return len(self.tareas)

    @rx.var
    def total_pendientes(self) -> int:
        return sum(1 for t in self.tareas if t["estado"] == "Pendiente")

    @rx.var
    def total_en_progreso(self) -> int:
        return sum(1 for t in self.tareas if t["estado"] == "En progreso")

    @rx.var
    def total_completadas(self) -> int:
        return sum(1 for t in self.tareas if t["estado"] == "Completada")

    @rx.var
    def porcentaje_completadas(self) -> str:
        total = len(self.tareas)
        if total == 0:
            return "0.0%"
        completadas = sum(1 for t in self.tareas if t["estado"] == "Completada")
        return f"{round((completadas / total) * 100, 1)}%"

    @rx.event
    def registrar_solicitud(self, datos: dict[str, Any]):
        nombre = str(datos.get("nombre", "")).strip()
        correo = str(datos.get("correo", "")).strip()
        tipo = str(datos.get("tipo", "")).strip()
        descripcion = str(datos.get("descripcion", "")).strip()

        if not nombre or not correo or not tipo or not descripcion:
            self.mensaje_solicitud = "Por favor, completa todos los campos antes de guardar la solicitud."
            self.error_solicitud = True
            return

        if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", correo):
            self.mensaje_solicitud = "El correo ingresado no parece válido. Revisa que esté bien escrito."
            self.error_solicitud = True
            return

        if len(descripcion) < 10:
            self.mensaje_solicitud = "Cuéntanos un poco más: la descripción debe tener al menos 10 caracteres."
            self.error_solicitud = True
            return

        nueva = {
            "id": f"SOL-{self.contador_solicitudes}",
            "nombre": nombre,
            "correo": correo,
            "tipo": tipo,
            "descripcion": descripcion,
        }
        self.contador_solicitudes += 1
        self.solicitudes.insert(0, nueva)
        self.error_solicitud = False
        self.mensaje_solicitud = f"¡Listo, {nombre}! Tu solicitud ya quedó anotada."

    @rx.event
    def eliminar_solicitud(self, id_sol: str):
        self.solicitudes = [s for s in self.solicitudes if s["id"] != id_sol]

    @rx.event
    def actualizar_busqueda(self, valor: str):
        self.busqueda_usuario = valor

    @rx.event
    async def cargar_usuarios_api(self):
        self.cargando_usuarios = True
        self.error_usuarios = ""
        try:
            async with httpx.AsyncClient() as cliente:
                respuesta = await cliente.get("https://jsonplaceholder.typicode.com/users", timeout=10.0)
                respuesta.raise_for_status()
                datos = respuesta.json()
                self.usuarios = [
                    {
                        "nombre": str(u.get("name", "Sin nombre")),
                        "username": str(u.get("username", "sin_usuario")),
                        "email": str(u.get("email", "Sin correo")),
                        "ciudad": str(u.get("address", {}).get("city", "Sin ciudad")),
                        "empresa": str(u.get("company", {}).get("name", "Independiente")),
                    }
                    for u in datos
                ]
        except Exception as e:
            self.error_usuarios = f"No se pudo conectar con el servidor en este momento ({str(e)})."
        finally:
            self.cargando_usuarios = False

    @rx.var
    def usuarios_filtrados(self) -> list[dict[str, str]]:
        termino = self.busqueda_usuario.strip().lower()
        if not termino:
            return self.usuarios
        return [
            u for u in self.usuarios
            if u["nombre"].lower().find(termino) != -1
        ]


def boton_pestana(id_vista: str, texto: str, color_activo: str, texto_activo: str) -> rx.Component:
    activo = EstadoApp.vista_activa == id_vista
    return rx.button(
        texto,
        on_click=EstadoApp.cambiar_vista(id_vista),
        background_color=rx.cond(activo, color_activo, PALETA["fondo_panel"]),
        color=rx.cond(activo, texto_activo, PALETA["texto_secundario"]),
        border=f"1px solid {PALETA['borde']}",
        border_radius="10px",
        padding_x="1.1rem",
        padding_y="0.65rem",
        font_weight="bold",
        cursor="pointer",
    )


def barra_navegacion() -> rx.Component:
    return rx.hstack(
        boton_pestana("ej1", "1. Tablero de Encargos", PALETA["acento_terracota"], PALETA["acento_terracota_texto"]),
        boton_pestana("ej2", "2. Panel de Avance", PALETA["acento_salvia"], PALETA["acento_salvia_texto"]),
        boton_pestana("ej3", "3. Registro de Solicitudes", PALETA["acento_melocoton"], PALETA["acento_melocoton_texto"]),
        boton_pestana("ej4", "4. Directorio de Contactos", PALETA["acento_lavanda"], PALETA["acento_lavanda_texto"]),
        spacing="3",
        justify="center",
        wrap="wrap",
        width="100%",
        padding_y="0.5rem",
    )


def tarjeta_kanban(tarea: dict[str, str]) -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.text(tarea["id"], font_size="0.75rem", font_weight="bold", color=PALETA["texto_secundario"]),
                rx.spacer(),
                rx.box(
                    rx.text(
                        tarea["estado"],
                        font_size="0.75rem",
                        font_weight="bold",
                        color=rx.cond(
                            tarea["estado"] == "Pendiente",
                            PALETA["acento_terracota_texto"],
                            rx.cond(
                                tarea["estado"] == "En progreso",
                                PALETA["acento_melocoton_texto"],
                                PALETA["acento_salvia_texto"],
                            ),
                        ),
                    ),
                    background_color=rx.cond(
                        tarea["estado"] == "Pendiente",
                        PALETA["acento_terracota"],
                        rx.cond(
                            tarea["estado"] == "En progreso",
                            PALETA["acento_melocoton"],
                            PALETA["acento_salvia"],
                        ),
                    ),
                    padding="0.15rem 0.6rem",
                    border_radius="999px",
                ),
                width="100%",
                align="center",
            ),
            rx.heading(tarea["titulo"], size="3", color=PALETA["texto_principal"]),
            rx.text(tarea["descripcion"], font_size="0.85rem", color=PALETA["texto_secundario"]),
            rx.divider(border_color=PALETA["borde"]),
            rx.hstack(
                rx.button(
                    "Pendiente",
                    on_click=EstadoApp.cambiar_estado_tarea(tarea["id"], "Pendiente"),
                    size="1",
                    background_color=PALETA["acento_terracota"],
                    color=PALETA["acento_terracota_texto"],
                    cursor="pointer",
                ),
                rx.button(
                    "En progreso",
                    on_click=EstadoApp.cambiar_estado_tarea(tarea["id"], "En progreso"),
                    size="1",
                    background_color=PALETA["acento_melocoton"],
                    color=PALETA["acento_melocoton_texto"],
                    cursor="pointer",
                ),
                rx.button(
                    "Completada",
                    on_click=EstadoApp.cambiar_estado_tarea(tarea["id"], "Completada"),
                    size="1",
                    background_color=PALETA["acento_salvia"],
                    color=PALETA["acento_salvia_texto"],
                    cursor="pointer",
                ),
                spacing="2",
                width="100%",
                justify="end",
            ),
            spacing="2",
            align="start",
            width="100%",
        ),
        padding="1rem",
        background_color=PALETA["tarjeta"],
        border=f"1px solid {PALETA['borde']}",
        border_radius="12px",
        box_shadow="0 2px 5px rgba(61, 53, 46, 0.04)",
        width="100%",
    )


def columna_estado(titulo: str, color_cabecera: str, color_texto: str, lista_tareas: list[dict[str, str]]) -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.box(
                rx.heading(titulo, size="4", color=color_texto),
                background_color=color_cabecera,
                padding="0.6rem 1rem",
                border_radius="8px",
                width="100%",
            ),
            rx.cond(
                lista_tareas.length() == 0,
                rx.box(
                    rx.text("No hay encargos en esta columna", font_size="0.85rem", color=PALETA["texto_secundario"]),
                    padding="1.5rem",
                    text_align="center",
                    width="100%",
                ),
                rx.vstack(
                    rx.foreach(lista_tareas, tarjeta_kanban),
                    spacing="3",
                    width="100%",
                ),
            ),
            spacing="3",
            width="100%",
        ),
        padding="1rem",
        background_color=PALETA["fondo_panel"],
        border=f"1px solid {PALETA['borde']}",
        border_radius="14px",
        width="100%",
    )


def vista_tablero_kanban() -> rx.Component:
    return rx.vstack(
        rx.box(
            rx.hstack(
                rx.vstack(
                    rx.heading("Encargos de la Semana", size="6", color=PALETA["texto_principal"]),
                    rx.cond(
                        EstadoApp.mostrar_solo_pendientes,
                        rx.text("Mostrando únicamente los encargos que están por empezar.", color=PALETA["acento_terracota_texto"], font_size="0.9rem", font_weight="medium"),
                        rx.text("Organiza y actualiza el estado de cada trabajo conforme avanza.", color=PALETA["texto_secundario"], font_size="0.9rem"),
                    ),
                    spacing="1",
                    align="start",
                ),
                rx.spacer(),
                rx.hstack(
                    rx.button(
                        rx.cond(EstadoApp.mostrar_solo_pendientes, "Ver todos los encargos", "Ver solo pendientes"),
                        on_click=EstadoApp.alternar_filtro,
                        background_color=rx.cond(EstadoApp.mostrar_solo_pendientes, PALETA["acento_terracota"], PALETA["acento_lavanda"]),
                        color=rx.cond(EstadoApp.mostrar_solo_pendientes, PALETA["acento_terracota_texto"], PALETA["acento_lavanda_texto"]),
                        border=f"1px solid {PALETA['borde']}",
                        cursor="pointer",
                    ),
                    rx.button(
                        rx.cond(EstadoApp.total_tareas > 0, "Vaciar lista", "Restaurar encargos"),
                        on_click=EstadoApp.vaciar_o_restaurar_tareas,
                        background_color=PALETA["tarjeta"],
                        color=PALETA["texto_principal"],
                        border=f"1px solid {PALETA['borde']}",
                        cursor="pointer",
                    ),
                    spacing="2",
                ),
                width="100%",
                align="center",
                wrap="wrap",
            ),
            padding="1.2rem",
            background_color=PALETA["fondo_panel"],
            border=f"1px solid {PALETA['borde']}",
            border_radius="12px",
            width="100%",
        ),
        rx.cond(
            EstadoApp.tareas_visibles.length() == 0,
            rx.box(
                rx.text(
                    "No hay encargos que coincidan con el filtro actual.",
                    font_weight="bold",
                    color=PALETA["acento_terracota_texto"],
                ),
                padding="2rem",
                background_color=PALETA["acento_terracota"],
                border_radius="12px",
                text_align="center",
                width="100%",
            ),
            rx.grid(
                columna_estado("Pendiente", PALETA["acento_terracota"], PALETA["acento_terracota_texto"], EstadoApp.tareas_pendientes_lista),
                columna_estado("En progreso", PALETA["acento_melocoton"], PALETA["acento_melocoton_texto"], EstadoApp.tareas_progreso_lista),
                columna_estado("Completada", PALETA["acento_salvia"], PALETA["acento_salvia_texto"], EstadoApp.tareas_completadas_lista),
                columns="3",
                spacing="4",
                width="100%",
            ),
        ),
        spacing="4",
        width="100%",
    )


def tarjeta_indicador(titulo: str, valor: rx.Var | str, subtexto: str, bg_color: str, text_color: str) -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.text(titulo, font_size="0.9rem", font_weight="bold", color=text_color),
            rx.heading(valor, size="8", color=text_color),
            rx.text(subtexto, font_size="0.8rem", color=text_color),
            spacing="2",
            align="start",
        ),
        padding="1.4rem",
        background_color=bg_color,
        border=f"1px solid {PALETA['borde']}",
        border_radius="14px",
        width="100%",
    )


def panel_indicadores() -> rx.Component:
    return rx.vstack(
        rx.box(
            rx.hstack(
                rx.vstack(
                    rx.heading("Resumen de Avance", size="6", color=PALETA["texto_principal"]),
                    rx.text("Un vistazo rápido a cómo van los encargos anotados en el tablero.", color=PALETA["texto_secundario"], font_size="0.9rem"),
                    spacing="1",
                    align="start",
                ),
                rx.spacer(),
                rx.button(
                    rx.cond(EstadoApp.total_tareas > 0, "Probar con lista vacía", "Restaurar encargos"),
                    on_click=EstadoApp.vaciar_o_restaurar_tareas,
                    background_color=PALETA["tarjeta"],
                    color=PALETA["texto_principal"],
                    border=f"1px solid {PALETA['borde']}",
                    cursor="pointer",
                ),
                width="100%",
                align="center",
            ),
            padding="1.2rem",
            background_color=PALETA["fondo_panel"],
            border=f"1px solid {PALETA['borde']}",
            border_radius="12px",
            width="100%",
        ),
        rx.grid(
            tarjeta_indicador("Total de encargos", EstadoApp.total_tareas.to_string(), "Anotados en el cuaderno", PALETA["acento_lavanda"], PALETA["acento_lavanda_texto"]),
            tarjeta_indicador("Pendientes", EstadoApp.total_pendientes.to_string(), "Por empezar", PALETA["acento_terracota"], PALETA["acento_terracota_texto"]),
            tarjeta_indicador("En progreso", EstadoApp.total_en_progreso.to_string(), "En los que se está trabajando hoy", PALETA["acento_melocoton"], PALETA["acento_melocoton_texto"]),
            tarjeta_indicador("Completados", EstadoApp.total_completadas.to_string(), "Terminados y entregados", PALETA["acento_salvia"], PALETA["acento_salvia_texto"]),
            columns="2",
            spacing="4",
            width="100%",
        ),
        rx.box(
            rx.hstack(
                rx.vstack(
                    rx.text("Porcentaje de encargos terminados", font_weight="bold", font_size="1.1rem", color=PALETA["acento_salvia_texto"]),
                    rx.text("Proporción de trabajos listos respecto al total registrado.", font_size="0.85rem", color=PALETA["texto_secundario"]),
                    align="start",
                    spacing="1",
                ),
                rx.spacer(),
                rx.heading(EstadoApp.porcentaje_completadas, size="9", color=PALETA["acento_salvia_texto"]),
                width="100%",
                align="center",
            ),
            padding="1.6rem",
            background_color=PALETA["tarjeta"],
            border=f"2px solid {PALETA['acento_salvia']}",
            border_radius="14px",
            width="100%",
        ),
        spacing="4",
        width="100%",
    )


def tarjeta_solicitud(item: dict[str, str]) -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.text(item["id"], font_size="0.75rem", font_weight="bold", color=PALETA["texto_secundario"]),
                rx.box(
                    rx.text(
                        item["tipo"],
                        font_size="0.75rem",
                        font_weight="bold",
                        color=rx.cond(
                            item["tipo"] == "Incidencia",
                            PALETA["acento_terracota_texto"],
                            rx.cond(item["tipo"] == "Requerimiento", PALETA["acento_melocoton_texto"], PALETA["acento_lavanda_texto"]),
                        ),
                    ),
                    background_color=rx.cond(
                        item["tipo"] == "Incidencia",
                        PALETA["acento_terracota"],
                        rx.cond(item["tipo"] == "Requerimiento", PALETA["acento_melocoton"], PALETA["acento_lavanda"]),
                    ),
                    padding="0.15rem 0.65rem",
                    border_radius="999px",
                ),
                rx.spacer(),
                rx.button(
                    "Eliminar",
                    on_click=EstadoApp.eliminar_solicitud(item["id"]),
                    size="1",
                    background_color=PALETA["fondo_panel"],
                    color=PALETA["acento_terracota_texto"],
                    cursor="pointer",
                ),
                width="100%",
                align="center",
            ),
            rx.heading(item["nombre"], size="3", color=PALETA["texto_principal"]),
            rx.text(item["correo"], font_size="0.8rem", color=PALETA["texto_secundario"]),
            rx.text(item["descripcion"], font_size="0.9rem", color=PALETA["texto_principal"]),
            spacing="2",
            align="start",
            width="100%",
        ),
        padding="1.1rem",
        background_color=PALETA["tarjeta"],
        border=f"1px solid {PALETA['borde']}",
        border_radius="12px",
        width="100%",
    )


def vista_registro_solicitudes() -> rx.Component:
    estilo_campo = {
        "background_color": PALETA["tarjeta"],
        "border": f"1px solid {PALETA['borde']}",
        "border_radius": "8px",
        "color": PALETA["texto_principal"],
        "width": "100%",
    }
    return rx.vstack(
        rx.box(
            rx.vstack(
                rx.heading("Registro de Solicitudes y Pedidos", size="6", color=PALETA["texto_principal"]),
                rx.text(
                    "Anota aquí consultas de clientes, pedidos de repuestos o cualquier problema técnico que haya surgido.",
                    color=PALETA["texto_secundario"],
                    font_size="0.9rem",
                ),
                spacing="1",
                align="start",
            ),
            padding="1.2rem",
            background_color=PALETA["fondo_panel"],
            border=f"1px solid {PALETA['borde']}",
            border_radius="12px",
            width="100%",
        ),
        rx.grid(
            rx.box(
                rx.vstack(
                    rx.heading("Nueva solicitud", size="4", color=PALETA["texto_principal"]),
                    rx.form(
                        rx.vstack(
                            rx.text("Nombre del solicitante", font_size="0.85rem", font_weight="bold"),
                            rx.input(name="nombre", placeholder="Ej. Camila Paredes", style=estilo_campo),
                            rx.text("Correo electrónico", font_size="0.85rem", font_weight="bold"),
                            rx.input(name="correo", placeholder="Ej. camila@estudio.pe", style=estilo_campo),
                            rx.text("Tipo de solicitud", font_size="0.85rem", font_weight="bold"),
                            rx.select(
                                ["Consulta", "Incidencia", "Requerimiento"],
                                name="tipo",
                                default_value="Consulta",
                                width="100%",
                            ),
                            rx.text("Descripción (mínimo 10 caracteres)", font_size="0.85rem", font_weight="bold"),
                            rx.text_area(
                                name="descripcion",
                                placeholder="Explica brevemente qué necesitas o qué inconveniente ocurrió...",
                                style=estilo_campo,
                            ),
                            rx.button(
                                "Guardar solicitud",
                                type="submit",
                                background_color=PALETA["acento_salvia"],
                                color=PALETA["acento_salvia_texto"],
                                font_weight="bold",
                                width="100%",
                                cursor="pointer",
                            ),
                            spacing="2",
                            align="start",
                            width="100%",
                        ),
                        on_submit=EstadoApp.registrar_solicitud,
                        reset_on_submit=True,
                        width="100%",
                    ),
                    rx.cond(
                        EstadoApp.mensaje_solicitud != "",
                        rx.box(
                            rx.text(
                                EstadoApp.mensaje_solicitud,
                                font_size="0.85rem",
                                font_weight="bold",
                                color=rx.cond(EstadoApp.error_solicitud, PALETA["acento_terracota_texto"], PALETA["acento_salvia_texto"]),
                            ),
                            padding="0.8rem",
                            background_color=rx.cond(EstadoApp.error_solicitud, PALETA["acento_terracota"], PALETA["acento_salvia"]),
                            border_radius="8px",
                            width="100%",
                        ),
                    ),
                    spacing="3",
                    align="start",
                    width="100%",
                ),
                padding="1.4rem",
                background_color=PALETA["fondo_panel"],
                border=f"1px solid {PALETA['borde']}",
                border_radius="14px",
                width="100%",
            ),
            rx.box(
                rx.vstack(
                    rx.heading("Solicitudes anotadas", size="4", color=PALETA["texto_principal"]),
                    rx.cond(
                        EstadoApp.solicitudes.length() == 0,
                        rx.box(
                            rx.text("No hay solicitudes registradas por el momento.", color=PALETA["texto_secundario"]),
                            padding="2rem",
                            text_align="center",
                            width="100%",
                        ),
                        rx.vstack(
                            rx.foreach(EstadoApp.solicitudes, tarjeta_solicitud),
                            spacing="3",
                            width="100%",
                        ),
                    ),
                    spacing="3",
                    align="start",
                    width="100%",
                ),
                padding="1.4rem",
                background_color=PALETA["fondo_panel"],
                border=f"1px solid {PALETA['borde']}",
                border_radius="14px",
                width="100%",
            ),
            columns="2",
            spacing="4",
            width="100%",
        ),
        spacing="4",
        width="100%",
    )


def tarjeta_directorio_usuario(u: dict[str, str]) -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.heading(u["nombre"], size="3", color=PALETA["texto_principal"]),
                rx.spacer(),
                rx.box(
                    rx.text(f"@{u['username']}", font_size="0.75rem", font_weight="bold", color=PALETA["acento_lavanda_texto"]),
                    background_color=PALETA["acento_lavanda"],
                    padding="0.1rem 0.55rem",
                    border_radius="999px",
                ),
                width="100%",
                align="center",
            ),
            rx.text(f"Correo: {u['email']}", font_size="0.85rem", color=PALETA["texto_secundario"]),
            rx.hstack(
                rx.box(
                    rx.text(f"Ciudad: {u['ciudad']}", font_size="0.75rem", color=PALETA["acento_melocoton_texto"]),
                    background_color=PALETA["acento_melocoton"],
                    padding="0.15rem 0.6rem",
                    border_radius="6px",
                ),
                rx.box(
                    rx.text(f"Empresa: {u['empresa']}", font_size="0.75rem", color=PALETA["acento_salvia_texto"]),
                    background_color=PALETA["acento_salvia"],
                    padding="0.15rem 0.6rem",
                    border_radius="6px",
                ),
                spacing="2",
                wrap="wrap",
            ),
            spacing="2",
            align="start",
            width="100%",
        ),
        padding="1.1rem",
        background_color=PALETA["tarjeta"],
        border=f"1px solid {PALETA['borde']}",
        border_radius="12px",
        width="100%",
    )


def vista_directorio_usuarios() -> rx.Component:
    return rx.vstack(
        rx.box(
            rx.hstack(
                rx.vstack(
                    rx.heading("Directorio de Contactos y Colaboradores", size="6", color=PALETA["texto_principal"]),
                    rx.text(
                        "Consulta la lista de contactos desde el servicio externo y filtra por nombre en tiempo real.",
                        color=PALETA["texto_secundario"],
                        font_size="0.9rem",
                    ),
                    spacing="1",
                    align="start",
                ),
                rx.spacer(),
                rx.button(
                    rx.cond(EstadoApp.usuarios.length() == 0, "Cargar contactos", "Actualizar lista"),
                    on_click=EstadoApp.cargar_usuarios_api,
                    loading=EstadoApp.cargando_usuarios,
                    background_color=PALETA["acento_lavanda"],
                    color=PALETA["acento_lavanda_texto"],
                    border=f"1px solid {PALETA['borde']}",
                    font_weight="bold",
                    cursor="pointer",
                ),
                width="100%",
                align="center",
                wrap="wrap",
            ),
            padding="1.2rem",
            background_color=PALETA["fondo_panel"],
            border=f"1px solid {PALETA['borde']}",
            border_radius="12px",
            width="100%",
        ),
        rx.box(
            rx.input(
                placeholder="Buscar contacto por nombre (no distingue mayúsculas ni minúsculas)...",
                value=EstadoApp.busqueda_usuario,
                on_change=EstadoApp.actualizar_busqueda,
                background_color=PALETA["tarjeta"],
                border=f"1px solid {PALETA['borde']}",
                border_radius="10px",
                color=PALETA["texto_principal"],
                width="100%",
            ),
            width="100%",
        ),
        rx.cond(
            EstadoApp.cargando_usuarios,
            rx.box(
                rx.hstack(
                    rx.spinner(size="3"),
                    rx.text("Descargando la lista de contactos, espera un momento...", color=PALETA["texto_secundario"]),
                    spacing="3",
                    justify="center",
                    align="center",
                ),
                padding="2rem",
                background_color=PALETA["fondo_panel"],
                border_radius="12px",
                width="100%",
            ),
        ),
        rx.cond(
            EstadoApp.error_usuarios != "",
            rx.box(
                rx.text(EstadoApp.error_usuarios, font_weight="bold", color=PALETA["acento_terracota_texto"]),
                padding="1.2rem",
                background_color=PALETA["acento_terracota"],
                border_radius="12px",
                width="100%",
            ),
        ),
        rx.cond(
            EstadoApp.usuarios.length() == 0,
            rx.cond(
                ~EstadoApp.cargando_usuarios,
                rx.box(
                    rx.text(
                        "Todavía no se han cargado los contactos. Pulsa el botón de arriba para consultarlos en la API.",
                        color=PALETA["texto_secundario"],
                    ),
                    padding="2.5rem",
                    background_color=PALETA["fondo_panel"],
                    border=f"1px dashed {PALETA['borde']}",
                    border_radius="12px",
                    text_align="center",
                    width="100%",
                ),
            ),
            rx.cond(
                EstadoApp.usuarios_filtrados.length() == 0,
                rx.box(
                    rx.text(
                        "No se encontró ningún contacto con ese nombre.",
                        font_weight="bold",
                        color=PALETA["acento_terracota_texto"],
                    ),
                    padding="2rem",
                    background_color=PALETA["acento_terracota"],
                    border_radius="12px",
                    text_align="center",
                    width="100%",
                ),
                rx.grid(
                    rx.foreach(EstadoApp.usuarios_filtrados, tarjeta_directorio_usuario),
                    columns="2",
                    spacing="3",
                    width="100%",
                ),
            ),
        ),
        spacing="4",
        width="100%",
    )


def index() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.vstack(
                rx.heading("Cuaderno de Encargos", size="7", color=PALETA["texto_principal"]),
                rx.text("Ejercicios Propuestos 1, 2, 3 y 4 — Desarrollo de Aplicaciones", color=PALETA["texto_secundario"]),
                align="center",
                spacing="1",
            ),
            barra_navegacion(),
            rx.divider(border_color=PALETA["borde"]),
            rx.cond(
                EstadoApp.vista_activa == "ej1",
                vista_tablero_kanban(),
                rx.cond(
                    EstadoApp.vista_activa == "ej2",
                    panel_indicadores(),
                    rx.cond(
                        EstadoApp.vista_activa == "ej3",
                        vista_registro_solicitudes(),
                        vista_directorio_usuarios(),
                    ),
                ),
            ),
            spacing="5",
            width="100%",
            max_width="1080px",
            padding_y="2rem",
            padding_x="1.5rem",
        ),
        width="100%",
        min_height="100vh",
        background_color=PALETA["fondo_app"],
        color=PALETA["texto_principal"],
    )


app = rx.App()
app.add_page(index, title="Cuaderno de Encargos - Ejercicios 1 al 4")