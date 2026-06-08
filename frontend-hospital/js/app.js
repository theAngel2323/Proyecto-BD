/*
 * app.js - Configuracion central de la API y funciones de ayuda
 */

const API_BASE = "http://127.0.0.1:8000/api";

const Auth = {
  getToken: function () {
    return localStorage.getItem("hdb_token");
  },
  getUser: function () {
    try {
      return JSON.parse(localStorage.getItem("hdb_user"));
    } catch (e) {
      return null;
    }
  },
  setSession: function (token, user) {
    localStorage.setItem("hdb_token", token);
    localStorage.setItem("hdb_user", JSON.stringify(user));

    // --- EL FIX DE SEGURIDAD AQUÍ ---
    // Extraemos el id_rol del usuario y lo guardamos para el layout.js
    if (user && user.id_rol) {
      localStorage.setItem("id_rol", user.id_rol);
    } else if (user && user.ROL_id_rol) {
      // Por si tu backend lo envía así
      localStorage.setItem("id_rol", user.ROL_id_rol);
    }
  },
  clear: function () {
    localStorage.removeItem("hdb_token");
    localStorage.removeItem("hdb_user");
    localStorage.removeItem("id_rol"); // Limpiamos también el rol al salir
  },
  isLoggedIn: function () {
    return !!localStorage.getItem("hdb_token");
  },
  requireLogin: function () {
    if (!this.isLoggedIn()) {
      window.location.href = "index.html";
    }
  },
};

function showToast(mensaje, tipo = "success") {
  // Si no existe el contenedor, lo creamos
  var container = document.getElementById("toast-container");
  if (!container) {
    container = document.createElement("div");
    container.id = "toast-container";
    document.body.appendChild(container);
  }

  // Seleccionamos el ícono correcto de Tabler Icons
  var icon = "ti-circle-check";
  if (tipo === "error") icon = "ti-alert-circle";
  if (tipo === "info") icon = "ti-info-circle";

  // Color del ícono
  var iconColor =
    tipo === "success" ? "#10b981" : tipo === "error" ? "#ef4444" : "#3b82f6";

  // Creamos la alerta
  var toast = document.createElement("div");
  toast.className = "toast-msg toast-" + tipo;
  toast.innerHTML =
    '<i class="ti ' +
    icon +
    '" style="font-size: 20px; color: ' +
    iconColor +
    '"></i><span>' +
    mensaje +
    "</span>";

  container.appendChild(toast);

  // Animación de entrada
  setTimeout(function () {
    toast.classList.add("show");
  }, 10);

  // Animación de salida y destrucción a los 3 segundos
  setTimeout(function () {
    toast.classList.remove("show");
    setTimeout(function () {
      toast.remove();
    }, 300);
  }, 3000);
}

async function apiRequest(method, endpoint, body) {
  var headers = { "Content-Type": "application/json" };
  var token = Auth.getToken();
  if (token) headers["Authorization"] = "Bearer " + token;

  var options = { method: method, headers: headers };
  if (body) options.body = JSON.stringify(body);

  var response = await fetch(API_BASE + endpoint, options);

  if (response.status === 401) {
    Auth.clear();
    window.location.href = "index.html";
    return;
  }
  if (!response.ok) {
    var errorData = await response.json().catch(function () {
      return {};
    });
    throw new Error(errorData.detail || "Error " + response.status);
  }
  var text = await response.text();
  return text ? JSON.parse(text) : null;
}

