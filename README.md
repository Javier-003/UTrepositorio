# Instalación de Gitea en Windows

## Requisitos previos

- Tener instalado Git para Windows: [Descargar Git](https://git-scm.com/download/win)
- Contar con permisos de administrador en el equipo.

## Pasos de instalación

1. **Descargar Gitea**
    - Accede a la página oficial: [https://dl.gitea.io/gitea/](https://dl.gitea.io/gitea/)
    - Descarga el archivo ejecutable para Windows (`gitea-x.x.x-windows-4.0-amd64.exe`).

2. **Crear una carpeta para Gitea**
    - Por ejemplo: `C:\gitea`

3. **Mover el ejecutable**
    - Copia el archivo descargado a la carpeta creada.

4. **Ejecutar Gitea**
    - Abre una terminal (CMD o PowerShell).
    - Navega a la carpeta de Gitea:  
      `cd C:\gitea`
    - Ejecuta el comando:  
      `.\gitea-x.x.x-windows-4.0-amd64.exe web`
    - Esto iniciará el servidor web de Gitea.

5. **Configurar Gitea**
    - Accede desde el navegador a: [http://localhost:3000](http://localhost:3000)
    - Sigue el asistente de configuración para definir la base de datos, usuario administrador y otros parámetros.

