// Ce script gère l'affichage commun (Navbar) et les outils
document.addEventListener("DOMContentLoaded", () => {
    loadNavbar();
});

function loadNavbar() {
    const navbarHTML = `
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary shadow-sm mb-4">
      <div class="container-fluid">
        <a class="navbar-brand fw-bold" href="/index.html"><i class="bi bi-wallet2 me-1"></i> Zadeet</a>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
        </button>
        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav me-auto">
            <li class="nav-item"><a class="nav-link" href="/index.html">Tableau de Bord</a></li>
            <li class="nav-item"><a class="nav-link" href="/transactions.html">Transactions</a></li>
            <li class="nav-item"><a class="nav-link" href="/categories.html">Catégories</a></li>
          </ul>
        </div>
      </div>
    </nav>`;
    
    document.getElementById("navbar-placeholder").innerHTML = navbarHTML;
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