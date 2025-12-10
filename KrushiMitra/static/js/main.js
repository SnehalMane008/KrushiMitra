/**
 * KrushiMitra - Agricultural Store Management System
 * Established: April 9, 2025
 * 
 * Main JavaScript file with optimizations
 */

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    initTooltips();
    
    // Initialize data tables
    initDataTables();
    
    // Setup dynamic form handlers
    setupDynamicForms();
    
    // Handle flash messages auto-dismiss
    setupFlashMessages();
    
    // Add loading indicators for forms
    setupLoadingIndicators();
});

/**
 * Initialize Bootstrap tooltips
 */
function initTooltips() {
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    [...tooltipTriggerList].map(tooltipTriggerEl => {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Initialize DataTables for better table interaction
 */
function initDataTables() {
    // Check if DataTable library is available and tables exist
    if (typeof $.fn.DataTable !== 'undefined' && document.querySelector('.data-table')) {
        $('.data-table').DataTable({
            responsive: true,
            language: {
                search: "_INPUT_",
                searchPlaceholder: "Search...",
                lengthMenu: "Show _MENU_ entries",
                info: "Showing _START_ to _END_ of _TOTAL_ entries",
                infoEmpty: "Showing 0 to 0 of 0 entries",
                infoFiltered: "(filtered from _MAX_ total entries)"
            },
            pageLength: 10,
            dom: '<"top"fl>rt<"bottom"ip>',
            initComplete: function() {
                // Add custom styling to DataTables elements
                $('.dataTables_filter input').addClass('form-control');
                $('.dataTables_length select').addClass('form-select');
            }
        });
    }
}

/**
 * Setup dynamic forms for sales and other multi-item forms
 */
function setupDynamicForms() {
    // Handle dynamic form fields for sales form
    const addItemBtn = document.getElementById('add-item-btn');
    if (addItemBtn) {
        addItemBtn.addEventListener('click', function() {
            const itemsContainer = document.getElementById('items-container');
            const itemCount = itemsContainer.querySelectorAll('.item-row').length;
            
            // Create new item row
            const newRow = document.createElement('div');
            newRow.className = 'row item-row mb-3';
            newRow.innerHTML = `
                <div class="col-md-5">
                    <select name="product_id[]" class="form-select" required>
                        <option value="">Select Product</option>
                        ${document.querySelector('select[name="product_id[]"]').innerHTML.split('<option value="">Select Product</option>')[1]}
                    </select>
                </div>
                <div class="col-md-5">
                    <input type="number" name="quantity[]" class="form-control" placeholder="Quantity" min="1" required>
                </div>
                <div class="col-md-2">
                    <button type="button" class="btn btn-danger remove-item"><i class="bi bi-trash"></i></button>
                </div>
            `;
            
            itemsContainer.appendChild(newRow);
            
            // Add event listener to remove button
            newRow.querySelector('.remove-item').addEventListener('click', function() {
                itemsContainer.removeChild(newRow);
            });
        });
    }
    
    // Remove item event delegation
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('remove-item') || e.target.parentElement.classList.contains('remove-item')) {
            const button = e.target.classList.contains('remove-item') ? e.target : e.target.parentElement;
            const row = button.closest('.item-row');
            if (row && row.parentElement) {
                row.parentElement.removeChild(row);
            }
        }
    });
}

/**
 * Setup auto-dismissing flash messages
 */
function setupFlashMessages() {
    const flashMessages = document.querySelectorAll('.alert-dismissible');
    flashMessages.forEach(function(message) {
        // Auto dismiss after 5 seconds
        setTimeout(function() {
            const closeBtn = message.querySelector('.btn-close');
            if (closeBtn) {
                closeBtn.click();
            }
        }, 5000);
    });
}

/**
 * Add loading indicators for form submissions
 */
function setupLoadingIndicators() {
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function() {
            const submitButton = form.querySelector('button[type="submit"]');
            if (submitButton) {
                const originalText = submitButton.innerHTML;
                submitButton.disabled = true;
                submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...';
                
                // If the form submission takes too long, re-enable the button after 10 seconds
                setTimeout(function() {
                    if (submitButton.disabled) {
                        submitButton.disabled = false;
                        submitButton.innerHTML = originalText;
                    }
                }, 10000);
            }
        });
    });
}

/**
 * Lazy loading images for better performance
 */
function lazyLoadImages() {
    if ('loading' in HTMLImageElement.prototype) {
        const images = document.querySelectorAll('img[loading="lazy"]');
        images.forEach(img => {
            img.src = img.dataset.src;
        });
    } else {
        // Fallback for browsers that don't support lazy loading
        const script = document.createElement('script');
        script.src = 'https://cdnjs.cloudflare.com/ajax/libs/lazysizes/5.3.2/lazysizes.min.js';
        document.body.appendChild(script);
    }
}

/**
 * Custom confirmation dialog
 * @param {string} message - The confirmation message
 * @param {function} callback - The callback function to execute if confirmed
 */
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// Add event listeners for delete buttons
document.addEventListener('click', function(e) {
    if (e.target.classList.contains('delete-btn') || e.target.parentElement.classList.contains('delete-btn')) {
        e.preventDefault();
        const button = e.target.classList.contains('delete-btn') ? e.target : e.target.parentElement;
        const url = button.getAttribute('href');
        const message = button.getAttribute('data-confirm') || 'Are you sure you want to delete this item?';
        
        confirmAction(message, function() {
            window.location.href = url;
        });
    }
}); 