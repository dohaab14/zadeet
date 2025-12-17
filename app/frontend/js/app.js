// Ce script gère l'affichage commun (Navbar) et les outils
document.addEventListener("DOMContentLoaded", () => {
    loadNavbar();
});

function loadNavbar() {
    const navbarHTML = `
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary shadow-sm mb-4">
      <div class="container-fluid">
        <a class="navbar-brand fw-bold d-flex align-items-center" href="/index.html">
          <img src="/static/logo.png" alt="Zadeet Logo" class="navbar-logo me-2" style="height: 40px; width: auto;">
          Zadeet
        </a>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav me-auto">
            <li class="nav-item"><a class="nav-link" href="/">Accueil</a></li>
            <li class="nav-item"><a class="nav-link" href="/transactions.html">Transactions</a></li>
            <li class="nav-item"><a class="nav-link" href="/categories.html">Catégories</a></li>
          </ul>
        </div>
        <button id="themeToggle" class="btn btn-warning" style="font-size: 1.5rem; padding: 0.5rem 0.75rem; white-space: nowrap;">
          🌙
        </button>
      </div>
    </nav>`;
    
    document.getElementById("navbar-placeholder").innerHTML = navbarHTML;
    
    // === Initialiser le thème sombre ===
    setupTheme();
}

function setupTheme() {
    const themeToggle = document.getElementById('themeToggle');
    
    if (!themeToggle) return;
    
    // Récupérer le thème sauvegardé
    const savedTheme = localStorage.getItem('theme') || 'light';
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-theme');
        themeToggle.textContent = '☀️';
    } else {
        themeToggle.textContent = '🌙';
    }
    
    // Écouter les clics
    themeToggle.addEventListener('click', () => {
        document.body.classList.toggle('dark-theme');
        const isDark = document.body.classList.contains('dark-theme');
        localStorage.setItem('theme', isDark ? 'dark' : 'light');
        themeToggle.textContent = isDark ? '☀️' : '🌙';
    });
}

// Fonction utilitaire pour formater l'argent
function formatMoney(amount) {
    return new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR' }).format(amount);
}

// Fonction utilitaire pour formater la date
function formatDate(dateString) {
    if (!dateString) return '';
    return new Date(dateString).toLocaleDateString('fr-FR');
}