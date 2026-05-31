/*
 * app.js - Configuracion central de la API y funciones de ayuda

 */

const API_BASE = 'http://127.0.0.1:8000/api';

const Auth = {
    getToken: function() {
        return localStorage.getItem('hdb_token');
    },
    getUser: function() {
        try {
            return JSON.parse(localStorage.getItem('hdb_user'));
        } catch (e) {
            return null;
        }
    },
    setSession: function(token, user) {
        localStorage.setItem('hdb_token', token);
        localStorage.setItem('hdb_user', JSON.stringify(user));
    },
    clear: function() {
        localStorage.removeItem('hdb_token');
        localStorage.removeItem('hdb_user');
    },
    isLoggedIn: function() {
        return !!localStorage.getItem('hdb_token');
    },
    requireLogin: function() {
        if (!this.isLoggedIn()) {
            window.location.href = 'index.html';
        }
    }
};

async function apiRequest(method, endpoint, body) {
    var headers = { 'Content-Type': 'application/json' };
    var token = Auth.getToken();
    if (token) headers['Authorization'] = 'Bearer ' + token;

    var options = { method: method, headers: headers };
    if (body) options.body = JSON.stringify(body);

    var response = await fetch(API_BASE + endpoint, options);

    if (response.status === 401) {
        Auth.clear();
        window.location.href = 'index.html';
        return;
    }
    if (!response.ok) {
        var errorData = await response.json().catch(function() { return {}; });
        throw new Error(errorData.detail || 'Error ' + response.status);
    }
    var text = await response.text();
    return text ? JSON.parse(text) : null;
}

var API = {

    // --- Autenticacion ---
    login: function(username, password) {
        return apiRequest('POST', '/auth/login', { username: username, password: password });
    },
    logout: function() {
        return apiRequest('POST', '/auth/logout');
    },

    // --- Pacientes ---
    getPacientes: function() {
        return apiRequest('GET', '/pacientes/');
    },
    getPaciente: function(id) {
        return apiRequest('GET', '/pacientes/' + id);
    },
    crearPaciente: function(data) {
        return apiRequest('POST', '/pacientes/', data);
    },
    editarPaciente: function(id, data) {
        return apiRequest('PUT', '/pacientes/' + id, data);
    },
    eliminarPaciente: function(id) {
        return apiRequest('DELETE', '/pacientes/' + id);
    },

    // --- Citas ---
    getCitas: function() {
        return apiRequest('GET', '/citas/');
    },
    crearCita: function(data) {
        return apiRequest('POST', '/citas/', data);
    },
    completarCita: function(id) {
        return apiRequest('PATCH', '/citas/' + id + '/completar');
    },
    cancelarCita: function(id) {
        return apiRequest('PATCH', '/citas/' + id + '/cancelar');
    },

    // --- Inventario ---
    getInventario: function() {
        return apiRequest('GET', '/inventario/');
    },
    getStockCritico: function() {
        return apiRequest('GET', '/inventario/stock-critico');
    },
    entradaStock: function(data) {
        return apiRequest('POST', '/inventario/entrada', data);
    },

    // --- Prescripciones y diagnosticos ---
    crearDiagnostico: function(data) {
        return apiRequest('POST', '/prescripciones/diagnostico', data);
    },
    crearPrescripcion: function(data) {
        return apiRequest('POST', '/prescripciones/', data);
    },
    getTopMedicamentos: function() {
        return apiRequest('GET', '/prescripciones/top-medicamentos');
    },
    getDiagnosticosPorCita: function(idCita) {
        return apiRequest('GET', '/prescripciones/cita/' + idCita);
    },

    // --- Ingresos ---
    getIngresos: function(idArea) {
        var url = '/ingresos/';
        if (idArea) url += '?id_area=' + idArea;
        return apiRequest('GET', url);
    },
    crearIngreso: function(data) {
        return apiRequest('POST', '/ingresos/', data);
    },
    getOcupacion: function() {
        return apiRequest('GET', '/ingresos/ocupacion');
    },
    darEgreso: function(idIngreso) {
        return apiRequest('PATCH', '/ingresos/' + idIngreso + '/egreso');
    }

    /*
     * NOTA: Administracion de usuarios no tiene endpoint en el backend.
     * Su pagina muestra datos estaticos.
     */
};

function showAlert(containerId, message, type) {
    var iconMap = {
        error:   'ti-alert-circle',
        success: 'ti-circle-check',
        warning: 'ti-alert-triangle',
        info:    'ti-info-circle'
    };
    var icon = iconMap[type] || 'ti-info-circle';
    var container = document.getElementById(containerId);
    if (!container) return;
    container.innerHTML =
        '<div class="alert alert-' + type + '">' +
        '<i class="ti ' + icon + '"></i>' +
        '<span>' + message + '</span>' +
        '</div>';
    container.classList.remove('hidden');
}

function hideAlert(containerId) {
    var container = document.getElementById(containerId);
    if (container) container.classList.add('hidden');
}

function setLoading(btnId, loading) {
    var btn = document.getElementById(btnId);
    if (!btn) return;
    if (loading) {
        btn.dataset.originalText = btn.innerHTML;
        btn.innerHTML = '<span class="spinner"></span>';
        btn.disabled = true;
    } else {
        btn.innerHTML = btn.dataset.originalText || btn.innerHTML;
        btn.disabled = false;
    }
}

function formatDate(dateStr) {
    if (!dateStr) return '-';
    try {
        return new Date(dateStr).toLocaleDateString('es-GT', {
            day: '2-digit', month: 'short', year: 'numeric'
        });
    } catch (e) { return dateStr; }
}

function formatTime(dateStr) {
    if (!dateStr) return '';
    try {
        return new Date(dateStr).toLocaleTimeString('es-GT', {
            hour: '2-digit', minute: '2-digit'
        });
    } catch (e) { return ''; }
}

function initUserUI() {
    var user = Auth.getUser();
    if (!user) return;
    var initials = (user.username || 'US').slice(0, 2).toUpperCase();
    document.querySelectorAll('.user-avatar').forEach(function(el) {
        el.textContent = initials;
    });
    document.querySelectorAll('.sidebar-user-name').forEach(function(el) {
        el.textContent = user.username || 'Usuario';
    });
    document.querySelectorAll('.sidebar-user-role').forEach(function(el) {
        el.textContent = user.rol || 'usuario';
    });
}

function initLogout() {
    document.querySelectorAll('.logout-btn').forEach(function(btn) {
        btn.addEventListener('click', async function(e) {
            e.preventDefault();
            try { await API.logout(); } catch (err) {}
            Auth.clear();
            window.location.href = 'index.html';
        });
    });
}

function openModal(id) {
    document.getElementById(id).classList.remove('hidden');
}

function closeModal(id) {
    document.getElementById(id).classList.add('hidden');
}