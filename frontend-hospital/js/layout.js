/*
 * layout.js - Genera el topnav y sidebar de forma dinamica
 * Cada pagina llama a renderLayout() pasando su propio nombre de archivo
 */

var PAGES = [
    { href: 'dashboard.html',      icon: 'ti-layout-dashboard', label: 'Dashboard'       },
    { href: 'pacientes.html',      icon: 'ti-users',            label: 'Pacientes'       },
    { href: 'citas.html',          icon: 'ti-calendar',         label: 'Citas Medicas'   },
    { href: 'prescripciones.html', icon: 'ti-stethoscope',      label: 'Prescripciones'  },
    { href: 'ingresos.html',       icon: 'ti-bed',              label: 'Ingresos'        },
    { href: 'administracion.html', icon: 'ti-shield',           label: 'Administracion'  },
    { href: 'etl.html',            icon: 'ti-upload',           label: 'Carga de Datos'  },
    { href: 'reportes.html',       icon: 'ti-chart-bar',        label: 'Reportes'        }
];

/*
 * Construye el topnav y el sidebar en la pagina actual
 * activePage: nombre del archivo HTML de la pagina actual
 */
function renderLayout(activePage) {

    // Topnav: Logo y avatar
    var topnavEl = document.getElementById('topnav');
    if (topnavEl) {
        topnavEl.innerHTML =
            '<a href="dashboard.html" class="topnav-logo">' +
                '<span>HospitalDB</span>' +
            '</a>' +
            '<div class="topnav-right">' +
                '<div class="user-avatar"></div>' +
            '</div>';
    }

    // Sidebar: lista completa de modulos
    var sidebarEl = document.getElementById('sidebar');
    if (sidebarEl) {
        var navLinks = PAGES.map(function(p) {
            var isActive = activePage === p.href ? 'active' : '';
            return '<a href="' + p.href + '" class="nav-item ' + isActive + '">' +
                '<i class="ti ' + p.icon + '"></i>' +
                p.label +
            '</a>';
        }).join('');

        sidebarEl.innerHTML =
            '<div class="sidebar-user">' +
                '<div class="sidebar-user-role">Cargando...</div>' +
                '<div class="sidebar-user-name">...</div>' +
            '</div>' +
            '<nav style="flex:1; padding:10px 0;">' +
                navLinks +
            '</nav>' +
            '<div class="sidebar-footer">' +
                '<a href="#" class="nav-item nav-item-danger logout-btn">' +
                    '<i class="ti ti-logout"></i>Cerrar Sesion' +
                '</a>' +
            '</div>';
    }

    initUserUI();
    initLogout();
}