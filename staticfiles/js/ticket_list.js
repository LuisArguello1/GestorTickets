document.addEventListener('DOMContentLoaded', function() {
    // Manejar eliminación de tickets
    document.querySelectorAll('.delete-ticket').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const url = this.getAttribute('data-url');
            const name = this.getAttribute('data-name');

            Swal.fire({
                title: '¿Eliminar Ticket?',
                text: `¿Estás seguro de que deseas eliminar el ticket "${name}"? Esta acción no se puede deshacer.`,
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#dc2626',
                cancelButtonColor: '#6b7280',
                confirmButtonText: 'Sí, eliminar',
                cancelButtonText: 'Cancelar'
            }).then((result) => {
                if (result.isConfirmed) {
                    // Crear y enviar formulario POST
                    const form = document.createElement('form');
                    form.method = 'POST';
                    form.action = url;

                    // Agregar CSRF token
                    const csrfInput = document.querySelector('#delete-form input[name=csrfmiddlewaretoken]');
                    if (csrfInput) {
                        form.appendChild(csrfInput.cloneNode(true));
                    }

                    document.body.appendChild(form);
                    form.submit();
                }
            });
        });
    });
});