document.addEventListener('DOMContentLoaded', function() {
    const sidebar = document.getElementById('sidebar');
    const sidebarToggle = document.getElementById('sidebarToggle');
    const mobileMenuToggle = document.getElementById('mobileMenuToggle');
    const overlay = document.getElementById('sidebarOverlay');

    if (!sidebar || !mobileMenuToggle || !overlay) {
        return;
    }

    function isMobile() {
        return window.innerWidth < 768;
    }

    function openSidebar() {
        sidebar.classList.add('show');
        overlay.classList.add('show');
        document.body.style.overflow = 'hidden';
    }

    function closeSidebar() {
        sidebar.classList.remove('show');
        overlay.classList.remove('show');
        document.body.style.overflow = '';
    }

    function syncToggleVisibility() {
        mobileMenuToggle.style.display = isMobile() ? 'block' : 'none';
        if (!isMobile()) {
            closeSidebar();
        }
    }

    syncToggleVisibility();

    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('show');
        });
    }

    mobileMenuToggle.addEventListener('click', openSidebar);
    overlay.addEventListener('click', closeSidebar);
    window.addEventListener('resize', syncToggleVisibility);

    let touchStartX = 0;
    let touchEndX = 0;

    sidebar.addEventListener('touchstart', function(e) {
        touchStartX = e.changedTouches[0].screenX;
    }, { passive: true });

    sidebar.addEventListener('touchend', function(e) {
        touchEndX = e.changedTouches[0].screenX;
        if (touchStartX - touchEndX > 50) {
            closeSidebar();
        }
    }, { passive: true });
});
// 移动端侧边栏切换逻辑
document.addEventListener('DOMContentLoaded', function () {
    const sidebar = document.getElementById('sidebar');
    const sidebarToggle = document.getElementById('sidebarToggle');
    const mobileMenuToggle = document.getElementById('mobileMenuToggle');
    const overlay = document.getElementById('sidebarOverlay');

    function isMobile() {
        return window.innerWidth < 768;
    }

    if (!sidebar || !mobileMenuToggle || !overlay) {
        return;
    }

    if (isMobile()) {
        mobileMenuToggle.style.display = 'block';
    }

    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function () {
            sidebar.classList.toggle('show');
        });
    }

    mobileMenuToggle.addEventListener('click', function () {
        sidebar.classList.add('show');
        overlay.classList.add('show');
        document.body.style.overflow = 'hidden';
    });

    overlay.addEventListener('click', function () {
        sidebar.classList.remove('show');
        overlay.classList.remove('show');
        document.body.style.overflow = '';
    });

    window.addEventListener('resize', function () {
        if (!isMobile()) {
            mobileMenuToggle.style.display = 'none';
            overlay.classList.remove('show');
            document.body.style.overflow = '';
        } else {
            mobileMenuToggle.style.display = 'block';
        }
    });

    let touchStartX = 0;
    let touchEndX = 0;

    sidebar.addEventListener('touchstart', function (e) {
        touchStartX = e.changedTouches[0].screenX;
    }, { passive: true });

    sidebar.addEventListener('touchend', function (e) {
        touchEndX = e.changedTouches[0].screenX;
        if (touchStartX - touchEndX > 50) {
            sidebar.classList.remove('show');
            overlay.classList.remove('show');
            document.body.style.overflow = '';
        }
    }, { passive: true });
});

