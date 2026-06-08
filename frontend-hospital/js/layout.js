var PAGES = [
  {
    href: "dashboard.html",
    icon: "ti-layout-dashboard",
    label: "Dashboard",
    id: "dashboard",
  },
  {
    href: "pacientes.html",
    icon: "ti-users",
    label: "Pacientes",
    id: "pacientes",
  },
  {
    href: "citas.html",
    icon: "ti-calendar",
    label: "Citas Medicas",
    id: "citas",
  },
  {
    href: "prescripciones.html",
    icon: "ti-stethoscope",
    label: "Prescripciones",
    id: "prescripciones",
  },
  { href: "ingresos.html", icon: "ti-bed", label: "Ingresos", id: "ingresos" },
  {
    href: "administracion.html",
    icon: "ti-shield",
    label: "Administracion",
    id: "administracion",
  },
  { href: "etl.html", icon: "ti-upload", label: "Carga de Datos", id: "etl" },
  {
    href: "reportes.html",
    icon: "ti-chart-bar",
    label: "Reportes",
    id: "reportes",
  },
];

async function aplicarSeguridadMenu() {
  // 1. Intentamos buscar el rol suelto en la memoria
  let idRol = localStorage.getItem("id_rol");

  // 2. Si no lo encuentra, lo busca dentro de los datos del usuario (hdb_user)
  if (!idRol || idRol === "undefined" || idRol === "null") {
    try {
      const userObj = JSON.parse(localStorage.getItem("hdb_user") || "{}");
      idRol = userObj.id_rol || userObj.ROL_id_rol;
    } catch (e) {
      console.warn("No se pudo leer hdb_user");
    }
  }

  console.log("ID de Rol detectado por el sistema:", idRol);

  if (!idRol) {
    console.error(
      "Alerta: No se encontró ningún id_rol en memoria. El menú no se ocultará.",
    );
    return;
  }

  try {
    const res = await fetch(
      `http://127.0.0.1:8000/api/usuarios/roles/${idRol}/modulos`,
    );
    const permitidos = await res.json();

    console.log(
      "Módulos permitidos devueltos por la base de datos:",
      permitidos,
    );

    // 3. Ocultar basado en el ID
    PAGES.forEach((p) => {
      const el = document.querySelector(`.menu-item-${p.id}`);
      if (el) {
        if (permitidos.includes(p.id)) {
          el.style.display = "block";
        } else {
          el.style.display = "none";
          console.log("Ocultando pestaña prohibida:", p.id);
        }
      }
    });
  } catch (e) {
    console.error("Error de red al consultar seguridad:", e);
  }
}

function renderLayout(activePage) {
  var topnavEl = document.getElementById("topnav");
  if (topnavEl) {
    topnavEl.innerHTML =
      '<a href="dashboard.html" class="topnav-logo"><span>HospitalDB</span></a>' +
      '<div class="topnav-right"><div class="user-avatar"></div></div>';
  }

  var sidebarEl = document.getElementById("sidebar");
  if (sidebarEl) {
    var navLinks = PAGES.map(function (p) {
      var isActive = activePage === p.href ? "active" : "";
      // AQUÍ ESTÁ LA CLAVE: Agregamos la clase menu-item-ID
      return (
        '<a href="' +
        p.href +
        '" class="nav-item menu-item-' +
        p.id +
        " " +
        isActive +
        '">' +
        '<i class="ti ' +
        p.icon +
        '"></i>' +
        p.label +
        "</a>"
      );
    }).join("");

    sidebarEl.innerHTML =
      '<div class="sidebar-user"><div class="sidebar-user-role">...</div></div>' +
      '<nav style="flex:1; padding:10px 0;">' +
      navLinks +
      "</nav>" +
      '<div class="sidebar-footer"><a href="#" class="nav-item nav-item-danger logout-btn"><i class="ti ti-logout"></i>Cerrar Sesion</a></div>';
  }

  // 1. Ejecutar la seguridad
  aplicarSeguridadMenu();

  // 2. Otras inicializaciones
  initUserUI();
  initLogout();
}