var API = {
  // --- Autenticacion ---
  login: async function (username, password) {
    var data = await apiRequest("POST", "/auth/login", {
      username: username,
      password: password,
    });
    if (data && data.id_rol) {
      localStorage.setItem("id_rol", data.id_rol);
    }

    return data;
  },
  logout: function () {
    return apiRequest("POST", "/auth/logout");
  },

  // --- Pacientes ---
  getPacientes: function () {
    return apiRequest("GET", "/pacientes/");
  },
  getPaciente: function (id) {
    return apiRequest("GET", "/pacientes/" + id);
  },
  crearPaciente: function (data) {
    return apiRequest("POST", "/pacientes/", data);
  },
  editarPaciente: function (id, data) {
    return apiRequest("PUT", "/pacientes/" + id, data);
  },
  eliminarPaciente: function (id) {
    return apiRequest("DELETE", "/pacientes/" + id);
  },

  // --- Citas ---
  getCitas: function () {
    return apiRequest("GET", "/citas/");
  },
  crearCita: function (data) {
    return apiRequest("POST", "/citas/", data);
  },
  completarCita: function (id) {
    return apiRequest("PATCH", "/citas/" + id + "/completar");
  },
  cancelarCita: function (id) {
    return apiRequest("PATCH", "/citas/" + id + "/cancelar");
  },

  // --- Inventario ---
  getInventario: function () {
    return apiRequest("GET", "/inventario/");
  },
  getStockCritico: function () {
    return apiRequest("GET", "/inventario/stock-critico");
  },
  entradaStock: function (data) {
    return apiRequest("POST", "/inventario/entrada", data);
  },

  // --- Prescripciones y diagnosticos ---
  crearDiagnostico: function (data) {
    return apiRequest("POST", "/prescripciones/diagnostico", data);
  },
  crearPrescripcion: function (data) {
    return apiRequest("POST", "/prescripciones/", data);
  },
  getTopMedicamentos: function () {
    return apiRequest("GET", "/prescripciones/top-medicamentos");
  },
  getDiagnosticosPorCita: function (idCita) {
    return apiRequest("GET", "/prescripciones/cita/" + idCita);
  },

  // --- Ingresos ---
  getIngresos: function (idArea) {
    var url = "/ingresos/";
    if (idArea) url += "?id_area=" + idArea;
    return apiRequest("GET", url);
  },
  crearIngreso: function (data) {
    return apiRequest("POST", "/ingresos/", data);
  },
  getOcupacion: function () {
    return apiRequest("GET", "/ingresos/ocupacion");
  },
  darEgreso: function (idIngreso) {
    return apiRequest("PATCH", "/ingresos/" + idIngreso + "/egreso");
  },

  // --- Administracion de Usuarios y Auditoria ---
  getUsuarios: function () {
    return apiRequest("GET", "/usuarios/");
  },
  crearUsuario: function (data) {
    return apiRequest("POST", "/usuarios/", data);
  },
  getAuditoria: function () {
    return apiRequest("GET", "/usuarios/auditoria");
  },
  getRoles: function () {
    return apiRequest("GET", "/usuarios/roles");
  },
  getPrivilegios: function (idRol) {
    return apiRequest("GET", "/usuarios/roles/" + idRol + "/privilegios");
  },
  
  // --- Administracion de Usuarios y Auditoria ---
  getUsuarios: function () {
    return apiRequest("GET", "/usuarios/");
  },
  crearUsuario: function (data) {
    return apiRequest("POST", "/usuarios/", data);
  },
  editarUsuario: function (id, data) {
    return apiRequest("PATCH", "/usuarios/" + id, data); // Agrega esta línea
  },
};

function showAlert(containerId, message, type) {
  var iconMap = {
    error: "ti-alert-circle",
    success: "ti-circle-check",
    warning: "ti-alert-triangle",
    info: "ti-info-circle",
  };
  var icon = iconMap[type] || "ti-info-circle";
  var container = document.getElementById(containerId);
  if (!container) return;
  container.innerHTML =
    '<div class="alert alert-' +
    type +
    '">' +
    '<i class="ti ' +
    icon +
    '"></i>' +
    "<span>" +
    message +
    "</span>" +
    "</div>";
  container.classList.remove("hidden");
}

function hideAlert(containerId) {
  var container = document.getElementById(containerId);
  if (container) container.classList.add("hidden");
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
  if (!dateStr) return "-";
  try {
    return new Date(dateStr).toLocaleDateString("es-GT", {
      day: "2-digit",
      month: "short",
      year: "numeric",
    });
  } catch (e) {
    return dateStr;
  }
}

function formatTime(dateStr) {
  if (!dateStr) return "";
  try {
    return new Date(dateStr).toLocaleTimeString("es-GT", {
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch (e) {
    return "";
  }
}

function initUserUI() {
  var user = Auth.getUser();
  if (!user) return;
  var initials = (user.username || "US").slice(0, 2).toUpperCase();
  document.querySelectorAll(".user-avatar").forEach(function (el) {
    el.textContent = initials;
  });
  document.querySelectorAll(".sidebar-user-name").forEach(function (el) {
    el.textContent = user.username || "Usuario";
  });
  document.querySelectorAll(".sidebar-user-role").forEach(function (el) {
    el.textContent = user.rol || "usuario";
  });
}

function initLogout() {
  document.querySelectorAll(".logout-btn").forEach(function (btn) {
    btn.addEventListener("click", async function (e) {
      e.preventDefault();
      try {
        await API.logout();
      } catch (err) {}
      Auth.clear();
      window.location.href = "index.html";
    });
  });
}

function openModal(id) {
  document.getElementById(id).classList.remove("hidden");
}

function closeModal(id) {
  document.getElementById(id).classList.add("hidden");
}
