/* ============================================================
   Chile Explorer - JavaScript personalizado
   Pequeñas mejoras de interacción (no es una SPA).
   ============================================================ */

// Coloca el año actual en el pie de página automáticamente.
function actualizarAnioFooter() {
    var anio = document.getElementById("anio-actual");
    if (anio) {
        anio.textContent = new Date().getFullYear();
    }
}

// Oculta las alertas de Bootstrap después de unos segundos.
function ocultarAlertasAutomaticamente() {
    var alertas = document.querySelectorAll(".alert-auto-ocultar");
    alertas.forEach(function (alerta) {
        setTimeout(function () {
            var bootstrapAlerta = bootstrap.Alert.getOrCreateInstance(alerta);
            bootstrapAlerta.close();
        }, 5000);
    });
}

// Muestra un enlace "volver arriba" al hacer scroll.
function inicializarBotonVolverArriba() {
    var boton = document.getElementById("btn-volver-arriba");
    if (!boton) {
        return;
    }
    window.addEventListener("scroll", function () {
        boton.style.display = window.scrollY > 300 ? "block" : "none";
    });
    boton.addEventListener("click", function () {
        window.scrollTo({ top: 0, behavior: "smooth" });
    });
}

// Inicialización cuando el documento está listo.
document.addEventListener("DOMContentLoaded", function () {
    actualizarAnioFooter();
    ocultarAlertasAutomaticamente();
    inicializarBotonVolverArriba();
});