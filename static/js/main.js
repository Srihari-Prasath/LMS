// Sidebar toggle for mobile
document.addEventListener('DOMContentLoaded', function() {
    const sidebarToggle = document.getElementById('sidebarToggle');
    const wrapper = document.getElementById('wrapper');

    if (sidebarToggle && wrapper) {
        sidebarToggle.addEventListener('click', function(e) {
            e.preventDefault();
            wrapper.classList.toggle('toggled');
        });

        // Close sidebar on outside click (mobile)
        document.addEventListener('click', function(e) {
            if (window.innerWidth < 992 && wrapper.classList.contains('toggled')) {
                if (!e.target.closest('#sidebar-wrapper') && !e.target.closest('#sidebarToggle')) {
                    wrapper.classList.remove('toggled');
                }
            }
        });
    }

    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            bsAlert.close();
        }, 5000);
    });
});
