# Sistema de Gestión de Inventario y Ventas (Estilo ERP)

Sistema de gestión de inventario y ventas desarrollado con Flask, diseñado para simular un entorno empresarial real enfocado en un negocio de repuestos automotrices.

Este proyecto fue desarrollado como parte de mi portafolio backend, con el objetivo de demostrar arquitectura modular, implementación de reglas de negocio y control de acceso basado en roles.

---

# Características Principales

- Arquitectura modular utilizando Flask Blueprints
- Control de acceso por roles (Administrador / Vendedor)
- Servicio centralizado para gestión de inventario (InventoryService)
- Registro de movimientos de inventario:
  - Entradas (compras)
  - Salidas (daños / pérdidas)
  - Ajustes
- Alertas de bajo stock
- Detección de productos sin rotación (30/60/90 días)
- Eliminación lógica (archivado de productos)
- Registro de auditoría de acciones
- Generación de reportes en PDF
- Interfaz profesional estilo ERP

---

##  Aspectos Técnicos Destacados

- Separación de responsabilidades (módulos + capa de servicios)
- Lógica de negocio centralizada para evitar inconsistencias
- Protección de rutas mediante decoradores por rol
- Estructura de carpetas preparada para escalabilidad
- Scripts de actualización de esquema de base de datos

---

##  Tecnologías Utilizadas

- Python
- Flask
- SQLAlchemy
- SQLite
- Jinja2
- HTML / CSS
- JavaScript

---

##  Instalación

Clonar el repositorio:

```bash
git clone https://github.com/tapt2108-dotcom/inventario-flask-erp.git
cd inventario-flask-erp
