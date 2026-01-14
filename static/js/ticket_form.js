document.addEventListener('DOMContentLoaded', function() {
    const addDetailBtn = document.getElementById('add-detail');
    const detailForms = document.getElementById('detail-forms');
    const totalFormsInput = document.querySelector('[name="form-TOTAL_FORMS"]');
    let formIndex = parseInt(totalFormsInput.value);

    // Función para crear un nuevo form de detalle
    function createDetailForm(index) {
        const template = `
            <tr class="detail-form border-b border-gray-200 hover:bg-gray-50" data-form-index="${index}">
                <td class="px-2 py-1.5">
                    <input type="text" name="form-${index}-product" maxlength="255" required class="block w-full px-2 py-1 text-xs border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-slate-500 focus:border-slate-500" id="id_form-${index}-product">
                </td>
                <td class="px-2 py-1.5">
                    <input type="number" name="form-${index}-quantity" step="0.00000001" min="0" required class="block w-full px-2 py-1 text-xs text-right border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-slate-500 focus:border-slate-500 quantity-input" id="id_form-${index}-quantity">
                </td>
                <td class="px-2 py-1.5">
                    <input type="number" name="form-${index}-unit_price" step="0.00000001" min="0" required class="block w-full px-2 py-1 text-xs text-right border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-slate-500 focus:border-slate-500 price-input" id="id_form-${index}-unit_price">
                </td>
                <td class="px-2 py-1.5 text-right">
                    <span class="text-xs font-medium text-gray-700 row-subtotal">$0.00</span>
                </td>
                <td class="px-2 py-1.5 text-center">
                    <input type="hidden" name="form-${index}-id" id="id_form-${index}-id">
                    <button type="button" class="remove-detail inline-flex items-center justify-center w-6 h-6 text-red-600 hover:bg-red-50 rounded border border-red-300 hover:border-red-400">
                        <i class="fas fa-times text-xs"></i>
                    </button>
                </td>
            </tr>
        `;
        return template;
    }

    // Agregar nuevo detalle
    if (addDetailBtn) {
        addDetailBtn.addEventListener('click', function() {
            const newFormHtml = createDetailForm(formIndex);
            detailForms.insertAdjacentHTML('beforeend', newFormHtml);
            formIndex++;
            totalFormsInput.value = formIndex;
            updateTotals();
        });
    }

    // Remover detalle
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('remove-detail') || e.target.closest('.remove-detail')) {
            e.preventDefault();
            const detailForm = e.target.closest('.detail-form');
            const currentForms = detailForms.querySelectorAll('.detail-form:not([style*="display: none"])').length;

            if (currentForms <= 1) {
                alert('Debe mantener al menos un detalle en el ticket.');
                return;
            }

            // Si tiene un campo DELETE (formset de Django), marcarlo
            const deleteInput = detailForm.querySelector('input[name*="DELETE"]');
            if (deleteInput) {
                deleteInput.checked = true;
                detailForm.style.display = 'none';
            } else {
                // Si es un formulario nuevo, simplemente eliminarlo
                detailForm.remove();
                formIndex--;
                totalFormsInput.value = formIndex;
            }
            updateTotals();
        }
    });

    // Calcular totales en tiempo real
    function updateTotals() {
        let subtotal = 0;
        const visibleForms = detailForms.querySelectorAll('.detail-form:not([style*="display: none"])');

        visibleForms.forEach(form => {
            const quantityInput = form.querySelector('input[name*="quantity"]');
            const priceInput = form.querySelector('input[name*="unit_price"]');
            const rowSubtotalSpan = form.querySelector('.row-subtotal');

            if (quantityInput && priceInput) {
                const quantity = parseFloat(quantityInput.value) || 0;
                const price = parseFloat(priceInput.value) || 0;
                const rowSubtotal = quantity * price;
                subtotal += rowSubtotal;

                if (rowSubtotalSpan) {
                    rowSubtotalSpan.textContent = `$${rowSubtotal.toFixed(2)}`;
                }
            }
        });

        const ivaPercentage = parseFloat(document.getElementById('iva-percentage').textContent) || 0;
        const ivaAmount = subtotal * (ivaPercentage / 100);
        const total = subtotal + ivaAmount;

        document.getElementById('subtotal-display').textContent = `$${subtotal.toFixed(2)}`;
        document.getElementById('iva-display').textContent = `$${ivaAmount.toFixed(2)}`;
        document.getElementById('total-display').textContent = `$${total.toFixed(2)}`;
    }

    // Actualizar totales al cambiar cantidad o precio
    document.addEventListener('input', function(e) {
        if (e.target.classList.contains('quantity-input') || e.target.classList.contains('price-input')) {
            updateTotals();
        }
    });

    // Calcular totales iniciales
    updateTotals();
});