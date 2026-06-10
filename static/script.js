// static/script.js
// Small UI helpers: search filter, dynamic order items, subtle animations

// Client-side table search (name column) for medicines
document.addEventListener('DOMContentLoaded', () => {
  // Apply fade-in animation to main content
  const main = document.querySelector('main');
  if (main) {
    main.style.opacity = 0;
    setTimeout(() => {
      main.style.transition = 'opacity 400ms ease';
      main.style.opacity = 1;
    }, 50);
  }

  const searchInput = document.getElementById('searchInput');
  const medTable = document.getElementById('medTable');
  if (searchInput && medTable) {
    searchInput.addEventListener('input', () => {
      const term = searchInput.value.toLowerCase();
      medTable.querySelectorAll('tbody tr').forEach(row => {
        const nameCell = row.querySelector('td:first-child');
        const text = (nameCell?.textContent || '').toLowerCase();
        row.style.display = text.includes(term) ? '' : 'none';
      });
    });
  }
});

// Dynamic order item rows
function addItemRow() {
  const container = document.getElementById('itemsContainer');
  if (!container) return;

  const template = container.querySelector('.item-row');
  const clone = template.cloneNode(true);

  // Reset values
  clone.querySelectorAll('input').forEach(i => i.value = '1');
  clone.querySelectorAll('select').forEach(s => s.selectedIndex = 0);

  container.appendChild(clone);
  lucide.createIcons(); // refresh icons in new row
}

function removeItemRow(btn) {
  const row = btn.closest('.item-row');
  const container = document.getElementById('itemsContainer');
  if (container && row && container.querySelectorAll('.item-row').length > 1) {
    row.remove();
  }
}
